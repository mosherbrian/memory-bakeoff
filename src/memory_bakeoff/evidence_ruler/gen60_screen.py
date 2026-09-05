"""Apply `gen60-generated-evidence-screen-v1` to measured bank outcomes.

The arithmetic lives here, apart from the subprocess work, so the decision the
screen makes can be tested directly against hand-written outcomes.

Order is the point. A bank that rejects known-correct code is UNSAFE_AS_GATE and
leaves the primary population before any of its verdicts on wrong code are
counted. Coverage is checked before sensitivity, so a corpus too thin to answer
the question reports UNEVALUABLE instead of a number nobody should trust.
"""
from __future__ import annotations

from typing import Any

SENSITIVITY_BAR = 0.5
SPECIFICITY_BAR = 0.25
MINIMUM_TASKS = 4
MINIMUM_WRONGS_PER_TASK = 2


def classify(task: dict[str, Any]) -> str:
    if not task.get("accepted_outputs"):
        return "NO_BANK"
    if not task["positives"]:
        return "NO_REFERENCE"
    return ("REFERENCE_VALID"
            if all(r["passed"] for r in task["positives"].values())
            else "UNSAFE_AS_GATE")


def apply_screen(tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    statuses = {name: classify(task) for name, task in tasks.items()}
    valid = [n for n, s in statuses.items() if s == "REFERENCE_VALID"]
    eligible = [n for n in valid if len(tasks[n]["wrongs"]) >= MINIMUM_WRONGS_PER_TASK]

    flagged_wrongs = sum(1 for n in eligible for r in tasks[n]["wrongs"].values()
                         if not r["passed"])
    total_wrongs = sum(len(tasks[n]["wrongs"]) for n in eligible)
    flagged_positives = sum(1 for n in eligible for r in tasks[n]["positives"].values()
                            if not r["passed"])
    total_positives = sum(len(tasks[n]["positives"]) for n in eligible)

    sensitivity = flagged_wrongs / total_wrongs if total_wrongs else None
    specificity = flagged_positives / total_positives if total_positives else None
    covered = len(eligible) >= MINIMUM_TASKS

    if not covered:
        verdict, reason = "UNEVALUABLE", (
            f"only {len(eligible)} reference-valid tasks carry at least "
            f"{MINIMUM_WRONGS_PER_TASK} wrong candidates; the screen requires "
            f"{MINIMUM_TASKS}")
    elif sensitivity >= SENSITIVITY_BAR and specificity <= SPECIFICITY_BAR:
        verdict, reason = "PASSED", (
            "flagged at least half of the known-wrong candidates without "
            "rejecting known-correct code")
    else:
        verdict, reason = "FAILED", (
            f"sensitivity {sensitivity:.3f} against a bar of {SENSITIVITY_BAR:.3f}, "
            f"specificity {specificity:.3f} against a bar of {SPECIFICITY_BAR:.3f}")

    return {
        "statuses": statuses,
        "reference_valid_tasks": valid,
        "unsafe_as_gate_tasks": [n for n, s in statuses.items() if s == "UNSAFE_AS_GATE"],
        "primary_population": {"tasks": eligible, "wrong_candidates": total_wrongs,
                               "positive_candidates": total_positives},
        "flagged_wrongs": flagged_wrongs, "flagged_positives": flagged_positives,
        "sensitivity": sensitivity, "specificity": specificity,
        "coverage_met": covered, "verdict": verdict, "reason": reason,
    }
