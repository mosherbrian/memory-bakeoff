from pathlib import Path
from memory_bakeoff.runner import run_provider


def test_claude_mem_is_ineligible_in_raw_mode_before_service_probe():
    row=run_provider("claude_mem",mode="raw",top_k=3)
    assert row["status"] == "ineligible"


def test_hindsight_is_raw_eligible_but_unavailable_without_service():
    row=run_provider("hindsight",mode="raw",top_k=3)
    assert row["status"] == "unavailable"
    assert row["probe"]["capabilities"]["raw_ingest"] is True


def test_runner_closes_provider_after_ingest_failure(monkeypatch):
    from memory_bakeoff.providers.base import ProviderUnavailable
    from memory_bakeoff.providers.external import HindsightProvider
    from memory_bakeoff.models import ProviderProbe
    import memory_bakeoff.runner as runner

    provider = HindsightProvider("http://hindsight")
    closed=[]
    monkeypatch.setitem(runner.PROVIDERS, "hindsight", lambda: provider)
    monkeypatch.setattr(provider, "probe", lambda: ProviderProbe(provider.name, True, "ok", provider.capabilities))
    monkeypatch.setattr(provider, "ingest", lambda records, mode: (_ for _ in ()).throw(ProviderUnavailable("synthetic failure")))
    monkeypatch.setattr(provider, "close", lambda: closed.append(True))

    row = run_provider("hindsight", mode="raw", top_k=3)
    assert row["status"] == "unavailable"
    assert closed == [True]


def test_claude_mem_default_port(monkeypatch):
    from memory_bakeoff.providers.external import _claude_mem_default_url
    monkeypatch.delenv("CLAUDE_MEM_URL", raising=False)
    monkeypatch.delenv("CLAUDE_MEM_WORKER_PORT", raising=False)
    monkeypatch.setattr("memory_bakeoff.providers.external.Path.home", lambda: Path("/definitely/missing"))
    monkeypatch.setattr("memory_bakeoff.providers.external.os.getuid", lambda: 42)
    assert _claude_mem_default_url() == "http://127.0.0.1:37742"


def test_stress_corpus_adds_deterministic_near_neighbors():
    from memory_bakeoff.corpus import build_corpus
    base, q1 = build_corpus()
    stress, q2 = build_corpus(distractors=25)
    stress2, _ = build_corpus(distractors=25)
    assert len(base) == 50
    assert len(stress) == 75
    assert [r.id for r in stress[-25:]] == [r.id for r in stress2[-25:]]
    assert stress[-25].id == "M051"
    assert [q.id for q in q1] == [q.id for q in q2]
