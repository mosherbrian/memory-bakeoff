"""Both repaired classes must fire on the failure and stay silent otherwise.

A repair that fires on everything is as useless as one that fires on nothing, so
each proof here has a control.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff import temporal_reachability as T
from memory_bakeoff.longitudinal import (
    FailureClass, TargetKind, build_longitudinal_fixture, fixture_sha256,
    score_answer_claim, score_longitudinal_case)

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "results/temporal_reachability_gen69/reachability.json"
# The hash carried by every committed Round-2 result.
FROZEN_FIXTURE = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"


def test_the_frozen_fixture_was_not_touched():
    """The repair is a run plan and a missing call, not a fixture edit."""
    assert fixture_sha256(build_longitudinal_fixture()) == FROZEN_FIXTURE


def test_returning_a_post_checkpoint_observation_is_future_leakage():
    fixture = build_longitudinal_fixture()
    case = next(c for c in fixture.cases if c.checkpoint_id == "CP01")
    visible = {o.id for o in fixture.prefix("CP01")}
    future = next(o.id for o in fixture.observations if o.id not in visible)
    score = score_longitudinal_case(fixture, case, tuple(case.expected_ids) + (future,))
    assert str(FailureClass.FUTURE_LEAKAGE) in score.failure_classes


def test_returning_only_visible_observations_is_not_leakage():
    fixture = build_longitudinal_fixture()
    case = next(c for c in fixture.cases if c.checkpoint_id == "CP01")
    score = score_longitudinal_case(fixture, case, tuple(case.expected_ids))
    assert str(FailureClass.FUTURE_LEAKAGE) not in score.failure_classes


def test_an_assertion_on_an_unknown_question_is_a_hallucination():
    fixture = build_longitudinal_fixture()
    case = next(c for c in fixture.cases
                if c.target_kind is TargetKind.NEGATIVE_UNKNOWN)
    graded = T.grade_negative_unknown(
        "The client lives at internal/gen/aurora_client.go.",
        expected_ids=case.expected_ids,
        score_answer_claim=score_answer_claim, case=case)
    assert str(FailureClass.UNKNOWN_HALLUCINATION) in graded["failure_classes"]


def test_declining_is_never_charged():
    fixture = build_longitudinal_fixture()
    case = next(c for c in fixture.cases
                if c.target_kind is TargetKind.NEGATIVE_UNKNOWN)
    for answer in ("Unknown.", "There is no record of that.", "", None):
        graded = T.grade_negative_unknown(
            answer, expected_ids=case.expected_ids,
            score_answer_claim=score_answer_claim, case=case)
        assert graded["failure_classes"] == (), answer


def test_a_case_with_real_evidence_is_left_to_the_retrieval_scorer():
    """Only questions whose answer is 'unknown' are graded on the answer claim."""
    assert T.assertion_supported("anything at all", expected_ids=("L001",)) is True


def test_decline_detection_is_not_fooled_by_a_confident_answer():
    assert T.declines("Unknown") is True
    assert T.declines("It is release/aurora-2.x.") is False


def test_the_recorded_proof_shows_both_classes_firing_with_controls():
    payload = json.loads(PROOF.read_text())
    leak = payload["future_leakage"]
    assert leak["cases_that_fire"] == leak["cases_tried"] > 0
    assert leak["control_is_clean_of_leakage"] is True
    claim = payload["unknown_hallucination"]
    assert claim["fires_on_assertion"] is True
    assert claim["silent_on_refusal"] is True
    assert payload["engines_run"] == 0


def test_the_excluded_engine_is_named_with_its_reason():
    payload = json.loads(PROOF.read_text())
    excluded = payload["exclusions"]["observational_memory_gen26_longitudinal"]
    assert excluded["recoverable_from_existing_artifacts"] is False
    assert "never produced retrieval results" in excluded["reason"]
    assert "no re-run" in excluded["not_done"]
