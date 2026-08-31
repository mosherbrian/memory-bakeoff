from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import time
from typing import Any, Mapping

from memory_bakeoff.llm.base import LLMMessage, LLMRequest
from memory_bakeoff.llm.sidecar import ChatGPTSidecarLLM


class SidecarOpenAIProxy:
    """Local OpenAI + Anthropic compatibility bridge backed by ChatGPTSidecarLLM.

    Supported HTTP surfaces:
      - OpenAI Chat Completions: POST /v1/chat/completions
      - Anthropic Messages:      POST /v1/messages

    Both normalize into the benchmark's OpenAI-shaped LLMRequest contract and block until
    the interactive ChatGPT worker writes a queue response. Streaming is *buffered*: the
    proxy emits a standards-shaped synthetic SSE response only after ChatGPT completes;
    it cannot expose ChatGPT's live token stream.
    """

    def __init__(self, sidecar: ChatGPTSidecarLLM, host: str = "127.0.0.1", port: int = 8765):
        self.sidecar = sidecar
        self.host = host
        self.port = port
        self._server: ThreadingHTTPServer | None = None

    def serve_forever(self) -> None:
        sidecar = self.sidecar

        class Handler(BaseHTTPRequestHandler):
            server_version = "MemoryBakeoffSidecar/2"

            def log_message(self, fmt: str, *args: Any) -> None:
                return

            def _json(self, status: int, payload: dict[str, Any]) -> None:
                raw = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _sse(self, events: list[tuple[str | None, dict[str, Any] | str]]) -> None:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                for event, data in events:
                    if event:
                        self.wfile.write(f"event: {event}\n".encode("utf-8"))
                    encoded = data if isinstance(data, str) else json.dumps(data)
                    self.wfile.write(f"data: {encoded}\n\n".encode("utf-8"))
                self.wfile.flush()

            def do_GET(self) -> None:  # noqa: N802
                if self.path.rstrip("/") == "/v1/models":
                    self._json(200, {"object": "list", "data": [{"id": sidecar.model_label, "object": "model", "owned_by": "chatgpt-sidecar"}]})
                elif self.path.rstrip("/") in {"/health", "/v1/health"}:
                    self._json(200, {"status": "ok", "backend": "chatgpt_sidecar", "compatibility": ["openai-chat", "anthropic-messages"]})
                else:
                    self._json(404, {"error": {"message": "not found"}})

            def do_POST(self) -> None:  # noqa: N802
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    payload = json.loads(self.rfile.read(length) or b"{}")
                    path = self.path.rstrip("/")
                    if path == "/v1/chat/completions":
                        self._handle_openai(payload)
                    elif path == "/v1/messages":
                        self._handle_anthropic(payload)
                    else:
                        self._json(404, {"error": {"message": "not found"}})
                except Exception as e:  # Keep proxy failures explicit to the client.
                    self._json(500, {"error": {"message": f"{type(e).__name__}: {e}"}})

            def _handle_openai(self, payload: dict[str, Any]) -> None:
                streaming = bool(payload.get("stream"))
                request = LLMRequest.from_openai(payload, metadata={"transport": "openai_proxy"})
                response = sidecar.complete(request)
                body = _openai_response(response, request)
                if not streaming:
                    self._json(200, body)
                    return
                choice = body["choices"][0]
                chunk = {
                    "id": body["id"],
                    "object": "chat.completion.chunk",
                    "created": body["created"],
                    "model": body["model"],
                    "choices": [{"index": 0, "delta": choice["message"], "finish_reason": choice["finish_reason"]}],
                }
                self._sse([(None, chunk), (None, "[DONE]")])

            def _handle_anthropic(self, payload: dict[str, Any]) -> None:
                streaming = bool(payload.get("stream"))
                request = _anthropic_request(payload)
                response = sidecar.complete(request)
                body = _anthropic_response(response, request)
                if not streaming:
                    self._json(200, body)
                    return
                self._sse(_anthropic_sse_events(body))

        self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        self._server.serve_forever()

    def shutdown(self) -> None:
        if self._server:
            self._server.shutdown()


def _openai_response(response, request: LLMRequest) -> dict[str, Any]:
    message: dict[str, Any] = {"role": "assistant", "content": response.content}
    if response.tool_calls:
        message["tool_calls"] = response.tool_calls
    return {
        "id": f"chatcmpl-{response.request_id or int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": response.model or request.model or "chatgpt-sidecar",
        "choices": [{"index": 0, "message": message, "finish_reason": response.finish_reason or "stop"}],
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        },
    }


