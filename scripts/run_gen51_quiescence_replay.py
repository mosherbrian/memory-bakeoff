"""Gen51 Part B: offline replay of normalized_quiescent_completion(K) over 48 recorded runs.

Nothing here runs a model. The hidden verifier is read only after the replay, to
score what the rule would have done; it is never an input to the rule.

Two arms leave two different kinds of record, so the receipt has two sources:

  * arms C and D wrote `derivation.ndjson`, which attributes a command, an exit
    status and a tree digest to each tool result. That is an authoritative
    observable receipt.
  * arm B wrote no derivation. Its receipts are rebuilt from `tools.ndjson`
    (calls) and `history.ndjson.gz` (outputs), paired first-in-first-out. That
    pairing is checkable on C and D, and its measured fidelity is reported.
"""
import gzip, json, re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"results/pi_gen51"; OUT.mkdir(parents=True, exist_ok=True)
GENS = {47: ROOT/"results/pi_state_control_gen47", 49: ROOT/"results/pi_state_control_gen49"}
K_SWEEP = [1, 2, 3, 5, 10]

import sys; sys.path.insert(0, str(ROOT/"src"))
from memory_bakeoff.pi_state_control.harness_state import (
    MUTATION_TOOLS, VALIDATION_RE, FORBIDDEN_IN_VALIDATION, DERIVATION_VERSION)

def is_check(command: str) -> bool:
    """The harness's own frozen recognizer, reused rather than reinvented."""
    return (bool(command) and not any(t in command for t in FORBIDDEN_IN_VALIDATION)
            and bool(VALIDATION_RE.search(command)))

def read_ndjson(path: Path):
    if not path.exists():
        return []
    handle = gzip.open(path, "rt") if path.suffix == ".gz" else open(path)
    with handle:
        return [json.loads(line) for line in handle if line.strip()]

def output_text(payload) -> str:
    raw = payload.get("output", "")
    try:
        blocks = json.loads(raw)
        return "\n".join(b.get("text", "") for b in blocks if isinstance(b, dict))
    except Exception:
        return raw if isinstance(raw, str) else ""

PYTEST_SUMMARY = re.compile(r"=+[^=\n]*\bin\s+[\d.]+s[^=\n]*=+")

def outcome_from_output(text: str):
    """Exact terminal signals only. Ambiguity is left unknown, never guessed."""
    stripped = text.strip()
    if not stripped:
        return None
    if re.search(r"Command exited with code [1-9]", stripped):
        return False
    last = stripped.splitlines()[-1].strip()
    if last == "all checks passed":
        return True
    match = PYTEST_SUMMARY.search(last)
    if match:
        lowered = last.lower()
        if "failed" in lowered or "error" in lowered:
            return False
        if "passed" in lowered:
            return True
    if last == "OK":
        return True
    if last.startswith("FAILED ("):
        return False
    return None

def events_from_derivation(run_dir: Path):
    """Arms C and D: the harness already attributed every result."""
    events, index = [], 0
    for row in read_ndjson(run_dir/"derivation.ndjson"):
        if row["kind"] == "tool_call":
            index += 1
            if row.get("tool") in MUTATION_TOOLS:
                events.append({"i": index, "kind": "mutation", "tool": row["tool"]})
        else:
            validation = row.get("validation") or {}
            if validation.get("command") and validation.get("passed") is not None:
                events.append({"i": index, "kind": "check", "command": validation["command"][:200],
                               "passed": bool(validation["passed"]),
                               "tree_digest": validation.get("tree_digest", ""),
                               "source": "harness_validation_record"})
    return events, index

def events_from_transcript(run_dir: Path):
    """Arm B: rebuild the same stream from calls and recorded outputs."""
    outputs = [output_text(h["payload"]) for h in read_ndjson(run_dir/"history.ndjson.gz")
               if h.get("type") == "tool_result"]
    events, pending, index, result_index = [], deque(), 0, 0
    for row in read_ndjson(run_dir/"tools.ndjson"):
        if row.get("phase") == "call":
            index += 1
            args = row.get("args") or {}
            command = (args.get("command") or args.get("cmd") or "") if row["tool"] == "bash" else ""
            pending.append((index, row["tool"], command))
            if row["tool"] in MUTATION_TOOLS:
                events.append({"i": index, "kind": "mutation", "tool": row["tool"]})
        else:
            call_index, _tool, command = pending.popleft() if pending else (index, "", "")
            if is_check(command):
                text = outputs[result_index] if result_index < len(outputs) else ""
                events.append({"i": call_index, "kind": "check", "command": command[:200],
                               "passed": outcome_from_output(text),
                               "source": "offline_reconstructed_observable_receipt"})
            result_index += 1
    events.sort(key=lambda e: e["i"])
    return events, index

