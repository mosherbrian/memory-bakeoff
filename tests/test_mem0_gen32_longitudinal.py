import json
from pathlib import Path

import pytest

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import mem0_longitudinal as M

FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
SCORER_SHA = "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"
ADAPTER_SHA = "f41e15212b435346fb50b7794ead1bd00898a4bf89db433cb89b98891502ac6d"
RESULTS = Path("results/mem0_gen32_longitudinal/summary.json")
SHARED_SEVEN = ("stale_persistence", "configuration_collapse", "failed_procedure_adoption",
                "late_history_corruption", "false_persistence", "missing_required_truth", "unsupported_evidence")


def test_frozen_ruler_and_adapter_hashes():
    assert L.fixture_sha256() == FIXTURE_SHA
    assert L.scorer_contract_sha256() == SCORER_SHA
    assert M.adapter_contract_sha256() == ADAPTER_SHA


def test_add_payload_matches_the_gen10_four_metadata_fields():
    for observation in L.build_longitudinal_fixture().observations:
        payload = M.add_arguments(observation)
        M.assert_public_only(payload)
        assert payload["infer"] is False
        assert payload["user_id"] == "memory-bakeoff"
        assert set(payload["metadata"]) == {"record_id", "source_ref", "scope", "timestamp"}
        assert payload["metadata"]["record_id"] == observation.id
        assert payload["metadata"]["timestamp"] == observation.ingestion_time.isoformat()


def test_configuration_is_never_handed_to_mem0_as_a_routing_key():
    for observation in L.build_longitudinal_fixture().observations:
        assert "configuration" not in M.add_arguments(observation)["metadata"]
    with pytest.raises(ValueError):
        M.assert_public_only({"text": "x", "metadata": {"configuration": "C1"}})
    with pytest.raises(ValueError):
        M.assert_public_only({"text": "x", "metadata": {"truth_key": "leak"}})


def test_scored_search_filters_on_the_constant_user_id_only():
    fixture = L.build_longitudinal_fixture()
    for case in fixture.cases:
        arguments = M.search_arguments(case, 5)
        assert arguments["filters"] == {"user_id": "memory-bakeoff"}
        assert arguments["threshold"] == 0.1 and arguments["limit"] == 5
        assert arguments["query"] == case.query
    contract = M.adapter_contract_payload()
    assert "deliberately NOT used" in contract["unscored_capability"]
    assert contract["lifecycle_calls"].startswith("none")


def test_every_case_uses_the_single_available_native_operation():
    fixture = L.build_longitudinal_fixture()
    assert {M.native_operation(c) for c in fixture.cases} == {"search_current_state"}
    assert M.adapter_contract_payload()["temporal_surface"].startswith("none")


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen32 results are produced by the runner")
def test_published_identity_and_no_llm_calls():
    summary = json.loads(RESULTS.read_text())
    identity = summary["system_identity"]
    assert identity["product_version"] == "2.0.19"
    assert identity["upstream_commit"] == "19cb89aff472325c707f64b2f34ae6afdbf7faf7"
    assert "770e825c74a004f165b78793f7c8fc4a95280878" in identity["dense_embedding"]
    assert "22b8d2af71a76161e18dd432d2cee0eefa66e412" in identity["sparse"]
    assert identity["spacy"].startswith("absent")
    assert summary["model_or_product_llm_calls"] is False
    assert summary["adapter_contract_sha256"] == ADAPTER_SHA
    assert len(summary["repetitions"]) == 3
    for repetition in summary["repetitions"]:
        assert repetition["cases"] == 20 and repetition["checkpoints"] == 9
        assert repetition["provenance_exact_all_cases"] is True
    assert summary["failure_totals_all_repetitions"].get("future_leakage", 0) == 0
    assert summary["failure_totals_all_repetitions"].get("unmapped_provenance", 0) == 0


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen32 results are produced by the runner")
def test_hypothesis_reporting_states_its_own_limits():
    hypothesis = json.loads(RESULTS.read_text())["preregistered_hypothesis"]
    assert set(hypothesis["shared_seven"]) == set(SHARED_SEVEN)
    assert hypothesis["reproduced_all_seven"] is True
    assert "not proof of causation" in hypothesis["interpretation"]
    assert "LQ20" in hypothesis["engine_specific_extra"]


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen32 results are produced by the runner")
def test_checkpoint_growth_and_absence_is_not_deletion():
    for path in sorted(Path("results/mem0_gen32_longitudinal").glob("repetition-*.json")):
        repetition = json.loads(path.read_text())
        states = [s for _, s in sorted(repetition["checkpoint_state"].items())]
        counts = [int(s["points"]) for s in states]
        assert counts == sorted(counts), "point count must never shrink across checkpoints"
        assert all(int(s["points"]) == int(s["expected_prefix"]) for s in states), "raw add must not dedup or merge"
        for evidence in (e for group in repetition["lifecycle"].values() for e in group):
            if evidence["active_current"] is False:
                assert evidence["disposition"] != "deleted"
