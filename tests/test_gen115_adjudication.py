"""The Gen115 guards must actually fire. An unexercised guard is Gen113's defect."""
import json
import pytest
from memory_bakeoff import gen115_adjudication as G


def test_contract_hash_is_stable_and_covers_the_rules():
    first = G.contract_hash()
    assert first == G.contract_hash()
    assert len(first) == 64


def test_r1_guard_fires_on_the_phrase_that_caused_this_generation():
    with pytest.raises(ValueError, match="machine label"):
        G.assert_machine_label_not_reused_as_finding(
            "In 21 of 24 tries the reader contradicts itself in 21 of 24 cells.")


def test_r1_guard_survives_reflow_and_case():
    with pytest.raises(ValueError):
        G.assert_machine_label_not_reused_as_finding(
            "The Reader   Contradicts\n  Itself In 21 of 24\ttries")


def test_r1_guard_allows_the_machine_label_reported_as_a_label():
    G.assert_machine_label_not_reused_as_finding(
        "v4 assigned mixed_contradictory_answer to 21 of 24 conflict cells.")


def test_r2_semantic_review_may_never_be_confirmatory():
    with pytest.raises(ValueError, match="confirmatory"):
        G.assert_not_confirmatory(
            {"call_index": 7, "semantic_category": G.UNRESOLVED_BOTH, "confirmatory": True})


def test_r2_allows_a_row_that_declares_itself_exploratory():
    G.assert_not_confirmatory(
        {"call_index": 7, "semantic_category": G.UNRESOLVED_BOTH, "confirmatory": False})


def test_r3_a_category_without_a_rationale_is_refused():
    with pytest.raises(ValueError, match="rationale"):
        G.assert_rationale_present(
            [{"call_index": 1, "semantic_category": G.CURRENT_ONLY, "rationale": "  "}])


def test_r3_accepts_a_written_rationale():
    G.assert_rationale_present(
        [{"call_index": 1, "semantic_category": G.CURRENT_ONLY,
          "rationale": "answers '512 GiB' and nothing else"}])


def test_categories_are_finer_than_the_v4_bucket_they_replace():
    for name in (G.UNRESOLVED_BOTH, G.RECONCILED_TO_CURRENT,
                 G.RECONCILED_TO_STALE, G.EXPLICIT_CONTRADICTION):
        assert name in G.SEMANTIC_CATEGORIES
    assert len(set(G.SEMANTIC_CATEGORIES)) == len(G.SEMANTIC_CATEGORIES)


def test_every_decision_rule_is_uniquely_identified():
    ids = [r["id"] for r in G.DECISION_RULES]
    assert ids == sorted(set(ids)) and len(ids) == 7


def test_gen114_is_classified_as_not_confirmatory():
    assert "NOT_CONFIRMATORY" in G.EVIDENCE_CLASSIFICATION["gen114"]
    assert "development-exposed" in G.EVIDENCE_CLASSIFICATION["development_exposed"]


def test_the_written_adjudication_obeys_its_own_contract():
    """The artifact this generation published must pass the guards it declares."""
    from pathlib import Path
    out = Path(__file__).resolve().parents[1] / "results/gen115/attempt4"
    table = json.loads((out / "gen115_conflict_adjudication.json").read_text())
    rows = table["rows"]
    assert len(rows) == 24
    G.assert_rationale_present(rows)
    for row in rows:
        G.assert_not_confirmatory(row)
        assert row["semantic_category"] in G.SEMANTIC_CATEGORIES
    assert table["stale_only_answers"] == 0
    # The retraction rests on these COMPUTED fields, not on the authored category.
    assert table["computed_stale_only_answers"] == 0
    assert table["computed_prompts_disclosing_recency"] == 0
    assert table["explicit_contradiction_is_computed"] is False
    assert all(r["asserts_stale_as_current"] is False for r in rows)
    assert all(r["prompt_discloses_recency"] == [] for r in rows)
    assert table["status"] == G.OPEN_EXPLORATORY


def test_the_claim_ledger_uses_only_declared_statuses():
    from pathlib import Path
    out = Path(__file__).resolve().parents[1] / "results/gen115/attempt4"
    ledger = json.loads((out / "gen115_claim_ledger.json").read_text())
    assert ledger["contract_hash"] == G.contract_hash()
    for claim in ledger["claims"]:
        assert claim["status"] in G.CLAIM_STATUSES
        assert claim["basis"].strip()
    retracted = [c for c in ledger["claims"] if c["status"] == G.RETRACTED]
    assert len(retracted) == 4


def test_unique_counts_are_labelled_by_method():
    """attempt1/2 published a per-case count under a global-sounding phrase."""
    from pathlib import Path
    out = Path(__file__).resolve().parents[1] / "results/gen115/attempt4"
    u = json.loads((out / "gen115_conflict_adjudication.json").read_text())["uniqueness"]
    assert u["all_cells_unique_global"] == 17
    assert u["all_cells_unique_per_case"] == 21
    assert u["conflict_unique_global"] == 9
    assert u["all_cells_unique_global"] != u["all_cells_unique_per_case"], \
        "the two methods differ; that is exactly why both must be published"


def test_the_recency_scan_actually_ran():
    from pathlib import Path
    out = Path(__file__).resolve().parents[1] / "results/gen115/attempt4"
    d = json.loads((out / "gen115_fixture_decidability.json").read_text())
    assert d["tokens_found"] == []
    assert "fails closed" in d["scan_performed_by"]
    assert len(d["tokens_scanned_for"]) == 8
