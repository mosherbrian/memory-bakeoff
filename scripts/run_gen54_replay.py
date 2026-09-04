#!/usr/bin/env python3
"""Gen54: replay v2 over 72 runs on a fingerprint that ignores build output.

Gen53's replay had to use the digests the runs recorded, which counted
`__pycache__`. This rebuilds each run's tree from its own recorded edits on a
fresh copy of the frozen fixture, so the net-tree-change predicate is finally
evaluated against the project's state rather than its build output.

A run whose edits cannot be replayed exactly is reported as unreconstructable
rather than guessed at.
"""
from __future__ import annotations

import gzip, json, re, shutil, statistics, subprocess, sys, tempfile
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import quiescent_v2 as Q          # noqa: E402
from memory_bakeoff.pi_state_control import tracked_digest as T        # noqa: E402
from memory_bakeoff.pi_state_control.harness_state import MUTATION_TOOLS  # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen54"
GENERATIONS = {
    47: (ROOT / "results/pi_state_control_gen47", ROOT / "results/pi_state_control_gen44"),
    49: (ROOT / "results/pi_state_control_gen49", ROOT / "results/pi_state_control_gen48"),
    52: (ROOT / "results/pi_quiescent_completion_gen52", ROOT / "results/pi_state_control_gen48"),
}
PYTEST_SUMMARY = re.compile(r"=+[^=\n]*\bin\s+[\d.]+s[^=\n]*=+")


def read_ndjson(path: Path):
    if not path.exists():
        return []
    handle = gzip.open(path, "rt") if path.suffix == ".gz" else open(path)
    with handle:
        return [json.loads(line) for line in handle if line.strip()]


def output_text(payload) -> str:
    raw = payload.get("output", "")
    try:
        return "\n".join(b.get("text", "") for b in json.loads(raw) if isinstance(b, dict))
    except Exception:
        return raw if isinstance(raw, str) else ""


def outcome_from_output(text: str):
    stripped = text.strip()
    if not stripped:
        return None
    if re.search(r"Command exited with code [1-9]", stripped):
        return False
    last = stripped.splitlines()[-1].strip()
    if last in ("all checks passed", "OK"):
        return True
    if last.startswith("FAILED ("):
        return False
    match = PYTEST_SUMMARY.search(last)
    if match:
        lowered = last.lower()
        if "failed" in lowered or "error" in lowered:
            return False
        if "passed" in lowered:
            return True
    return None


