"""Capability and routing must stay separable, and zero evidence must not pass.

The pooled-total trap is the thing these guard: an engine that lacks a clock, an
engine whose clock is never consulted, and an engine whose clock is consulted and
does not work all look identical in a pooled column.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff import temporal_capability as C

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "results/temporal_capability_gen71/capability.json"


def payload() -> dict:
    return json.loads(REPORT.read_text())


def test_an_operation_with_no_temporal_parameter_is_current_only():
    entry = C.classify_operation("search_current_state", cases=39, leaked=36)
    assert entry["classification"] == C.CURRENT_ONLY
    assert entry["claims"] is None


def test_a_temporal_operation_that_never_leaks_earns_its_clock():
    entry = C.classify_operation("recall_hybrid_valid_at", cases=12, leaked=0)
    assert entry["classification"] == C.EFFECTIVE_TIME


def test_a_temporal_operation_that_leaks_is_a_failed_surface():
    entry = C.classify_operation("recall_query_timestamp", cases=15, leaked=15)
    assert entry["classification"] == C.FAILED_SURFACE
    assert "after the queried moment" in entry["why"]


def test_one_leak_is_enough_to_fail_a_surface():
    assert C.classify_operation("recall_query_timestamp", cases=15, leaked=1
                                )["classification"] == C.FAILED_SURFACE


def test_an_unexercised_operation_is_undetermined_not_passing():
    entry = C.classify_operation("recall_hybrid_as_of", cases=0, leaked=0)
    assert entry["classification"] == C.UNDETERMINED


def test_a_temporal_question_sent_to_a_current_only_operation_is_a_routing_gap():
    operations = {"search_now": {"classification": C.CURRENT_ONLY},
                  "as_of": {"classification": C.KNOWLEDGE_TIME}}
    routes = {"historical_belief": {"search_now": 3}}
    gaps = C.misrouted(routes, operations, ["historical_belief"])
    assert gaps and gaps[0]["verdict"] == "routing gap"
    assert gaps[0]["engine_has_a_working_temporal_operation"] == ["as_of"]


def test_an_engine_with_no_temporal_surface_is_not_called_a_routing_gap():
    operations = {"search_now": {"classification": C.CURRENT_ONLY}}
    gaps = C.misrouted({"historical_belief": {"search_now": 3}}, operations,
                       ["historical_belief"])
    assert gaps[0]["verdict"] == "no temporal surface"


def test_perseus_holds_both_clocks_and_leaks_nothing_temporal():
    perseus = payload()["engines"]["perseus"]
    classes = {name: op["classification"] for name, op in perseus["operations"].items()}
    assert classes["recall_hybrid_valid_at"] == C.EFFECTIVE_TIME
    assert classes["recall_hybrid_as_of"] == C.KNOWLEDGE_TIME
    assert perseus["leakage_on_temporal_questions"]["leaked"] == 0
    assert perseus["has_failed_temporal_surface"] == []


def test_hindsight_has_a_temporal_surface_that_failed():
    hindsight = payload()["engines"]["hindsight"]
    assert hindsight["has_failed_temporal_surface"] == ["recall_query_timestamp"]
    assert hindsight["has_working_temporal_operation"] == []


def test_current_question_leakage_is_annotated_as_expected_not_a_defect():
    for engine in payload()["engines"].values():
        assert "must not be read as a defect" in \
            engine["leakage_on_current_questions"]["note"]


def test_hallucination_is_closed_as_not_applicable_at_this_layer():
    closed = payload()["unknown_hallucination"]
    assert closed["status"] == "CLOSED_NOT_APPLICABLE"
    assert closed["layer"] == "retrieval engine"
    assert "reader" in closed["reserved_for"]


def test_the_contract_forbids_ranking_on_pooled_totals():
    assert "must not be used to order engines" in C.contract()["not_a_ranking"]
