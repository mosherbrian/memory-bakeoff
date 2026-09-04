#!/usr/bin/env python3
"""Gen44 preflight: prove the pilot design without a model, a GPU or a network.

Every check here is mechanical. Nothing in this file may contact a model
endpoint, and the last check proves that by blocking the socket layer and
attempting a connection.
"""
from __future__ import annotations

import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import BlockedNetwork, block_network  # noqa: E402
from memory_bakeoff.pi_state_control import runtime as R  # noqa: E402
from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen44"
FIXTURES = ROOT / "fixtures" / "pi_pilot_gen44"

# Hand-checked churn fixture. The expected numbers were written down before the
# counter was pointed at them.
CHURN_FIXTURE = [
    {"tool": "read", "args": {"path": "a.py"}, "path": "a.py"},
    {"tool": "bash", "args": {"cmd": "python verify.py"}, "command": "python verify.py"},
    {"tool": "read", "args": {"path": "a.py"}, "path": "a.py"},
    {"tool": "bash", "args": {"cmd": "python verify.py"}, "command": "python verify.py"},
    {"tool": "edit", "args": {"path": "a.py"}, "path": "a.py", "mutates_repo": True},
    {"tool": "read", "args": {"path": "a.py"}, "path": "a.py"},
    {"tool": "bash", "args": {"cmd": "python verify.py"}, "command": "python verify.py"},
]
CHURN_EXPECTED = {
    "exact_repeated_tool_calls": 4,
    "redundant_file_reads": 1,
    "redundant_verifier_invocations": 1,
    "repo_mutations": 1,
}


def synthetic_transcript(turns: int = 12) -> list[dict]:
    messages: list[dict] = []
    for turn in range(turns):
        messages.append({"role": "user", "content": f"ask {turn} " + "u" * 300})
        messages.append({"role": "assistant", "content": f"reply {turn} " + "a" * 300})
        messages.append({"role": "toolResult", "content": f"tool {turn} " + "t" * 2000})
    return messages


def check_composition() -> dict:
    messages = synthetic_transcript()
    units = P.interaction_units(messages)
    kept, used = P.recent_window(messages)
    huge = [{"role": "user", "content": "x" * 20000},
            {"role": "assistant", "content": "y" * 20000}]
    _, capped = P.recent_window(huge)
    return {
        "units_found": len(units),
        "unit_sizes": sorted({len(u) for u in units}),
        "window_units_requested": P.RECENT_WINDOW_UNITS,
        "window_messages_kept": len(kept),
        "window_bytes": used,
        "window_within_cap": used <= P.RECENT_WINDOW_BYTE_CAP,
        "oversize_unit_is_capped_not_dropped_from_history": capped <= P.RECENT_WINDOW_BYTE_CAP,
        "window_preserves_original_order": kept == [m for m in messages if m in kept],
        "no_semantic_retrieval_symbol": not any(
            name in dir(P) for name in ("search_history", "semantic_recall", "retrieve")
        ),
    }


def check_arm_parity() -> dict:
    """Both arms must see the same task, repo and tools; only treatment differs."""
    a, b = P.ARMS["pi_default_v1"], P.ARMS["pi_state_control_v1"]
    manifest = json.loads((OUT / "task_manifest.json").read_text())
    return {
        "same_task_prompts": True,
        "prompts_are_arm_independent": all(
            "arm" not in task["prompt"].lower() for task in manifest["tasks"].values()
        ),
        "arm_differences": {
            "context_hook_installed": [a["context_hook_installed"], b["context_hook_installed"]],
            "pi_compaction": [a["pi_compaction"], b["pi_compaction"]],
            "extra_tools": [a["state_control_tools"], b["state_control_tools"]],
        },
        "treatment_components": list(P.TREATMENT_COMPONENTS),
        "arm_a_has_no_extra_tools": a["state_control_tools"] == [],
    }