def receipt_valid_at_end(events, require_mutation: bool):
    """A passing check that nothing has invalidated since."""
    mutated, valid = False, False
    for event in events:
        if event["kind"] == "mutation":
            mutated, valid = True, False
        elif event.get("passed") is True:
            valid = True
        elif event.get("passed") is False:
            valid = False
    return valid and (mutated or not require_mutation)

def replay(events, total_calls, k):
    mutated, qualifying, position = False, None, None
    for index, event in enumerate(events):
        if event["kind"] == "mutation":
            mutated, qualifying = True, None
            continue
        if event.get("passed") is True and mutated:
            qualifying, position = event, index
        elif event.get("passed") is False:
            qualifying = None
        if qualifying is None:
            continue
        if total_calls - qualifying["i"] >= k:
            downstream = events[position + 1:]
            later_mutations = [e for e in downstream if e["kind"] == "mutation"]
            later_failures = [e for e in downstream if e.get("passed") is False
                              and (not later_mutations or e["i"] < later_mutations[0]["i"])]
            return {"triggered": True, "trigger_call_index": qualifying["i"],
                    "qualifying_command": qualifying["command"],
                    "receipt_source": qualifying["source"],
                    "tool_calls_after_trigger": total_calls - qualifying["i"],
                    "would_truncate_observed_progress": bool(later_mutations),
                    "first_later_mutation_call": later_mutations[0]["i"] if later_mutations else None,
                    "later_visible_contradiction": bool(later_failures)}
    return {"triggered": False}

def pairing_fidelity():
    """How often FIFO pairing reproduces the attribution the harness recorded."""
    agree = total = 0
    for base in GENS.values():
        for run_dir in sorted((base/"runs").iterdir()):
            if not (run_dir/"derivation.ndjson").exists():
                continue
            recorded = [r for r in read_ndjson(run_dir/"derivation.ndjson") if r["kind"] == "tool_result"]
            pending, paired = deque(), []
            for row in read_ndjson(run_dir/"tools.ndjson"):
                if row.get("phase") == "call":
                    pending.append(row)
                else:
                    call = pending.popleft() if pending else {}
                    args = call.get("args") or {}
                    paired.append((args.get("command") or "") if call.get("tool") == "bash" else "")
            for got, expected in zip(paired, recorded):
                total += 1
                agree += got.strip() == (expected.get("command") or "").strip()
    return {"results_compared": total, "command_attribution_agrees": agree,
            "fidelity": round(agree/total, 4) if total else None,
            "note": ("measured on arms C and D, where the harness recorded the true attribution; "
                     "arm B's pairing cannot be checked directly and is assumed to share this fidelity")}

runs, agreement, disagreements, unknown_outcomes = [], {"compared": 0, "agree": 0}, [], []
for generation, base in GENS.items():
    for run_dir in sorted((base/"runs").iterdir()):
        if not (run_dir/"leaf.json").exists():
            continue
        leaf = json.loads((run_dir/"leaf.json").read_text())
        derived = (run_dir/"derivation.ndjson").exists()
        events, total_calls = (events_from_derivation if derived else events_from_transcript)(run_dir)
        requests = read_ndjson(run_dir/"requests.ndjson")
        checks = [e for e in events if e["kind"] == "check"]
        unknown = sum(1 for c in checks if c.get("passed") is None)
        if unknown:
            unknown_outcomes.append({"run": run_dir.name, "checks": len(checks), "unknown": unknown})

        row = {"generation": generation, "run": run_dir.name, "arm": leaf["slot"]["arm"],
               "task": leaf["slot"]["task"], "repetition": leaf["slot"]["repetition"],
               "status": leaf["run"]["status"], "verifier_passed": leaf["verifier"]["passed"],
               "receipt_source": "harness_validation_record" if derived
                                 else "offline_reconstructed_observable_receipt",
               "total_tool_calls": total_calls, "provider_requests": len(requests),
               "mutations": sum(1 for e in events if e["kind"] == "mutation"),
               "checks": len(checks), "checks_with_unknown_outcome": unknown,
               "reconstructed_valid_receipt_at_end": receipt_valid_at_end(events, require_mutation=False),
               "k": {}}
        for k in K_SWEEP:
            outcome = replay(events, total_calls, k)
            if outcome["triggered"]:
                share = outcome["tool_calls_after_trigger"]/max(1, total_calls)
                outcome["provider_requests_after_trigger_estimated"] = round(len(requests)*share, 1)
                outcome["would_stop_wrong_tree"] = (not leaf["verifier"]["passed"]
                                                    and not outcome["would_truncate_observed_progress"])
            row["k"][str(k)] = outcome

        harness_path = run_dir/"harness_state.json"
        if harness_path.exists():
            recorded = bool(json.loads(harness_path.read_text()).get("valid_receipt_at_end"))
            agreement["compared"] += 1
            agreement["agree"] += recorded == row["reconstructed_valid_receipt_at_end"]
            if recorded != row["reconstructed_valid_receipt_at_end"]:
                disagreements.append({"run": run_dir.name, "recorded": recorded,
                                      "reconstructed": row["reconstructed_valid_receipt_at_end"]})
            row["recorded_valid_receipt_at_end"] = recorded
        runs.append(row)

