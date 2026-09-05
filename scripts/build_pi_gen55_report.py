#!/usr/bin/env python3
"""Aggregate the Gen55 leaves, verify retained evidence, and audit every stop.

Three outcome axes are kept apart on purpose: what the hidden verifier says, how
the run ended, and whether a current-tree visible receipt was in hand at the end.
Collapsing them into one pass rate is what would hide the result.
"""
from __future__ import annotations

import json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import raw_evidence as R  # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen55"
ARCHIVE = Path.home() / "gen55-raw-archive"
ARM_C = "pi_harness_state_control_v1"
ARM_E = "pi_harness_state_control_quiescent_tracked_k3_v1"


def leaves() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted((OUT / "runs").glob("*/leaf.json"))]


def median(values):
    return statistics.median(values) if values else None


def arm_summary(rows: list[dict]) -> dict:
    measured = [r["measured"] for r in rows]
    return {
        "runs": len(rows),
        "hidden_verifier_passed": sum(1 for r in rows if r["verifier"]["passed"]),
        "termination": {name: sum(1 for r in rows if r["termination_class"] == name)
                        for name in ("model_completed", "quiescent_stop", "timeout",
                                     "crash_or_orchestration_failure")},
        "control_valid_done": sum(1 for m in measured
                                  if (m.get("harness") or {}).get("valid_receipt_at_end")),
        "failed_requirements": sorted({r["verifier"].get("failed_requirement")
                                       for r in rows if not r["verifier"]["passed"]} - {None}),
        "median_requests": median([m["request_count"] for m in measured]),
        "median_payload_bytes": median([m["payload_bytes_total"] for m in measured]),
        "median_request_bytes": median([m["request_bytes_total"] for m in measured]),
        "median_tool_calls": median([m["tool_calls"] for m in measured]),
        "total_tool_calls": sum(m["tool_calls"] for m in measured),
        "median_repeated_or_redundant": median([m["churn"].get("repeated_or_redundant", 0)
                                                for m in measured]),
        "median_wall_seconds": median([r["run"]["wall_seconds"] for r in rows]),
        "total_wall_seconds": round(sum(r["run"]["wall_seconds"] for r in rows), 1),
    }


def harness_tree(row: dict) -> str:
    """The tree digest the harness itself last recorded, i.e. at the stop."""
    path = OUT / "runs" / (f"{row['slot']['index']:02d}-{row['slot']['task']}"
                           f"-r{row['slot']['repetition']}-{row['slot']['arm']}") / "harness_state.json"
    if not path.exists():
        return ""
    return (json.loads(path.read_text()).get("state") or {}).get("tree_digest", "")


def check_loop(row: dict) -> dict:
    """How much of a run was the same passing check, re-run on an unchanged tree.

    This is the shape the stop rule is blind to. A passing check re-arms the
    receipt and resets the count, so a run that idles by repeating the check
    that already passed never accumulates the K ordinary completions the rule
    waits for. Measured here rather than argued.
    """
    path = OUT / "runs" / (f"{row['slot']['index']:02d}-{row['slot']['task']}"
                           f"-r{row['slot']['repetition']}-{row['slot']['arm']}") / "derivation.ndjson"
    if not path.exists():
        return {"repeated_passing_checks_on_one_tree": 0, "longest_run_of_repeats": 0}
    seen, longest, current, previous = set(), 0, 0, None
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        validation = (json.loads(line).get("validation") or {})
        event = validation.get("event")
        if not event or event in seen or not validation.get("passed"):
            continue
        seen.add(event)
        key = (validation.get("command"), validation.get("tree_digest"))
        current = current + 1 if key == previous else 1
        previous = key
        longest = max(longest, current)
    return {"repeated_passing_checks_on_one_tree": max(0, len(seen)),
            "longest_run_of_repeats": longest}


