#!/usr/bin/env python3
"""Gen43: drive the Pi state/control prototype over a fixed synthetic trace.

Architecture prototype evidence. No model, no network, no benchmark corpus, no
task-success claim. The trace is invented, deterministic and digested before it
is measured.
"""
from __future__ import annotations

import argparse, json, shutil, sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import contract as C  # noqa: E402
from memory_bakeoff.pi_state_control import runtime as R  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen43"
GOAL = "teach the ledger importer to accept the second date format"

NOISE = (
    "resolved 214 packages in 3.1s\n"
    + "\n".join(f"  {name}@{major}.{major % 7}.{major % 3} (cached)"
               for major, name in enumerate(
                   ["astral", "bindle", "cartouche", "dovetail", "escutcheon", "fettle",
                    "gimbal", "haversack", "inglenook", "jetsam", "kestrel", "lintel",
                    "mullion", "newel", "oriel", "purlin", "quoin", "rebate", "sarking",
                    "transom", "undercroft", "voussoir", "wainscot", "xystus", "yett",
                    "zephyr"] * 8, start=1))
)


def trace_steps() -> list[dict]:
    """The fixed synthetic trace. Written before any metric was looked at."""
    steps: list[dict] = [
        {"do": "observe", "tool": "ls", "output": "importer/ parser.py dates.py tests/ ledger.csv",
         "keep": True},
        {"do": "patch", "ops": [{"op": "append", "field": "active_files", "value": "importer/dates.py"},
                                {"op": "set", "field": "current_process_or_tool", "value": "ls"}]},
        {"do": "observe", "tool": "read", "output": "dates.py parses only ISO-8601 with a strict regex",
         "keep": True},
        {"do": "patch", "ops": [{"op": "append", "field": "important_findings",
                                 "value": "dates.py accepts ISO-8601 only, via a strict regex"}]},
        # a large, irrelevant tool result: history keeps it, context does not
        {"do": "observe", "tool": "bash", "output": NOISE, "keep": False},
        {"do": "patch", "ops": [{"op": "append", "field": "important_findings",
                                 "value": "dependency install is clean; not relevant to the change"}]},
        # an early decision that will matter again much later
        {"do": "patch", "ops": [{"op": "append", "field": "important_findings",
                                 "value": "DECISION: ledger.csv rows are never rewritten in place"}]},
        {"do": "transition", "to": "plan"},
        {"do": "patch", "ops": [{"op": "set", "field": "next_actions",
                                 "value": ["add a second pattern", "extend the parser tests"]}]},
        # the intentionally illegal transition: plan cannot jump to done
        {"do": "transition", "to": "done", "expect": "rejected"},
        # plan revision
        {"do": "observe", "tool": "read", "output": "tests/test_dates.py pins the strict regex directly",
         "keep": True},
        {"do": "patch", "ops": [{"op": "set", "field": "next_actions",
                                 "value": ["loosen the pattern", "retire the pinned regex assertion",
                                           "extend the parser tests"]},
                                {"op": "append", "field": "open_questions",
                                 "value": "does any caller depend on the strict failure?"}]},
        {"do": "transition", "to": "implement"},
    ]

    # first implementation attempt, then a failing validation
    steps += [
        {"do": "observe", "tool": "edit", "output": "dates.py: added a second pattern", "keep": True},
        {"do": "patch", "ops": [{"op": "append", "field": "completed_checkpoints",
                                 "value": "second date pattern added"}]},
        {"do": "transition", "to": "validate"},
        {"do": "artifact", "path": "check.json", "content": '{"passed": false, "failed": ["test_dates::strict"]}',
         "kind": "validation_receipt", "passed": False},
        {"do": "observe", "tool": "bash", "output": "1 failed: test_dates::strict expects a rejection",
         "keep": True},
        # done is refused: the only receipt in state records a failure
        {"do": "transition", "to": "done", "expect": "rejected"},
        {"do": "transition", "to": "implement"},
        {"do": "observe", "tool": "edit", "output": "tests/test_dates.py: retired the pinned assertion",
         "keep": True},
        {"do": "patch", "ops": [{"op": "append", "field": "completed_checkpoints",
                                 "value": "pinned regex assertion retired"}]},
    ]

    # padding that exercises the bounds: findings and checkpoints overflow and
    # are archived to history rather than dropped
    for index in range(1, 15):
        steps.append({"do": "observe", "tool": "bash",
                      "output": f"probe {index}: {'quiet' if index % 3 else 'noisy'} output {'x' * (200 * index)}",
                      "keep": index % 4 == 0})
        steps.append({"do": "patch", "ops": [{"op": "append", "field": "important_findings",
                                              "value": f"probe {index} changed nothing material"}]})

    # a stale patch: the revision it names is no longer current
    steps.append({"do": "stale_patch"})
    # a malformed patch: wrong type for a list field
    steps.append({"do": "patch", "ops": [{"op": "set", "field": "active_files", "value": "not-a-list"}],
                  "expect": "rejected"})

    # the restart boundary
    steps.append({"do": "restart"})

    # the old decision becomes relevant again and is recalled from history
    steps += [
        {"do": "recall_decision"},
        {"do": "patch", "ops": [{"op": "append", "field": "open_questions",
                                 "value": "recalled: rows are never rewritten in place"}]},
        {"do": "transition", "to": "validate"},
        # the superseding artifact: a newer check result that passes
        {"do": "artifact", "path": "check.json", "content": '{"passed": true, "failed": []}',
         "kind": "validation_receipt", "passed": True},
        {"do": "observe", "tool": "bash", "output": "12 passed", "keep": True},
        {"do": "transition", "to": "done"},
    ]
    return steps


