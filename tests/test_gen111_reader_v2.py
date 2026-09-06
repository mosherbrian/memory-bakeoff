"""Gen111: the four repairs, enforced."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference_v2 as V

ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "results" / "gen111" / "attempt1"


def frozen():
    path = ATTEMPT / "reader_interference_v2.json"
    if not path.exists():
        pytest.skip("v2 not frozen in this checkout")
    return json.loads(path.read_text())


# --- repair 1: answer VALUE, not record prose --------------------------------
def test_short_and_full_sentence_answers_classify_identically():
    """The Gen110 defect: a correct short answer graded citation_mismatch."""
    case = next(c for c in V.build_fixture()["cases"]
                if c["core"] == "throughput:atlas" and c["condition"] == "CLEAN_CURRENT")
    cite = [case["current_opaque"]]
    short = V.grade(V.parse_response(json.dumps(
        {"answer": "41 t/s", "citations": cite})), case)
    long = V.grade(V.parse_response(json.dumps(
        {"answer": "Atlas measured 41 t/s after the cache fix.", "citations": cite})), case)
    assert short["outcome"] == long["outcome"] == V.CORRECT_CURRENT


def test_canonical_values_are_distinct_after_normalisation():
    for core, values in V.CANONICAL.items():
        fold = values["casefold"]
        assert V.normalise(values["current"], casefold=fold) != \
               V.normalise(values["stale"], casefold=fold), core


def test_normalisation_forbids_fuzzy_matching():
    for banned in ("LLM", "embedding", "fuzzy match", "semantic similarity"):
        assert banned in V.NORMALIZATION["forbidden"]


# --- repair 2: abstention is contract-legal ----------------------------------
def test_abstention_is_expressible_and_correct_in_its_control():
    case = next(c for c in V.build_fixture()["cases"]
                if c["condition"] == "INSUFFICIENT_CONTROL")
    parsed = V.parse_response('{"answer": "INSUFFICIENT", "citations": []}')
    assert parsed["parsed"]
    assert V.grade(parsed, case)["outcome"] == V.CORRECT_INSUFFICIENCY


def test_abstention_with_citations_fails_closed():
    case = next(c for c in V.build_fixture()["cases"]
                if c["condition"] == "CLEAN_CURRENT")
    reply = json.dumps({"answer": "INSUFFICIENT",
                        "citations": [case["current_opaque"]]})
    assert V.grade(V.parse_response(reply), case)["outcome"] == V.UNPARSED_OUTCOME


def test_abstention_where_an_answer_exists_is_incorrect():
    case = next(c for c in V.build_fixture()["cases"]
                if c["condition"] == "CLEAN_CURRENT")
    parsed = V.parse_response('{"answer": "INSUFFICIENT", "citations": []}')
    assert V.grade(parsed, case)["outcome"] == V.INCORRECT_ABSTENTION


# --- repair 3: blinding ------------------------------------------------------
@pytest.mark.parametrize("leak", ["C0-CUR", "C0-SUP", "C1-CUR", "C1-SUP",
                                  "C2-CUR", "C2-SUP", "C3-CUR", "C3-SUP"])
def test_no_prompt_contains_a_role_bearing_gen110_id(leak):
    for case in V.build_fixture()["cases"]:
        assert leak not in V.project_prompt(case)


def test_every_opaque_id_is_role_neutral():
    for case in V.build_fixture()["cases"]:
        for record in case["records"]:
            V.assert_id_is_role_neutral(record["opaque_id"])


def test_the_blinding_audit_fires_on_a_leaking_id():
    case = dict(next(c for c in V.build_fixture()["cases"]
                     if c["condition"] == "CLEAN_CURRENT"))
    case["records"] = [{**case["records"][0], "opaque_id": "REC-CUR-1"}]
    case["context_order"] = ["REC-CUR-1"]
    with pytest.raises(ValueError, match="leaks role"):
        V.assert_prompt_is_blind(case)


def test_prompt_contains_only_model_facing_content():
    for case in V.build_fixture()["cases"]:
        prompt = V.project_prompt(case)
        for forbidden in ("role", "condition", "current_answer", "stale_answer",
                          "superseded", "canonical"):
            assert forbidden.lower() not in prompt.lower(), case["id"]


def test_paired_conflict_prompts_differ_only_in_record_order():
    fixture = V.build_fixture()
    for core in fixture["cores"]:
        a, b = (next(c for c in fixture["cases"]
                     if c["core"] == core and c["condition"] == cond)
                for cond in V.CONFLICT_PAIR)
        assert {r["opaque_id"] for r in a["records"]} == \
               {r["opaque_id"] for r in b["records"]}
        assert a["context_order"] != b["context_order"]
        assert sorted(a["context_order"]) == sorted(b["context_order"])
        assert sorted(V.project_prompt(a).splitlines()) == \
               sorted(V.project_prompt(b).splitlines())


def test_same_opaque_id_used_for_a_record_across_paired_conditions():
    fixture = V.build_fixture()
    for core in fixture["cores"]:
        a, b = (next(c for c in fixture["cases"]
                     if c["core"] == core and c["condition"] == cond)
                for cond in V.CONFLICT_PAIR)
        assert a["current_opaque"] == b["current_opaque"]
        assert a["stale_opaque"] == b["stale_opaque"]


# --- repair 4: condition-relative grading ------------------------------------
def test_stale_answer_in_the_negative_control_is_correct():
    """v1 charged this prohibited_stale_answer. It is the control WORKING."""
    case = next(c for c in V.build_fixture()["cases"]
                if c["core"] == "throughput:atlas"
                and c["condition"] == "CLEAN_STALE_NEGATIVE_CONTROL")
    reply = json.dumps({"answer": "27 t/s", "citations": [case["stale_opaque"]]})
    assert V.grade(V.parse_response(reply), case)["outcome"] == V.CORRECT_STALE_CONTROL


def test_stale_answer_where_current_is_expected_is_prohibited():
    case = next(c for c in V.build_fixture()["cases"]
                if c["core"] == "throughput:atlas"
                and c["condition"] == "CONFLICT_STALE_FIRST")
    reply = json.dumps({"answer": "27 t/s", "citations": [case["stale_opaque"]]})
    assert V.grade(V.parse_response(reply), case)["outcome"] == V.PROHIBITED_STALE


def test_every_outcome_is_reachable_and_none_are_pooled():
    outcomes = {r["outcome"] for r in frozen()["truth_table"]}
    assert outcomes == set(V.OUTCOMES)
    assert len(set(V.OUTCOMES)) == 9


def test_each_truth_table_row_has_exactly_one_outcome():
    for row in frozen()["truth_table"]:
        assert isinstance(row["outcome"], str) and row["outcome"] in V.OUTCOMES


# --- Q5 / Q6 -----------------------------------------------------------------
@pytest.mark.parametrize("case", V.VALID_FIXTURES, ids=lambda c: c["name"])
def test_every_valid_synthetic_form_parses(case):
    assert V.parse_response(case["text"])["parsed"] is True


@pytest.mark.parametrize("case", V.INVALID_FIXTURES, ids=lambda c: c["name"])
def test_every_malformed_form_fails_closed(case):
    parsed = V.parse_response(case["text"])
    assert parsed["parsed"] is False
    assert parsed["parse_status"] in V.UNPARSED_STATES


def test_the_json_fence_decision_is_explicit_and_tested():
    assert V.ACCEPT_JSON_FENCE is True
    fenced = '```json\n{"answer": "x", "citations": []}\n```'
    assert V.parse_response(fenced)["parsed"] is True


def test_parser_decides_no_semantics():
    parsed = V.parse_response('{"answer": "41 t/s", "citations": ["REC-X"]}')
    assert set(parsed) == {"parse_status", "parsed", "answer", "citations"}
    for banned in ("outcome", "grade", "decision", "current", "stale"):
        assert banned not in parsed


# --- control gates -----------------------------------------------------------
def test_a_core_with_all_controls_correct_is_interpretable():
    cells = [{"condition": c, "outcome": V.CONTROL_RULE["expected"][c]}
             for c in V.CONTROL_CONDITIONS for _ in range(3)]
    assert V.core_is_interpretable(cells) is True


def test_one_bad_control_repetition_makes_the_core_uninterpretable():
    cells = [{"condition": c, "outcome": V.CONTROL_RULE["expected"][c]}
             for c in V.CONTROL_CONDITIONS for _ in range(3)]
    cells[0] = {"condition": "CLEAN_CURRENT", "outcome": V.CITATION_MISMATCH}
    assert V.core_is_interpretable(cells) is False


def test_q4_cannot_issue_a_label_without_all_cores_interpretable():
    q4 = next(q for q in V.QUESTIONS if q["id"] == "Q4")
    assert V.NOT_INTERPRETABLE in q4["rule"]
    assert "never averaged" in q4["rule"]


# --- preservation ------------------------------------------------------------
def test_v1_is_marked_superseded_without_being_rewritten():
    assert frozen()["supersedes"]["status"] == "SUPERSEDED_AS_RULER / NON_EVIDENCE"
    assert frozen()["supersedes"]["artifacts_unchanged"] is True


def test_gen109_and_gen110_artifacts_still_verify():
    for gen, count in (("gen109", 1), ("gen110", 6)):
        path = ROOT / "results" / gen / "attempt1"
        if not path.exists():
            pytest.skip(f"{gen} not present")
        result = EV.verify(path)
        assert result["verified"] is True and result["artifacts"] == count


def test_gen111_declares_it_ran_nothing():
    f = frozen()
    assert f["status"] == "FROZEN_UNRUN"
    assert f["future_run"]["gen111_runs_nothing"] is True
    assert "reuse Gen110 responses as a reader result" in f["future_run"]["must_not"]


def test_change_ledger_names_all_four_defects_and_who_found_them():
    ledger = frozen()["change_ledger"]
    changed = [e for e in ledger if e["defect"]]
    assert len(changed) == 4
    # Two defects were mine, found in my own output; two were the control
    # plane's, found by reading the requests I actually sent.
    by_control_plane = [e for e in changed
                        if e["found_by"].startswith("control plane")]
    by_executor = [e for e in changed if e["found_by"].startswith("executor")]
    assert len(by_control_plane) == 2 and len(by_executor) == 2


def test_contract_hash_matches_and_changes_when_edited(monkeypatch):
    assert frozen()["contract_sha256"] == V.contract_hash()
    before = V.contract_hash()
    monkeypatch.setattr(V, "ACCEPT_JSON_FENCE", False)
    assert V.contract_hash() != before
