"""Gen86: the decision channel repaired, and order stability made measurable."""
from __future__ import annotations

import json
import math
import pathlib

import pytest

from memory_bakeoff import reader_contract_v3 as v3
from memory_bakeoff.longitudinal import (build_longitudinal_fixture, score_answer_claim,
                                         score_longitudinal_case, FailureClass)

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "order_stability_gen86"
ADOPTION = str(FailureClass.FAILED_PROCEDURE_ADOPTION)
MISSING = str(FailureClass.PROCEDURE_RECOMMENDATION_MISSING)
HALLUCINATION = str(FailureClass.UNKNOWN_HALLUCINATION)


@pytest.fixture(scope="module")
def fixture():
    return build_longitudinal_fixture()


@pytest.fixture(scope="module")
def cases(fixture):
    by_id = {c.id: c for c in fixture.cases}
    return by_id["LQ10"], by_id["LQ16"]


def test_the_gen85_defect_is_fixed(fixture, cases):
    """Adopting the right record while contrasting the wrong one must score clean."""
    procedure, _ = cases
    parsed = v3.parse_procedure(v3.CANNED_PROCEDURE["adopts_it_while_contrasting_the_failure"])
    graded = v3.score_procedure(score_longitudinal_case, fixture, procedure, parsed)
    assert graded["adopted"] == "L008"
    assert "L007" in graded["contrast"]
    assert graded["classes"] == () and graded["correct"] is True


def test_a_contrast_citation_can_never_fail_the_decision(fixture, cases):
    """The scorer sees the adopted id alone, whatever else the reader named."""
    procedure, _ = cases
    noisy = ("Warmup wins.\nADOPT: L008\nSUPPORT: L001 L002 L004\n"
             "CONTRAST: L007 L003 L005")
    graded = v3.score_procedure(score_longitudinal_case, fixture, procedure,
                                v3.parse_procedure(noisy))
    assert graded["classes"] == ()


def test_adopting_the_wrong_record_still_fails(fixture, cases):
    procedure, _ = cases
    graded = v3.score_procedure(score_longitudinal_case, fixture, procedure,
                                v3.parse_procedure(v3.CANNED_PROCEDURE["adopts_the_failed_attempt"]))
    assert ADOPTION in graded["classes"]


def test_declining_is_distinct_from_adopting_wrongly(fixture, cases):
    procedure, _ = cases
    graded = v3.score_procedure(score_longitudinal_case, fixture, procedure,
                                v3.parse_procedure(v3.CANNED_PROCEDURE["declines"]))
    assert graded["classes"] == (MISSING,)
    assert ADOPTION not in graded["classes"]


def test_both_unknown_paths_fire_and_stay_silent(fixture, cases):
    _, unknown = cases
    abstain = v3.score_unknown(score_answer_claim, unknown,
                               v3.parse_unknown(v3.CANNED_UNKNOWN["abstains"]))
    assert abstain["claim_classes"] == () and abstain["correct"] is True
    assert_ = v3.score_unknown(score_answer_claim, unknown,
                               v3.parse_unknown(v3.CANNED_UNKNOWN["asserts"]))
    assert assert_["claim_classes"] == (HALLUCINATION,)


def test_unparsed_is_excluded_from_both_verdicts(fixture, cases):
    procedure, unknown = cases
    p = v3.score_procedure(score_longitudinal_case, fixture, procedure,
                           v3.parse_procedure(v3.CANNED_PROCEDURE["ignores_the_format"]))
    u = v3.score_unknown(score_answer_claim, unknown,
                         v3.parse_unknown(v3.CANNED_UNKNOWN["ignores_the_format"]))
    for graded in (p, u):
        assert graded["status"] == v3.UNPARSED
        assert graded["excluded_from_scoring"] is True
        assert graded["correct"] is None


def test_the_prompt_still_carries_no_truth_or_engine_identity():
    prompt = v3.build_prompt("procedure", "Recommended procedure",
                             (("L008", "Forge C2 reproduction with warmup succeeded."),))
    v3.assert_reader_input_clean(prompt, engine="perseus")
    with pytest.raises(ValueError):
        v3.assert_reader_input_clean({"system": "s", "user": "procedure_outcome: success"},
                                     engine="perseus")


def test_the_two_templates_ask_for_different_decision_lines():
    procedure = v3.build_prompt("procedure", "q", (("L001", "a"),))["user"]
    unknown = v3.build_prompt("unknown", "q", (("L001", "a"),))["user"]
    assert "ADOPT:" in procedure and "ANSWER:" not in procedure
    assert "ANSWER:" in unknown and "ADOPT:" not in unknown


def test_the_contract_is_frozen_and_supersedes_gen85():
    contract = v3.contract()
    assert contract["supersedes"] == "reader-layer-gen85-v2"
    assert contract["engines_rerun"] is False
    assert contract["sampling"]["temperature"] == 0.0
    assert len(v3.contract_sha256()) == 64


# --- results of the sweep -------------------------------------------------
@pytest.fixture(scope="module")
def sweep():
    return json.loads((RESULTS / "stability.json").read_text())


def test_every_feasible_permutation_was_run(sweep):
    for case_id, entry in sweep["cases"].items():
        for evidence in entry["evidence_sets"]:
            assert evidence["permutations"] == math.factorial(len(evidence["records"]))


def test_engines_sharing_an_evidence_set_are_pooled(sweep):
    """Three engines returned the identical LQ16 set; they are one row, not three."""
    sets = sweep["cases"]["LQ16"]["evidence_sets"]
    shared = [e for e in sets if len(e["engines"]) > 1]
    assert shared, "the shared LQ16 evidence set must be pooled"
    assert set(shared[0]["engines"]) == {"perseus", "mem0", "hindsight"}


def test_order_stability_is_recorded_for_every_evidence_set(sweep):
    for entry in sweep["cases"].values():
        for evidence in entry["evidence_sets"]:
            assert evidence["order_stable"] in (True, False)
            assert 0.0 <= evidence["correct_fraction"] <= 1.0


def test_the_sweep_used_the_frozen_contract(sweep):
    assert sweep["contract_sha256"] == v3.contract_sha256()
    assert sweep["contract"]["model"] == v3.MODEL
    assert sweep["model_calls"] == sum(
        e["permutations"] for entry in sweep["cases"].values()
        for e in entry["evidence_sets"])
