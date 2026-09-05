"""Gen89: the current_truth row decomposed by mechanism, not pooled."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import current_truth_audit as audit
from memory_bakeoff.longitudinal import (build_longitudinal_fixture, score_longitudinal_case,
                                         FailureClass, TargetKind)

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "current_truth_gen89" / "decomposition.json"
STALE = str(FailureClass.STALE_PERSISTENCE)
MISSING = str(FailureClass.MISSING_REQUIRED_TRUTH)


@pytest.fixture(scope="module")
def fixture():
    return build_longitudinal_fixture()


@pytest.fixture(scope="module")
def report():
    return json.loads(RESULTS.read_text())


def test_the_seven_cases_are_the_current_truth_row(fixture):
    current = tuple(c.id for c in fixture.cases if c.target_kind is TargetKind.CURRENT)
    assert current == audit.CASES
    assert len(current) * 3 == 21, "the pooled denominator was 21"


def test_every_failure_class_fires_and_the_case_can_stay_silent(fixture, report):
    control = report["controls"]
    assert control["clean_on_current_alone"]["classes"] == []
    assert control["stale_persistence_on_co_return"]["classes"] == [STALE]
    assert MISSING in control["stale_persistence_on_stale_alone"]["classes"]
    assert control["missing_on_empty"]["classes"] == [MISSING]


def test_the_scorer_ignores_rank_on_this_row(report):
    """Which version came first makes no difference to the score."""
    ranked = report["controls"]["rank_is_ignored_by_the_scorer"]
    assert ranked["current_first"] == ranked["stale_first"] == [STALE]


def test_the_current_fact_was_never_simply_lost(report):
    """missing_current_fact is a real, reachable class that never occurred."""
    assert report["mechanism_totals"].get(audit.MISSING, 0) == 0
    present = sum(report["mechanism_totals"][m] for m in
                  (audit.CLEAN, audit.WINDOW, audit.CONFLICTING))
    scoreable = sum(v for k, v in report["mechanism_totals"].items()
                    if k != audit.NOT_DEMONSTRABLE)
    assert present == 63 and scoreable == 72


def test_most_failures_are_co_return_not_loss(report):
    totals = report["mechanism_totals"]
    co_return = totals[audit.WINDOW] + totals[audit.CONFLICTING]
    assert co_return == 36
    assert totals[audit.STALE_ONLY] == 9
    assert co_return > 3 * totals[audit.STALE_ONLY]


def test_a_window_effect_names_the_limit_that_would_pass(report):
    windows = [r for r in report["rows"] if r["mechanism"] == audit.WINDOW]
    assert windows
    for row in windows:
        assert row["tighter_window_would_pass"] is True
        assert row["expected_rank"] < row["prohibited_rank"]
        assert row["passing_limit"] == row["expected_rank"]


def test_a_conflicting_row_is_a_real_ranking_failure(report):
    for row in report["rows"]:
        if row["mechanism"] == audit.CONFLICTING:
            assert row["prohibited_rank"] < row["expected_rank"]
            assert row["tighter_window_would_pass"] is False


def test_three_cases_are_failed_by_another_layer(report):
    impure = report["purity_audit"]["cases_carrying_another_layer"]
    assert set(impure) == {"LQ02", "LQ12", "LQ15"}
    assert impure["LQ02"]["layer"] == "configuration"
    assert impure["LQ12"]["layer"] == "temporal"
    assert impure["LQ15"]["layer"] == "abstention"
    assert set(report["purity_audit"]["pure_current_truth_cases"]) == \
        {"LQ01", "LQ11", "LQ14", "LQ17"}


def test_the_abstention_case_is_not_demonstrable_not_a_zero(report):
    rows = [r for r in report["rows"] if r["case"] == "LQ15"]
    assert len(rows) == 12
    assert all(r["mechanism"] == audit.NOT_DEMONSTRABLE for r in rows)


def test_the_pooled_counts_are_recorded_only_as_what_is_being_replaced(report):
    pooled = report["pooled_counts_being_replaced"]
    assert pooled == {"perseus": "6/21", "mem0": "6/21", "hindsight": "6/21",
                      "agentmemory": "9/21"}
    assert report["contract"]["pooled_counts_status"].startswith(
        "6/21, 6/21, 6/21 and 9/21 are NOT preserved")


def test_classify_distinguishes_loss_from_co_return():
    assert audit.classify(("A",), ("B",), ["A"])["mechanism"] == audit.CLEAN
    assert audit.classify(("A",), ("B",), ["B"])["mechanism"] == audit.STALE_ONLY
    assert audit.classify(("A",), ("B",), ["C"])["mechanism"] == audit.MISSING
    assert audit.classify(("A",), ("B",), ["A", "B"])["mechanism"] == audit.WINDOW
    assert audit.classify(("A",), ("B",), ["B", "A"])["mechanism"] == audit.CONFLICTING
    assert audit.classify((), ("B",), ["B"])["mechanism"] == audit.NOT_DEMONSTRABLE


def test_every_row_is_accounted_for(report):
    assert len(report["rows"]) == len(audit.CASES) * len(audit.ENGINES) * 3 == 84
    assert sum(report["mechanism_totals"].values()) == 84
    assert report["contract"]["no_engine_runs"] is True
