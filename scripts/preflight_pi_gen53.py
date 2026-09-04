#!/usr/bin/env python3
"""Gen53 Part B: freeze the v2 contract and prove both Gen52 defects are fixed.

No model, no GPU, no network. Run before any replay outcome is inspected.
"""
from __future__ import annotations

import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import block_network            # noqa: E402
from memory_bakeoff.pi_state_control import quiescent_v2 as Q       # noqa: E402
from memory_bakeoff.pi_state_control import raw_evidence as R       # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen53"
GEN52 = ROOT / "results" / "pi_quiescent_completion_gen52"
ARCHIVE = Path.home() / "gen52-raw-archive"

CHECK = "cd . && python -m pytest tests/ -q"
OTHER_CHECK = "python run_checks.py"
HIDDEN = "python /outside/verifier.py"
T0, TA, TB = "tree-initial", "tree-A", "tree-B"


def drive(steps, k=3):
    """Feed a scripted trace. Each step is (tool, command, tree) or a batch list."""
    rule = Q.QuiescentV2(k=k)
    rule.initial_tree = T0
    rule.current_tree = T0
    stops = []
    for step in steps:
        batch = step if isinstance(step, list) else [step]
        for tool, _command, _tree in batch:
            rule.observe_call(tool)
        for tool, command, tree in batch:
            check = Q.is_visible_check(command)
            passed = None
            if check:
                passed = not command.endswith("#fail")
            if rule.observe_result(passed=passed, tree=tree, fresh_check=check):
                stops.append(rule.tool_index)
    return rule, stops


def bash(command, tree):
    return ("bash", command, tree)


def edit(tree):
    return ("edit", "", tree)


