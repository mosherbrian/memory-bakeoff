"""Gen91: what produces stale-before-current ordering, per engine, within its own scale."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import ranking_mechanism as mech

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "ranking_mechanism_gen91" / "mechanism.json"


@pytest.fixture(scope="module")
def report():
    return json.loads(RESULTS.read_text())


def test_all_nine_ranking_failures_are_classified(report):
    assert len(report["rows"]) == 9
    assert sum(report["mechanism_totals"].values()) == 9


def test_each_engine_lands_in_a_different_bucket(report):
    by_engine = {}
    for row in report["rows"]:
        by_engine.setdefault(row["engine"], set()).add(row["mechanism"])
    assert by_engine["perseus"] == {mech.OPAQUE}
    assert by_engine["mem0"] == {mech.NEAR_TIE}
    assert by_engine["hindsight"] == {mech.MEANINGFUL_PREFERENCE}
    assert report["mechanism_totals"] == {mech.OPAQUE: 3, mech.NEAR_TIE: 3,
                                          mech.MEANINGFUL_PREFERENCE: 3}


def test_perseus_records_no_score_at_all(report):
    for row in report["rows"]:
        if row["engine"] == "perseus":
            assert row["stale_score"] is None and row["current_score"] is None
            assert row["observable"] is False
            assert row["verdict"] == mech.NOT_DEMONSTRABLE


def test_the_perseus_flip_hypothesis_is_not_answered(report):
    """Sol asked for the tie test explicitly; it cannot be run, and that is the result."""
    flip = report["perseus_flip_test"]
    assert flip["verdict"] == mech.NOT_DEMONSTRABLE
    assert flip["same_record_set"] is True
    assert flip["distinct_orders"] == 2
    assert "tie-break" in flip["hypothesis"]
    assert "NOT asserted" in flip["not_claimed"]
    assert "per-hit scores" in flip["rerun_prerequisite"]


def test_mem0_is_a_near_tie_within_its_own_list(report):
    rows = [r for r in report["rows"] if r["engine"] == "mem0"]
    for row in rows:
        assert row["share_of_field"] < mech.NEAR_TIE_SHARE
        assert row["pair_gap"] < row["field_gap"] / 20


def test_hindsight_separation_is_real_and_comes_from_the_reranker(report):
    rows = [r for r in report["rows"] if r["engine"] == "hindsight"]
    for row in rows:
        assert row["share_of_field"] > mech.NEAR_TIE_SHARE
    attribution = next(a for a in report["component_attribution"]
                       if a["engine"] == "hindsight")
    assert attribution["dominant_component"] == "reranker"
    assert attribution["identical_components"] == ["keyword"]
    gaps = attribution["component_gaps"]
    assert gaps["keyword"] == 0.0
    assert abs(gaps["reranker"]) > 40 * abs(gaps["semantic"])


def test_no_cross_engine_normalisation_is_performed(report):
    """Every judgement uses a within-engine, unit-free comparison."""
    assert "no_cross_engine_normalisation" in report["contract"]
    for row in report["rows"]:
        if row["observable"]:
            assert row["share_of_field"] == pytest.approx(
                row["pair_gap"] / row["field_gap"])


def test_repetition_identity_is_preserved(report):
    assert report["contract"]["repetition_identity"].startswith("preserved")
    keys = {(r["case"], r["engine"], r["repetition"]) for r in report["rows"]}
    assert len(keys) == 9


def test_classify_handles_the_three_shapes():
    assert mech.classify(None, None, [])["mechanism"] == mech.OPAQUE
    tie = mech.classify(0.91, 0.905, [0.39])
    assert tie["mechanism"] == mech.NEAR_TIE
    clear = mech.classify(0.88, 0.80, [0.001])
    assert clear["mechanism"] == mech.MEANINGFUL_PREFERENCE


def test_component_attribution_ignores_the_fused_score():
    result = mech.component_attribution(
        {"final": 0.9, "keyword": 0.3, "semantic": 0.87, "reranker": 0.89},
        {"final": 0.8, "keyword": 0.3, "semantic": 0.86, "reranker": 0.81})
    assert result["dominant_component"] == "reranker"
    assert "final" not in (result["identical_components"] or [])


def test_a_missing_component_is_not_guessed():
    result = mech.component_attribution({"keyword": None, "semantic": 0.8},
                                        {"keyword": 0.3, "semantic": 0.7})
    assert result["component_gaps"]["keyword"] is None
    assert result["dominant_component"] == "semantic"


def test_no_engine_runs(report):
    assert report["contract"]["no_engine_runs"] is True
