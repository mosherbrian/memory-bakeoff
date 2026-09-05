"""The guardrail must reject a hollowed bank before it can be called valid.

Written against hand-made outcomes as well as the recorded run, so a later change
to the rule fails here rather than quietly restating what Gen62 concluded.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from memory_bakeoff.evidence_ruler import retention_screen as S

ROOT = Path(__file__).resolve().parents[1]


def outcome(passed: bool) -> dict:
    return {"passed": passed, "tail": ""}


def task(positives, wrongs, original=10, surviving=10) -> dict:
    return {
        "accepted_outputs": 1,
        "original_tests": original, "surviving_tests": surviving,
        "positives": {f"p{i}": outcome(p) for i, p in enumerate(positives)},
        "wrongs": {f"w{i}": outcome(w) for i, w in enumerate(wrongs)},
    }


def four_good(**kw) -> dict:
    return {f"t{i}": task([True, True], [False, False, False], **kw) for i in range(4)}


def test_a_full_bank_retains_everything():
    assert S.retention(task([True], [False], original=10, surviving=10)) == 1.0


def test_an_emptied_bank_is_reported_as_emptied_not_valid():
    assert S.classify(task([True, True], [False], original=10, surviving=0)) == "EMPTIED"


def test_a_bank_below_the_floor_is_hollowed():
    assert S.classify(task([True, True], [False], original=10, surviving=4)) == "HOLLOWED"


def test_exactly_half_retained_clears_the_floor():
    assert S.classify(task([True, True], [False], original=10, surviving=5)) == "REFERENCE_VALID"


def test_a_hollowed_bank_is_never_called_reference_valid():
    """This is the Gen62 failure: safety earned by deleting the evidence."""
    tasks = four_good(original=100, surviving=16)
    result = S.apply_screen(tasks)
    assert result["reference_valid_tasks"] == []
    assert sorted(result["hollowed_tasks"]) == sorted(tasks)
    assert result["verdict"] == "UNEVALUABLE"


def test_the_guardrail_outranks_the_unsafe_label():
    # Both hollowed and rejecting a positive: the hollowing is the reportable fact.
    assert S.classify(task([True, False], [False], original=10, surviving=2)) == "HOLLOWED"


def test_a_task_without_retention_data_falls_back_to_the_gen60_rule():
    bare = {"accepted_outputs": 1,
            "positives": {"p0": outcome(True)}, "wrongs": {"w0": outcome(False)}}
    assert S.classify(bare) == "REFERENCE_VALID"


def test_an_intact_run_still_passes():
    result = S.apply_screen(four_good())
    assert result["verdict"] == "PASSED"
    assert result["sensitivity"] == 1.0
    assert result["hollowed_tasks"] == []


def test_the_recorded_rescore_reproduces_from_its_own_file():
    payload = json.loads(
        (ROOT / "results/pi_retention_guardrail_gen63/rescore.json").read_text())
    gen62 = payload["rescored"]["gen62"]
    assert gen62["as_recorded"]["verdict"] == "PASSED"
    assert gen62["under_guardrail"]["verdict"] == "UNEVALUABLE"
    assert len(gen62["under_guardrail"]["hollowed_tasks"]) == 8
    for label in ("gen60", "gen61"):
        entry = payload["rescored"][label]
        assert entry["changed"] is False
        assert entry["under_guardrail"]["hollowed_tasks"] == []


def test_gen62_retention_was_far_below_the_floor():
    payload = json.loads(
        (ROOT / "results/pi_retention_guardrail_gen63/rescore.json").read_text())
    kept = payload["rescored"]["gen62"]["under_guardrail"]["retention"]
    assert all(value < S.MINIMUM_RETENTION for value in kept.values())
    assert max(kept.values()) < 0.35


def test_the_contract_says_it_is_retrospective():
    contract = S.contract()
    assert contract["retrospective"].startswith("re-reads recorded outcomes only")
    assert "not new evidence" in contract["does_not_re_measure"]
