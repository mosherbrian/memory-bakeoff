import json
from pathlib import Path

import pytest

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import agentmemory_longitudinal as A

FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
SCORER_SHA = "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"
ADAPTER_SHA = "a06482525d718dd1540c9491c80efe468c5414dcaf0ab6393781ac5254ff9b26"
RESULTS = Path("results/agentmemory_gen33_longitudinal/summary.json")


def truth_map():
    return {o.id: {"corrects_id": o.corrects_id, "supersedes_id": o.supersedes_id}
            for o in L.build_longitudinal_fixture().observations}


def test_frozen_ruler_and_adapter_hashes():
    assert L.fixture_sha256() == FIXTURE_SHA
    assert L.scorer_contract_sha256() == SCORER_SHA
    assert A.adapter_contract_sha256() == ADAPTER_SHA


def test_remember_payload_is_public_only_with_native_provenance():
    for observation in L.build_longitudinal_fixture().observations:
        payload = A.remember_arguments(observation, "agent-x")
        A.assert_public_only(payload)
        assert payload["sourceObservationIds"] == [observation.id]
        assert payload["project"] == A.PROJECT
        assert set(payload) == {"agentId", "project", "content", "sourceObservationIds"}


def test_scope_and_configuration_are_never_sent_as_fields():
    for observation in L.build_longitudinal_fixture().observations:
        assert "scope" not in A.remember_arguments(observation, "agent-x")
    for leak in ("scope", "configuration", "truth_key"):
        with pytest.raises(ValueError):
            A.assert_public_only({"content": "x", leak: "y"})


def test_supersession_classifier_judges_against_frozen_truth_only():
    truth = truth_map()
    assert A.classify_supersession("L001", "L003", truth) == "false_supersession"
    assert A.classify_supersession("L002", "L004", truth) == "legitimate_supersession"
    assert A.classify_supersession(None, "L003", truth) == "unmapped"
    assert A.classify_supersession("L001", None, truth) == "unmapped"


def test_adapter_declares_product_owned_retirement_and_no_harness_lifecycle():
    contract = A.adapter_contract_payload()
    assert contract["harness_lifecycle_calls"].startswith("none")
    rule = contract["native_lifecycle_rule"]
    assert rule["threshold"] == 0.7 and rule["predecessors_per_write"] == 1
    assert "not deletion" in rule["retired_state"]
    assert contract["temporal_surface"].startswith("none")


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen33 results are produced by the runner")
def test_treatment_activation_is_measured_not_inferred():
    activation = json.loads(RESULTS.read_text())["treatment_activation"]
    assert activation["activated"] is True
    assert activation["supersessions_per_repetition"] == [2, 2, 2]
    events = activation["events_repetition_1"]
    assert {(e["predecessor_canonical_id"], e["successor_canonical_id"]) for e in events} == {("L001", "L003"), ("L002", "L004")}
    assert {e["classification"] for e in events} == {"false_supersession", "legitimate_supersession"}
    validation = activation["preflight_validation"]
    assert validation["synthetic_pair_superseded"] is True
    assert validation["retired_row_still_in_kv"] is True
    assert validation["retired_row_absent_from_search"] is True


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen33 results are produced by the runner")
def test_false_supersession_is_unique_to_the_retiring_engine():
    contrast = json.loads(RESULTS.read_text())["four_engine_contrast"]
    # false_supersession is a LIFECYCLE class, scored by score_lifecycle_state -
    # it never appears in the case-level failure table. Reading it from the wrong
    # stream is the mistake that produced fabricated Gen31 lifecycle numbers.
    summary = json.loads(RESULTS.read_text())
    assert summary["lifecycle_failure_totals_all_repetitions"].get("false_supersession", 0) > 0
    assert "false_supersession" not in summary["failure_totals_all_repetitions"]
    assert "must never be merged" in summary["scorer_streams"]
    # history_erasure and correction_failure are shared with Perseus, so must NOT be called new
    assert set(contrast["present_in_perseus_only_among_append_only"]) == {"correction_failure", "history_erasure"}


@pytest.mark.skipif(not RESULTS.exists(), reason="Gen33 results are produced by the runner")
def test_retired_records_are_never_called_deleted():
    for path in sorted(Path("results/agentmemory_gen33_longitudinal").glob("repetition-*.json")):
        repetition = json.loads(path.read_text())
        for evidence in (e for group in repetition["lifecycle"].values() for e in group):
            assert evidence["disposition"] != "deleted"
            if evidence["active_current"] is False:
                assert evidence["historically_recoverable"] is True, "retired rows stay addressable in KV"