def stop_table(rows: list[dict]) -> list[dict]:
    table = []
    for row in rows:
        stop = row["measured"].get("quiescent_stop") or {}
        table.append({
            "run": f"{row['slot']['index']:02d}-{row['slot']['task']}-r{row['slot']['repetition']}",
            "became_eligible": stop.get("became_eligible"),
            "triggered": stop.get("triggered"),
            "valid_receipt_tree": stop.get("valid_receipt_tree"),
            "valid_receipt_tool_index": stop.get("valid_receipt_tool_index"),
            "initial_tree_digest": stop.get("initial_tree_digest"),
            "current_tree_digest": stop.get("current_tree_digest"),
            "net_tree_changed": stop.get("net_tree_changed"),
            "trigger_tool_index": stop.get("trigger_tool_index"),
            "effective_stop_tool_index": stop.get("effective_stop_tool_index"),
            "idle_count": stop.get("idle_count"),
            "same_batch_overshoot_calls": stop.get("same_batch_overshoot_calls"),
            "mutations": stop.get("mutations"),
            "termination_class": row["termination_class"],
            "hidden_verifier_passed": row["verifier"]["passed"],
            **check_loop(row),
            # The trigger never saw this. It is scored afterwards, and it is the
            # safety outcome that matters most.
            "live_stop_wrong_tree": bool(stop.get("triggered")) and not row["verifier"]["passed"],
            # Compare the receipt against the tree the harness saw at the stop,
            # not against `final_tree`: that is measured after the run, once the
            # runner has cleared `__pycache__`, so it is a different tree by
            # construction and would make a correct stop look wrong.
            # v2 records both directly, so no cross-file comparison is needed.
            "tree_unchanged_between_receipt_and_stop":
                (stop.get("valid_receipt_tree") == stop.get("current_tree_digest"))
                if stop.get("triggered") else None,
            # A run may mutate and then undo itself. Eligibility asks only that a
            # mutation happened, so a run that reverts its own work still
            # qualifies while its tree is back where it started.
            "net_source_change_recorded_in_leaf": row["task"]["final_tree"] != row["task"]["start_tree"],
            "stopped_on_a_tree_identical_to_the_start":
                bool(stop.get("triggered"))
                and stop.get("current_tree_digest") == stop.get("initial_tree_digest"),
        })
    return table


def contract_audit(rows: list[dict]) -> dict:
    """Every trigger must satisfy every frozen condition. One that does not is a
    controller failure, not a data point."""
    violations, triggers = [], []
    for row in rows:
        stop = row["measured"].get("quiescent_stop") or {}
        if not stop:
            continue
        run = f"{row['slot']['index']:02d}-{row['slot']['task']}-r{row['slot']['repetition']}"
        # HARD FAILURE conditions, checked on every run whether it stopped or not
        if stop.get("triggered") and stop.get("current_tree_digest") == stop.get("initial_tree_digest"):
            violations.append({"run": run, "violation": "stopped on a tree equal to its start"})
        if stop.get("triggered"):
            checks = {
                "at_least_one_mutation": (stop.get("mutations") or 0) >= 1,
                "net_tree_changed": bool(stop.get("net_tree_changed")),
                "receipt_on_the_current_tree":
                    stop.get("valid_receipt_tree") == stop.get("current_tree_digest"),
                "three_idle_completions": (stop.get("idle_count") or 0) >= 3,
                "last_visible_check_passed": stop.get("last_visible_check_passed") is True,
                "stop_at_or_after_the_trigger":
                    (stop.get("effective_stop_tool_index") or 0) >= (stop.get("trigger_tool_index") or 0),
            }
            triggers.append({"run": run, **checks, "stop": stop})
            for name, ok in checks.items():
                if not ok:
                    violations.append({"run": run, "violation": f"trigger without {name}"})
    return {"triggers": triggers, "violations": violations,
            "all_triggers_satisfied_the_frozen_contract": not violations,
            "stops_on_a_tree_equal_to_start": sum(
                1 for v in violations if v["violation"].startswith("stopped on a tree"))}


