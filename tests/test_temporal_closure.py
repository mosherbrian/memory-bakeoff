"""The closure must keep the axes independent and the retractions visible.

The failure this guards against is a later generation quietly averaging the axes
into a "temporal score", or reinstating a Perseus effective-time claim that the
evidence never supported.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff import temporal_closure as C

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "results/temporal_closure_gen75/closure.json"


def payload() -> dict:
    return json.loads(REPORT.read_text())


def engine(name: str) -> dict:
    return next(e for e in payload()["engines"] if e["engine"] == name)


def test_perseus_keeps_transaction_time_and_effective_time_is_not_demonstrable():
    entry = engine("perseus")
    assert entry["transaction_time_history"] == C.KEPT
    assert entry["effective_time_history"] == C.NOT_DEMONSTRABLE
    assert "cannot be on this build" in entry["temporal_query_surface_note"]


def test_not_demonstrable_is_distinct_from_not_kept():
    """Recording an untestable capability as a failure is as wrong as passing it."""
    assert C.NOT_DEMONSTRABLE != C.NOT_KEPT
    assert engine("hindsight")["effective_time_history"] == C.NOT_KEPT


def test_hindsight_surface_is_present_and_fails():
    assert engine("hindsight")["temporal_query_surface"] == C.SURFACE_FAILS


def test_engines_without_a_surface_are_not_called_failing():
    for name in ("mem0", "agentmemory"):
        assert engine(name)["temporal_query_surface"] == C.NO_SURFACE


def test_a_failed_surface_is_not_the_same_as_no_surface():
    assert C.SURFACE_FAILS != C.NO_SURFACE


def test_every_perseus_effective_time_claim_is_listed_with_a_status():
    statuses = {r["claim"]: r["status"] for r in payload()["retractions"]}
    assert statuses["recall_hybrid_valid_at is effective_time_capable"] == "RETRACTED"
    assert statuses["Perseus makes backfilled event-time facts unreachable"] == "RETRACTED"
    assert "QUALIFIED" in statuses.values()
    assert "REATTRIBUTED" in statuses.values()


def test_each_retraction_names_the_generation_that_found_it():
    for item in payload()["retractions"]:
        assert "Gen7" in item["because"] or "Gen6" in item["because"], item["claim"]


def test_the_surviving_claims_each_carry_evidence():
    surviving = payload()["surviving"]
    assert len(surviving) >= 4
    for item in surviving:
        assert item["evidence"].strip()


def test_the_closure_refuses_a_single_temporal_score():
    assert "must not be collapsed" in payload()["no_single_score"]


def test_the_scope_names_the_exact_builds():
    scope = payload()["scope"]
    for version in ("2.23.2", "0.9.2", "2.0.19", "0.9.29"):
        assert version in scope


def test_no_engine_was_run():
    assert payload()["engines_run"] == 0
