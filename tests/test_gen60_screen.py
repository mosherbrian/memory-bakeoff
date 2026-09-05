"""The Gen60 screen must reach the same verdict a careful reader would.

These cases are written against hand-made outcomes, not against the measured
run, so a change in the arithmetic fails here rather than quietly changing what
a generation is reported to have shown.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from memory_bakeoff.evidence_ruler import gen60_screen as S

ROOT = Path(__file__).resolve().parents[1]


def outcome(passed: bool) -> dict:
    return {"passed": passed, "tail": ""}


def task(positives: list[bool], wrongs: list[bool], outputs: int = 3) -> dict:
    """`wrongs` are pass/fail of the bank; a wrong is FLAGGED when the bank fails."""
    return {
        "accepted_outputs": outputs,
        "positives": {f"p{i}": outcome(p) for i, p in enumerate(positives)},
        "wrongs": {f"w{i}": outcome(w) for i, w in enumerate(wrongs)},
    }


def four_good() -> dict:
    return {f"t{i}": task([True, True], [False, False, False]) for i in range(4)}


def test_a_bank_that_passes_every_positive_is_reference_valid():
    assert S.classify(task([True, True], [False])) == "REFERENCE_VALID"


def test_a_bank_that_rejects_one_known_correct_tree_is_unsafe_as_gate():
    assert S.classify(task([True, False], [False])) == "UNSAFE_AS_GATE"


def test_a_task_with_no_accepted_output_has_no_bank():
    assert S.classify(task([], [], outputs=0)) == "NO_BANK"


def test_an_unsafe_bank_contributes_nothing_even_when_it_flags_every_wrong():
    tasks = four_good()
    # This bank catches all three wrongs, but it also rejects correct code, so
    # none of its verdicts may count toward sensitivity.
    tasks["rogue"] = task([True, False], [False, False, False])
    result = S.apply_screen(tasks)
    assert "rogue" not in result["primary_population"]["tasks"]
    assert result["primary_population"]["wrong_candidates"] == 12
    assert result["flagged_wrongs"] == 12


def test_three_eligible_tasks_is_unevaluable_rather_than_failed():
    tasks = {f"t{i}": task([True, True], [False, False, False]) for i in range(3)}
    result = S.apply_screen(tasks)
    assert result["verdict"] == "UNEVALUABLE"
    assert result["coverage_met"] is False


def test_a_reference_valid_task_with_one_wrong_does_not_count_toward_coverage():
    tasks = {f"t{i}": task([True, True], [False, False, False]) for i in range(3)}
    tasks["thin"] = task([True, True], [False])
    result = S.apply_screen(tasks)
    assert "thin" not in result["primary_population"]["tasks"]
    assert result["verdict"] == "UNEVALUABLE"


def test_catching_too_few_wrongs_fails_rather_than_reading_unevaluable():
    tasks = {f"t{i}": task([True, True], [True, True, False]) for i in range(4)}
    result = S.apply_screen(tasks)
    assert result["verdict"] == "FAILED"
    assert result["sensitivity"] == pytest.approx(1 / 3)


def test_exactly_half_the_wrongs_meets_the_bar():
    tasks = {f"t{i}": task([True, True], [False, True]) for i in range(4)}
    result = S.apply_screen(tasks)
    assert result["sensitivity"] == 0.5
    assert result["verdict"] == "PASSED"


def test_specificity_is_zero_among_eligible_tasks_by_construction():
    """Any positive failure removes its task, so the specificity bar can only
    ever be met - it is implied by the validity gate, not an independent test."""
    result = S.apply_screen(four_good())
    assert result["specificity"] == 0.0
    assert result["flagged_positives"] == 0


def test_the_measured_gen60_result_reproduces_from_its_own_recorded_outcomes():
    recorded = json.loads(
        (ROOT / "results/pi_generated_evidence_gen60/screen_result.json").read_text())
    replayed = S.apply_screen(recorded["tasks"])
    assert replayed["verdict"] == recorded["verdict"]
    assert replayed["sensitivity"] == recorded["sensitivity"]
    assert replayed["reference_valid_tasks"] == recorded["reference_valid_tasks"]
    assert replayed["unsafe_as_gate_tasks"] == recorded["unsafe_as_gate_tasks"]