def main() -> int:
    block_network()
    OUT.mkdir(parents=True, exist_ok=True)

    idle = bash("ls", TA)
    scenarios = {}

    # 1. the ordinary case still works
    rule, stops = drive([edit(TA), bash(CHECK, TA), idle, idle, idle])
    scenarios["mutate_pass_three_idle_fires_at_k3"] = {"fired": bool(stops), "at": stops[:1],
                                                       "idle": rule.idle}

    # 2. THE GEN52 STARVATION DEFECT: repeated passes on one tree are idle now
    rule, stops = drive([edit(TA), bash(CHECK, TA),
                         bash(CHECK, TA), bash(CHECK, TA), bash(CHECK, TA)])
    scenarios["repeated_same_tree_passes_count_as_idle"] = {
        "fired": bool(stops), "at": stops[:1],
        "same_tree_passes_counted_idle": rule.same_tree_passes_counted_idle}

    # 2b. a different check command on the same tree is still idle, not a re-arm
    rule, stops = drive([edit(TA), bash(CHECK, TA),
                         bash(OTHER_CHECK, TA), bash(OTHER_CHECK, TA), bash(OTHER_CHECK, TA)])
    scenarios["different_check_command_same_tree_is_still_idle"] = {
        "fired": bool(stops), "same_tree_passes_counted_idle": rule.same_tree_passes_counted_idle}

    # 3. a mix of repeated passes and ordinary calls
    rule, stops = drive([edit(TA), bash(CHECK, TA), bash(CHECK, TA), idle, idle])
    scenarios["one_repeat_pass_then_two_idle_fires_at_k3"] = {"fired": bool(stops), "at": stops[:1]}

    # 4. THE GEN52 REVERT DEFECT: back at the starting tree is never complete
    rule, stops = drive([edit(TA), edit(T0), bash(CHECK, T0)] + [idle_ for idle_ in
                        [bash("ls", T0)] * 12])
    scenarios["revert_to_initial_tree_is_never_eligible"] = {
        "fired": bool(stops), "became_eligible": rule.became_eligible,
        "net_tree_changed": rule.net_tree_changed(), "mutations": rule.mutations}

    # 5. a pass before any mutation
    rule, stops = drive([bash(CHECK, T0), bash("ls", T0), bash("ls", T0), bash("ls", T0)])
    scenarios["pass_before_any_mutation_is_ineligible"] = {
        "fired": bool(stops), "became_eligible": rule.became_eligible}

    # 6. a mutation after the receipt resets everything
    rule, stops = drive([edit(TA), bash(CHECK, TA), idle, edit(TB),
                         bash("ls", TB), bash("ls", TB)])
    scenarios["mutation_after_receipt_resets"] = {"fired": bool(stops), "idle": rule.idle,
                                                  "receipt": rule.receipt_tree}

    # 7. a failing check clears the receipt; a later pass may create a new one
    rule, stops = drive([edit(TA), bash(CHECK, TA), bash(CHECK + "#fail", TA),
                         bash("ls", TA), bash("ls", TA), bash("ls", TA)])
    scenarios["visible_fail_resets_then_no_receipt"] = {"fired": bool(stops), "idle": rule.idle}
    rule, stops = drive([edit(TA), bash(CHECK + "#fail", TA), bash(CHECK, TA),
                         idle, idle, idle])
    scenarios["pass_after_a_fail_rearms"] = {"fired": bool(stops), "at": stops[:1]}

    # 8. a second mutation starts the count fresh on the new tree
    rule, stops = drive([edit(TA), bash(CHECK, TA), edit(TB), bash(CHECK, TB),
                         bash("ls", TB), bash("ls", TB), bash("ls", TB)])
    scenarios["second_tree_counts_fresh"] = {"fired": bool(stops), "at": stops[:1],
                                             "receipt": rule.receipt_tree}

    # 9. an in-flight batch is never killed
    rule, stops = drive([edit(TA), bash(CHECK, TA), bash("ls", TA),
                         [bash("ls", TA), bash("ls", TA), bash("ls", TA)]])
    scenarios["stop_waits_for_the_batch_to_drain"] = {
        "fired": bool(stops), "overshoot": rule.overshoot,
        "trigger_index": rule.trigger_index, "effective_stop_index": rule.effective_stop_index}

    # 10. the hidden verifier is not a check
    rule, stops = drive([edit(TA), bash(HIDDEN, TA), bash("ls", TA), bash("ls", TA), bash("ls", TA)])
    scenarios["hidden_verifier_is_not_a_visible_check"] = {
        "fired": bool(stops), "became_eligible": rule.became_eligible}

    checks = {
        "mutate_pass_three_idle_fires_at_k3": scenarios["mutate_pass_three_idle_fires_at_k3"]["fired"],
        "repeated_same_tree_passes_count_as_idle":
            scenarios["repeated_same_tree_passes_count_as_idle"]["fired"]
            and scenarios["repeated_same_tree_passes_count_as_idle"]["same_tree_passes_counted_idle"] >= 3,
        "different_check_command_same_tree_is_still_idle":
            scenarios["different_check_command_same_tree_is_still_idle"]["fired"],
        "one_repeat_pass_then_two_idle_fires_at_k3":
            scenarios["one_repeat_pass_then_two_idle_fires_at_k3"]["fired"],
        "revert_to_initial_tree_is_never_eligible":
            scenarios["revert_to_initial_tree_is_never_eligible"]["fired"] is False
            and scenarios["revert_to_initial_tree_is_never_eligible"]["became_eligible"] is False
            and scenarios["revert_to_initial_tree_is_never_eligible"]["mutations"] >= 2,
        "pass_before_any_mutation_is_ineligible":
            scenarios["pass_before_any_mutation_is_ineligible"]["fired"] is False,
        "mutation_after_receipt_resets": scenarios["mutation_after_receipt_resets"]["fired"] is False,
        "visible_fail_resets": scenarios["visible_fail_resets_then_no_receipt"]["fired"] is False,
        "pass_after_a_fail_rearms": scenarios["pass_after_a_fail_rearms"]["fired"],
        "second_tree_counts_fresh": scenarios["second_tree_counts_fresh"]["fired"],
        "stop_waits_for_the_batch_to_drain":
            scenarios["stop_waits_for_the_batch_to_drain"]["fired"]
            and scenarios["stop_waits_for_the_batch_to_drain"]["overshoot"] >= 1,
        "hidden_verifier_is_not_a_visible_check":
            scenarios["hidden_verifier_is_not_a_visible_check"]["fired"] is False,
    }

    # K sensitivity of the two repaired shapes, frozen before any replay is read.
    sensitivity = {}
    for k in Q.K_SWEEP:
        loop_rule, loop_stops = drive([edit(TA), bash(CHECK, TA)] + [bash(CHECK, TA)] * 12, k=k)
        revert_rule, revert_stops = drive([edit(TA), edit(T0), bash(CHECK, T0)]
                                          + [bash("ls", T0)] * 12, k=k)
        sensitivity[str(k)] = {
            "repeated_check_loop_fires": bool(loop_stops),
            "repeated_check_loop_first_stop": loop_stops[:1],
            "revert_to_start_fires": bool(revert_stops)}

    retention = R.verify_retention(
        json.loads((GEN52 / "raw_stream_manifest.json").read_text()), ARCHIVE)

    report = {
        "evidence_class": "architecture_quiescent_completion_refinement_offline_replay_no_score",
        "contract": Q.contract(),
        "scenarios": scenarios,
        "checks": checks,
        "k_sensitivity_of_the_two_repaired_shapes": sensitivity,
        "gen52_archive_reverified": {"retention_verified": retention["retention_verified"],
                                     "streams": len(retention["streams"]),
                                     "failures": retention["failures"]},
        "no_network": True,
    }
    report["passed"] = (all(checks.values())
                        and all(v["repeated_check_loop_fires"] for v in sensitivity.values())
                        and not any(v["revert_to_start_fires"] for v in sensitivity.values())
                        and retention["retention_verified"])
    (OUT / "v2_contract.json").write_text(json.dumps(Q.contract(), indent=2, sort_keys=True) + "\n")
    (OUT / "preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"checks": checks, "k_sensitivity": sensitivity,
                      "archive": report["gen52_archive_reverified"],
                      "passed": report["passed"]}, indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