def run(root: Path) -> dict:
    proto = R.Prototype(root=root, goal=GOAL)
    steps, restarts = trace_steps(), []
    outcomes: list[dict] = []
    # The harness owns the metric series, so a restart does not erase it.
    series: list[dict] = []

    for index, step in enumerate(steps, start=1):
        kind = step["do"]
        requested: list[str] = []
        if kind == "observe":
            event = proto.observe(step["tool"], step["output"], keep_in_context=step["keep"])
        elif kind == "patch":
            event = proto.apply_patch({"base_revision": proto.revision, "ops": step["ops"]})
        elif kind == "stale_patch":
            event = proto.apply_patch({"base_revision": proto.revision - 1,
                                       "ops": [{"op": "append", "field": "next_actions", "value": "stale"}]})
        elif kind == "transition":
            event = proto.transition(step["to"])
        elif kind == "artifact":
            (root / step["path"]).write_text(step["content"])
            ref = proto.record_receipt(step["path"], step["kind"], step["passed"])
            event = proto.apply_patch({
                "base_revision": proto.revision,
                "ops": [{"op": "set", "field": "validated_artifact_refs", "value": [ref.to_dict()]}],
            })
        elif kind == "recall_decision":
            found = proto.history.search("DECISION: ledger.csv rows are never rewritten")
            if not found:
                raise RuntimeError("the archived decision is not recoverable from history")
            event = proto.recall(found[0]["id"])
            requested = [found[0]["id"]]
        elif kind == "restart":
            before = {"phase": proto.state["phase"], "goal": proto.state["goal"],
                      "next_actions": list(proto.state["next_actions"]),
                      "state_digest": proto.state_digest(),
                      "history_head": proto.history.head_digest(),
                      "history_events": len(proto.history.events),
                      "artifact_status": proto.artifact_status()}
            del proto
            proto = R.Prototype.restore(root)
            after = {"phase": proto.state["phase"], "goal": proto.state["goal"],
                     "next_actions": list(proto.state["next_actions"]),
                     "state_digest": proto.state_digest(),
                     "history_head": proto.history.head_digest(),
                     "history_events": len(proto.history.events),
                     "artifact_status": proto.artifact_status()}
            restarts.append({"step": index, "before": before, "after": after,
                             "identical": before == after})
            outcomes.append({"step": index, "do": kind, "event": "restart"})
            continue
        else:
            raise RuntimeError(f"unknown step {kind}")

        series.append(asdict(proto.record_step(index, event["id"], requested)))
        outcome = {"step": index, "do": kind, "event_type": event["type"], "event_id": event["id"]}
        if step.get("expect") == "rejected" and not event["type"].endswith("rejected"):
            raise RuntimeError(f"step {index} was expected to be rejected and was not")
        outcomes.append(outcome)

    # the old decision must still be recoverable and must NOT be sticky
    decision = proto.history.search("DECISION: ledger.csv rows are never rewritten")
    in_state = any("never rewritten in place" in f for f in proto.state["important_findings"])

    return {
        "goal": GOAL,
        "steps": len(steps),
        "outcomes": outcomes,
        "restarts": restarts,
        "final_phase": proto.state["phase"],
        "final_state": proto.state,
        "final_state_digest": proto.state_digest(),
        "history_events": len(proto.history.events),
        "history_head_digest": proto.history.head_digest(),
        "metrics": series,
        "counters": proto.counters,
        "archived_decision_recoverable": bool(decision),
        "archived_decision_still_in_active_state": in_state,
        "artifact_status": proto.artifact_status(),
    }, proto