def fresh_worktree(repo: Path) -> Path:
    target = Path(tempfile.mkdtemp(prefix="gen54-replay-"))
    shutil.rmtree(target)
    shutil.copytree(repo, target)
    shutil.rmtree(target / ".git", ignore_errors=True)
    for command in (["git", "init", "-q"], ["git", "add", "-A"],
                    ["git", "-c", "user.email=p@x.invalid", "-c", "user.name=p",
                     "commit", "-qm", "run"]):
        subprocess.run(command, cwd=target, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return target


def resolve(worktree: Path, recorded: str) -> Path:
    """Map a recorded absolute path in the original worktree onto this copy."""
    parts = Path(recorded).parts
    for index, part in enumerate(parts):
        if part.startswith("run_"):
            return worktree.joinpath(*parts[index + 1:])
    return worktree / Path(recorded).name


def apply_mutation(worktree: Path, tool: str, args: dict) -> str | None:
    """Apply one recorded mutation. Returns None when it cannot be replayed exactly."""
    recorded = args.get("path") or args.get("file_path")
    if not recorded:
        return None
    target = resolve(worktree, recorded)
    if tool in ("edit", "multi_edit"):
        edits = args.get("edits") or []
        if not edits or not target.exists():
            return None
        text = target.read_text()
        for edit in edits:
            old, new = edit.get("oldText"), edit.get("newText")
            if old is None or new is None or old not in text:
                return None
            text = text.replace(old, new, 1)
        target.write_text(text)
        return "edit"
    if tool == "write":
        content = args.get("content")
        if content is None:
            return None
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return "write"
    return None


def events_for(run_dir: Path, worktree: Path):
    """Ordered events, with tracked digests recomputed as the tree really changed."""
    derived = (run_dir / "derivation.ndjson").exists()
    tools = read_ndjson(run_dir / "tools.ndjson")
    validations, seen = {}, set()
    if derived:
        for row in read_ndjson(run_dir / "derivation.ndjson"):
            validation = row.get("validation") or {}
            event = validation.get("event")
            if event and event not in seen and validation.get("passed") is not None:
                seen.add(event)
                validations[len(validations)] = bool(validation["passed"])
    outputs = [output_text(h["payload"]) for h in read_ndjson(run_dir / "history.ndjson.gz")
               if h.get("type") == "tool_result"]

    events, pending, index, result_index, check_number = [], deque(), 0, 0, 0
    digest = T.tracked_digest(worktree)
    unreconstructable = []
    for row in tools:
        if row.get("phase") == "call":
            index += 1
            args = row.get("args") or {}
            command = (args.get("command") or args.get("cmd") or "") if row["tool"] == "bash" else ""
            pending.append((index, row["tool"], command, args))
            continue
        call_index, tool, command, args = pending.popleft() if pending else (index, "", "", {})
        if tool in MUTATION_TOOLS:
            applied = apply_mutation(worktree, tool, args)
            if applied is None:
                unreconstructable.append({"tool": tool, "call": call_index})
            digest = T.tracked_digest(worktree)
            events.append({"i": call_index, "kind": "mutation", "tree": digest})
        elif Q.is_visible_check(command):
            passed = validations.get(check_number) if derived else \
                outcome_from_output(outputs[result_index] if result_index < len(outputs) else "")
            check_number += 1
            if passed is not None:
                events.append({"i": call_index, "kind": "check", "passed": passed, "tree": digest})
            else:
                events.append({"i": call_index, "kind": "call", "tree": digest})
        else:
            events.append({"i": call_index, "kind": "call", "tree": digest})
        result_index += 1
    return events, index, unreconstructable


def replay(events, initial: str, k: int):
    rule = Q.QuiescentV2(k=k)
    rule.initial_tree = initial
    rule.current_tree = initial
    stop_at = None
    for event in events:
        rule.observe_call("edit" if event["kind"] == "mutation" else "bash")
        fresh = event["kind"] == "check"
        if stop_at is None and rule.observe_result(passed=event.get("passed"),
                                                   tree=event["tree"], fresh_check=fresh):
            stop_at = rule.tool_index
    return rule, stop_at


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    runs = []
    for generation, (base, manifest_dir) in GENERATIONS.items():
        manifest = json.loads((manifest_dir / "task_manifest.json").read_text())
        for run_dir in sorted((base / "runs").iterdir()):
            leaf_path = run_dir / "leaf.json"
            if not leaf_path.exists():
                continue
            leaf = json.loads(leaf_path.read_text())
            repo = ROOT / manifest["tasks"][leaf["slot"]["task"]]["repo_path"]
            censored = bool((leaf.get("measured", {}).get("quiescent_stop") or {}).get("triggered"))
            row = {"generation": generation, "run": run_dir.name, "arm": leaf["slot"]["arm"],
                   "task": leaf["slot"]["task"], "repetition": leaf["slot"]["repetition"],
                   "status": leaf["run"]["status"], "verifier_passed": leaf["verifier"]["passed"],
                   "trajectory_censored_by_prior_live_stop": censored,
                   "receipt_source": ("harness_validation_record"
                                      if (run_dir / "derivation.ndjson").exists()
                                      else "offline_reconstructed_observable_receipt"),
                   "k": {}}
            for k in Q.K_SWEEP:
                worktree = fresh_worktree(repo)
                initial = T.tracked_digest(worktree)
                events, total, unreconstructable = events_for(run_dir, worktree)
                rule, stop_at = replay(events, initial, k)
                after = [e for e in events if rule.trigger_index and e["i"] > rule.trigger_index]
                later_mutations = [e for e in after if e["kind"] == "mutation"]
                outcome = {
                    "triggered": stop_at is not None,
                    "became_eligible": rule.became_eligible,
                    "trigger_tool_index": rule.trigger_index,
                    "final_tracked_digest_equals_initial": rule.current_tree == initial,
                    "net_tree_changed_at_end": rule.net_tree_changed(),
                    "same_tree_passes_counted_idle": rule.same_tree_passes_counted_idle,
                    "tool_calls_after_trigger": len(after),
                    "would_truncate_observed_progress": bool(later_mutations) and not censored,
                    "would_stop_wrong_tree": (stop_at is not None) and not leaf["verifier"]["passed"],
                }
                row["k"][str(k)] = outcome
                if k == Q.K_SWEEP[0]:
                    row["total_tool_calls"] = total
                    row["unreconstructable_mutations"] = unreconstructable
                    row["fully_reconstructable"] = not unreconstructable
                    row["initial_tracked_digest"] = initial
                shutil.rmtree(worktree, ignore_errors=True)
            runs.append(row)

    per_k = {}
    for k in Q.K_SWEEP:
        key = str(k)
        fired = [r for r in runs if r["k"][key]["triggered"]]
        observed = [r for r in fired if not r["trajectory_censored_by_prior_live_stop"]]
        truncating = [r for r in observed if r["k"][key]["would_truncate_observed_progress"]]
        after = sorted(r["k"][key]["tool_calls_after_trigger"] for r in fired)
        per_k[key] = {
            "runs_triggered": len(fired), "of_runs": len(runs),
            "would_truncate_observed_progress": len(truncating),
            "truncated_runs": [r["run"] for r in truncating],
            "would_stop_wrong_tree": sum(1 for r in fired if r["k"][key]["would_stop_wrong_tree"]),
            "wrong_tree_runs": [r["run"] for r in fired if r["k"][key]["would_stop_wrong_tree"]],
            "timeout_runs_caught": sum(1 for r in fired if r["status"] == "timeout"),
            "timeout_runs_total": sum(1 for r in runs if r["status"] == "timeout"),
            "triggered_on_a_tree_equal_to_initial":
                sum(1 for r in fired if r["k"][key]["final_tracked_digest_equals_initial"]),
            "median_tool_calls_after_trigger": statistics.median(after) if after else None,
            "total_tool_calls_after_trigger": sum(after),
        }

    focal = {name: {k: next(r["k"][k] for r in runs if r["run"].startswith(name))
                    for k in map(str, Q.K_SWEEP)}
             for name in ("11-IP1-r1", "23-IP1-r2")}
    zero_truncation = [k for k in Q.K_SWEEP if per_k[str(k)]["would_truncate_observed_progress"] == 0]
    catches_loop = [k for k in Q.K_SWEEP if focal["23-IP1-r2"][str(k)]["triggered"]]
    declines_revert = [k for k in Q.K_SWEEP if not focal["11-IP1-r1"][str(k)]["triggered"]]
    satisfying = [k for k in Q.K_SWEEP
                  if k in zero_truncation and k in catches_loop and k in declines_revert]

    result = {
        "evidence_class": "architecture_quiescent_completion_tracked_digest_offline_replay_no_score",
        "rule_contract": Q.contract(),
        "digest_contract": T.contract(),
        "runs": runs, "per_k": per_k, "focal_runs": focal,
        "reconstruction": {
            "runs_fully_reconstructable": sum(1 for r in runs if r["fully_reconstructable"]),
            "of_runs": len(runs),
            "runs_with_unreplayable_mutations":
                [r["run"] for r in runs if not r["fully_reconstructable"]],
            "note": ("each run's tree is rebuilt from its own recorded edits on a fresh copy of the "
                     "frozen fixture, so the digest reflects the project rather than its build "
                     "output. A mutation whose recorded text cannot be applied exactly is reported, "
                     "never guessed."),
        },
        "decision": {
            "k_with_zero_observed_progress_truncation": zero_truncation,
            "k_catching_the_repeated_check_timeout": catches_loop,
            "k_declining_the_revert_to_start_stop": declines_revert,
            "k_satisfying_all_criteria": satisfying,
            "recommended_k": min(satisfying) if satisfying else None,
        },
    }
    (OUT / "replay_72_runs_tracked_digest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"per_k": per_k, "reconstruction": result["reconstruction"],
                      "decision": result["decision"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