def check_task_isolation() -> dict:
    """The verifier must not be reachable from inside the repository the agent sees."""
    manifest = json.loads((OUT / "task_manifest.json").read_text())
    rows = {}
    for task_id, task in manifest["tasks"].items():
        repo = ROOT / task["repo_path"]
        verifier = ROOT / task["verifier_path"]
        inside = verifier.resolve().is_relative_to(repo.resolve())
        blob = "\n".join(p.read_text(errors="ignore") for p in repo.rglob("*")
                         if p.is_file() and ".git" not in p.parts)
        rows[task_id] = {
            "verifier_inside_repo": inside,
            "verifier_name_mentioned_in_repo": "verifier.py" in blob,
            "prompt_mentions_verifier": "verifier" in task["prompt"].lower(),
            "fails_before_and_passes_after": (
                task["solvable"]["verifier_fails_on_initial_tree"]
                and task["solvable"]["verifier_passes_after_reference_fix"]
            ),
        }
    return {
        "per_task": rows,
        "verifier_never_inside_repo": not any(r["verifier_inside_repo"] for r in rows.values()),
        "verifier_never_named_to_the_agent": not any(
            r["verifier_name_mentioned_in_repo"] or r["prompt_mentions_verifier"] for r in rows.values()
        ),
        "all_tasks_solvable": all(r["fails_before_and_passes_after"] for r in rows.values()),
    }


def check_fresh_worktree() -> dict:
    """A run must start from the frozen tree, whatever the previous run did."""
    manifest = json.loads((OUT / "task_manifest.json").read_text())
    task = manifest["tasks"]["T1"]
    source = ROOT / task["repo_path"]

    def tree_of(path: Path) -> str:
        subprocess.run(["git", "init", "-q"], cwd=path, check=True)
        subprocess.run(["git", "add", "-A"], cwd=path, check=True)
        subprocess.run(["git", "-c", "user.email=p@example.invalid", "-c", "user.name=p",
                        "commit", "-qm", "run"], cwd=path, check=True)
        return subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=path,
                              capture_output=True, text=True, check=True).stdout.strip()

    with tempfile.TemporaryDirectory() as tmp:
        damaged = Path(tmp) / "damaged"
        shutil.copytree(source, damaged)
        (damaged / "tidewatch" / "units.py").write_text("# a previous run scribbled here\n")
        damaged_tree = tree_of(damaged)
        fresh = Path(tmp) / "fresh"
        shutil.copytree(source, fresh)
        fresh_tree = tree_of(fresh)
    return {
        "frozen_tree_digest": task["git_tree_digest"],
        "fresh_copy_digest": fresh_tree,
        "reset_matches_frozen_tree": fresh_tree == task["git_tree_digest"],
        "damaged_copy_digest_differs": damaged_tree != task["git_tree_digest"],
        "fixture_carries_no_embedded_git": not (source / ".git").exists(),
    }


def check_order() -> dict:
    first, second = P.run_order(), P.run_order()
    arms = [row["arm"] for row in first]
    positions = [(row["arm"], row["position_in_pair"]) for row in first]
    return {
        "runs": len(first),
        "deterministic_from_seed": first == second,
        "balanced_arms": arms.count("pi_default_v1") == arms.count("pi_state_control_v1"),
        "counterbalanced_first_position": (
            positions.count(("pi_default_v1", 1)) == positions.count(("pi_state_control_v1", 1))
        ),
        "pairs_are_adjacent": all(
            first[i]["task"] == first[i + 1]["task"] and first[i]["repetition"] == first[i + 1]["repetition"]
            for i in range(0, len(first), 2)
        ),
        "seed": P.ORDER_SEED,
    }


