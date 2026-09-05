"""Each revision shape must be attributed to a mechanism, never averaged.

The Perseus/Hindsight mirror is the finding, and a pooled score would erase it,
so these pin the mechanism attribution and the two discriminators.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff import correction_semantics as S

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "results/correction_semantics_gen72/semantics.json"


def payload() -> dict:
    return json.loads(REPORT.read_text())


def call(kind, expected, prohibited, returned, cluster="correction"):
    return S.mechanism(kind=kind, expected=expected, prohibited=prohibited,
                       returned=returned, cluster=cluster)["mechanism"]


def test_returning_the_asked_for_version_alone_is_clean():
    assert call("corrected_historical_truth", ["L005"], ["L001"], ["L005"]) == S.CLEAN


def test_answering_a_past_belief_with_its_successor_is_belief_confusion():
    assert call("historical_belief", ["L001"], ["L005"], ["L005"]) == S.BELIEF_CONFUSION


def test_a_past_belief_that_returns_nothing_reads_as_overwritten():
    assert call("historical_belief", ["L001"], ["L005"], []) == S.OVERWROTE


def test_serving_the_stale_value_is_a_correction_not_applied():
    assert call("as_of_event_truth", ["L005"], ["L001"], ["L001"]) == S.NOT_APPLIED


def test_a_backfilled_fact_that_is_absent_is_not_integrated():
    assert call("late_arriving_history", ["L011"], [], [], "late_arrival") == \
        S.NOT_INTEGRATED


def test_a_backfilled_fact_answered_with_the_later_one_is_misplaced():
    assert call("as_of_event_truth", ["L011"], ["L010"], ["L010"], "late_arrival") == \
        S.MISPLACED


def test_absent_and_misfiled_are_different_mechanisms():
    """Perseus is absent; the others are misfiled. Conflating them loses the finding."""
    assert S.NOT_INTEGRATED != S.MISPLACED


def test_perseus_retains_belief_but_cannot_place_a_late_fact():
    reading = payload()["engines"]["perseus"]["storage_reading"]
    assert reading["belief_truth_confusions"] == 0
    assert reading["retains_superseded_belief"] is True
    assert reading["integrates_late_arrival"] is False
    assert reading["late_arrival_not_integrated"] > 0


def test_hindsight_is_the_exact_mirror():
    reading = payload()["engines"]["hindsight"]["storage_reading"]
    assert reading["retains_superseded_belief"] is False
    assert reading["integrates_late_arrival"] is True


def test_no_engine_keeps_both_clocks_on_this_fixture():
    for engine, entry in payload()["engines"].items():
        reading = entry["storage_reading"]
        assert not (reading["retains_superseded_belief"]
                    and reading["integrates_late_arrival"]), engine


def test_every_reading_carries_its_scope_caveat():
    for entry in payload()["engines"].values():
        assert "does not prove a storage design" in entry["storage_reading"]["caveat"]


def test_the_contract_refuses_a_pooled_temporal_accuracy_score():
    assert "must not be averaged" in S.contract()["not_pooled"]
