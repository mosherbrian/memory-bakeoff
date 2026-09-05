#!/usr/bin/env python3
"""Gen59 Parts E/F: prove the corpus is not degenerate, that a future generator
cannot reach evaluator truth, and freeze the Gen60 screen before any model output.
"""
from __future__ import annotations

import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.evidence_ruler.tasks_gen59 import TASKS   # noqa: E402
from memory_bakeoff.pi_state_control import challenge_generation as C  # noqa: E402

FIXTURES = ROOT / "fixtures" / "evidence_generation_gen59_v1"
OUT = ROOT / "results" / "pi_evidence_ruler_gen59"
GENERATOR_VISIBLE = ("spec.txt", "repo")
FORBIDDEN_TOKENS = ("verifier", "candidates.json", "failed_requirement", "VERIFIER OK")


def main() -> int:
    matrix = json.loads((OUT / "candidate_matrix.json").read_text())
    admitted = [t for t, m in matrix["tasks"].items() if m["admitted"]]

    # --- Part E: anti-triviality sentinels ------------------------------------
    sentinels = {}
    for task in admitted:
        rows = matrix["tasks"][task]["rows"]
        wrongs = [r for r in rows if r["kind"] == "wrong"]
        positives = [r for r in rows if r["kind"] == "positive"]
        sentinels[task] = {
            "visible_tests_do_not_reject_every_wrong":
                any(r["visible"]["passed"] for r in wrongs),
            "hidden_rejects_every_wrong": all(not r["hidden"]["passed"] for r in wrongs),
            "hidden_accepts_every_positive": all(r["hidden"]["passed"] for r in positives),
            "positives_differ_structurally":
                len({r["tracked_digest"] for r in positives}) == len(positives),
            "has_partial_implementation":
                any(r["failed_requirement"] == "B" for r in wrongs),
        }
    corpus_level = {
        "some_task_has_a_self_modified_visible_test": any(
            r.get("self_modified_visible_test")
            for t in admitted for r in matrix["tasks"][t]["rows"] if r["kind"] == "wrong"),
        "mechanism_diversity": len({TASKS[t]["mechanism"] for t in admitted}),
        "not_eight_copies_of_one_shape": len({TASKS[t]["mechanism"] for t in admitted}) >= 4,
    }

    # --- Part B/E: the generator must not be able to reach evaluator truth ----
    leak = {"tasks_checked": [], "leaks": []}
    for task in admitted:
        visible = {}
        spec = (FIXTURES / task / "spec.txt").read_text()
        for path in sorted((FIXTURES / task / "repo").rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                visible[str(path.relative_to(FIXTURES / task / "repo"))] = path.read_text()
        blob = spec + "\n" + "\n".join(visible.values())
        for token in FORBIDDEN_TOKENS:
            if token in blob:
                leak["leaks"].append({"task": task, "token": token})
        # the prompt a future generator would actually receive
        prompt = C.build_prompt(spec, FIXTURES / task / "repo")
        for token in FORBIDDEN_TOKENS:
            if token in prompt:
                leak["leaks"].append({"task": task, "token": token, "where": "assembled prompt"})
        leak["tasks_checked"].append(task)
    leak["truth_is_outside_the_generator_visible_paths"] = all(
        not (FIXTURES / t / "repo" / "truth").exists()
        and (FIXTURES / t / "truth" / "verifier.py").exists() for t in admitted)
    leak["clean"] = not leak["leaks"] and leak["truth_is_outside_the_generator_visible_paths"]

    # --- Part F: freeze the Gen60 screen, before any generated output exists ---
    screen = {
        "contract_version": "gen60-generated-evidence-screen-v1",
        "frozen_before": "any Gen60 generator call; no generated output exists yet",
        "applies_to": "the SAME Gen58 generator contract and pinned model role, unchanged",
        "task_validity": ("a generated bank is usable for a task only if it passes ALL trusted "
                          "positive implementations for that task; any failure marks the task "
                          "UNSAFE_AS_GATE, which is kept and reported and never repaired"),
        "primary_population": "candidates from tasks whose banks are reference-valid",
        "sensitivity": "the bank must flag at least 50% of known-wrong candidates in that population",
        "specificity": "the bank must flag no more than 25% of trusted-positive candidates",
        "coverage_requirement": ("at least FOUR primary tasks must remain reference-valid, each with "
                                 "at least two hidden-wrong candidates in the measured population; "
                                 "below that the screen is UNEVALUABLE rather than failed"),
        "no_result_shopping": ("no tuning of prompt, sanitizer, task set, aggregation or thresholds "
                               "after exposure"),
        "absence_is_not_sufficiency": ("a bank that raises no challenge proves nothing about task "
                                       "correctness; generated tests stay proposition-scoped "
                                       "evidence candidates"),
        "ruler": {
            "name": "evidence-generation-gen59-v1",
            "admitted_tasks": sorted(admitted),
            "known_wrong_candidates": matrix["summary"]["total_known_wrong_candidates"],
            "visible_pass_hidden_fail": matrix["summary"]["total_visible_pass_hidden_fail"],
        },
    }
    screen["contract_sha256"] = hashlib.sha256(
        json.dumps(screen, sort_keys=True).encode()).hexdigest()

    report = {"sentinels": sentinels, "corpus_level": corpus_level, "isolation": leak}
    report["passed"] = (all(all(v.values()) for v in sentinels.values())
                        and all(corpus_level[k] for k in
                                ("some_task_has_a_self_modified_visible_test",
                                 "not_eight_copies_of_one_shape"))
                        and leak["clean"])
    (OUT / "isolation_preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (OUT / "gen60_frozen_screen.json").write_text(json.dumps(screen, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"corpus_level": corpus_level,
                      "isolation": {k: v for k, v in leak.items() if k != "tasks_checked"},
                      "sentinel_failures": {t: [k for k, v in s.items() if not v]
                                            for t, s in sentinels.items()
                                            if not all(s.values())},
                      "screen_sha256": screen["contract_sha256"][:16],
                      "passed": report["passed"]}, indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
