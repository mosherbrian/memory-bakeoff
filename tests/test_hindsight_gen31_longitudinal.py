import json
from pathlib import Path

import pytest

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import hindsight_longitudinal as H
from memory_bakeoff.providers import perseus_longitudinal as P

FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
SCORER_SHA = "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"
ADAPTER_SHA = "c9025733aa894fa5abac43632e9dc916c37e526065d089a882257427c14d60ff"
PERSEUS_ADAPTER_SHA = "09f2414e1e02784176016cdbe2ffda799cf24c2812a9a0c9a3c5342ecea9a4e2"
RESULTS = Path("results/hindsight_gen31_longitudinal/summary.json")


def fixture():
    return L.build_longitudinal_fixture()


def test_frozen_ruler_and_both_adapters_are_unchanged():
    assert L.fixture_sha256() == FIXTURE_SHA
    assert L.scorer_contract_sha256() == SCORER_SHA
    assert H.adapter_contract_sha256() == ADAPTER_SHA
    assert P.adapter_contract_sha256() == PERSEUS_ADAPTER_SHA


def test_retain_payload_is_public_only_and_carries_native_provenance():
    for observation in fixture().observations:
        payload = H.retain_arguments(observation, "bank")
        H.assert_public_only(payload)
        assert payload["document_id"] == f"record-{observation.id}"
        assert payload["metadata"]["record_id"] == observation.id
        assert payload["timestamp"] == observation.ingestion_time.isoformat()
        assert set(payload["metadata"]) == set(H.adapter_contract_payload()["metadata_fields"])
    with pytest.raises(ValueError):
        H.assert_public_only({"content": "x", "metadata": {"truth_key": "leak"}})


def test_one_bank_holds_every_scope_and_configuration():
    payloads = [H.retain_arguments(o, "bank") for o in fixture().observations]
    assert {p["bank_id"] for p in payloads} == {"bank"}, "scope must never become a bank boundary"
    forge = [p for p in payloads if p["metadata"]["scope"] == "server:forge"]
    assert len({p["metadata"]["configuration"] for p in forge}) > 1


def test_routing_uses_only_public_coordinates():
    f = fixture()
    for case in f.cases:
        arguments = H.recall_arguments(case, "bank", 5)
        assert not set(arguments) & set(H.FORBIDDEN_FIELDS)
        operation = H.native_operation(case)
        assert ("query_timestamp" in arguments) == (operation == "recall_query_timestamp")
        if "query_timestamp" in arguments:
            assert arguments["query_timestamp"] == case.event_time.isoformat()
    assert set(H.adapter_contract_payload()["routing_inputs"]) == {"target_kind", "event_time", "scope"}


def test_adapter_declares_no_lifecycle_or_occurred_range_calls():
    contract = H.adapter_contract_payload()
    assert contract["lifecycle_calls"].startswith("none")
    assert contract["occurred_range"].startswith("not set")
    assert contract["post_filtering"].startswith("none")


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen31 results are produced by the runner")
def test_published_gen31_identity_and_isolation():
    summary = json.loads(RESULTS.read_text())
    identity = summary["system_identity"]
    assert identity["product_version"] == "0.9.2"
    assert identity["llm_provider"] == "none" and identity["reader"] == "none" and identity["inference_server"] == "none"
    assert "614241f622f53c4eeff9890bdc4f31cfecc418b3" in identity["embeddings"]
    assert "17.11" in identity["database"] and "0.8.6" in identity["database"]
    assert summary["model_or_product_llm_calls"] is False
    assert summary["fixture_sha256"] == FIXTURE_SHA and summary["scorer_contract_sha256"] == SCORER_SHA
    assert summary["adapter_contract_sha256"] == ADAPTER_SHA
    assert len(summary["repetitions"]) == 3
    for repetition in summary["repetitions"]:
        assert repetition["cases"] == 20 and repetition["checkpoints"] == 9
        assert repetition["provenance_exact_all_cases"] is True
    assert summary["failure_totals_all_repetitions"].get("future_leakage", 0) == 0
    assert summary["failure_totals_all_repetitions"].get("unmapped_provenance", 0) == 0
    assert summary["query_side_effects"]["database_changed_by_reads"] == "no change"


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen31 results are produced by the runner")
def test_paired_contrast_is_qualitative_and_preserves_gen29():
    contrast = json.loads(RESULTS.read_text())["paired_contrast_gen29_perseus"]
    assert "not a numeric leaderboard" in contrast["note"]
    assert set(contrast["only_in_gen29_perseus"]) == {"correction_failure", "history_erasure"}
    assert set(contrast["only_in_gen31_hindsight"]) == {"belief_truth_confusion", "scope_collapse"}
    assert "stale_persistence" in contrast["in_both"]


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen31 results are produced by the runner")
def test_checkpoint_prefix_discipline_and_absence_is_not_deletion():
    for path in sorted(Path("results/hindsight_gen31_longitudinal").glob("repetition-*.json")):
        repetition = json.loads(path.read_text())
        assert len(repetition["receipts"]) == 16
        counts = [int(state["documents"]) for _, state in sorted(repetition["checkpoint_state"].items())]
        assert counts == sorted(counts), "document count must never shrink across checkpoints"
        for evidence in (e for group in repetition["lifecycle"].values() for e in group):
            if evidence["active_current"] is False:
                assert evidence["disposition"] != "deleted"
