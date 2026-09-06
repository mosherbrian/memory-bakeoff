"""Gen110: execution integrity, and the marker that stops this attempt being cited."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference as R

ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "results" / "gen110" / "attempt1"
FROZEN = ROOT / "results" / "gen109" / "attempt1" / "reader_interference_v1.json"


def _load(name):
    path = ATTEMPT / name
    if not path.exists():
        pytest.skip("Gen110 attempt not present in this checkout")
    return json.loads(path.read_text())


def _lines(name):
    path = ATTEMPT / name
    if not path.exists():
        pytest.skip("Gen110 attempt not present in this checkout")
    return [json.loads(l) for l in path.read_text().splitlines()]


# --- the attempt is non-evidence and must stay that way ----------------------
def test_attempt_is_marked_non_evidence():
    marker = _load("NON_EVIDENCE.json")
    assert marker["status"] == "NON_EVIDENCE"
    assert marker["attempt_preserved"] and marker["raw_evidence_intact"]
    assert len(marker["defects"]) == 2


def test_no_q_verdict_is_claimed_anywhere_in_the_attempt():
    results = _load("reader_interference_results.json")
    for banned in ("q1", "q2", "q3", "q4", "q5", "verdict",
                   "replicated_across_cores", "partial_replication"):
        assert banned not in json.dumps(results).lower(), banned


def test_the_report_issues_no_reader_effect():
    report = (ROOT / "research" / "PI_READER_INTERFERENCE_RESULT_GEN110.md").read_text()
    assert "NON_EVIDENCE" in report[:400]
    assert "No Q1–Q5 verdict is issued" in report


# --- execution identity and statelessness ------------------------------------
def test_every_planned_call_has_exactly_one_terminal_disposition():
    schedule = _load("call_schedule.json")["calls"]
    responses = _lines("reader_responses.jsonl")
    assert len(schedule) == 60 and len(responses) == 60
    indices = [r["call_index"] for r in responses]
    assert sorted(indices) == list(range(1, 61)), "a cell was omitted or retried"
    assert all(r["disposition"] in ("COMPLETED", "FAILED") for r in responses)


def test_no_cell_was_silently_retried():
    responses = _lines("reader_responses.jsonl")
    assert len({r["call_index"] for r in responses}) == len(responses)


def test_inference_settings_are_identical_across_every_cell():
    addendum = _load("execution_addendum.json")
    for key in ("temperature", "seed", "max_tokens", "requested_model", "endpoint"):
        assert key in addendum, key
    assert addendum["temperature"] == 0.0 and addendum["seed"] == 0
    assert addendum["stateless"] is True and addendum["no_silent_retry"] is True


def test_served_model_is_the_requested_pinned_model():
    responses = [r for r in _lines("reader_responses.jsonl")
                 if r["disposition"] == "COMPLETED"]
    assert {r["served_model"] for r in responses} == {"qwen3.6-35b-vulkan-nothink"}


# --- raw evidence linkage ----------------------------------------------------
def test_each_response_fingerprint_links_to_exactly_one_parser_input():
    responses = _lines("reader_responses.jsonl")
    cells = _load("reader_interference_results.json")["cells"]
    by_index = {r["call_index"]: r for r in responses}
    for cell in cells:
        assert cell["response_sha256"] == by_index[cell["call_index"]]["response_sha256"]


def test_requests_and_responses_cover_the_same_schedule():
    req = {r["call_index"] for r in _lines("reader_requests.jsonl")}
    res = {r["call_index"] for r in _lines("reader_responses.jsonl")}
    assert req == res == set(range(1, 61))


# --- the Gen109 freeze was not mutated ---------------------------------------
def test_frozen_contract_bytes_are_unchanged():
    import hashlib
    if not FROZEN.exists():
        pytest.skip("Gen109 freeze not present")
    digest = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    assert digest == "04222baddf36e6a31758ea152b1d0913a1e1a9635bcf00b147d657b15b67d879"
    assert json.loads(FROZEN.read_text())["contract_sha256"] == R.contract_hash()


def test_gen109_remains_frozen_unrun():
    assert json.loads(FROZEN.read_text())["status"] == "FROZEN_UNRUN" \
        if FROZEN.exists() else pytest.skip("Gen109 freeze not present")


# --- manifest integrity ------------------------------------------------------
def test_gen110_manifest_verifies_over_every_artifact():
    if not ATTEMPT.exists():
        pytest.skip("Gen110 attempt not present")
    result = EV.verify(ATTEMPT)
    assert result["verified"] is True
    assert result["missing"] == [] and result["mismatched"] == []


def test_a_second_write_into_the_attempt_is_refused(tmp_path):
    out = EV.next_attempt(tmp_path, 110)
    EV.write_evidence(out, "reader_responses.jsonl", {"a": 1})
    with pytest.raises(FileExistsError):
        EV.write_evidence(out, "reader_responses.jsonl", {"a": 2})


# --- the defects themselves, pinned so a repair must address them ------------
def test_grader_defect_is_reproducible():
    """A correct short answer must not grade as citation_mismatch once repaired."""
    parsed = R.parse_response("ANSWER: 41 t/s\nCITE: C0-CUR")
    graded = R.grade(parsed, current_id="C0-CUR", stale_id="C0-SUP",
                     current_answer="Atlas measured 41 t/s after the cache fix.",
                     stale_answer="Atlas measured 26 t/s.", answerable=True)
    assert graded["grade"] == R.CITATION_MISMATCH, \
        "defect 1 has been repaired - move this assertion to the new contract"


def test_abstention_defect_is_reproducible():
    """A prose abstention with CITE: NONE must not parse once repaired."""
    parsed = R.parse_response(
        "The provided records do not contain that information.\nCITE: NONE")
    assert parsed["parse_status"] == R.UNPARSED_NO_ANSWER, \
        "defect 2 has been repaired - move this assertion to the new contract"