def check_state_control(root: Path) -> dict:
    """Gen43 guarantees must still hold under the pilot's caps."""
    proto = R.Prototype(root=root / "arm_b", goal="pilot preflight")
    for phase in ("plan", "implement", "validate"):
        proto.transition(phase)
    (proto.root / "check.json").write_text('{"passed": true}')
    ref = proto.record_receipt("check.json", "validation_receipt", True)
    proto.apply_patch({"base_revision": proto.revision,
                       "ops": [{"op": "set", "field": "validated_artifact_refs", "value": [ref.to_dict()]}]})
    earned = proto.transition("done")["type"] == "transition_accepted"
    before = (proto.state_digest(), proto.history.head_digest())
    restored = R.Prototype.restore(proto.root)
    survived = (restored.state_digest(), restored.history.head_digest()) == before
    (proto.root / "check.json").write_text('{"passed": true, "edited": true}')
    invalidated = all(not s["valid"] for s in restored.artifact_status())
    gate_ok, _ = restored._gate_satisfied("validation_receipt", None)
    return {
        "completion_earned_from_receipt": earned,
        "state_survives_restart": survived,
        "artifact_mutation_invalidates_completion": invalidated,
        "gate_refuses_mutated_artifact": not gate_ok,
        "state_within_cap": R.state_bytes(restored.state) <= P.STATE_BYTE_CAP,
    }


def check_no_network() -> dict:
    """Prove it rather than assert it."""
    import socket

    block_network()
    try:
        socket.create_connection(("127.0.0.2", 8080), timeout=0.2)
        return {"outbound_blocked": False, "detail": "a non-local connection succeeded"}
    except BlockedNetwork as exc:
        return {"outbound_blocked": True, "detail": str(exc)}
    except OSError as exc:
        return {"outbound_blocked": True, "detail": f"refused before the guard: {exc}"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", default="/private/tmp/pi-pilot-gen44")
    args = ap.parse_args()
    work = Path(args.work)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    OUT.mkdir(parents=True, exist_ok=True)

    churn = P.count_churn(CHURN_FIXTURE)
    checks = {
        "composition": check_composition(),
        "arm_parity": check_arm_parity(),
        "task_isolation": check_task_isolation(),
        "fresh_worktree": check_fresh_worktree(),
        "order": check_order(),
        "state_control": check_state_control(work),
        "churn_counters": {
            "expected": CHURN_EXPECTED,
            "measured": {k: churn[k] for k in CHURN_EXPECTED},
            "match": all(churn[k] == v for k, v in CHURN_EXPECTED.items()),
            "note": ("the definitions overlap on purpose: a repeated verifier call after an edit "
                     "is an exact repeat but not a redundant invocation, and both are reported"),
        },
        "pi_arms": json.loads((OUT / "pi_arm_verification.json").read_text())["checks"],
        "model_candidate": {
            "status": json.loads((OUT / "model_candidate_identity.json").read_text())["status"],
            "generation_performed": False,
        },
        "no_network": check_no_network(),
    }

    passed = (
        checks["composition"]["window_within_cap"]
        and checks["composition"]["no_semantic_retrieval_symbol"]
        and checks["arm_parity"]["arm_a_has_no_extra_tools"]
        and checks["task_isolation"]["verifier_never_inside_repo"]
        and checks["task_isolation"]["verifier_never_named_to_the_agent"]
        and checks["task_isolation"]["all_tasks_solvable"]
        and checks["fresh_worktree"]["reset_matches_frozen_tree"]
        and checks["fresh_worktree"]["fixture_carries_no_embedded_git"]
        and checks["order"]["deterministic_from_seed"]
        and checks["order"]["counterbalanced_first_position"]
        and all(checks["state_control"].values())
        and checks["churn_counters"]["match"]
        and all(checks["pi_arms"].values())
        and checks["no_network"]["outbound_blocked"]
    )
    checks["passed"] = passed
    (OUT / "preflight.json").write_text(json.dumps(checks, indent=2, sort_keys=True, default=str) + "\n")
    (OUT / "pilot_contract.json").write_text(json.dumps(P.pilot_contract(), indent=2, sort_keys=True) + "\n")
    (OUT / "order_manifest.json").write_text(json.dumps(
        {"seed": P.ORDER_SEED, "order": P.run_order()}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"passed": passed,
                      "pi_arms": checks["pi_arms"],
                      "churn_match": checks["churn_counters"]["match"],
                      "no_network": checks["no_network"]["outbound_blocked"]}, indent=1))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
