"""Gen90: the prefix-window curve for the four pure current-truth cases."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import window_ablation as ablation
from memory_bakeoff.longitudinal import build_longitudinal_fixture, score_longitudinal_case

ROOT = pathlib.Path(__file__).resolve().parents[1]
CURVE = ROOT / "results" / "window_ablation_gen90" / "curve.json"


@pytest.fixture(scope="module")
def report():
    return json.loads(CURVE.read_text())


def test_only_the_four_pure_cases_are_ablated(report):
    from memory_bakeoff import current_truth_audit as audit
    assert ablation.PURE_CASES == tuple(
        c for c in audit.CASES if audit.PURITY[c]["pure"])
    assert {r["case"] for r in report["rows"]} == set(ablation.PURE_CASES)


def test_a_window_is_a_prefix_and_nothing_else():
    ablation.assert_truncation_only(["A", "B", "C"], ["A", "B"])
    with pytest.raises(ValueError, match="prefix"):
        ablation.assert_truncation_only(["A", "B", "C"], ["B", "A"])
    with pytest.raises(ValueError, match="prefix"):
        ablation.assert_truncation_only(["A", "B", "C"], ["A", "C"])


def test_every_row_carries_the_full_curve(report):
    for row in report["rows"]:
        assert [p["k"] for p in row["points"]] == list(ablation.WINDOWS)
        for point in row["points"]:
            assert point["returned"] == row["returned"][:point["k"]]


def test_no_window_is_selected(report):
    assert "no_k_is_selected" in report["summary"]
    assert "smallest_clean_window" in report["rows"][0]
    assert set(report["summary"]["clean_count_at_each_window"]) == \
        {str(k) for k in ablation.WINDOWS}


def test_the_curve_is_not_monotonic(report):
    """Narrowing helps up to a point and then starts losing the current fact."""
    counts = {int(k): v for k, v in
              report["summary"]["clean_count_at_each_window"].items()}
    assert counts[2] > counts[1], "k=1 loses current facts that sit at rank 2"
    assert counts[2] > counts[3], "k=3 admits the stale record"
    assert counts[3] == counts[4] == counts[5]


def test_a_narrow_window_is_not_free(report):
    """k=1 costs required current facts - the counterweight to 'just truncate'."""
    lost = [r for r in report["rows"]
            if "missing_required_truth" in r["points"][0]["classes"]]
    assert len(lost) == 17
    assert {r["case"] for r in lost} == {"LQ11", "LQ14"}


def test_truncation_never_breaks_an_already_clean_result(report):
    broken = [r for r in report["rows"]
              if r["points"][-1]["clean"] and not r["points"][0]["clean"]]
    assert broken == []


def test_the_two_outcomes_are_separated(report):
    verdicts = report["summary"]["verdicts"]
    assert verdicts[ablation.ALREADY_CLEAN] == 24
    assert verdicts[ablation.WINDOW_POLICY] == 15
    assert verdicts[ablation.RANKING_FAILURE] == 9
    assert sum(verdicts.values()) == report["summary"]["observations"] == 48
    for row in report["rows"]:
        if row["verdict"] == ablation.RANKING_FAILURE:
            assert row["clean_windows"] == []
        if row["verdict"] == ablation.WINDOW_POLICY:
            assert row["clean_windows"] and not row["points"][-1]["clean"]


def test_the_ranking_failures_are_concentrated(report):
    failures = [r for r in report["rows"]
                if r["verdict"] == ablation.RANKING_FAILURE]
    by_engine = {}
    for row in failures:
        by_engine[row["engine"]] = by_engine.get(row["engine"], 0) + 1
    assert by_engine == {"perseus": 3, "mem0": 3, "hindsight": 3}
    assert "agentmemory" not in by_engine


def test_perseus_rank_instability_flips_the_verdict(report):
    """The reason repetitions are not pooled: the same query, a different answer."""
    verdicts = {r["repetition"]: r["verdict"] for r in report["rows"]
                if r["engine"] == "perseus" and r["case"] == "LQ11"}
    assert verdicts == {1: ablation.RANKING_FAILURE, 2: ablation.WINDOW_POLICY,
                        3: ablation.RANKING_FAILURE}
    assert report["contract"]["repetitions_pooled"] is False


def test_no_forbidden_transform_is_applied(report):
    contract = report["contract"]
    assert contract["transform"] == "returned[:k], and nothing else"
    for forbidden in ("deduplication", "label_aware_stopping", "reader_reasoning",
                      "semantic_post_filter", "reordering"):
        assert forbidden in contract["forbidden"]
    assert contract["no_engine_runs"] is True


def test_curve_scores_a_constructed_example():
    fixture = build_longitudinal_fixture()
    case = next(c for c in fixture.cases if c.id == "LQ11")
    stale_first = ablation.curve(score_longitudinal_case, fixture, case,
                                 ["L009", "L010"])
    assert stale_first["verdict"] == ablation.RANKING_FAILURE
    current_first = ablation.curve(score_longitudinal_case, fixture, case,
                                   ["L010", "L009"])
    assert current_first["verdict"] == ablation.WINDOW_POLICY
    assert current_first["smallest_clean_window"] == 1
