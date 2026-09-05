"""Gen92: is there a scored perseus read that keeps the Round-2 semantics?"""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import perseus_scored_read as scored

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "perseus_scored_read_gen92" / "feasibility.json"


@pytest.fixture(scope="module")
def report():
    return json.loads(RESULTS.read_text())


def test_the_round2_path_is_the_one_being_matched():
    assert scored.ROUND2_OPERATION == "perseus_vault_recall"
    assert scored.ROUND2_MODE == "hybrid"
    assert scored.CANDIDATES["perseus_vault_recall (mode=hybrid)"]["same_semantics"]


def test_no_candidate_both_scores_and_preserves_semantics():
    assert scored.qualifying_candidates() == []
    for name, entry in scored.CANDIDATES.items():
        assert not (entry["same_semantics"] and entry["returns_per_hit_scores"]), name


def test_the_scored_alternatives_are_declined_for_a_stated_reason():
    for name in ("perseus_vault_recall (mode=fused)", "perseus_vault_semantic_search"):
        entry = scored.CANDIDATES[name]
        assert entry["returns_per_hit_scores"] is True
        assert entry["same_semantics"] is False
        assert entry["evidence"]
    assert "different strategy" in scored.verdict()["substitution_declined"]


def test_the_hybrid_response_carries_no_relevance_score(report):
    probe = report["live_probe"]
    assert probe["mode"] == "hybrid"
    assert len(probe["per_hit_fields"]) == 35
    assert set(probe["per_hit_fields"]) == set(scored.HYBRID_ITEM_FIELDS)
    for field in probe["per_hit_fields"]:
        assert "relevance" not in field
        assert field not in ("score", "rank", "similarity", "bm25", "rrf")


def test_the_score_shaped_fields_are_shown_not_to_be_relevance(report):
    """decay_score and why_served look score-ish; the probe shows they are not."""
    probe = report["live_probe"]
    assert probe["decay_score_identical_for_both_hits"] is True
    assert probe["why_served_is_identical_for_both_hits"] is True
    for field in ("decay_score", "why_served", "certainty", "retrieval_profile"):
        assert field in scored.NOT_RELEVANCE


def test_the_product_itself_refuses_the_scored_trace_on_hybrid(report):
    """Measured by calling it, not by reading the parameter description."""
    refusal = report["selection_decisions_on_hybrid"]
    assert refusal["is_error"] is True
    assert "requires mode='fused'" in refusal["message"]
    assert scored.SELECTION_DECISIONS_ON_HYBRID["is_error"] is True


def test_the_verdict_is_opaque_and_the_rerun_is_not_unblocked():
    verdict = scored.verdict()
    assert verdict["verdict"] == scored.OPAQUE
    assert verdict["lq11_perseus_cause"] == scored.NOT_DEMONSTRABLE
    assert verdict["gen93_targeted_rerun"].startswith("NOT UNBLOCKED")
    assert verdict["no_benchmark_rerun"] is True


def test_the_other_two_mechanisms_are_closed_as_established():
    closed = scored.closed_mechanisms()
    assert closed["mem0"]["mechanism"] == "NEAR_TIE"
    assert closed["hindsight"]["mechanism"] == "MEANINGFUL_PREFERENCE"
    for entry in closed.values():
        assert entry["status"] == "CLOSED"
        assert entry["further_experiment"].startswith("none")


def test_the_method_used_a_live_response_not_documentation():
    assert "live shape probe" in scored.contract()["method"]
    assert "not from documentation" in scored.contract()["method"]


def test_qualifying_candidates_would_report_a_path_if_one_existed(monkeypatch):
    """The verdict is not hard-coded: give it a qualifying candidate and it changes."""
    monkeypatch.setitem(scored.CANDIDATES, "hypothetical",
                        {"same_semantics": True, "returns_per_hit_scores": True,
                         "evidence": "constructed"})
    assert scored.qualifying_candidates() == ["hypothetical"]
    assert scored.verdict()["verdict"] == scored.QUALIFIES
