from __future__ import annotations

import os
from typing import Any, Sequence

import requests

from memory_bakeoff.llm.base import LLMBackendError, LLMClient, LLMRequest, LLMResponse, LLMUsage


class OpenAICompatibleLLM(LLMClient):
    """OpenAI Chat Completions client for OpenAI, llama.cpp, vLLM, SGLang, etc."""

    name = "openai_compat"

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_s: float = 120.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL")
        self.timeout_s = timeout_s

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = request.to_openai(default_model=self.model)
        payload["stream"] = False
        try:
            r = requests.post(
                self.base_url + "/chat/completions",
                headers=self._headers(),
                json=payload,
                timeout=self.timeout_s,
            )
        except requests.RequestException as e:
            raise LLMBackendError(f"OpenAI-compatible request failed: {e}") from e
        if not r.ok:
            raise LLMBackendError(f"OpenAI-compatible HTTP {r.status_code}: {r.text[:500]}")
        raw: dict[str, Any] = r.json()
        choices = raw.get("choices") or []
        if not choices:
            raise LLMBackendError("OpenAI-compatible response contained no choices")
        choice = choices[0]
        message = choice.get("message") or {}
        usage = raw.get("usage") or {}
        return LLMResponse(
            content=message.get("content") or "",
            model=raw.get("model") or payload["model"],
            finish_reason=choice.get("finish_reason"),
            usage=LLMUsage(
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
                usage.get("total_tokens"),
            ),
            tool_calls=list(message.get("tool_calls") or []),
            raw=raw,
            request_id=request.request_id,
        )

    def complete_batch(self, requests_: Sequence[LLMRequest]) -> list[LLMResponse]:
        # Chat Completions has no universal batch endpoint across local servers. Keep
        # ordering deterministic; callers may parallelize at a higher orchestration layer.
        return [self.complete(r) for r in requests_]
