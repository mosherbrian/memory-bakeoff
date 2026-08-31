from __future__ import annotations

from datetime import datetime, timezone
from types import ModuleType, SimpleNamespace
import sys

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, ProviderProbe, QueryCase
from memory_bakeoff.providers.external import AgentMemoryProvider, ClaudeMemProvider, HindsightProvider


def record(rid: str = "M001") -> MemoryRecord:
    return MemoryRecord(
        id=rid,
        text="Use shipit release --cluster pdx for production deploys.",
        timestamp=datetime(2026, 8, 1, 12, tzinfo=timezone.utc),
        session_id="s1",
        scope="repo:atlas",
        outcome="success",
    )


def case() -> QueryCase:
    return QueryCase("QX", "procedure", "How do I deploy Atlas?", ("M001",), scope="repo:atlas")


class Resp:
    def __init__(self, payload=None, status=200):
        self._payload = payload if payload is not None else {}
        self.status_code = status
        self.ok = 200 <= status < 300
        self.text = "ok" if self.ok else "error"

    def json(self):
        return self._payload


def test_agentmemory_uses_supported_type_for_provenance_and_reconstructs_compact_result(monkeypatch):
    p = AgentMemoryProvider("http://agentmemory")
    p.project = "bench-project"
    monkeypatch.setattr(
        p,
        "probe",
        lambda: ProviderProbe(p.name, True, "ok", p.capabilities),
    )
    posts = []

    def fake_post(url, json, headers, timeout):
        posts.append((url, json))
        if url.endswith("/remember"):
            return Resp({"ok": True})
        return Resp({"results": [{"type": "memory-bakeoff:M001", "score": 0.91, "title": "Deploy"}]})

    monkeypatch.setattr("memory_bakeoff.providers.external.requests.post", fake_post)
    p.ingest([record()])
    remember_payload = posts[0][1]
    assert remember_payload == {
        "project": "bench-project",
        "content": record().text,
        "type": "memory-bakeoff:M001",
    }
    assert "metadata" not in remember_payload

    result = p.retrieve(case(), 5)
    assert posts[-1][1]["format"] == "compact"
    assert result.ids == ["M001"]
    assert result.items[0].text == record().text


def test_claude_mem_search_requests_full_observations(monkeypatch):
    p = ClaudeMemProvider("http://claude-mem")
    p.project = "bench-project"
    p.remember_records([record()])
    seen = {}

    def fake_get(url, params, timeout):
        seen.update(params)
        return Resp({"observations": [{"text": record().text, "score": 0.8}]})

    monkeypatch.setattr("memory_bakeoff.providers.external.requests.get", fake_get)
    result = p.retrieve(case(), 5)
    assert seen["type"] == "observations"
    assert seen["format"] == "full"
    assert result.ids == ["M001"]


def test_hindsight_retain_uses_datetime_and_recall_results(monkeypatch):
    retained = []
    monkeypatch.setenv("HINDSIGHT_RAW_LLM_PROVIDER", "none")

    class FakeHindsight:
        def __init__(self, base_url):
            self.base_url = base_url

        def retain(self, **kwargs):
            retained.append(kwargs)

        def recall(self, **kwargs):
            return SimpleNamespace(results=[SimpleNamespace(text=record().text, score=0.77, document_id="M001")])

    module = ModuleType("hindsight_client")
    module.Hindsight = FakeHindsight
    monkeypatch.setitem(sys.modules, "hindsight_client", module)
    real_find_spec = __import__("importlib").util.find_spec
    monkeypatch.setattr(
        "memory_bakeoff.providers.external.importlib.util.find_spec",
        lambda name: object() if name == "hindsight_client" else real_find_spec(name),
    )

    p = HindsightProvider("http://hindsight")
    p.ingest([record()], mode="raw")
    assert isinstance(retained[0]["timestamp"], datetime)
    assert retained[0]["document_id"] == "M001"

    result = p.retrieve(case(), 5)
    assert result.ids == ["M001"]
    assert result.items[0].text == record().text


def test_hindsight_raw_mode_requires_explicit_no_llm_declaration(monkeypatch):
    p = HindsightProvider("http://hindsight")
    monkeypatch.delenv("HINDSIGHT_RAW_LLM_PROVIDER", raising=False)
    import pytest
    from memory_bakeoff.providers.base import ProviderUnavailable
    with pytest.raises(ProviderUnavailable, match="explicit HINDSIGHT_RAW_LLM_PROVIDER=none"):
        p.ingest([record()], mode="raw")