def corruption_tests(root: Path, proto: R.Prototype) -> dict:
    """Every one of these must fail closed. A silent repair would be worse."""
    results: dict[str, dict] = {}

    def record(name: str, ok: bool, detail: str) -> None:
        results[name] = {"failed_closed": ok, "detail": detail}

    event = proto.transition("inspect")
    record("illegal_transition_from_done", event["type"] == "transition_rejected",
           event["payload"].get("reason", ""))

    (root / "check.json").write_text('{"passed": true, "failed": [], "tampered": true}')
    status = proto.artifact_status()
    record("artifact_mutation_invalidates_completion",
           all(not s["valid"] for s in status), json.dumps(status))
    gate_ok, why = proto._gate_satisfied("validation_receipt", None)
    record("done_gate_rejects_mutated_artifact", not gate_ok, why)

    event = proto.apply_patch({"base_revision": proto.revision - 3,
                               "ops": [{"op": "append", "field": "next_actions", "value": "x"}]})
    record("stale_revision_rejected", event["type"] == "state_patch_rejected",
           event["payload"].get("reason", ""))

    event = proto.apply_patch({"base_revision": proto.revision,
                               "ops": [{"op": "set", "field": "goal", "value": 17}]})
    record("type_violation_rejected", event["type"] == "state_patch_rejected",
           event["payload"].get("reason", ""))

    event = proto.apply_patch({"base_revision": proto.revision,
                               "ops": [{"op": "set", "field": "phase", "value": "done"}]})
    record("phase_change_via_patch_rejected", event["type"] == "state_patch_rejected",
           event["payload"].get("reason", ""))

    event = proto.apply_patch({"base_revision": proto.revision,
                               "ops": [{"op": "set", "field": "not_a_field", "value": 1}]})
    record("unknown_field_rejected", event["type"] == "state_patch_rejected",
           event["payload"].get("reason", ""))

    whole_history = C.canonical([e["payload"] for e in proto.history.events])
    event = proto.apply_patch({"base_revision": proto.revision,
                               "ops": [{"op": "set", "field": "goal", "value": whole_history}]})
    record("history_stuffed_into_state_rejected", event["type"] == "state_patch_rejected",
           event["payload"].get("reason", ""))

    try:
        proto.history.get("e999999")
        record("missing_history_reference_rejected", False, "no error raised")
    except R.HistoryError as exc:
        record("missing_history_reference_rejected", True, str(exc))

    tampered = root.parent / "tampered"
    if tampered.exists():
        shutil.rmtree(tampered)
    shutil.copytree(root, tampered)
    lines = (tampered / "history.ndjson").read_text().splitlines()
    victim = json.loads(lines[3])
    victim["payload"] = {"tool": "read", "output": "a quietly different past"}
    lines[3] = C.canonical(victim)
    (tampered / "history.ndjson").write_text("\n".join(lines) + "\n")
    try:
        R.Prototype.restore(tampered)
        record("tampered_history_detected", False, "restore accepted a tampered log")
    except R.HistoryError as exc:
        record("tampered_history_detected", True, str(exc))

    broken = root.parent / "broken"
    if broken.exists():
        shutil.rmtree(broken)
    broken.mkdir(parents=True)
    (broken / "history.ndjson").write_text("")
    try:
        R.Prototype.restore(broken)
        record("restart_without_persisted_state_rejected", False, "restore invented a state")
    except R.StateError as exc:
        record("restart_without_persisted_state_rejected", True, str(exc))

    results["all_failed_closed"] = all(r["failed_closed"] for r in results.values())
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--work", default="/private/tmp/pi-state-control-gen43")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(args.work) / "run"
    if work.parent.exists():
        shutil.rmtree(work.parent)
    work.mkdir(parents=True)

    fixture = trace_steps()
    (out / "synthetic_trace.json").write_text(json.dumps(
        {"goal": GOAL, "steps": fixture, "step_count": len(fixture),
         "fixture_digest": C.digest(fixture)}, indent=2, sort_keys=True) + "\n")

    result, proto = run(work)
    corruption = corruption_tests(work, proto)

    (out / "contract.json").write_text(json.dumps(C.contract_identity(), indent=2, sort_keys=True) + "\n")
    (out / "trace_metrics.json").write_text(json.dumps(
        {k: v for k, v in result.items() if k != "restarts"}, indent=2, sort_keys=True) + "\n")
    (out / "restart_recovery.json").write_text(json.dumps(
        {"restarts": result["restarts"],
         "archived_decision_recoverable": result["archived_decision_recoverable"],
         "archived_decision_still_in_active_state": result["archived_decision_still_in_active_state"]},
        indent=2, sort_keys=True) + "\n")
    (out / "corruption_tests.json").write_text(json.dumps(corruption, indent=2, sort_keys=True) + "\n")

    metrics = result["metrics"]
    print(json.dumps({
        "steps": result["steps"],
        "history_events": result["history_events"],
        "final_phase": result["final_phase"],
        "first_context_bytes": metrics[0]["composed_context_bytes"],
        "last_context_bytes": metrics[-1]["composed_context_bytes"],
        "last_history_bytes": metrics[-1]["history_bytes"],
        "last_state_bytes": metrics[-1]["state_bytes"],
        "restarts_identical": [r["identical"] for r in result["restarts"]],
        "corruption_all_failed_closed": corruption["all_failed_closed"],
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