def _anthropic_request(payload: Mapping[str, Any]) -> LLMRequest:
    messages: list[LLMMessage] = []
    system = payload.get("system")
    if system:
        messages.append(LLMMessage("system", _anthropic_content_text(system)))
    for raw in payload.get("messages") or []:
        role = str(raw.get("role") or "user")
        messages.append(LLMMessage(role, _anthropic_content_text(raw.get("content", ""))))

    tools = []
    for tool in payload.get("tools") or []:
        if not isinstance(tool, Mapping) or not tool.get("name"):
            continue
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": str(tool["name"]),
                    "description": str(tool.get("description") or ""),
                    "parameters": tool.get("input_schema") or {"type": "object"},
                },
            }
        )

    tool_choice: str | dict[str, Any] | None = None
    raw_choice = payload.get("tool_choice")
    if isinstance(raw_choice, Mapping):
        kind = raw_choice.get("type")
        if kind == "tool" and raw_choice.get("name"):
            tool_choice = {"type": "function", "function": {"name": raw_choice["name"]}}
        elif kind == "any":
            tool_choice = "required"
        elif kind in {"auto", "none"}:
            tool_choice = str(kind)

    return LLMRequest(
        messages=tuple(messages),
        model=payload.get("model"),
        temperature=float(payload.get("temperature", 0.0) or 0.0),
        max_tokens=payload.get("max_tokens"),
        tools=tuple(tools),
        tool_choice=tool_choice,
        metadata={"transport": "anthropic_proxy"},
        request_id=payload.get("request_id"),
    )


def _anthropic_content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return str(content or "")
    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
            continue
        if not isinstance(block, Mapping):
            continue
        kind = block.get("type")
        if kind == "text":
            parts.append(str(block.get("text") or ""))
        elif kind == "tool_result":
            # Preserve tool results as tagged text so they remain visible to the model.
            parts.append(f"<tool_result tool_use_id={block.get('tool_use_id','')}>{_anthropic_content_text(block.get('content',''))}</tool_result>")
        elif kind == "image":
            parts.append("[image omitted by ChatGPT sidecar compatibility bridge]")
    return "\n".join(x for x in parts if x)


def _anthropic_response(response, request: LLMRequest) -> dict[str, Any]:
    content: list[dict[str, Any]] = []
    if response.content:
        content.append({"type": "text", "text": response.content})
    for call in response.tool_calls:
        fn = call.get("function") or {}
        args = fn.get("arguments") or "{}"
        try:
            parsed = json.loads(args) if isinstance(args, str) else args
        except json.JSONDecodeError:
            parsed = {"_raw": str(args)}
        content.append(
            {
                "type": "tool_use",
                "id": call.get("id") or f"toolu_{int(time.time() * 1000)}",
                "name": fn.get("name") or "tool",
                "input": parsed,
            }
        )
    stop_reason = "tool_use" if response.tool_calls else _anthropic_stop_reason(response.finish_reason)
    return {
        "id": f"msg_{response.request_id or int(time.time() * 1000)}",
        "type": "message",
        "role": "assistant",
        "content": content,
        "model": response.model or request.model or "chatgpt-sidecar",
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": response.usage.prompt_tokens or 0,
            "output_tokens": response.usage.completion_tokens or 0,
        },
    }


def _anthropic_stop_reason(reason: str | None) -> str:
    if reason in {"length", "max_tokens"}:
        return "max_tokens"
    if reason == "tool_use":
        return "tool_use"
    return "end_turn"


def _anthropic_sse_events(body: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    start = dict(body)
    blocks = start.pop("content", [])
    start["content"] = []
    events: list[tuple[str, dict[str, Any]]] = [
        ("message_start", {"type": "message_start", "message": start}),
    ]
    for index, block in enumerate(blocks):
        if block.get("type") == "tool_use":
            initial = {"type": "tool_use", "id": block["id"], "name": block["name"], "input": {}}
            events.append(("content_block_start", {"type": "content_block_start", "index": index, "content_block": initial}))
            events.append(("content_block_delta", {"type": "content_block_delta", "index": index, "delta": {"type": "input_json_delta", "partial_json": json.dumps(block.get("input") or {})}}))
        else:
            events.append(("content_block_start", {"type": "content_block_start", "index": index, "content_block": {"type": "text", "text": ""}}))
            events.append(("content_block_delta", {"type": "content_block_delta", "index": index, "delta": {"type": "text_delta", "text": block.get("text", "")}}))
        events.append(("content_block_stop", {"type": "content_block_stop", "index": index}))
    events.append(("message_delta", {"type": "message_delta", "delta": {"stop_reason": body.get("stop_reason"), "stop_sequence": None}, "usage": {"output_tokens": body.get("usage", {}).get("output_tokens", 0)}}))
    events.append(("message_stop", {"type": "message_stop"}))
    return events
