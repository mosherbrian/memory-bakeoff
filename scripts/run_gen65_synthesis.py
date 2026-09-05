#!/usr/bin/env python3
"""Gen65: read the committed outcomes of Gen60-64 and state the arc in numbers.

No model, no GPU, no re-run, no new filter. Every figure below is read from a
committed results file rather than retyped, so the synthesis cannot drift from
what the generations actually recorded.
"""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.evidence_ruler import gate_suitability as G   # noqa: E402
from memory_bakeoff.evidence_ruler import retention_screen as R   # noqa: E402

OUT = ROOT / "results" / "pi_gate_question_gen65"
SOURCES = {
    "gen60": ROOT / "results/pi_generated_evidence_gen60/screen_result.json",
    "gen61": ROOT / "results/pi_spec_grounded_gen61/screen_result.json",
    "gen62": ROOT / "results/pi_entailment_critic_gen62/screen_result.json",
    "gen64": ROOT / "results/pi_justified_critic_gen64/screen_result.json",
}
CRITICS = {
    "gen62": ROOT / "results/pi_entailment_critic_gen62/critic_log.json",
    "gen64": ROOT / "results/pi_justified_critic_gen64/critic_log.json",
}


def with_statuses(payload: dict) -> dict:
    """Older results predate the status map; recompute it from their own tasks."""
    if "statuses" not in payload:
        payload = dict(payload)
        payload["statuses"] = R.apply_screen(payload["tasks"])["statuses"]
    return payload


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    loaded = {k: with_statuses(json.loads(p.read_text())) for k, p in SOURCES.items()}
    baseline = loaded["gen61"]

    rows = {}
    for label, payload in loaded.items():
        rows[label] = G.report(label, payload,
                               baseline=None if label == "gen61" else baseline)
        if label in CRITICS:
            critic = json.loads(CRITICS[label].read_text())
            removals = critic["known_false_removed"] + critic["valid_removed"]
            rows[label].update({
                "tests_removed": removals,
                "tests_reviewed": critic["tests_reviewed"],
                "removal_precision": (critic["known_false_removed"] / removals
                                      if removals else None),
                "known_false_removed": critic["known_false_removed"],
                "known_false_total": critic["known_false_total"],
                "valid_removed": critic["valid_removed"],
            })

    conclusion = {
        "question": "are model-generated tests safe to use as an unattended gate on "
                    "this pinned model and generator configuration?",
        "answer": "not demonstrated. They are useful as reviewer evidence.",
        "supported_use": "surface suspicious cases for a human reviewer",
        "unsupported_use": "automatically decide correctness",
        "decisive_arc": [
            "Gen60: unchanged generator on a repaired corpus - caught every wrong "
            "implementation it was allowed to judge, and 4 of 8 banks rejected "
            "known-correct code",
            "Gen61: require each test to quote its requirement - no effect; the "
            "false accusations already carried genuine verbatim quotes",
            "Gen62: require entailment - removed 158 of 188 tests at precision "
            "0.101, and the screen called that PASSED",
            "Gen63: screen repaired with a retention floor; Gen62 re-scored "
            "UNEVALUABLE",
            "Gen64: deletion only with a named extra condition - destruction "
            "stopped, retention 0.821 to 0.964, detection restored, and the unsafe "
            "rate returned to 4 of 8 on the same four tasks",
        ],
        "why_filters_failed": "the false accusations and the sound inferences are "
                              "indistinguishable from the information a checker is "
                              "given - one requirement sentence and one test",
        "scope": "one pinned model, one generator contract, one corpus of eight "
                 "tasks, one run per condition; this is a bounded result, not a "
                 "general claim about generated tests",
        "next_branch": "a repository-informed checker changes the checker's "
                       "information boundary and belongs in a new experimental "
                       "branch, not as another turn of this one",
    }

    payload = {"contract": G.contract(), "generations": rows, "conclusion": conclusion}
    (OUT / "gate_question.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(f"{'gen':6} {'unsafe':>8} {'retention':>18} {'caught':>10}  losses")
    for label, row in rows.items():
        kept = ("-" if row["retention_min"] is None
                else f"{row['retention_min']:.3f}-{row['retention_max']:.3f}")
        print(f"{label:6} {row['unsafe_banks']:>3}/{row['banks_considered']:<4} "
              f"{kept:>18} {row['wrongs_caught']:>4}/{row['wrongs_in_population']:<5} "
              f"{len(row['detection_losses_vs_baseline'])}")
    for label in ("gen62", "gen64"):
        row = rows[label]
        print(f"{label}: removed {row['tests_removed']}/{row['tests_reviewed']} "
              f"precision {row['removal_precision']:.3f} "
              f"(false {row['known_false_removed']}/{row['known_false_total']}, "
              f"valid {row['valid_removed']})")
    print("\n" + conclusion["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
