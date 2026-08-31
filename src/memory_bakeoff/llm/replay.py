from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from memory_bakeoff.llm.base import LLMBackendError, LLMClient, LLMRequest, LLMResponse, LLMUsage


class ReplayLLM(LLMClient):
    """Replay an archived ChatGPT-sidecar trace with fingerprint validation.

    This is an audit/reproducibility backend, not a model. It refuses to return a saved
    answer unless the current request has the same request_id and semantic fingerprint as
    the archived request that produced that answer.
    """

    name = "replay"

    def __init__(self, trace_dir: str | Path):
        self.trace_dir = Path(trace_dir).resolve()
        self.requests_dir = self.trace_dir / "requests"
        self.responses_dir = self.trace_dir / "responses"
        if not self.requests_dir.is_dir() or not self.responses_dir.is_dir():
            raise LLMBackendError(
                f"Replay trace must contain requests/ and responses/: {self.trace_dir}"
            )

    def complete(self, request: LLMRequest) -> LLMResponse:
        if not request.request_id:
            raise LLMBackendError("Replay requests require a stable request_id")
        rid = request.request_id
        req_path = self.requests_dir / f"{rid}.json"
        resp_path = self.responses_dir / f"{rid}.json"
        if not req_path.exists() or not resp_path.exists():
            raise LLMBackendError(f"Replay trace has no complete request/response pair for {rid}")
        try:
            archived_req = json.loads(req_path.read_text())
            archived_resp = json.loads(resp_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise LLMBackendError(f"Invalid replay artifact for {rid}: {exc}") from exc

        expected = archived_req.get("fingerprint")
        actual = request.fingerprint()
        if not expected or expected != actual:
            raise LLMBackendError(
                f"Replay fingerprint mismatch for {rid}: archived={expected!r}, current={actual!r}"
            )
        if archived_resp.get("request_id") != rid:
            raise LLMBackendError(f"Replay response ID mismatch for {rid}")

        usage = archived_resp.get("usage") or {}
        return LLMResponse(
            content=str(archived_resp.get("content") or ""),
            model=archived_resp.get("model") or "replay",
            finish_reason=archived_resp.get("finish_reason") or "stop",
            usage=LLMUsage(
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
                usage.get("total_tokens"),
            ),
            tool_calls=list(archived_resp.get("tool_calls") or []),
            raw=archived_resp,
            request_id=rid,
        )

    def complete_batch(self, requests: Sequence[LLMRequest]) -> list[LLMResponse]:
        return [self.complete(request) for request in requests]
