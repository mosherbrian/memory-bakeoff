from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import time
import uuid
from typing import Any, Sequence

from memory_bakeoff.llm.base import LLMBackendError, LLMClient, LLMRequest, LLMResponse, LLMUsage


PROTOCOL_VERSION = 1


class SidecarTimeout(LLMBackendError):
    def __init__(self, pending_ids: Sequence[str], queue_dir: Path):
        self.pending_ids = tuple(pending_ids)
        self.queue_dir = queue_dir
        super().__init__(f"Timed out waiting for ChatGPT sidecar responses: {', '.join(pending_ids)} (queue: {queue_dir})")


class ChatGPTSidecarLLM(LLMClient):
    """File-queue bridge that lets this ChatGPT conversation act as an LLM backend.

    It does not expose or intercept ChatGPT's completion stream. The harness writes
    requests atomically, waits, and an interactive ChatGPT tool loop reads pending
    requests and atomically writes response JSON files. `complete_batch` writes the
    entire batch before waiting so outstanding calls can be answered together.
    """

    name = "chatgpt_sidecar"

    def __init__(
        self,
        queue_dir: str | Path | None = None,
        timeout_s: float = 900.0,
        poll_interval_s: float = 0.25,
        model_label: str = "chatgpt-sidecar",
    ) -> None:
        self.queue_dir = Path(queue_dir or os.getenv("CHATGPT_SIDECAR_DIR") or ".memory-bakeoff-sidecar").resolve()
        self.timeout_s = timeout_s
        self.poll_interval_s = poll_interval_s
        self.model_label = model_label
        for name in ("requests", "responses", "batches", "archive"):
            (self.queue_dir / name).mkdir(parents=True, exist_ok=True)

    def complete(self, request: LLMRequest) -> LLMResponse:
        return self.complete_batch([request])[0]

    def complete_batch(self, requests: Sequence[LLMRequest]) -> list[LLMResponse]:
        if not requests:
            return []
        batch_id = uuid.uuid4().hex
        ids: list[str] = []
        for index, request in enumerate(requests):
            request_id = request.request_id or f"req_{uuid.uuid4().hex}"
            if request_id in ids:
                raise LLMBackendError(f"Duplicate sidecar request_id in batch: {request_id}")
            ids.append(request_id)
            payload = {
                "protocol_version": PROTOCOL_VERSION,
                "request_id": request_id,
                "batch_id": batch_id,
                "batch_index": index,
                "created_at": time.time(),
                "fingerprint": request.fingerprint(),
                "openai_request": request.to_openai(default_model=self.model_label),
                "metadata": request.metadata,
                "worker_instruction": (
                    "Answer this LLM request as the model. Write a response JSON file named "
                    f"responses/{request_id}.json conforming to the ChatGPT sidecar protocol."
                ),
            }
            _atomic_write_json(self.queue_dir / "requests" / f"{request_id}.json", payload)
        _atomic_write_json(
            self.queue_dir / "batches" / f"{batch_id}.json",
            {
                "protocol_version": PROTOCOL_VERSION,
                "batch_id": batch_id,
                "request_ids": ids,
                "created_at": time.time(),
                "status": "pending",
            },
        )

        deadline = time.monotonic() + self.timeout_s
        pending = set(ids)
        raw_responses: dict[str, dict[str, Any]] = {}
        while pending and time.monotonic() < deadline:
            for request_id in list(pending):
                response_path = self.queue_dir / "responses" / f"{request_id}.json"
                if response_path.exists():
                    try:
                        raw = json.loads(response_path.read_text())
                    except (OSError, json.JSONDecodeError):
                        continue  # Writer may not have finished if it ignored atomic protocol.
                    _validate_response(raw, request_id)
                    raw_responses[request_id] = raw
                    pending.remove(request_id)
            if pending:
                time.sleep(self.poll_interval_s)
        if pending:
            raise SidecarTimeout(sorted(pending), self.queue_dir)

        result: list[LLMResponse] = []
        for request_id in ids:
            raw = raw_responses[request_id]
            usage = raw.get("usage") or {}
            result.append(
                LLMResponse(
                    content=str(raw.get("content") or ""),
                    model=raw.get("model") or self.model_label,
                    finish_reason=raw.get("finish_reason") or "stop",
                    usage=LLMUsage(
                        usage.get("prompt_tokens"),
                        usage.get("completion_tokens"),
                        usage.get("total_tokens"),
                    ),
                    tool_calls=list(raw.get("tool_calls") or []),
                    raw=raw,
                    request_id=request_id,
                )
            )
        self._mark_batch_complete(batch_id)
        return result

    def _mark_batch_complete(self, batch_id: str) -> None:
        path = self.queue_dir / "batches" / f"{batch_id}.json"
        try:
            data = json.loads(path.read_text())
            data["status"] = "complete"
            data["completed_at"] = time.time()
            _atomic_write_json(path, data)
        except OSError:
            pass


def list_pending(queue_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(queue_dir).resolve()
    requests_dir = root / "requests"
    responses_dir = root / "responses"
    if not requests_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(requests_dir.glob("*.json"), key=lambda p: p.stat().st_mtime):
        request_id = path.stem
        if (responses_dir / f"{request_id}.json").exists():
            continue
        try:
            out.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def write_sidecar_response(
    queue_dir: str | Path,
    request_id: str,
    content: str,
    *,
    model: str = "chatgpt-sidecar",
    finish_reason: str = "stop",
    usage: dict[str, int | None] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> Path:
    path = Path(queue_dir).resolve() / "responses" / f"{request_id}.json"
    payload = {
        "protocol_version": PROTOCOL_VERSION,
        "request_id": request_id,
        "content": content,
        "model": model,
        "finish_reason": finish_reason,
        "usage": usage or {},
        "tool_calls": tool_calls or [],
        "created_at": time.time(),
    }
    _atomic_write_json(path, payload)
    return path


def _validate_response(raw: dict[str, Any], request_id: str) -> None:
    if raw.get("protocol_version") != PROTOCOL_VERSION:
        raise LLMBackendError(f"Unsupported sidecar protocol version for {request_id}: {raw.get('protocol_version')!r}")
    if raw.get("request_id") != request_id:
        raise LLMBackendError(f"Sidecar response ID mismatch: expected {request_id}, got {raw.get('request_id')!r}")
    if "content" not in raw:
        raise LLMBackendError(f"Sidecar response {request_id} has no content field")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
