from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import time
import uuid
from typing import Any, Mapping, Sequence


RPC_PROTOCOL_VERSION = 1


class ToolRPCError(RuntimeError):
    pass


class ToolRPCTimeout(ToolRPCError):
    def __init__(self, pending_ids: Sequence[str], queue_dir: Path):
        self.pending_ids = tuple(pending_ids)
        self.queue_dir = queue_dir
        super().__init__(
            f"Timed out waiting for tool-loop RPC responses: {', '.join(pending_ids)} "
            f"(queue: {queue_dir})"
        )


@dataclass(frozen=True)
class ToolRPCRequest:
    """One auditable request for a capability only the ChatGPT tool layer can access.

    `method` is intentionally namespaced, e.g. `github.fetch_file`, `web.search`,
    or `artifact.fetch`. The sandbox never gets arbitrary network access: a human/
    ChatGPT orchestration turn must explicitly service each request.
    """

    method: str
    params: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: str | None = None

    def fingerprint(self) -> str:
        body = {"method": self.method, "params": self.params}
        raw = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ToolRPCResponse:
    request_id: str
    ok: bool
    result: Any = None
    error: dict[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ToolLoopRPCClient:
    """Blocking file-queue RPC client serviced by the ChatGPT tool loop.

    This is cooperative pseudo-egress, not networking. `call_batch` writes every
    outstanding request before waiting so one ChatGPT turn can service the batch.
    """

    def __init__(
        self,
        queue_dir: str | Path | None = None,
        *,
        timeout_s: float = 900.0,
        poll_interval_s: float = 0.25,
    ) -> None:
        self.queue_dir = Path(
            queue_dir or os.getenv("MEMORY_BAKEOFF_RPC_DIR") or ".memory-bakeoff-rpc"
        ).resolve()
        self.timeout_s = timeout_s
        self.poll_interval_s = poll_interval_s
        for name in ("requests", "responses", "batches", "archive"):
            (self.queue_dir / name).mkdir(parents=True, exist_ok=True)

    def call(self, request: ToolRPCRequest) -> ToolRPCResponse:
        return self.call_batch([request])[0]

    def call_batch(self, requests: Sequence[ToolRPCRequest]) -> list[ToolRPCResponse]:
        if not requests:
            return []
        batch_id = f"rpcbatch_{uuid.uuid4().hex}"
        request_ids: list[str] = []
        for index, request in enumerate(requests):
            request_id = request.request_id or f"rpc_{uuid.uuid4().hex}"
            if request_id in request_ids:
                raise ToolRPCError(f"Duplicate RPC request_id in batch: {request_id}")
            request_ids.append(request_id)
            payload = {
                "protocol_version": RPC_PROTOCOL_VERSION,
                "request_id": request_id,
                "batch_id": batch_id,
                "batch_index": index,
                "created_at": time.time(),
                "fingerprint": request.fingerprint(),
                "method": request.method,
                "params": dict(request.params),
                "metadata": dict(request.metadata),
                "worker_instruction": (
                    "Service this request using the named ChatGPT/tool capability, then write "
                    f"responses/{request_id}.json with the tool-loop RPC response envelope."
                ),
            }
            _atomic_write_json(self.queue_dir / "requests" / f"{request_id}.json", payload)

        _atomic_write_json(
            self.queue_dir / "batches" / f"{batch_id}.json",
            {
                "protocol_version": RPC_PROTOCOL_VERSION,
                "batch_id": batch_id,
                "request_ids": request_ids,
                "created_at": time.time(),
                "status": "pending",
            },
        )

        deadline = time.monotonic() + self.timeout_s
        pending = set(request_ids)
        raw_responses: dict[str, dict[str, Any]] = {}
        while pending and time.monotonic() < deadline:
            for request_id in list(pending):
                path = self.queue_dir / "responses" / f"{request_id}.json"
                if not path.exists():
                    continue
                try:
                    raw = json.loads(path.read_text())
                except (OSError, json.JSONDecodeError):
                    continue
                _validate_response(raw, request_id)
                raw_responses[request_id] = raw
                pending.remove(request_id)
            if pending:
                time.sleep(self.poll_interval_s)

        if pending:
            raise ToolRPCTimeout(sorted(pending), self.queue_dir)

        responses = [
            ToolRPCResponse(
                request_id=request_id,
                ok=bool(raw_responses[request_id]["ok"]),
                result=raw_responses[request_id].get("result"),
                error=raw_responses[request_id].get("error"),
                metadata=dict(raw_responses[request_id].get("metadata") or {}),
            )
            for request_id in request_ids
        ]
        self._mark_batch_complete(batch_id)
        return responses

    def _mark_batch_complete(self, batch_id: str) -> None:
        path = self.queue_dir / "batches" / f"{batch_id}.json"
        try:
            data = json.loads(path.read_text())
            data["status"] = "complete"
            data["completed_at"] = time.time()
            _atomic_write_json(path, data)
        except (OSError, json.JSONDecodeError):
            pass


def list_pending_rpc(queue_dir: str | Path) -> list[dict[str, Any]]:
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


def write_rpc_response(
    queue_dir: str | Path,
    request_id: str,
    *,
    result: Any = None,
    ok: bool = True,
    error: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> Path:
    if ok and error:
        raise ToolRPCError("Successful RPC response cannot also contain an error")
    if not ok and not error:
        error = {"type": "ToolRPCRemoteError", "message": "remote tool call failed"}
    payload = {
        "protocol_version": RPC_PROTOCOL_VERSION,
        "request_id": request_id,
        "ok": bool(ok),
        "result": result,
        "error": dict(error) if error else None,
        "metadata": dict(metadata or {}),
        "created_at": time.time(),
    }
    path = Path(queue_dir).resolve() / "responses" / f"{request_id}.json"
    _atomic_write_json(path, payload)
    return path


def write_rpc_error(
    queue_dir: str | Path,
    request_id: str,
    message: str,
    *,
    error_type: str = "ToolRPCRemoteError",
    details: Mapping[str, Any] | None = None,
) -> Path:
    error = {"type": error_type, "message": message}
    if details:
        error["details"] = dict(details)
    return write_rpc_response(queue_dir, request_id, ok=False, error=error)


def _validate_response(raw: Mapping[str, Any], request_id: str) -> None:
    if raw.get("protocol_version") != RPC_PROTOCOL_VERSION:
        raise ToolRPCError(
            f"Unsupported RPC protocol version for {request_id}: "
            f"{raw.get('protocol_version')!r}"
        )
    if raw.get("request_id") != request_id:
        raise ToolRPCError(
            f"RPC response ID mismatch: expected {request_id}, got {raw.get('request_id')!r}"
        )
    if not isinstance(raw.get("ok"), bool):
        raise ToolRPCError(f"RPC response {request_id} must contain boolean `ok`")
    if not raw.get("ok") and not isinstance(raw.get("error"), Mapping):
        raise ToolRPCError(f"Failed RPC response {request_id} must contain an error object")


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
