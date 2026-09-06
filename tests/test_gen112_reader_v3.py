"""Gen112: D1-D6. The v2 grading defect, made unrepresentable."""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference_v2 as V2
from memory_bakeoff import reader_interference_v3 as V3

ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "results" / "gen112" / "attempt1"


def frozen():
    path = ATTEMPT / "reader_interference_v3.json"
    if not path.exists():
        pytest.skip("v3 not frozen in this checkout")
    return json.loads(path.read_text())


def case_for(condition, core="throughput:atlas"):
    return next(c for c in V3.build_fixture()["cases"]
                if c["core"] == core and c["condition"] == condition)


# --- D1: classification is independent of case composition -------------------
def test_classify_answer_cannot_see_the_case():
    """The defect is unrepresentable: the signature has no case parameter."""
    params = set(inspect.signature(V3.classify_answer).parameters)
    assert params == {"answer", "core"}


def test_both_values_detected_when_only_one_record_is_present():
    text = "41 t/s and 27 t/s"
    assert V3.classify_answer(text, "throughput:atlas") == "BOTH"


@pytest.mark.parametrize("condition", V3.CONDITIONS)
def test_classification_is_the_same_in_every_condition(condition):
    text = "41 t/s and 27 t/s"
    assert V3.classify_answer(text, "throughput:atlas") == "BOTH", condition


def test_single_values_remain_detectable_when_their_record_is_absent():
    assert V3.classify_answer("27 t/s", "throughput:atlas") == "STALE_ONLY"
    assert V3.classify_answer("41 t/s", "throughput:atlas") == "CURRENT_ONLY"


# --- D2: both witnesses repaired ---------------------------------------------
def test_witness_one_clean_current_now_grades_mixed():
    case = case_for("CLEAN_CURRENT")
    reply = json.dumps({"answer": "41 t/s, previously 27 t/s",
                        "citations": [case["current_opaque"]]})
    assert V2.grade(V2.parse_response(reply), case)["outcome"] == V2.CORRECT_CURRENT
    assert V3.grade(V3.parse_response(reply), case)["outcome"] == V3.MIXED


def test_witness_two_stale_control_now_grades_mixed():
    case = case_for("CLEAN_STALE_NEGATIVE_CONTROL")
    reply = json.dumps({"answer": "27 t/s, now 41 t/s",
                        "citations": [case["stale_opaque"]]})
    assert V2.grade(V2.parse_response(reply), case)["outcome"] == V2.CORRECT_STALE_CONTROL
    assert V3.grade(V3.parse_response(reply), case)["outcome"] == V3.MIXED


def test_the_audit_records_both_witnesses_with_both_outcomes():
    audit = json.loads((ATTEMPT / "gen111_grading_defect_audit.json").read_text()) \
        if ATTEMPT.exists() else pytest.skip("audit not present")
    assert len(audit["witnesses"]) == 2
    for w in audit["witnesses"]:
        assert w["v3_outcome"] == V3.MIXED and w["v2_outcome"] != V3.MIXED
    assert audit["gen111_artifacts_modified"] is False


# --- D3: the matrix is total and exclusive -----------------------------------
def test_every_matrix_row_resolves_to_exactly_one_outcome():
    for row in frozen()["truth_matrix"]:
        assert row["outcome"] in V3.OUTCOMES


def test_every_outcome_is_reachable():
    assert {r["outcome"] for r in frozen()["truth_matrix"]} == set(V3.OUTCOMES)


def test_no_row_is_skipped_because_a_role_pointer_is_null():
    rows = frozen()["truth_matrix"]
    for condition in V3.CONDITIONS:
        classes = {r["answer_class"] for r in rows if r["condition"] == condition}
        assert classes == set(V3.ANSWER_CLASSES), condition


# --- D4: controls have exactly one passing form ------------------------------
def test_no_control_pass_from_a_contradiction_or_bad_citation():
    V3.assert_no_control_pass_from_a_bad_answer(frozen()["truth_matrix"])


def test_each_control_has_exactly_one_passing_form():
    forms = V3.control_passing_forms()
    assert forms == {
        "CLEAN_CURRENT": {"answer_class": "CURRENT_ONLY",
                          "citation_relation": "MATCHES_CURRENT"},
        "CLEAN_STALE_NEGATIVE_CONTROL": {"answer_class": "STALE_ONLY",
                                         "citation_relation": "MATCHES_STALE"},
        "INSUFFICIENT_CONTROL": {"answer_class": "INSUFFICIENT",
                                 "citation_relation": "EMPTY"}}


