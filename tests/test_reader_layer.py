"""Gen85: one reader over frozen evidence, and the controls that bound the result."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import reader_layer as reader
from memory_bakeoff.longitudinal import (build_longitudinal_fixture, score_answer_claim,
                                         score_longitudinal_case, FailureClass)

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "reader_layer_gen85"
ADOPTION = str(FailureClass.FAILED_PROCEDURE_ADOPTION)
MISSING = str(FailureClass.PROCEDURE_RECOMMENDATION_MISSING)
HALLUCINATION = str(FailureClass.UNKNOWN_HALLUCINATION)


@pytest.fixture(scope="module")
def fixture():
    return build_longitudinal_fixture()


@pytest.fixture(scope="module")
def cases(fixture):
    return ({c.id: c for c in fixture.cases}["LQ10"],
            {c.id: c for c in fixture.cases}["LQ16"])


def test_the_prompt_carries_no_truth_no_scorer_state_and_no_engine_identity():
    prompt = reader.build_prompt(
        "Recommended procedure",
        (("L008", "Forge C2 reproduction with warmup and fixed batch succeeded."),))
    reader.assert_reader_input_clean(prompt, engine="perseus")
    for term in reader.FORBIDDEN_IN_PROMPT:
        assert term not in (prompt["system"] + prompt["user"]).lower()
    with pytest.raises(ValueError):
        reader.assert_reader_input_clean(
            {"system": "s", "user": "procedure_outcome: success"}, engine="perseus")
    with pytest.raises(ValueError):
        reader.assert_reader_input_clean(
            {"system": "s", "user": "records from perseus"}, engine="perseus")


def test_only_public_fields_reach_the_reader(fixture):
    """The assertion text shown is the same text that was written to the engines."""
    for observation in fixture.observations:
        public = observation.public_dict()
        assert "procedure_outcome" not in public and "historical_only" not in public
        assert public["assertion"] == observation.assertion


def test_parsing_is_deterministic_and_names_its_own_failure():
    assert reader.parse_answer("x\nCITE: L008")["cited_ids"] == ("L008",)
    assert reader.parse_answer("x\nCITE: NONE")["refused"] is True
    # The attempt-1 defect: an inline citation must still parse.
    inline = reader.parse_answer("The records do not specify one. CITE: NONE")
    assert inline["parsed"] is True and inline["refused"] is True
    # The last citation wins.
    assert reader.parse_answer("CITE: L001\nmore\nCITE: L008")["cited_ids"] == ("L008",)
    # No citation is its own state, never a silent refusal.
    absent = reader.parse_answer("I think it is the second one.")
    assert absent["parsed"] is False and absent["refused"] is None


def test_unparsed_is_excluded_from_both_verdicts(fixture, cases):
    _, unknown = cases
    grade = reader.grade_abstention(score_answer_claim, score_longitudinal_case,
                                    fixture, unknown,
                                    reader.parse_answer("no cite line here"))
    assert grade["status"] == reader.UNPARSED
    assert grade["excluded_from_scoring"] is True
    assert grade["claim_classes"] == () and grade["retrieval_classes"] == ()


def test_controls_run_before_any_model_call(fixture, cases):
    procedure, unknown = cases
    control = reader.controls(score_longitudinal_case, score_answer_claim,
                              fixture, procedure, unknown)
    adoption = control["procedure_adoption"]
    assert adoption["cites_the_successful_attempt"]["classes"] == ()
    assert ADOPTION in adoption["cites_both"]["classes"]
    assert MISSING in adoption["cites_the_failed_attempt"]["classes"]
    abstention = control["unknown_abstention"]
    assert abstention["declines"]["claim_classes"] == ()
    assert abstention["asserts_without_support"]["claim_classes"] == (HALLUCINATION,)
    assert abstention["ignores_the_format"]["status"] == reader.UNPARSED


def test_the_reader_configuration_is_frozen_and_hashed():
    contract = reader.contract()
    assert contract["model"] == reader.MODEL
    assert contract["sampling"]["temperature"] == 0.0
    assert contract["engines_rerun"] is False
    assert contract["status_of_retrieval_only_results"].startswith("NOT_DEMONSTRABLE")
    assert len(reader.contract_sha256()) == 64


def test_every_engine_got_the_identical_reader():
    payload = json.loads((RESULTS / "reader.json").read_text())
    assert payload["reader_contract_sha256"] == reader.contract_sha256()
    assert payload["reader_contract"]["model"] == reader.MODEL
    assert set(payload["runs"]) == {"perseus", "hindsight", "mem0", "agentmemory"}


def test_the_reader_was_stable_across_repetitions():
    payload = json.loads((RESULTS / "reader.json").read_text())
    for engine, by_case in payload["runs"].items():
        for case_id, entry in by_case.items():
            cites = {str(r["parsed"]["raw_cite"]) for r in entry["repetitions"]}
            assert len(cites) == 1, f"{engine} {case_id} varied: {cites}"
            assert len(entry["repetitions"]) == reader.REPETITIONS


def test_perseus_evidence_produced_the_correct_procedure_reasoning():
    """The answer is right and the scorer still charges it - recorded, not smoothed."""
    payload = json.loads((RESULTS / "reader.json").read_text())
    row = payload["runs"]["perseus"]["LQ10"]["repetitions"][0]
    assert set(row["parsed"]["cited_ids"]) == {"L008", "L007"}
    assert row["classes"] == [ADOPTION]
    assert "warmup" in row["answer"].lower()


def test_unknown_hallucination_fired_for_the_first_time():
    payload = json.loads((RESULTS / "reader.json").read_text())
    fired = [e for e, by_case in payload["runs"].items()
             if by_case["LQ16"]["repetitions"][0]["grade"]["claim_classes"] == [HALLUCINATION]]
    assert sorted(fired) == ["mem0", "perseus"]


def test_the_abstention_split_is_an_order_effect_not_an_engine_difference():
    payload = json.loads((RESULTS / "reader.json").read_text())
    sets = {e: set(by_case["LQ16"]["retrieved_ids"])
            for e, by_case in payload["runs"].items()}
    assert sets["perseus"] == sets["mem0"] == sets["hindsight"], \
        "three engines returned the identical evidence set"
    ablation = json.loads((RESULTS / "order_ablation.json").read_text())
    assert ablation["orders_tried"] == 24
    assert ablation["verdict"] == "ORDER_EFFECT"
    assert 0 < ablation["abstained"] < ablation["orders_tried"]


def test_the_superseded_attempt_is_kept_with_its_reason():
    readme = (RESULTS / "superseded_attempt_1" / "README.md").read_text()
    assert "CITE_PATTERN" in readme
    assert (RESULTS / "superseded_attempt_1" / "reader.json").exists()
    assert reader.READER_VERSION.endswith("v2")
