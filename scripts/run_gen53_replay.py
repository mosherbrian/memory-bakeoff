#!/usr/bin/env python3
"""Gen53 Part C: replay `quiescent-completion-toolcall-v2` over 72 recorded runs.

No model, no GPU, no network. The hidden verifier is read only after the replay,
to score what the rule would have done; it is never an input.

How the tree is modelled, because it decides the result: a run's tree is its
recorded `start_tree` until something changes it. A mutation tool moves it to an
unknown-but-different state. A recognized visible check carries the digest the
harness actually recorded at that moment, and that digest is authoritative.
Receipts are only ever created at a check, so every eligibility decision is made
against a digest the harness really measured, not against a guess.
"""
from __future__ import annotations

import gzip, json, re, statistics, sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import quiescent_v2 as Q      # noqa: E402
from memory_bakeoff.pi_state_control.harness_state import MUTATION_TOOLS  # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen53"
GENERATIONS = {
    47: ROOT / "results/pi_state_control_gen47",
    49: ROOT / "results/pi_state_control_gen49",
    52: ROOT / "results/pi_quiescent_completion_gen52",
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
    if last == "all checks passed" or last == "OK":
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


def events_from_derivation(run_dir: Path):
    """Arms C, D and E: the harness attributed every result and every digest."""
    events, index, seen = [], 0, set()
    for row in read_ndjson(run_dir / "derivation.ndjson"):
        if row["kind"] == "tool_call":
            index += 1
            if row.get("tool") in MUTATION_TOOLS:
                events.append({"i": index, "kind": "mutation"})
            else:
                events.append({"i": index, "kind": "call"})
            continue
        validation = row.get("validation") or {}
        event = validation.get("event")
        if event and event not in seen and validation.get("passed") is not None:
            seen.add(event)
            events.append({"i": index, "kind": "check", "passed": bool(validation["passed"]),
                           "tree": validation.get("tree_digest", ""),
                           "source": "harness_validation_record"})
    return events, index


def events_from_transcript(run_dir: Path):
    """Gen47 arm B: no derivation ever existed, so this is a labelled rebuild."""
    outputs = [output_text(h["payload"]) for h in read_ndjson(run_dir / "history.ndjson.gz")
               if h.get("type") == "tool_result"]
    events, pending, index, result_index = [], deque(), 0, 0
    for row in read_ndjson(run_dir / "tools.ndjson"):
        if row.get("phase") == "call":
            index += 1
            args = row.get("args") or {}
            command = (args.get("command") or args.get("cmd") or "") if row["tool"] == "bash" else ""
            pending.append((index, row["tool"], command))
            events.append({"i": index, "kind": "mutation" if row["tool"] in MUTATION_TOOLS else "call"})
        else:
            call_index, _tool, command = pending.popleft() if pending else (index, "", "")
            if Q.is_visible_check(command):
                text = outputs[result_index] if result_index < len(outputs) else ""
                passed = outcome_from_output(text)
                if passed is not None:
                    events.append({"i": call_index, "kind": "check", "passed": passed, "tree": "",
                                   "source": "offline_reconstructed_observable_receipt"})
            result_index += 1
    events.sort(key=lambda e: e["i"])
    return events, index


def replay(events, start_tree: str, k: int):
    """Run v2 over one recorded trajectory. Returns the rule and its trace."""
    rule = Q.QuiescentV2(k=k)
    rule.initial_tree = start_tree
    rule.current_tree = start_tree
    modelled, stop_at = 0, None
    for event in events:
        if event["kind"] in ("mutation", "call"):
            rule.observe_call("edit" if event["kind"] == "mutation" else "bash")
            if event["kind"] == "mutation":
                modelled += 1
                # unknown, but certainly not the tree we had a moment ago
                rule.current_tree = f"post-mutation-{modelled}"
            if stop_at is None and rule.observe_result(passed=None, tree=rule.current_tree,
                                                       fresh_check=False):
                stop_at = rule.tool_index
            continue
        # a recognized visible check: its digest is authoritative when recorded
        tree = event["tree"] or rule.current_tree
        rule.observe_call("bash")
        if stop_at is None and rule.observe_result(passed=event["passed"], tree=tree,
                                                   fresh_check=True):
            stop_at = rule.tool_index
    return rule, stop_at


def analyse(events, rule, stop_at, leaf, censored: bool):
    """What happened after the hypothetical trigger, in the recorded trajectory."""
    if stop_at is None:
        return {"triggered": False, "became_eligible": rule.became_eligible,
                "net_tree_changed_at_end": rule.net_tree_changed()}
    trigger = rule.trigger_index
    after = [e for e in events if e["i"] > trigger]
    later_mutations = [e for e in after if e["kind"] == "mutation"]
    later_fail = [e for e in after if e["kind"] == "check" and e["passed"] is False
                  and (not later_mutations or e["i"] < later_mutations[0]["i"])]
    return {
        "triggered": True,
        "became_eligible": True,
        "trigger_tool_index": trigger,
        "effective_stop_tool_index": rule.effective_stop_index,
        "qualifying_receipt_tree": rule.receipt_tree,
        "initial_tree": rule.initial_tree,
        "current_tree_differs_from_initial": rule.net_tree_changed(),
        "same_tree_passes_counted_idle_before_trigger": rule.same_tree_passes_counted_idle,
        "same_batch_overshoot_calls": rule.overshoot,
        "tool_calls_after_trigger": max(0, len([e for e in after])),
        "would_truncate_observed_progress": bool(later_mutations) and not censored,
        "first_later_mutation_index": later_mutations[0]["i"] if later_mutations else None,
        "later_visible_contradiction": bool(later_fail),
        "trigger_tree_equals_final_tree": (rule.receipt_tree == leaf["task"]["final_tree"]),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    runs = []
    for generation, base in GENERATIONS.items():
        for run_dir in sorted((base / "runs").iterdir()):
            leaf_path = run_dir / "leaf.json"
            if not leaf_path.exists():
                continue
            leaf = json.loads(leaf_path.read_text())
            derived = (run_dir / "derivation.ndjson").exists()
            events, total = (events_from_derivation if derived else events_from_transcript)(run_dir)
            checks = [e for e in events if e["kind"] == "check"]
            source = ("harness_validation_record" if derived
                      else "offline_reconstructed_observable_receipt")
            # This run was actually ended by the v1 policy, so it has no tail.
            censored = bool((leaf.get("measured", {}).get("quiescent_stop") or {}).get("triggered"))
            row = {
                "generation": generation, "run": run_dir.name, "arm": leaf["slot"]["arm"],
                "task": leaf["slot"]["task"], "repetition": leaf["slot"]["repetition"],
                "status": leaf["run"]["status"],
                "termination_class": leaf.get("termination_class"),
                "verifier_passed": leaf["verifier"]["passed"],
                "receipt_source": source,
                "trajectory_censored_by_prior_live_stop": censored,
                "start_tree": leaf["task"]["start_tree"],
                "final_tree": leaf["task"]["final_tree"],
                "tree_digest_available": derived,
                # A run whose recorded start and final trees match made no net
                # change to the tracked source, whatever the harness digest said
                # in between. This is the measure change A was meant to use.
                "start_tree_equals_final_tree":
                    leaf["task"]["start_tree"] == leaf["task"]["final_tree"],
                "total_tool_calls": total, "checks": len(checks),
                "mutations": sum(1 for e in events if e["kind"] == "mutation"),
                "provider_requests": len(read_ndjson(run_dir / "requests.ndjson")),
                "k": {},
            }
            for k in Q.K_SWEEP:
                rule, stop_at = replay(events, leaf["task"]["start_tree"], k)
                outcome = analyse(events, rule, stop_at, leaf, censored)
                if outcome["triggered"]:
                    share = outcome["tool_calls_after_trigger"] / max(1, total)
                    outcome["provider_requests_after_trigger_estimated"] = round(
                        row["provider_requests"] * share, 1)
                    outcome["would_stop_wrong_tree"] = not leaf["verifier"]["passed"]
                row["k"][str(k)] = outcome
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
            "fully_observed_triggers": len(observed),
            "would_truncate_observed_progress": len(truncating),
            "truncated_runs": [r["run"] for r in truncating],
            "would_stop_wrong_tree": sum(1 for r in fired if r["k"][key].get("would_stop_wrong_tree")),
            "wrong_tree_runs": [r["run"] for r in fired if r["k"][key].get("would_stop_wrong_tree")],
            "later_visible_contradiction": sum(1 for r in fired
                                               if r["k"][key]["later_visible_contradiction"]),
            "timeout_runs_caught": sum(1 for r in fired if r["status"] == "timeout"),
            "timeout_runs_total": sum(1 for r in runs if r["status"] == "timeout"),
            "median_tool_calls_after_trigger": statistics.median(after) if after else None,
            "total_tool_calls_after_trigger": sum(after),
            "same_tree_passes_counted_idle": sum(
                r["k"][key]["same_tree_passes_counted_idle_before_trigger"] for r in fired),
            "by_generation": {str(g): sum(1 for r in fired if r["generation"] == g)
                              for g in sorted(GENERATIONS)},
            # Triggers on runs that ended with the tracked source back at its
            # starting state. Change A was supposed to make this zero; it does
            # not, because the harness digest counts untracked build artifacts.
            "triggered_on_runs_with_no_net_source_change":
                sum(1 for r in fired if r["start_tree_equals_final_tree"]),
            "runs_with_no_net_source_change":
                [r["run"] for r in fired if r["start_tree_equals_final_tree"]],
        }

    focal = {name: {k: next(r["k"][k] for r in runs if r["run"].startswith(name))
                    for k in map(str, Q.K_SWEEP)}
             for name in ("11-IP1-r1", "23-IP1-r2")}

    zero_truncation = [k for k in Q.K_SWEEP
                       if per_k[str(k)]["would_truncate_observed_progress"] == 0]
    catches_loop = [k for k in Q.K_SWEEP if focal["23-IP1-r2"][str(k)]["triggered"]]
    declines_revert = [k for k in Q.K_SWEEP if not focal["11-IP1-r1"][str(k)]["triggered"]]
    satisfying = [k for k in Q.K_SWEEP
                  if k in zero_truncation and k in catches_loop and k in declines_revert]

    result = {
        "evidence_class": "architecture_quiescent_completion_refinement_offline_replay_no_score",
        "contract": Q.contract(),
        "runs": runs, "per_k": per_k,
        "focal_runs": focal,
        "gen54_decision_rule": {
            "k_with_zero_observed_progress_truncation": zero_truncation,
            "k_catching_the_repeated_check_timeout": catches_loop,
            "k_declining_the_revert_to_start_stop": declines_revert,
            "k_satisfying_all_criteria": satisfying,
            "recommended_k": min(satisfying) if satisfying else None,
        },
        "tree_modelling": (
            "start_tree from the leaf; a mutation moves the tree to an unknown-but-different "
            "state; a recognized check carries the digest the harness recorded. Receipts are only "
            "created at checks, so every eligibility decision uses a measured digest."),
        "change_a_effectiveness": {
            "question": "does net-tree-change eligibility decline the Gen52 revert-to-start stop?",
            "answer": "no, not on the recorded evidence",
            "why": ("the harness tree digest is `git add -A` over the worktree, so it includes "
                    "untracked build artifacts. Running the visible tests creates __pycache__ and "
                    ".pytest_cache, which changes the digest on its own. In 11-IP1-r1 the agent "
                    "reverted its source exactly - the leaf's start_tree and final_tree are the "
                    "same digest, 732a4b97 - but the digest recorded at the qualifying check was "
                    "966c0910, so `current != initial` was satisfied by bytecode."),
            "consequence": ("v2 still triggers on that run at K=1, 2 and 3. It declines at K=5 and "
                            "K=10 only because the run ran out of calls, not because the new "
                            "predicate engaged. The criterion is met incidentally, not in substance."),
        },
        "known_limits": [
            "Gen47 arm B has no recorded tree digests at all, so its net-tree-change predicate is "
            "modelled from mutation events and cannot test the revert case",
            "the harness tree digest includes untracked build artifacts such as __pycache__, so "
            "running the tests alone changes it",
        ],
    }
    (OUT / "replay_72_runs.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"runs": len(runs), "per_k": per_k,
                      "decision": result["gen54_decision_rule"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