per_k = {}
for k in K_SWEEP:
    fired = [r for r in runs if r["k"][str(k)]["triggered"]]
    truncating = [r for r in fired if r["k"][str(k)]["would_truncate_observed_progress"]]
    after = sorted(r["k"][str(k)]["tool_calls_after_trigger"] for r in fired)
    per_k[str(k)] = {
        "runs_triggered": len(fired), "of_runs": len(runs),
        "would_truncate_observed_progress": len(truncating),
        "truncated_runs": [r["run"] for r in truncating],
        "would_stop_wrong_tree": sum(1 for r in fired if r["k"][str(k)].get("would_stop_wrong_tree")),
        "later_visible_contradiction": sum(1 for r in fired if r["k"][str(k)]["later_visible_contradiction"]),
        "median_tool_calls_after_trigger": after[len(after)//2] if after else None,
        "max_tool_calls_after_trigger": after[-1] if after else None,
        "total_tool_calls_after_trigger": sum(after),
        "estimated_provider_requests_after_trigger": round(
            sum(r["k"][str(k)]["provider_requests_after_trigger_estimated"] for r in fired), 1),
        "timeout_runs_triggered": sum(1 for r in fired if r["status"] == "timeout"),
        "by_arm": {arm: sum(1 for r in fired if r["arm"] == arm) for arm in sorted({r["arm"] for r in runs})},
    }

zero = [k for k in K_SWEEP if per_k[str(k)]["would_truncate_observed_progress"] == 0]
timeouts = [r for r in runs if r["status"] == "timeout"]
result = {
  "evidence_class": "architecture_evidence_retention_and_quiescence_offline_calibration_no_score",
  "derivation_version": DERIVATION_VERSION,
  "contract": {
    "name": "normalized_quiescent_completion",
    "eligibility": ["at least one repository mutation has occurred in the run",
                    "the most recent recognized visible check PASSED",
                    "no repository mutation since that passing check",
                    "no later recognized visible check FAILED before the next mutation",
                    "K further tool calls have elapsed with no mutation"],
    "hidden_verifier_is_never_an_input": True,
    "recognized_checks": "harness-state-v1 VALIDATION_RE, reused unchanged",
    "hidden_verifier_exclusion": list(FORBIDDEN_IN_VALIDATION),
    "mutation_tools": sorted(MUTATION_TOOLS),
    "clock_substitution": ("the brief counts K in provider requests. The committed logs order tool "
                           "events and provider requests in separate files with no joint sequence, "
                           "so K is counted in tool calls after the qualifying check and provider "
                           "requests after the trigger are reported as a proportional estimate. "
                           "This is a deviation from the frozen brief, stated rather than hidden."),
    "k_sweep": K_SWEEP, "no_live_tuning": True, "no_k_baked_into_any_arm": True},
  "receipt_reconstruction": {
    "arms_with_authoritative_receipts": ["pi_harness_state_control_v1", "pi_harness_state_control_task_floor_v1"],
    "arms_reconstructed_offline": ["pi_state_control_v1"],
    "pairing_fidelity": pairing_fidelity(),
    "agreement_with_recorded_harness_receipts": agreement,
    "disagreements": disagreements,
    "runs_with_unknown_check_outcomes": unknown_outcomes},
  "instrumentation_blocker": bool(disagreements),
  "per_k": per_k,
  "timeout_runs": [{"run": r["run"], "arm": r["arm"], "verifier_passed": r["verifier_passed"],
                    "total_tool_calls": r["total_tool_calls"],
                    "k1": r["k"]["1"], "k3": r["k"]["3"], "k10": r["k"]["10"]} for r in timeouts],
  "runs": runs,
  "k_with_zero_progress_truncation": zero,
  "most_conservative_zero_truncation_k": min(zero) if zero else None}
(OUT/"quiescence_replay_48_runs.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
(OUT/"quiescence_contract.json").write_text(json.dumps(result["contract"], indent=2, sort_keys=True)+"\n")
print(json.dumps({"receipt_reconstruction": result["receipt_reconstruction"],
                  "blocker": result["instrumentation_blocker"], "per_k": per_k,
                  "zero_truncation_k": zero, "timeouts": len(timeouts)}, indent=1))
