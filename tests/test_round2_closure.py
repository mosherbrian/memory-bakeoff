"""Gen94: the canonical Round-2 retrieval result, and the guards on it."""
from __future__ import annotations

import pytest

from memory_bakeoff import round2_closure as closure
from memory_bakeoff import current_truth_closure, round2_reconciliation as rec
from memory_bakeoff.layer_boundary import READER_LAYER_KINDS


@pytest.fixture(scope="module")
def report():
    return closure.synthesis()


def test_every_claim_names_its_layer_and_status(report):
    for claim in report["surviving_claims"]:
        assert claim["layer"] in ("frozen_configuration", "native_capability")
        assert any(token in claim["status"] for token in
                   ("MEASURED", "NOT_DEMONSTRABLE", "NOT_APPLICABLE"))
        assert claim["provenance"].startswith("Gen")


def test_the_two_layers_are_both_present_and_kept_apart(report):
    assert set(report["frozen_configuration"]) == set(rec.RETRIEVAL_KINDS)
    assert set(report["native_capability"]) == {
        "scope_isolation", "configuration_isolation", "effective_time_recording"}
    layers = {c["layer"] for c in report["surviving_claims"]}
    assert layers == {"frozen_configuration", "native_capability"}


def test_the_scope_claim_appears_at_the_capability_layer_not_the_configuration_one(report):
    scope = [c for c in report["surviving_claims"] if "isolate scopes" in c["claim"]]
    assert len(scope) == 1
    assert scope[0]["layer"] == "native_capability"
    # and the frozen table still records the configuration truth separately
    for engine in ("mem0", "hindsight", "agentmemory"):
        assert report["frozen_configuration"]["scope_truth"][engine]["status"] == \
            rec.NOT_DEMONSTRABLE


def test_no_ranking_is_reconstructed(report):
    assert "no_ranking" in report
    closure.assert_no_ranking(report["no_ranking"])
    for claim in report["surviving_claims"]:
        closure.assert_no_ranking(claim["claim"])
    for entry in report["method"].values():
        closure.assert_no_ranking(entry["rule"])


def test_the_ranking_guard_rejects_a_league_table():
    for bad in ("perseus is the winner overall",
                "the best engine is perseus",
                "hindsight ranked first on temporal",
                "mem0 beats the others on scope"):
        with pytest.raises(ValueError, match="not a ranking"):
            closure.assert_no_ranking(bad)


def test_the_four_method_rules_each_cite_more_than_one_generation(report):
    method = report["method"]
    assert set(method) == {
        "prove_reachability_before_reading_a_zero",
        "never_read_an_adapter_choice_as_a_product_capability",
        "never_mix_the_retrieval_and_reader_layers",
        "decompose_a_pooled_failure_before_comparing_systems"}
    for name, entry in method.items():
        assert len(entry["established_by"]) >= 2, name
        assert entry["prevented"], name


def test_the_reader_kinds_are_excluded_and_named(report):
    assert sorted(report["reader_layer_excluded"]) == sorted(READER_LAYER_KINDS)
    for kind in READER_LAYER_KINDS:
        assert kind not in report["frozen_configuration"]


def test_the_synthesis_is_composed_not_retyped(report):
    """The numbers must come from the modules that measured them."""
    assert report["status_counts"] == rec.counts()
    assert report["current_truth"] == current_truth_closure.closure()
    assert closure.residue_summary()["hindsight"] == \
        current_truth_closure.DEMONSTRATED


def test_the_temporal_retractions_travel_with_the_result(report):
    assert len(report["temporal_retractions"]) == 4
    statuses = {r["status"] for r in report["temporal_retractions"]}
    assert statuses == {"RETRACTED", "QUALIFIED", "REATTRIBUTED"}
    assert report["temporal_surviving"]


def test_the_current_truth_residue_is_one_defect_one_tie_one_blind_spot_and_none():
    residue = closure.residue_summary()
    assert residue["hindsight"] == current_truth_closure.DEMONSTRATED
    assert residue["mem0"] == current_truth_closure.UNRESOLVED
    assert residue["perseus"] == current_truth_closure.UNDIAGNOSABLE
    assert residue["agentmemory"] == current_truth_closure.NONE_OBSERVED


def test_the_round_is_closed_with_no_engine_runs(report):
    assert report["round_status"] == "CLOSED"
    assert report["no_engine_runs"] is True
    assert report["generations_frozen"] == "Gen68 through Gen93"
