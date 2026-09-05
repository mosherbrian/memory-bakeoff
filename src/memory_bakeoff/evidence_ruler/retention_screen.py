"""`gen63-retention-guardrail-v1`: a filter may not buy safety by deleting evidence.

Gen62 exposed a defect in the screen, not in the corpus. A critic removed 158 of
188 tests - 142 of them sound - and every bank became "reference-valid" simply
because almost nothing was left to disagree with anything. The screen returned
PASSED. It had no way to notice that the evidence had been hollowed out, because
every quantity it measures improves as tests disappear.

This adds the missing requirement, and it is a precondition rather than a metric:
a bank is only admissible if it still contains a substantial share of the tests
it started with. Sensitivity and specificity are then read from banks that still
exist, which is what those numbers were always assumed to mean.

Two rules, both predeclared:

- **Retention.** At least half of a bank's original distinct tests must survive.
- **Liveness.** No bank may be emptied, whatever the ratio says.

This is a retrospective correction. It re-reads outcomes that were already
recorded; it involves no model call, changes no filter, and cannot alter what any
generation actually produced. It says what the screen should have concluded.
"""
from __future__ import annotations

from typing import Any

from memory_bakeoff.evidence_ruler import gen60_screen as G

CONTRACT_VERSION = "gen63-retention-guardrail-v1"
MINIMUM_RETENTION = 0.5


def retention(task: dict[str, Any]) -> float | None:
    """Surviving distinct tests over original distinct tests, or None if unknown."""
    original = task.get("original_tests")
    if not original:
        return None
    return task.get("surviving_tests", 0) / original


def classify(task: dict[str, Any]) -> str:
    """The Gen60 classification, with the guardrail applied first.

    Order matters. A hollowed bank must not be called REFERENCE_VALID on its way
    out, because that is precisely the label Gen62 earned by deleting evidence.
    """
    kept = retention(task)
    if kept is not None:
        if task.get("surviving_tests", 0) == 0:
            return "EMPTIED"
        if kept < MINIMUM_RETENTION:
            return "HOLLOWED"
    return G.classify(task)


def apply_screen(tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    statuses = {name: classify(task) for name, task in tasks.items()}
    valid = [n for n, s in statuses.items() if s == "REFERENCE_VALID"]
    eligible = [n for n in valid
                if len(tasks[n]["wrongs"]) >= G.MINIMUM_WRONGS_PER_TASK]

    flagged_wrongs = sum(1 for n in eligible for r in tasks[n]["wrongs"].values()
                         if not r["passed"])
    total_wrongs = sum(len(tasks[n]["wrongs"]) for n in eligible)
    flagged_positives = sum(1 for n in eligible for r in tasks[n]["positives"].values()
                            if not r["passed"])
    total_positives = sum(len(tasks[n]["positives"]) for n in eligible)

    sensitivity = flagged_wrongs / total_wrongs if total_wrongs else None
    specificity = flagged_positives / total_positives if total_positives else None
    covered = len(eligible) >= G.MINIMUM_TASKS

    hollowed = [n for n, s in statuses.items() if s in ("HOLLOWED", "EMPTIED")]
    if not covered:
        verdict = "UNEVALUABLE"
        reason = (f"only {len(eligible)} tasks carry an admissible bank with at least "
                  f"{G.MINIMUM_WRONGS_PER_TASK} wrong candidates; the screen requires "
                  f"{G.MINIMUM_TASKS}")
        if hollowed:
            reason += (f". {len(hollowed)} bank(s) were discarded for retaining under "
                       f"{int(MINIMUM_RETENTION * 100)}% of their tests: "
                       + ", ".join(sorted(hollowed)))
    elif sensitivity >= G.SENSITIVITY_BAR and specificity <= G.SPECIFICITY_BAR:
        verdict = "PASSED"
        reason = ("flagged at least half of the known-wrong candidates, without "
                  "rejecting known-correct code and without hollowing out the bank")
    else:
        verdict = "FAILED"
        reason = (f"sensitivity {sensitivity:.3f} against a bar of {G.SENSITIVITY_BAR:.3f}, "
                  f"specificity {specificity:.3f} against a bar of {G.SPECIFICITY_BAR:.3f}")

    return {
        "screen_version": CONTRACT_VERSION,
        "statuses": statuses,
        "retention": {n: retention(t) for n, t in tasks.items()},
        "hollowed_tasks": hollowed,
        "reference_valid_tasks": valid,
        "unsafe_as_gate_tasks": [n for n, s in statuses.items() if s == "UNSAFE_AS_GATE"],
        "primary_population": {"tasks": eligible, "wrong_candidates": total_wrongs,
                               "positive_candidates": total_positives},
        "flagged_wrongs": flagged_wrongs, "flagged_positives": flagged_positives,
        "sensitivity": sensitivity, "specificity": specificity,
        "coverage_met": covered, "verdict": verdict, "reason": reason,
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "adds_to": "gen60-generated-evidence-screen-v1 at b694f7b8",
        "why": "Gen62 achieved zero unsafe banks by deleting 158 of 188 tests, 142 of "
               "them sound, and the screen returned PASSED because every quantity it "
               "measured improves as evidence disappears",
        "retention_rule": f"a bank must retain at least {int(MINIMUM_RETENTION * 100)}% "
                          "of its original distinct tests",
        "liveness_rule": "no bank may be emptied, whatever the ratio says",
        "applied_before": "the reference-validity check, so a hollowed bank is never "
                          "labelled REFERENCE_VALID on its way out",
        "retrospective": "re-reads recorded outcomes only; no model call, no "
                         "regeneration, no change to any filter or generated test",
        "does_not_re_measure": "this says what the screen should have concluded about "
                               "Gen62; it is not new evidence about critic quality",
    }
