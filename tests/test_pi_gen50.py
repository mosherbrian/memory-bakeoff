"""Gen50 focused tests: selection frozen first, taxonomy honest, integrity failure recorded."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results" / "pi_failure_audit_gen50"


def _json(name: str) -> dict:
    path = OUT / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


def test_selection_was_frozen_before_reading_and_is_outcome_based():
    sel = _json("selection_manifest.json")
    assert sel["frozen_before_any_raw_transcript_was_read"] is True
    assert len(sel["cases"]) == 6
    for case in sel["cases"]:
        assert case["why"] and case["anomaly"]


def test_every_focal_case_has_a_reconstruction_and_an_analysis():
    sel = _json("selection_manifest.json")
    for case in sel["cases"]:
        path = OUT / "cases" / f"{case['id']}.json"
        if not path.exists():
            pytest.skip("case files not present")
        data = json.loads(path.read_text())
        assert data["timeline"]
        assert data["analysis"]["primary_mechanism"]
        assert data["analysis"]["critical_point"]


def test_the_deleted_raw_streams_are_recorded_as_my_own_failure():
    integ = _json("raw_integrity.json")
    finding = integ["finding"]
    assert finding["raw_streams_available"] is False
    assert finding["self_inflicted"] is True
    assert "pi_state_control_gen47" in finding["manifests_corrected"]
    assert "pi_state_control_gen49" in finding["manifests_corrected"]


def test_the_corrected_manifests_no_longer_claim_retention():
    for gen in ("pi_state_control_gen47", "pi_state_control_gen49"):
        path = ROOT / "results" / gen / "raw_stream_manifest.json"
        if not path.exists():
            pytest.skip(f"{gen} manifest missing")
        data = json.loads(path.read_text())
        assert data["streams_still_exist"] is False
        assert "CORRECTION" in data["correction"]


def test_no_failure_was_classified_as_missing_context():
    """The audit's central negative: say it, do not soften it."""
    matrix = _json("cross_case_matrix.json")
    assert matrix["context_problems"] == []
    assert matrix["cases_needing_unavailable_old_history"] == []
    assert "none" in matrix["retrieval_evidence"].lower()


def test_the_two_timeouts_had_already_reached_task_truth():
    timeouts = _json("cross_case_matrix.json")["timeout_cases"]
    for key in ("gen47-T3-r1-B", "gen49-IP2-r1-C"):
        assert timeouts[key]["mutations_after"] == 0
        assert timeouts[key]["calls_after_last_mutation"] > 100


def test_the_candidate_invariant_is_proposed_not_implemented():
    candidate = _json("cross_case_matrix.json")["minimal_candidate_invariant"]
    assert candidate["not_implemented_in_gen50"] is True
    assert candidate["caveat"]
    assert set(candidate["would_have_affected"]) == {"gen47-T3-r1-B", "gen49-IP2-r1-C"}


def test_the_floor_is_recorded_as_having_no_mechanical_effect_on_any_failure():
    matrix = _json("cross_case_matrix.json")
    assert len(matrix["counterfactual_summary"]["no_mechanical_effect_for_the_floor"]) == 5


def test_gen49_prose_correction_is_labelled_and_changed_no_numbers():
    report = (ROOT / "research" / "PI_HUMAN_DIRECTION_FLOOR_GEN49_LIVE.md").read_text()
    assert "a quarter of the treated runs" in report
    assert "Prose arithmetic only" in report
    assert "11/12" in report


def test_no_gen47_or_gen49_leaf_was_altered():
    for gen, digest_name in (("pi_state_control_gen47", "6063e3c857f213b1"),
                             ("pi_state_control_gen49", "4fd91e505b80f12a")):
        path = ROOT / "results" / gen / "scientific_digest.txt"
        if not path.exists():
            pytest.skip(f"{gen} digest missing")
        assert path.read_text().strip().startswith(digest_name)
