from __future__ import annotations

import os
from typing import Any

import requests

from memory_bakeoff.llm.base import LLMBackendError, LLMClient, LLMRequest, LLMResponse, LLMUsage


class AnthropicLLM(LLMClient):
    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout_s: float = 120.0):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-5"
        self.timeout_s = timeout_s

    def complete(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            raise LLMBackendError("ANTHROPIC_API_KEY is not set")
        system_parts = [m.content for m in request.messages if m.role == "system"]
        messages = [m.to_openai() for m in request.messages if m.role != "system"]
        payload: dict[str, Any] = {
            "model": request.model or self.model,
            "messages": messages,
            "max_tokens": request.max_tokens or 2048,
            "temperature": request.temperature,
        }
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)
        if request.tools:
            # OpenAI and Anthropic tool schemas are not identical. Most function tools map
            # cleanly enough for benchmark use; reject unsupported shapes explicitly.
            mapped = []
            for tool in request.tools:
                fn = tool.get("function") if tool.get("type") == "function" else None
                if not fn:
                    raise LLMBackendError("Anthropic backend only maps OpenAI function tools")
                mapped.append({"name": fn["name"], "description": fn.get("description", ""), "input_schema": fn.get("parameters", {"type": "object"})})
            payload["tools"] = mapped
        try:
            r = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
                timeout=self.timeout_s,
            )
        except requests.RequestException as e:
            raise LLMBackendError(f"Anthropic request failed: {e}") from e
        if not r.ok:
            raise LLMBackendError(f"Anthropic HTTP {r.status_code}: {r.text[:500]}")
        raw = r.json()
        texts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        for block in raw.get("content") or []:
            if block.get("type") == "text":
                texts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                tool_calls.append({
                    "id": block.get("id"),
                    "type": "function",
                    "function": {"name": block.get("name"), "arguments": __import__("json").dumps(block.get("input") or {})},
                })
        usage = raw.get("usage") or {}
        p = usage.get("input_tokens")
        c = usage.get("output_tokens")
        return LLMResponse(
            content="".join(texts),
            model=raw.get("model") or payload["model"],
            finish_reason=raw.get("stop_reason"),
            usage=LLMUsage(p, c, (p + c) if isinstance(p, int) and isinstance(c, int) else None),
            tool_calls=tool_calls,
            raw=raw,
            request_id=request.request_id,
        )
