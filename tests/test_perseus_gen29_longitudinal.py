import hashlib
import json
from pathlib import Path

import pytest

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import perseus_longitudinal as A

FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
SCORER_SHA = "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"
ADAPTER_SHA = "09f2414e1e02784176016cdbe2ffda799cf24c2812a9a0c9a3c5342ecea9a4e2"
TARBALL_SHA = "e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb"
RESULTS = Path("results/perseus_vault_gen29_longitudinal/summary.json")

TRUTH_FIELDS = ("truth_key", "transition", "corrects_id", "supersedes_id", "retracts_id", "invalidates_id",
                "historical_only", "procedure_outcome", "expected_ids", "prohibited_ids", "rationale")


def fixture():
    return L.build_longitudinal_fixture()


def test_frozen_ruler_and_adapter_hashes_are_unchanged():
    assert L.fixture_sha256() == FIXTURE_SHA
    assert L.scorer_contract_sha256() == SCORER_SHA
    assert A.adapter_contract_sha256() == ADAPTER_SHA


def test_write_envelope_carries_no_benchmark_truth():
    for observation in fixture().observations:
        body = A.body_for_observation(observation)
        A.assert_public_only(body)
        assert not set(body) & set(TRUTH_FIELDS)
        assert set(body) == set(A.adapter_contract_payload()["body_fields"])
    with pytest.raises(ValueError):
        A.assert_public_only({"assertion": "x", "truth_key": "leak"})


def test_workspace_is_scope_only_and_never_prefilters_configuration():
    f = fixture()
    forge = [o for o in f.observations if o.scope == "server:forge"]
    assert len({A.workspace_for_scope(o.scope) for o in forge}) == 1
    assert len({o.configuration for o in forge}) > 1, "C1 and C2 must coexist in one workspace"
    assert A.workspace_for_scope("server:forge") != A.workspace_for_scope("repo:aurora")


def test_temporal_routing_uses_only_public_coordinates():
    f = fixture()
    base = A.TimeBase(tuple(o.ingestion_time.isoformat() for o in f.observations), tuple(1000 + 100 * i for i in range(16)))
    for case in f.cases:
        arguments = A.recall_arguments(case, base, 5)
        assert arguments["mode"] == "hybrid"
        assert arguments["limit"] == 5
        assert not set(arguments) & set(TRUTH_FIELDS)
        operation = A.native_operation(case)
        assert (operation == "recall_hybrid") == ("as_of_unix_ms" not in arguments and "valid_at" not in arguments)
    assert set(A.adapter_contract_payload()["routing_inputs"]) == {"target_kind", "event_time", "scope"}


def test_time_base_maps_fixture_instants_into_the_store_timeline():
    base = A.TimeBase(("2026-01-10T00:00:00+00:00", "2026-01-12T00:00:00+00:00", "2026-01-20T00:00:00+00:00"), (1000, 2000, 3000))
    assert base.store_instant("2026-01-01T00:00:00+00:00") == 999
    assert base.store_instant("2026-01-11T00:00:00+00:00") == 1500
    assert base.store_instant("2026-01-30T00:00:00+00:00") == 3001


def test_scorer_flags_future_leakage_and_unmapped_provenance():
    f = fixture()
    case = next(c for c in f.cases if c.checkpoint_id == "CP01")
    later = [o.id for o in f.observations if o.ingestion_order > 1][0]
    assert "future_leakage" in L.score_longitudinal_case(f, case, (later,)).failure_classes
    assert "unmapped_provenance" in L.score_longitudinal_case(f, case, ("not-a-record",)).failure_classes


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen29 results are produced by the runner")
def test_published_gen29_results_are_exact_and_isolated():
    summary = json.loads(RESULTS.read_text())
    identity = summary["system_identity"]
    assert identity["release_tarball_sha256"] == TARBALL_SHA
    assert identity["product_version"] == "2.23.2"
    assert identity["adapter_contract_sha256"] == ADAPTER_SHA
    assert identity["read_isolation"] == "byte-for-byte vault snapshot per checkpoint"
    assert identity["reader"] == "none" and identity["llm"] == "none" and identity["inference_server"] == "none"
    assert summary["fixture_sha256"] == FIXTURE_SHA
    assert summary["scorer_contract_sha256"] == SCORER_SHA
    assert len(summary["repetitions"]) == 3
    for repetition in summary["repetitions"]:
        assert repetition["provenance_exact_all_cases"] is True
        assert repetition["cases"] == 20
        assert repetition["checkpoints"] == 9
    assert summary["failure_totals_all_repetitions"].get("future_leakage", 0) == 0


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen29 results are produced by the runner")
def test_absence_from_active_state_is_never_called_deletion():
    for path in sorted(Path("results/perseus_vault_gen29_longitudinal").glob("repetition-*.json")):
        repetition = json.loads(path.read_text())
        for evidence in (e for group in repetition["lifecycle"].values() for e in group):
            if evidence["active_current"] is False:
                assert evidence["disposition"] != "deleted"