@pytest.mark.parametrize("condition,good,bad", [
    ("CLEAN_CURRENT", "41 t/s", "41 t/s and 27 t/s"),
    ("CLEAN_STALE_NEGATIVE_CONTROL", "27 t/s", "27 t/s and 41 t/s"),
])
def test_adding_a_contradictory_value_breaks_the_control(condition, good, bad):
    """The exact proof Gen112 was asked for."""
    case = case_for(condition)
    cite = [case["current_opaque"] or case["stale_opaque"]]
    passing = V3.grade(V3.parse_response(
        json.dumps({"answer": good, "citations": cite})), case)
    failing = V3.grade(V3.parse_response(
        json.dumps({"answer": bad, "citations": cite})), case)
    assert passing["outcome"] in V3.CONTROL_PASSING
    assert failing["outcome"] == V3.MIXED


def test_a_mixed_control_cell_makes_the_core_uninterpretable():
    cells = [{"condition": c, "outcome": V3.CONTROL_RULE["expected"][c]}
             for c in V3.CONTROL_CONDITIONS for _ in range(3)]
    assert V3.core_is_interpretable(cells) is True
    cells[0] = {"condition": "CLEAN_CURRENT", "outcome": V3.MIXED}
    assert V3.core_is_interpretable(cells) is False


# --- D5: prompts unchanged and blind -----------------------------------------
def test_all_twenty_prompts_are_byte_identical_to_v2():
    cases = V3.build_fixture()["cases"]
    assert len(cases) == 20
    for case in cases:
        assert V3.project_prompt(case) == V2.project_prompt(case), case["id"]


def test_prompt_hashes_match_the_frozen_record():
    import hashlib
    recorded = frozen()["prompt_sha256"]
    for case in V3.build_fixture()["cases"]:
        digest = hashlib.sha256(V3.project_prompt(case).encode()).hexdigest()
        assert recorded[case["id"]] == digest


def test_no_prompt_leaks_evaluator_truth():
    for case in V3.build_fixture()["cases"]:
        V3.assert_prompt_is_blind(case)


def test_paired_conflict_prompts_still_differ_only_in_order():
    fixture = V3.build_fixture()
    for core in fixture["cores"]:
        a, b = (next(c for c in fixture["cases"]
                     if c["core"] == core and c["condition"] == cond)
                for cond in V3.CONFLICT_PAIR)
        assert a["context_order"] != b["context_order"]
        assert sorted(V3.project_prompt(a).splitlines()) == \
               sorted(V3.project_prompt(b).splitlines())


# --- parser carried forward unchanged ----------------------------------------
@pytest.mark.parametrize("case", V3.VALID_FIXTURES, ids=lambda c: c["name"])
def test_valid_forms_still_parse(case):
    assert V3.parse_response(case["text"])["parsed"] is True


@pytest.mark.parametrize("case", V3.INVALID_FIXTURES, ids=lambda c: c["name"])
def test_malformed_forms_still_fail_closed(case):
    assert V3.parse_response(case["text"])["parsed"] is False


# --- D6: history intact ------------------------------------------------------
@pytest.mark.parametrize("gen,count", [(109, 1), (110, 6), (111, 2)])
def test_every_earlier_attempt_still_verifies(gen, count):
    path = ROOT / "results" / f"gen{gen}" / "attempt1"
    if not path.exists():
        pytest.skip(f"gen{gen} not present")
    result = EV.verify(path)
    assert result["verified"] is True and result["artifacts"] == count


def test_v2_is_superseded_without_being_rewritten():
    assert frozen()["supersedes"]["status"] == "SUPERSEDED_AS_RULER / NON_EVIDENCE"
    assert frozen()["supersedes"]["artifacts_unchanged"] is True
    assert frozen()["supersedes"]["never_executed"] is True


def test_v2_implementation_still_exists_beside_v3():
    assert (ROOT / "src/memory_bakeoff/reader_interference_v2.py").exists()
    assert (ROOT / "src/memory_bakeoff/reader_interference_v3.py").exists()


def test_gen112_declares_it_ran_nothing():
    assert frozen()["status"] == "FROZEN_UNRUN"
    assert frozen()["future_run"]["gen112_runs_nothing"] is True


def test_contract_hash_matches_and_moves_when_edited(monkeypatch):
    assert frozen()["contract_sha256"] == V3.contract_hash()
    before = V3.contract_hash()
    monkeypatch.setattr(V3, "ANSWER_CLASSES", V3.ANSWER_CLASSES + ("SNEAKY",))
    assert V3.contract_hash() != before