def retention() -> dict:
    streams = {}
    for row in leaves():
        raw = row["run"].get("raw_stream")
        if not raw:
            continue
        key = f"{row['slot']['index']:02d}-{row['slot']['task']}-r{row['slot']['repetition']}-{row['slot']['arm']}"
        streams[f"{key}/stdout.txt"] = {
            "run_id": key, "name": "stdout.txt",
            "archive_relative_path": raw["archive_relative_path"],
            "sha256": raw["sha256"], "bytes": raw["bytes"],
            "retention_policy": "archive_and_retain",
            "exists_when_manifest_written": (ARCHIVE / raw["archive_relative_path"]).exists()}
    manifest = {"contract_version": R.CONTRACT_VERSION, "streams": streams,
                "retention_verified": False,
                "archive_root": str(ARCHIVE),
                "note": "raw streams are retained locally under the durable archive and never committed"}
    verified = R.verify_retention(manifest, ARCHIVE)
    verified["total_retained_bytes"] = sum(s["bytes"] for s in streams.values())
    return verified


def finalize_capture(manifest: dict) -> dict:
    """Remove the in-repo capture copies, but only once the archive holds them.

    The raw streams are far too large to commit. Gen47 and Gen49 solved that by
    deleting them and claiming they were kept; here the durable archive copy is
    verified first, the capture is removed second, and the archive is re-read
    afterwards. If anything is missing the capture stays and the generation is
    incomplete.
    """
    R.assert_retained(manifest, ARCHIVE)
    captures = sorted((OUT / "runs").glob("*/stdout.txt"))
    report = R.cleanup_capture(captures, manifest, ARCHIVE)
    verified = R.verify_retention(manifest, ARCHIVE)
    report["retention_verified_after_cleanup"] = verified["retention_verified"]
    report["failures"] = verified["failures"]
    return report


