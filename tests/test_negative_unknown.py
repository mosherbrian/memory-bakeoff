"""Gen84: the negative_unknown axis split into the two capabilities it conflates."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import negative_unknown as audit
from memory_bakeoff.longitudinal import (build_longitudinal_fixture, score_answer_claim,
                                         score_longitudinal_case, FailureClass, TargetKind)

ROOT = pathlib.Path(__file__).resolve().parents[1]
UNSUPPORTED = str(FailureClass.UNSUPPORTED_EVIDENCE)
HALLUCINATION = str(FailureClass.UNKNOWN_HALLUCINATION)


@pytest.fixture(scope="module")
def fixture():
    return build_longitudinal_fixture()


@pytest.fixture(scope="module")
def case(fixture):
    return next(c for c in fixture.cases if c.id == audit.CASE_ID)


def test_lq16_is_the_whole_axis(fixture):
    negative = [c.id for c in fixture.cases if c.target_kind is TargetKind.NEGATIVE_UNKNOWN]
    assert negative == [audit.CASE_ID]


def test_only_an_empty_result_scores_clean(fixture, case):
    assert case.expected_ids == ()
    assert score_longitudinal_case(fixture, case, ()).failure_classes == ()
    for returned in (("L001",), ("L001", "L002"), ("L001", "L002", "L003", "L004")):
        assert UNSUPPORTED in score_longitudinal_case(fixture, case, returned).failure_classes


def test_both_layers_fire_and_stay_silent(fixture, case):
    control = audit.controls(score_longitudinal_case, score_answer_claim, fixture, case)
    retrieval = control["retrieval_abstention"]
    assert retrieval["silent_on_empty"]["classes"] == ()
    assert retrieval["fires_on_one_record"]["classes"] == (UNSUPPORTED,)
    assert retrieval["fires_on_the_whole_store"]["classes"] == (UNSUPPORTED,)
    answer = control["answer_abstention"]
    assert answer["silent_on_refusal"]["classes"] == ()
    assert answer["fires_on_assertion"]["classes"] == (HALLUCINATION,)


def test_the_two_layers_are_scored_by_different_functions(fixture, case):
    """The split is real in the code, not just in the prose."""
    assert score_longitudinal_case(fixture, case, ()).failure_classes == ()
    assert score_answer_claim(case, assertion_supported=False) == (HALLUCINATION,)
    # The retrieval scorer can never emit the hallucination class...
    assert HALLUCINATION not in score_longitudinal_case(
        fixture, case, ("L001", "L002", "L003", "L004")).failure_classes
    # ...and the claim scorer can never emit the retrieval class.
    assert UNSUPPORTED not in score_answer_claim(case, assertion_supported=False)


def test_only_mem0_exposes_a_caller_settable_floor():
    floors = {e: s["status"] for e, s in audit.ABSTENTION_SURFACE.items()}
    assert floors["mem0"] == audit.FLOOR_PRESENT
    assert floors["perseus"] == floors["hindsight"] == floors["agentmemory"] == audit.NO_FLOOR


def test_the_adapter_argument_lists_match_the_frozen_adapters():
    from memory_bakeoff.providers import (agentmemory_longitudinal, hindsight_longitudinal,
                                          mem0_longitudinal, perseus_longitudinal)
    fixture = build_longitudinal_fixture()
    case = next(c for c in fixture.cases if c.id == audit.CASE_ID)
    live = {
        "mem0": set(mem0_longitudinal.search_arguments(case, 5)),
        "hindsight": set(hindsight_longitudinal.recall_arguments(case, "bank", 5)),
        "agentmemory": set(agentmemory_longitudinal.search_arguments(case, "agent", 5)),
    }
    for engine, arguments in live.items():
        assert arguments == set(audit.ABSTENTION_SURFACE[engine]["arguments"]), engine
    assert "threshold" in live["mem0"]
    assert "threshold" not in live["hindsight"] and "threshold" not in live["agentmemory"]
    assert perseus_longitudinal.adapter_contract_payload()["post_filtering"].startswith("none")


def test_no_threshold_separates_the_unanswerable_question():
    """The core measurement: abstaining on LQ16 costs real answers everywhere."""
    for engine in audit.OBSERVED:
        result = audit.separable(engine)
        assert result["separable"] is not True, f"{engine} would be separable"
        if result["separable"] is not audit.NOT_DEMONSTRABLE:
            assert result["legitimate_cases_lost_at_that_floor"] > 0


def test_agentmemory_is_most_confident_on_the_question_with_no_answer():
    entry = audit.OBSERVED["agentmemory"]
    assert entry["top_score"] > 1.0
    assert entry["cases_scoring_lower"] > entry["total_scored_cases"] / 2


def test_committed_records_show_the_whole_store_returned():
    from scripts.run_gen84_negative_unknown import committed
    data = committed(ROOT)
    for engine, entry in data.items():
        assert len(entry["repetitions"]) == audit.REPETITIONS
        for row in entry["repetitions"]:
            assert row["failure_classes"] == [UNSUPPORTED]
            assert len(row["returned"]) == audit.OBSERVED[engine]["returned"]
        if entry["cases_scoring_lower"] is not None:
            assert entry["cases_scoring_lower"] == audit.OBSERVED[engine]["cases_scoring_lower"]


def test_perseus_returns_no_score_so_no_floor_is_expressible():
    assert audit.OBSERVED["perseus"]["top_score"] is None
    assert audit.separable("perseus")["separable"] == audit.NOT_DEMONSTRABLE


def test_verdict_retracts_rather_than_confirms():
    verdict = audit.verdict()
    assert verdict["answer_abstention"] == audit.NOT_DEMONSTRABLE
    assert verdict["gen68_line_status"].startswith("RETRACTED")
    assert verdict["no_reader_added"] is True
    assert verdict["no_engine_runs"] is True


def test_no_reader_was_added_by_this_generation():
    module = (ROOT / "src" / "memory_bakeoff" / "negative_unknown.py").read_text()
    runner = (ROOT / "scripts" / "run_gen84_negative_unknown.py").read_text()
    for source in (module, runner):
        assert "reader_eval" not in source
        assert "llm" not in source.replace("llm_", "")


def test_audit_payload_was_written():
    payload = json.loads((ROOT / "results" / "negative_unknown_gen84" / "audit.json").read_text())
    assert payload["contract"]["contract_version"] == audit.CONTRACT_VERSION
    assert payload["corpus_at_checkpoint"] == audit.CORPUS_AT_CHECKPOINT
