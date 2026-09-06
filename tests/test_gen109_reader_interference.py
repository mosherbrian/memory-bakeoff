"""Gen109: the ten failure conditions the frozen contract must not permit."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference as R

ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "results" / "gen109" / "attempt1"


def frozen():
    path = ATTEMPT / "reader_interference_v1.json"
    if not path.exists():
        pytest.skip("contract not frozen in this checkout")
    return json.loads(path.read_text())


# --- 1. no Gen85 output may influence anything -------------------------------
def test_no_gen85_quarantined_output_influences_the_contract():
    R.assert_no_gen85_influence(frozen())


def test_gen85_is_recorded_quarantined_and_absent_from_main():
    assert R.GEN85_STATUS["verdict"] == "QUARANTINED / NOT EVIDENCE"
    assert R.GEN85_STATUS["on_main"] is False
    marker = ROOT / "research" / "GEN85_READER_QUARANTINE.md"
    assert marker.exists()
    assert "quarantined: not-evidence" in marker.read_text()[:120]


def test_gen85_influence_guard_fires():
    with pytest.raises(ValueError, match="used as evidence"):
        R.assert_no_gen85_influence({"threshold_from": "gen85 order_ablation"})


# --- 2. placement may not change parsing -------------------------------------
def test_inline_and_line_separated_citations_parse_identically():
    """The exact Gen85 defect, as a permanent regression test."""
    assert R.parse_response("ANSWER: 240 CITE: C2-CUR") == \
           R.parse_response("ANSWER: 240\nCITE: C2-CUR")


@pytest.mark.parametrize("case", R.PARSER_FIXTURES, ids=lambda c: c["name"])
def test_parser_regression_fixtures(case):
    parsed = R.parse_response(case["text"])
    assert parsed["parsed"] is case["expect_parsed"], case["name"]
    assert parsed["cited_record_ids"] == case["expect_ids"], case["name"]


def test_parser_is_not_anchored_to_line_start():
    """An anchored pattern is what quarantined Gen85."""
    assert not R.CITE_PATTERN.pattern.startswith("^")
    assert not R.ANSWER_PATTERN.pattern.startswith("^")


# --- 3. parse status and semantic decision stay separate ---------------------
def test_an_unparsed_reply_is_never_graded_as_a_substantive_answer():
    parsed = R.parse_response("no fields at all")
    result = R.grade(parsed, current_id="C2-CUR", stale_id="C2-SUP",
                     current_answer="240", stale_answer="180", answerable=True)
    assert result["grade"] == R.UNPARSED_OUTCOME
    assert result["decision"] == "UNPARSED"
    R.assert_parse_and_grade_are_separate({**parsed, **result})


def test_separation_guard_fires_when_they_are_collapsed():
    with pytest.raises(ValueError, match="not a stale answer"):
        R.assert_parse_and_grade_are_separate(
            {"parse_status": R.UNPARSED_NO_CITE, "grade": R.PROHIBITED_STALE})


# --- 4. the four outcomes may not be pooled ----------------------------------
def test_frozen_contract_pools_no_outcomes():
    R.assert_no_outcome_pooling(frozen())


@pytest.mark.parametrize("key", ["total_failures", "reader_score",
                                 "error_rate", "pooled_outcomes"])
def test_pooling_guard_fires_on_each_pooled_shape(key):
    with pytest.raises(ValueError, match="pools distinct reader outcomes"):
        R.assert_no_outcome_pooling({key: 3})


def test_all_seven_grades_stay_distinct():
    assert len(set(R.GRADES)) == 7


# --- 5. the conflict pair differs only in order ------------------------------
def test_conflict_conditions_differ_only_in_order():
    fixture = frozen()["fixture"]
    for core in fixture["cores"]:
        pair = [c for c in fixture["cases"]
                if c["core"] == core and c["condition"] in R.CONFLICT_PAIR]
        assert len(pair) == 2
        R.assert_conflict_pair_differs_only_in_order(*pair)


def test_order_guard_fires_when_something_else_drifts():
    a = {"condition": "A", "context_order": ["x", "y"], "temperature": 0.0}
    b = {"condition": "B", "context_order": ["y", "x"], "temperature": 0.7}
    with pytest.raises(ValueError, match="differ in 'temperature'"):
        R.assert_conflict_pair_differs_only_in_order(a, b)


def test_order_guard_fires_when_order_is_identical():
    a = {"condition": "A", "context_order": ["x", "y"]}
    b = {"condition": "B", "context_order": ["x", "y"]}
    with pytest.raises(ValueError, match="must differ in context_order"):
        R.assert_conflict_pair_differs_only_in_order(a, b)


# --- 6. a fixture may not cross core, scope or configuration -----------------
def test_no_case_crosses_a_core_scope_or_configuration_boundary():
    for case in frozen()["fixture"]["cases"]:
        R.assert_within_core(case)


def test_core_guard_fires_on_a_mixed_case():
    with pytest.raises(ValueError, match="crosses scope"):
        R.assert_within_core({"id": "x", "records": [
            {"core": "a", "scope": "s1", "configuration": "c"},
            {"core": "a", "scope": "s2", "configuration": "c"}]})


# --- 7. cores may not be averaged --------------------------------------------
def test_across_core_verdicts_are_the_only_generalisation_allowed():
    assert set(R.ACROSS_CORE_VERDICTS) == {
        "REPLICATED_ACROSS_CORES", "PARTIAL_REPLICATION", "FIXTURE_SPECIFIC"}
    q4 = next(q for q in R.QUESTIONS if q["id"] == "Q4")
    assert "never averaged" in q4["rule"].lower()


def test_every_question_reports_cores_separately():
    for q in R.QUESTIONS:
        if q["id"] in ("Q1", "Q2", "Q3"):
            assert q["rule"].startswith("per core"), q["id"]


# --- 8. the design generation invokes no execution path ----------------------
def test_the_freeze_script_imports_no_engine_or_model_client():
    source = (ROOT / "scripts" / "run_gen109_freeze.py").read_text()
    banned = ("mem0", "hindsight", "agentmemory", "perseus", "openai",
              "requests", "httpx", "subprocess")
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in getattr(node, "names", [])]
            names.append(getattr(node, "module", "") or "")
            for name in names:
                assert not any(b in name.lower() for b in banned), name


def test_the_contract_declares_it_ran_nothing():
    f = frozen()
    assert f["status"] == "FROZEN_UNRUN"
    assert f["execution_boundary"]["gen109_runs_nothing"] is True
    assert "OPEN" in f["reader_question_state"]


# --- 9. artefacts live under immutable-evidence-v1 and cannot overwrite ------
def test_frozen_contract_is_manifested_and_verifies():
    if not ATTEMPT.exists():
        pytest.skip("contract not frozen in this checkout")
    result = EV.verify(ATTEMPT)
    assert result["verified"] is True and result["mismatched"] == []


def test_a_second_write_to_the_attempt_is_refused(tmp_path):
    out = EV.next_attempt(tmp_path, 109)
    EV.write_evidence(out, "reader_interference_v1.json", {"a": 1})
    with pytest.raises(FileExistsError):
        EV.write_evidence(out, "reader_interference_v1.json", {"a": 2})


def test_no_fixed_mutable_result_path_in_the_freeze_script():
    source = (ROOT / "scripts" / "run_gen109_freeze.py").read_text()
    assert 'ROOT / "results"' not in source
    assert "next_attempt" in source


# --- 10. the frozen contract cannot change without its hash changing --------
def test_contract_hash_matches_the_frozen_artifact():
    assert frozen()["contract_sha256"] == R.contract_hash()


def test_changing_the_contract_changes_the_hash(monkeypatch):
    before = R.contract_hash()
    monkeypatch.setattr(R, "CONDITIONS", R.CONDITIONS + ("SNEAKY",))
    assert R.contract_hash() != before


def test_changing_the_parser_changes_the_hash(monkeypatch):
    import re
    before = R.contract_hash()
    monkeypatch.setattr(R, "CITE_PATTERN", re.compile(r"^CITE:(.*)$", re.M))
    assert R.contract_hash() != before


# --- grader behaviour, so the ruler is demonstrated before it is used -------
@pytest.mark.parametrize("reply,expected", [
    ("ANSWER: 240\nCITE: C2-CUR", R.CORRECT_CURRENT),
    ("ANSWER: 180\nCITE: C2-SUP", R.PROHIBITED_STALE),
    ("ANSWER: it is 240, previously 180\nCITE: C2-CUR", R.MIXED_ANSWER),
    ("ANSWER: the records do not say\nCITE: NONE", R.INCORRECT_ABSTENTION),
])
def test_grader_assigns_each_outcome_from_benchmark_truth(reply, expected):
    result = R.grade(R.parse_response(reply), current_id="C2-CUR",
                     stale_id="C2-SUP", current_answer="240",
                     stale_answer="180", answerable=True)
    assert result["grade"] == expected


def test_abstention_is_correct_only_when_nothing_supports_an_answer():
    parsed = R.parse_response("ANSWER: the records do not say\nCITE: NONE")
    result = R.grade(parsed, current_id=None, stale_id=None,
                     current_answer=None, stale_answer=None, answerable=False)
    assert result["grade"] == R.CORRECT_INSUFFICIENCY
