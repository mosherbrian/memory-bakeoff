from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from memory_bakeoff.llm.base import LLMClient, LLMRequest, LLMResponse, LLMUsage, simple_token_estimate


class DeterministicFakeLLM(LLMClient):
    """Fixture-first fake LLM for plumbing and bulk deterministic tests.

    If a request fingerprint exists in the fixture mapping, that response is returned.
    Otherwise the backend returns either metadata['fake_response'] or a deterministic
    echo of the last user message. It is deliberately *not* a semantic LLM substitute.
    """

    name = "fake"

    def __init__(self, fixtures: dict[str, str] | None = None, fixture_path: str | Path | None = None):
        loaded: dict[str, str] = {}
        if fixture_path:
            loaded = json.loads(Path(fixture_path).read_text())
        self.fixtures = {**loaded, **(fixtures or {})}

    def complete(self, request: LLMRequest) -> LLMResponse:
        fp = request.fingerprint()
        content = self.fixtures.get(fp)
        if content is None:
            content = request.metadata.get("fake_response")
        if content is None:
            user = next((m.content for m in reversed(request.messages) if m.role == "user"), "")
            if request.response_format and request.response_format.get("type") in {"json_object", "json_schema"}:
                content = json.dumps({"fake": True, "text": user}, ensure_ascii=False)
            else:
                content = f"[fake] {user}"
        prompt = "\n".join(m.content for m in request.messages)
        p = simple_token_estimate(prompt)
        c = simple_token_estimate(content)
        return LLMResponse(
            content=content,
            model=request.model or "deterministic-fake",
            finish_reason="stop",
            usage=LLMUsage(p, c, p + c),
            request_id=request.request_id,
            raw={"fixture": fp in self.fixtures, "fingerprint": fp},
        )
