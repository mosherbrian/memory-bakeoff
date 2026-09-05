"""Gen93: the current_truth row closed, and the guards that keep it honest."""
from __future__ import annotations

import pytest

from memory_bakeoff import current_truth_closure as closure
from memory_bakeoff import round2_reconciliation as rec


@pytest.fixture(scope="module")
def report():
    return closure.closure()


def test_the_decomposition_accounts_for_every_observation(report):
    d = report["decomposition"]
    assert d["observations"] == 48
    assert d["already_clean"] + d["retrieval_window_policy"] + \
        d["no_prefix_can_succeed"] == 48
    assert (d["already_clean"], d["retrieval_window_policy"],
            d["no_prefix_can_succeed"]) == (24, 15, 9)


def test_the_current_fact_was_never_lost(report):
    lost = report["current_fact_never_lost"]
    assert lost["observed"] == 0 and lost["of"] == 84
    assert "reachable" in lost["note"]


def test_the_nine_split_one_way_per_engine(report):
    residue = report["residue"]
    assert sum(e["count"] for e in residue.values()) == 9
    assert residue["hindsight"]["status"] == closure.DEMONSTRATED
    assert residue["mem0"]["status"] == closure.UNRESOLVED
    assert residue["perseus"]["status"] == closure.UNDIAGNOSABLE
    assert residue["agentmemory"]["status"] == closure.NONE_OBSERVED
    assert residue["agentmemory"]["count"] == 0


def test_only_hindsight_is_a_demonstrated_ranking_defect(report):
    assert report["only_one_is_a_ranking_quality_defect"] == "hindsight"
    demonstrated = [e for e, v in report["residue"].items()
                    if v["status"] == closure.DEMONSTRATED]
    assert demonstrated == ["hindsight"]


def test_perseus_repetition_instability_is_preserved_not_averaged(report):
    instability = report["perseus_instability"]
    assert instability["orders"] == {1: ["L009", "L010"], 2: ["L010", "L009"],
                                     3: ["L009", "L010"]}
    assert len(set(instability["verdicts"].values())) == 2
    assert "pooling" in instability["why_kept"]


def test_the_window_curve_is_recorded_but_not_prescribed(report):
    assert report["window_curve"] == {1: 31, 2: 35, 3: 24, 4: 24, 5: 24}
    closure.assert_not_a_recommendation(report["window_is_not_a_recommendation"])
    assert "not free" in report["window_is_not_a_recommendation"]


def test_the_guard_rejects_a_recommendation():
    for bad in ("the curve peaks at k=2, so we should use k=2",
                "we recommend a window of 2",
                "adopt k=2 as the default",
                "the best k is 2"):
        with pytest.raises(ValueError, match="not a policy"):
            closure.assert_not_a_recommendation(bad)
    closure.assert_not_a_recommendation(
        "the curve peaks at k=2 on this fixture and falls away on either side")


def test_the_row_excludes_the_three_impure_cases(report):
    excluded = report["excluded_from_this_row"]
    assert set(excluded) - {"provenance"} == {"LQ02", "LQ12", "LQ15"}


# --- the Round-2 table actually changed ----------------------------------
def test_the_pooled_row_is_replaced_in_the_reconciliation_table():
    row = rec.frozen_configuration()["current_truth"]
    for engine, entry in row.items():
        assert "REPLACED, not restated" in entry["provenance"]
        assert entry["value"] == closure.RESIDUE[engine]["status"]
        assert "never once lost" in entry["finding"]


def test_the_old_pooled_counts_appear_nowhere_in_the_table():
    """6/21 and 9/21 must not survive anywhere in the rebuilt row."""
    row = rec.frozen_configuration()["current_truth"]
    blob = " ".join(f"{e['finding']} {e['provenance']} {e['value']}"
                    for e in row.values())
    for stale in ("6/21", "9/21", "6 of 21", "9 of 21"):
        assert stale not in blob


def test_the_table_still_validates_after_the_replacement():
    report = rec.reconciliation()
    rec.assert_complete(report["frozen_configuration"])
    assert rec.counts()["frozen_configuration"][rec.MEASURED] == 14


def test_the_line_is_closed_with_no_engine_runs(report):
    assert report["line_status"] == "CLOSED"
    assert report["no_engine_runs"] is True
    assert report["replaces"].startswith("the pooled current_truth row")
