"""Point-in-time grouping must keep the clocks apart and name the blind spots.

Written against hand-made records as well as the committed Gen68 output, so a
later change to the grouping fails here rather than silently restating history.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff import point_in_time as P

ROOT = Path(__file__).resolve().parents[1]
GEN68 = ROOT / "results/round2_point_in_time_gen68/point_in_time.json"


def test_each_target_kind_is_tied_to_a_clock():
    assert P.CLOCK["current_truth"] == "now"
    assert P.CLOCK["as_of_event_truth"] == "event time"
    assert P.CLOCK["historical_belief"] == "knowledge time"


def test_grouping_separates_kinds_and_counts_clean_cases():
    cases = [
        {"case_id": "A", "failure_classes": []},
        {"case_id": "B", "failure_classes": ["stale_persistence"]},
        {"case_id": "C", "failure_classes": []},
    ]
    kinds = {"A": "current_truth", "B": "current_truth", "C": "historical_belief"}
    grouped = P.by_target_kind(cases, kinds)
    assert grouped["current_truth"]["cases"] == 2
    assert grouped["current_truth"]["clean"] == 1
    assert grouped["current_truth"]["clean_rate"] == 0.5
    assert grouped["historical_belief"]["clean_rate"] == 1.0
    assert grouped["historical_belief"]["clock"] == "knowledge time"


def test_a_case_with_two_failures_counts_both_but_is_one_case():
    cases = [{"case_id": "A", "failure_classes": ["a", "b"]}]
    grouped = P.by_target_kind(cases, {"A": "current_truth"})
    assert grouped["current_truth"]["cases"] == 1
    assert grouped["current_truth"]["failures"] == {"a": 1, "b": 1}


def test_reachability_separates_silence_from_impossibility():
    report = P.reachability(
        declared=["seen", "silent", "impossible"],
        observed=["seen"],
        unreachable={"impossible": "the harness never creates the opportunity"})
    assert report["observed"] == ["seen"]
    assert report["never_observed_but_reachable"] == ["silent"]
    assert "impossible" in report["unmeasurable_by_construction"]


def test_provenance_gaps_name_the_engines_that_cannot_answer():
    gaps = P.provenance_gaps({
        "full": {"has_per_case": True, "has_lifecycle": True},
        "thin": {"has_per_case": False, "has_lifecycle": False},
    })
    assert gaps["no_per_case_records"] == ["thin"]
    assert gaps["no_lifecycle_evidence"] == ["thin"]
    assert gaps["lifecycle_classes_not_cross_comparable"] is True


def test_the_recorded_run_declares_its_blind_spots():
    payload = json.loads(GEN68.read_text())
    reach = payload["ruler_reachability"]
    assert "future_leakage" in reach["unmeasurable_by_construction"]
    assert reach["declared"] == 16
    # A class is only "observed" when it actually fired for somebody.
    assert "future_leakage" not in reach["observed"]


def test_one_engine_has_no_per_case_records_and_is_named():
    payload = json.loads(GEN68.read_text())
    assert payload["provenance"]["no_per_case_records"] == [
        "observational_memory_gen26_longitudinal"]


def test_every_scored_engine_covers_all_eight_target_kinds():
    payload = json.loads(GEN68.read_text())
    for name, entry in payload["engines"].items():
        if not entry["has_per_case"]:
            continue
        assert len(entry["by_target_kind"]) == 8, name
        assert entry["cases_scored"] == 60, name
