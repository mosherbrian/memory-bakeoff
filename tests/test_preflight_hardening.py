from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers import PROVIDERS
from memory_bakeoff.providers.base import MemoryProvider
from memory_bakeoff.providers.external import ClaudeMemProvider, Mem0Provider, MemBukkitProvider
from memory_bakeoff.reader_eval import ANSWER_SPECS, prepare_reader_requests, write_reader_results
from memory_bakeoff.repro import capture_execution_environment
from memory_bakeoff.runner import run_provider, write_results


def test_experiment_classes_preserve_mode_distinctions():
    assert PROVIDERS["bm25"]().experiment_class("raw") == "baseline"
    assert PROVIDERS["membukkit_core_lsa"]().experiment_class("raw") == "controlled_core"
    assert PROVIDERS["membukkit_core_lsa"]().experiment_class("product") == "controlled_core"
    assert PROVIDERS["membukkit"]().experiment_class("raw") == "raw_product"
    assert PROVIDERS["membukkit"]().experiment_class("product") == "product"


def test_membukkit_product_probe_fails_closed_when_package_is_absent(monkeypatch):
    monkeypatch.delenv("MEMBUKKIT_UPSTREAM_PATH", raising=False)
    monkeypatch.setattr(
        "memory_bakeoff.providers.external.importlib.util.find_spec",
        lambda _name: (_ for _ in ()).throw(ModuleNotFoundError("membukkit")),
    )
    probe = MemBukkitProvider().probe()
    assert probe.available is False
    assert "upstream membukkit package not installed" in probe.reason


def test_fuzzy_subtext_provenance_is_exploratory_only():
    provider = ClaudeMemProvider("http://unused")
    records, _ = __import__("memory_bakeoff.corpus", fromlist=["build_corpus"]).build_corpus()
    provider.remember_records(records[:1])
    assert provider.resolve_record_id(records[0].text) == records[0].id
    report = provider.provenance_report()
    assert report["methods"] == {"fuzzy_subtext": 1}
    assert report["publishable"] is False
    assert report["status"] == "exploratory_only"


def test_mem0_raw_retrieval_fails_closed_without_native_metadata():
    records, cases = __import__("memory_bakeoff.corpus", fromlist=["build_corpus"]).build_corpus()
    provider = Mem0Provider()
    provider.remember_records(records[:1])

    class FakeMemory:
        def search(self, *_args, **_kwargs):
            return {"results": [{"id": "foreign", "memory": records[0].text, "metadata": {}}]}

    provider.mem = FakeMemory()
    with pytest.raises(RuntimeError, match="native canonical record_id"):
        provider.retrieve(cases[0])


def test_run_metadata_and_authoritative_leaderboard_gate(tmp_path: Path):
    publishable = run_provider("bm25", top_k=3)
    assert publishable["schema_version"] == 2
    assert publishable["experiment_class"] == "baseline"
    assert publishable["publishability"]["publishable"] is True

    exploratory = deepcopy(publishable)
    exploratory["provider"] = "fuzzy-diagnostic"
    exploratory["provenance"] = {
        "status": "exploratory_only",
        "publishable": False,
        "methods": {"fuzzy_subtext": 1},
        "reason": "test fixture",
    }
    exploratory["publishability"] = {
        "status": "non_publishable",
        "publishable": False,
        "reasons": ["test fixture"],
    }

    out = tmp_path / "new-results"
    write_results([publishable, exploratory], out)
    leaderboard = (out / "leaderboard.md").read_text()
    assert "bm25" in leaderboard
    assert "fuzzy-diagnostic" not in leaderboard
    assert "fuzzy-diagnostic" in (out / "summary.md").read_text()

    with pytest.raises(FileExistsError, match="already exists"):
        write_results([publishable], out)
    write_results([publishable], out, allow_overwrite=True)


def test_execution_environment_fingerprint_is_secret_free_and_stable():
    first = capture_execution_environment()
    second = capture_execution_environment()
    assert first == second
    assert first["system"]
    assert first["machine"]
    assert len(first["fingerprint_sha256"]) == 64
    assert "hostname" not in first


def test_reader_eval_drops_nonpublishable_context_before_llm(monkeypatch):
    class FuzzyProvider(MemoryProvider):
        name = "fuzzy-test"
        capabilities = ProviderCapabilities(raw_ingest=True, product_ingest=False)

        def reset(self):
            self._records.clear()

        def ingest(self, records: list[MemoryRecord], mode: str = "raw"):
            self.reset()
            self.remember_records(records)

        def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
            record = next(iter(self._records.values()))
            return RetrievalResult([RetrievalItem(self.resolve_record_id(record.text), record.text)], 0.0)

    monkeypatch.setitem(PROVIDERS, "fuzzy-test", FuzzyProvider)
    requests, contexts, unavailable = prepare_reader_requests(
        ["fuzzy-test"], specs=(next(spec for spec in ANSWER_SPECS if spec.case_id == "Q003"),)
    )
    assert requests == []
    assert contexts == []
    assert unavailable[0]["status"] == "non_publishable"


def test_reader_result_writer_also_fails_closed(tmp_path: Path):
    out = tmp_path / "reader-results"
    result = {"provider_summary": {}, "unavailable": [], "details": []}
    write_reader_results(result, out)
    with pytest.raises(FileExistsError, match="already exists"):
        write_reader_results(result, out)
    write_reader_results(result, out, allow_overwrite=True)


def test_cli_refuses_existing_directory_before_running_provider(monkeypatch, tmp_path: Path):
    from memory_bakeoff import cli

    out = tmp_path / "already-there"
    out.mkdir()
    monkeypatch.setattr(cli, "run_provider", lambda *_args, **_kwargs: pytest.fail("provider should not run"))
    with pytest.raises(FileExistsError, match="already exists"):
        cli.main(["run", "--providers", "bm25", "--out", str(out)])