def main() -> int:
    finalize = "--finalize" in sys.argv
    rows = leaves()
    by_arm = {ARM_C: [r for r in rows if r["slot"]["arm"] == ARM_C],
              ARM_E: [r for r in rows if r["slot"]["arm"] == ARM_E]}
    pairs = []
    for row in by_arm[ARM_C]:
        mate = next((r for r in by_arm[ARM_E]
                     if r["slot"]["task"] == row["slot"]["task"]
                     and r["slot"]["repetition"] == row["slot"]["repetition"]), None)
        if not mate:
            continue
        pairs.append({
            "task": row["slot"]["task"], "repetition": row["slot"]["repetition"],
            "C": {"verifier": row["verifier"]["passed"], "termination": row["termination_class"],
                  "requests": row["measured"]["request_count"],
                  "tool_calls": row["measured"]["tool_calls"],
                  "payload_bytes": row["measured"]["payload_bytes_total"],
                  "wall_seconds": row["run"]["wall_seconds"]},
            "E": {"verifier": mate["verifier"]["passed"], "termination": mate["termination_class"],
                  "requests": mate["measured"]["request_count"],
                  "tool_calls": mate["measured"]["tool_calls"],
                  "payload_bytes": mate["measured"]["payload_bytes_total"],
                  "wall_seconds": mate["run"]["wall_seconds"]},
            "agree_on_verifier": row["verifier"]["passed"] == mate["verifier"]["passed"]})

    # H1 on live data, not just on the synthetic probe: the first composed
    # request of a run depends only on the task prompt and the empty state, so
    # if E added anything model-facing it would show up here. It must be
    # byte-identical across arms within a task.
    first_request = {}
    for row in rows:
        requests = row.get("requests") or []
        if not requests:
            continue
        first_request.setdefault(row["slot"]["task"], {}).setdefault(
            row["slot"]["arm"], set()).add(requests[0]["bytes"])
    integrity = {task: {arm: sorted(sizes) for arm, sizes in arms.items()}
                 for task, arms in first_request.items()}
    identical = all(len({size for sizes in arms.values() for size in sizes}) == 1
                    for arms in first_request.values())

    aggregate = {
        "evidence_class": "architecture_quiescent_completion_ablation_paired_live",
        "h1_first_request_bytes_identical_across_arms": identical,
        "h1_first_request_bytes_by_task": integrity,
        "runs": len(rows),
        "arms": {ARM_C: arm_summary(by_arm[ARM_C]), ARM_E: arm_summary(by_arm[ARM_E])},
        "pairs_agreeing_on_verifier": sum(1 for p in pairs if p["agree_on_verifier"]),
        "pairs": len(pairs),
        "stop_policy": {
            # what actually ran: the Gen53 semantics on the Gen54 fingerprint
            "contract": "quiescent-completion-toolcall-v2",
            "tree_digest_contract": "tracked-tree-digest-v1",
            "k": 3,
            "k_choice": ("frozen at 3 by the Gen55 brief; a deliberate, labelled deviation from "
                         "the Gen54 historical rule that mechanically named K=1"),
            "eligible_runs": sum(1 for t in stop_table(by_arm[ARM_E]) if t["became_eligible"]),
            "triggered_runs": sum(1 for t in stop_table(by_arm[ARM_E]) if t["triggered"]),
            "live_stop_wrong_tree": sum(1 for t in stop_table(by_arm[ARM_E]) if t["live_stop_wrong_tree"]),
            "total_same_batch_overshoot": sum(t["same_batch_overshoot_calls"] or 0
                                              for t in stop_table(by_arm[ARM_E])),
            "tree_unchanged_between_receipt_and_stop_all_triggers": all(
                t["tree_unchanged_between_receipt_and_stop"]
                for t in stop_table(by_arm[ARM_E]) if t["triggered"]),
            "stopped_on_a_tree_identical_to_the_start": sum(
                1 for t in stop_table(by_arm[ARM_E]) if t["stopped_on_a_tree_identical_to_the_start"]),
            # The blind spot, measured: runs that idled by repeating the check
            # that had already passed, which re-arms the receipt every time.
            "runs_looping_on_the_qualifying_check": sum(
                1 for t in stop_table(by_arm[ARM_E]) if t["longest_run_of_repeats"] >= 3),
            "worst_repeat_run_length": max(
                [t["longest_run_of_repeats"] for t in stop_table(by_arm[ARM_E])] or [0])},
        "contract_audit": contract_audit(by_arm[ARM_E]),
        "runtime_seconds": {"C": arm_summary(by_arm[ARM_C])["total_wall_seconds"],
                            "E": arm_summary(by_arm[ARM_E])["total_wall_seconds"]},
    }
    aggregate["runtime_seconds"]["total"] = round(
        aggregate["runtime_seconds"]["C"] + aggregate["runtime_seconds"]["E"], 1)

    (OUT / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    (OUT / "pairs.json").write_text(json.dumps(pairs, indent=2, sort_keys=True) + "\n")
    (OUT / "stop_and_safety_table.json").write_text(
        json.dumps(stop_table(by_arm[ARM_E]), indent=2, sort_keys=True) + "\n")
    manifest = retention()
    if finalize:
        manifest["cleanup"] = finalize_capture(manifest)
        manifest["streams_still_exist"] = manifest["retention_verified"]
    (OUT / "raw_stream_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print(json.dumps({"runs": len(rows), "arms": aggregate["arms"],
                      "contract_audit": {k: v for k, v in aggregate["contract_audit"].items()
                                         if k != "triggers"},
                      "stop_policy": aggregate["stop_policy"],
                      "pairs_agreeing": aggregate["pairs_agreeing_on_verifier"],
                      "runtime": aggregate["runtime_seconds"],
                      "retention_verified": manifest["retention_verified"],
                      "retained_bytes": manifest["total_retained_bytes"]}, indent=1))
    return 0 if manifest["retention_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
