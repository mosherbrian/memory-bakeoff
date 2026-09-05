"""Gen88: the corrected retrieval-layer table, and the rules that keep it honest."""
from __future__ import annotations

import pytest

from memory_bakeoff import layer_boundary as lb
from memory_bakeoff import round2_reconciliation as rec


@pytest.fixture(scope="module")
def report():
    return rec.reconciliation()


def test_only_retrieval_layer_kinds_appear(report):
    assert set(report["frozen_configuration"]) == set(rec.RETRIEVAL_KINDS)
    assert len(rec.RETRIEVAL_KINDS) == 6
    for kind in lb.READER_LAYER_KINDS:
        assert kind not in report["frozen_configuration"]
    assert sorted(report["excluded_reader_kinds"]) == sorted(lb.READER_LAYER_KINDS)


def test_the_exclusion_is_enforced_not_manual():
    """Adding a reader kind to the frozen table must raise, not just look wrong."""
    table = rec.frozen_configuration()
    table["negative_unknown"] = {e: rec.cell(rec.MEASURED, "x", "y") for e in rec.ENGINES}
    with pytest.raises(ValueError, match="reader/full-product"):
        lb.assert_no_layer_mixing(table, layer=lb.RETRIEVAL_ONLY)


def test_every_cell_carries_a_status_and_provenance(report):
    for table in (report["frozen_configuration"], report["native_capability"]):
        for row, cells in table.items():
            for engine, entry in cells.items():
                assert entry["status"] in rec.STATUSES, (row, engine)
                assert entry["provenance"].strip(), (row, engine)
                assert "Gen" in entry["provenance"], (row, engine)


def test_a_cell_without_provenance_is_rejected():
    with pytest.raises(ValueError, match="where it comes from"):
        rec.cell(rec.MEASURED, "a finding", "")
    with pytest.raises(ValueError, match="unknown status"):
        rec.cell("GOOD", "a finding", "Gen88")


def test_a_missing_cell_is_a_construction_error():
    table = rec.frozen_configuration()
    del table["current_truth"]["mem0"]
    with pytest.raises(ValueError, match="no cell for"):
        rec.assert_complete(table)


def test_the_retracted_temporal_claims_are_not_reprinted_as_results(report):
    """Gen75's retractions must show as NOT_DEMONSTRABLE, not as perseus failures."""
    frozen = report["frozen_configuration"]
    for kind in ("as_of_event_truth", "corrected_historical_truth",
                 "late_arriving_history"):
        entry = frozen[kind]["perseus"]
        assert entry["status"] == rec.NOT_DEMONSTRABLE, kind
        assert "Gen7" in entry["provenance"], kind


def test_the_surviving_temporal_claims_are_kept(report):
    frozen = report["frozen_configuration"]
    assert frozen["historical_belief"]["perseus"]["status"] == rec.MEASURED
    assert frozen["as_of_event_truth"]["hindsight"]["status"] == rec.MEASURED
    assert "ignored" in frozen["as_of_event_truth"]["hindsight"]["finding"]


def test_scope_is_not_demonstrable_where_the_harness_never_asked(report):
    frozen = report["frozen_configuration"]
    assert frozen["scope_truth"]["perseus"]["status"] == rec.MEASURED
    for engine in ("mem0", "hindsight", "agentmemory"):
        assert frozen["scope_truth"][engine]["status"] == rec.NOT_DEMONSTRABLE


def test_the_ablation_table_records_the_opposite_scope_result(report):
    """The same three engines isolate perfectly once bound - and that is not a clash."""
    native = report["native_capability"]
    for engine in ("mem0", "hindsight", "agentmemory"):
        assert native["scope_isolation"][engine]["status"] == rec.MEASURED
        assert "Gen78" in native["scope_isolation"][engine]["provenance"]
    assert "never share a ranking column" in report["two_tables_rule"]


def test_the_one_real_engine_difference_is_recorded_in_the_ablation_table(report):
    native = report["native_capability"]
    for engine in ("perseus", "mem0", "hindsight"):
        assert native["configuration_isolation"][engine]["value"] == "0/3 collapse"
    agentmemory = native["configuration_isolation"]["agentmemory"]
    assert agentmemory["value"] == "3/3 collapse"
    assert "NO_USABLE_SECOND_SURFACE" in agentmemory["provenance"]


def test_no_engine_is_given_a_total(report):
    assert "no_single_score" in report
    for table in (report["frozen_configuration"], report["native_capability"]):
        for cells in table.values():
            for entry in cells.values():
                assert "score" not in entry and "total" not in entry


def test_the_report_states_that_old_numbers_were_not_carried_forward(report):
    assert report["superseded_numbers_not_carried"].startswith("no Gen68 cell")
    assert report["no_engine_runs"] is True


def test_counts_are_consistent_with_the_tables():
    tally = rec.counts()
    assert sum(tally["frozen_configuration"].values()) == 6 * len(rec.ENGINES)
    assert sum(tally["native_capability"].values()) == 3 * len(rec.ENGINES)
    assert tally["frozen_configuration"][rec.NOT_DEMONSTRABLE] > 0
