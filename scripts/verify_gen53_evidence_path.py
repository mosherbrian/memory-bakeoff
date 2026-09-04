#!/usr/bin/env python3
"""Gen53 Part A: prove the quiescence snapshot survives an abrupt kill, and that
the TypeScript arm and the Python rule decide identically. No model, no network.
"""
from __future__ import annotations

import json, os, signal, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import quiescent_v2 as Q   # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen53"
ARM_V2 = ROOT / "extensions/pi_state_control/pi_pilot_quiescent_v2.ts"
BUN = Path.home() / ".bun" / "bin" / "bun"
PI_DIST = Path("/tmp/pi73/node_modules/@mariozechner/pi-coding-agent/dist")

ABRUPT = '''
const PI_DIST = process.env.PI_DIST!;
const { loadExtensions } = await import(`${PI_DIST}/core/extensions/loader.js`);
const { writeFileSync } = await import("node:fs");
const WORKTREE = process.env.PI_PILOT_WORKTREE!;
const ext = (await loadExtensions([process.env.ARM_V2!], process.cwd())).extensions?.[0]!;
const call = (ext.handlers.get("tool_call") ?? [])[0];
const result = (ext.handlers.get("tool_result") ?? [])[0];
const ctx = { abort: () => {} };
const CHECK = `cd ${WORKTREE} && python -m pytest tests/ -q`;
await call({ toolName: "edit", input: {} }, ctx);
writeFileSync(`${WORKTREE}/a.py`, "x = 2\\n");
await result({ toolName: "edit", input: {}, result: { exitCode: 0 } }, ctx);
await call({ toolName: "bash", input: { command: CHECK } }, ctx);
await result({ toolName: "bash", input: { command: CHECK }, result: { exitCode: 0 } }, ctx);
for (let i = 0; i < 500; i++) {
  await call({ toolName: "bash", input: { command: "ls" } }, ctx);
  await result({ toolName: "bash", input: { command: "ls" }, result: { exitCode: 0 } }, ctx);
  await new Promise((r) => setTimeout(r, 20));
}
'''

EQUIVALENCE = '''
const { QuiescentStopV2 } = await import(process.env.ARM_V2!);
const traces = JSON.parse(process.env.TRACES!);
const out: any = {};
let ev = 0;
for (const [name, steps] of Object.entries<any>(traces)) {
  const s = new QuiescentStopV2();
  s.initialTree = "tree-initial"; s.currentTree = "tree-initial";
  const stops: number[] = [];
  for (const step of steps) {
    const batch = Array.isArray(step[0]) ? step : [step];
    for (const [tool] of batch) s.observeCall(tool);
    for (const [, command, tree, isCheck, passed] of batch) {
      const validation = isCheck ? { command, passed, tree_digest: tree, event: `e${ev++}` } : {};
      if (s.observeResult(validation, tree)) stops.push(s.toolIndex);
    }
  }
  out[name] = { stops, snapshot: s.snapshot() };
}
console.log(JSON.stringify(out));
'''

CHECK, OTHER, HIDDEN = "cd . && python -m pytest tests/ -q", "python run_checks.py", "python /outside/verifier.py"
T0, TA, TB = "tree-initial", "tree-A", "tree-B"
FIELDS = ("initial_tree_digest", "current_tree_digest", "net_tree_changed", "valid_receipt_tree",
          "idle_count", "eligible", "became_eligible", "mutations",
          "same_tree_passes_counted_idle", "triggered", "trigger_tool_index",
          "effective_stop_tool_index", "same_batch_overshoot_calls", "tool_index")


def worktree() -> Path:
    tree = Path(tempfile.mkdtemp(prefix="gen53-evidence-"))
    (tree / "a.py").write_text("x = 1\n")
    for command in (["git", "init", "-q"], ["git", "add", "-A"],
                    ["git", "-c", "user.email=p@x.invalid", "-c", "user.name=p",
                     "commit", "-qm", "base"]):
        subprocess.run(command, cwd=tree, check=True)
    return tree


def abrupt_termination() -> dict:
    tree = worktree()
    side = tree.parent / f"{tree.name}-side"
    side.mkdir()
    probe = side / "abrupt.ts"
    probe.write_text(ABRUPT)
    env = dict(os.environ, PI_DIST=str(PI_DIST), ARM_V2=str(ARM_V2),
               PI_PILOT_WORKTREE=str(tree), PI_PILOT_OUT=str(side / "out"), PI_OFFLINE="1")
    process = subprocess.Popen([str(BUN), str(probe)], env=env, cwd=tree,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    time.sleep(4)
    process.send_signal(signal.SIGKILL)      # the harshest termination available
    process.wait(timeout=30)
    path = side / "out" / "quiescent_stop.json"
    if not path.exists():
        return {"snapshot_exists": False}
    snapshot = json.loads(path.read_text())
    return {
        "killed_with": "SIGKILL", "snapshot_exists": True, "snapshot_parses": True,
        "internally_consistent": (snapshot["contract"] == Q.CONTRACT_VERSION
                                  and isinstance(snapshot["idle_count"], int)
                                  and snapshot["tool_index"] >= snapshot["idle_count"]
                                  and bool(snapshot["initial_tree_digest"])
                                  and bool(snapshot["current_tree_digest"])),
        "initial_tree_recorded_before_first_action":
            snapshot["initial_tree_digest"] != snapshot["current_tree_digest"],
        "no_partial_files_left": not list((side / "out").glob(".quiescent_stop.json.*")),
        "fields": sorted(snapshot), "snapshot": snapshot,
    }


def annotate(step):
    if isinstance(step[0], list):
        return [annotate(inner) for inner in step]
    tool, command, tree = step
    check = Q.is_visible_check(command)
    return [tool, command, tree, check,
            (not command.endswith("#fail")) if check else None]


def equivalence() -> dict:
    def bash(command, tree): return ["bash", command, tree]
    def edit(tree): return ["edit", "", tree]
    traces = {
        "ordinary": [edit(TA), bash(CHECK, TA), bash("ls", TA), bash("ls", TA), bash("ls", TA)],
        "repeat_pass_loop": [edit(TA), bash(CHECK, TA), bash(CHECK, TA), bash(CHECK, TA), bash(CHECK, TA)],
        "other_check_same_tree": [edit(TA), bash(CHECK, TA), bash(OTHER, TA), bash(OTHER, TA), bash(OTHER, TA)],
        "revert_to_start": [edit(TA), edit(T0), bash(CHECK, T0)] + [bash("ls", T0)] * 12,
        "pass_before_mutation": [bash(CHECK, T0), bash("ls", T0), bash("ls", T0), bash("ls", T0)],
        "mutation_after_receipt": [edit(TA), bash(CHECK, TA), bash("ls", TA), edit(TB),
                                   bash("ls", TB), bash("ls", TB)],
        "fail_then_pass": [edit(TA), bash(CHECK + "#fail", TA), bash(CHECK, TA),
                           bash("ls", TA), bash("ls", TA), bash("ls", TA)],
        "second_tree": [edit(TA), bash(CHECK, TA), edit(TB), bash(CHECK, TB),
                        bash("ls", TB), bash("ls", TB), bash("ls", TB)],
        "batch": [edit(TA), bash(CHECK, TA), bash("ls", TA),
                  [bash("ls", TA), bash("ls", TA), bash("ls", TA)]],
        "hidden": [edit(TA), bash(HIDDEN, TA), bash("ls", TA), bash("ls", TA), bash("ls", TA)],
    }
    traces = {name: [annotate(step) for step in steps] for name, steps in traces.items()}

    expected = {}
    for name, steps in traces.items():
        rule = Q.QuiescentV2(k=3)
        rule.initial_tree, rule.current_tree = T0, T0
        stops = []
        for step in steps:
            batch = step if isinstance(step[0], list) else [step]
            for tool, *_ in batch:
                rule.observe_call(tool)
            for _tool, _command, tree, check, passed in batch:
                if rule.observe_result(passed=passed, tree=tree, fresh_check=check):
                    stops.append(rule.tool_index)
        expected[name] = {"stops": stops, "snapshot": rule.snapshot()}

    side = Path(tempfile.mkdtemp(prefix="gen53-equiv-"))
    probe = side / "equivalence.ts"
    probe.write_text(EQUIVALENCE)
    env = dict(os.environ, ARM_V2=str(ARM_V2), TRACES=json.dumps(traces), PI_OFFLINE="1")
    done = subprocess.run([str(BUN), str(probe)], env=env, capture_output=True, text=True, timeout=120)
    if done.returncode:
        return {"error": done.stderr[-1500:]}
    actual = json.loads(done.stdout.strip().splitlines()[-1])

    disagreements = []
    for name in traces:
        if expected[name]["stops"] != actual[name]["stops"]:
            disagreements.append({"trace": name, "field": "stops",
                                  "python": expected[name]["stops"], "typescript": actual[name]["stops"]})
        for field in FIELDS:
            if expected[name]["snapshot"].get(field) != actual[name]["snapshot"].get(field):
                disagreements.append({"trace": name, "field": field,
                                      "python": expected[name]["snapshot"].get(field),
                                      "typescript": actual[name]["snapshot"].get(field)})
    return {"traces": sorted(traces), "fields_compared": list(FIELDS),
            "disagreements": disagreements, "agree": not disagreements}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"abrupt_termination": abrupt_termination(), "typescript_python_equivalence": equivalence()}
    abrupt = report["abrupt_termination"]
    report["passed"] = bool(
        abrupt.get("snapshot_exists") and abrupt.get("internally_consistent")
        and abrupt.get("initial_tree_recorded_before_first_action")
        and abrupt.get("no_partial_files_left")
        and report["typescript_python_equivalence"].get("agree"))
    (OUT / "evidence_path_and_equivalence.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"abrupt": {k: v for k, v in abrupt.items() if k not in ("snapshot", "fields")},
                      "equivalence": {"traces": len(report["typescript_python_equivalence"].get("traces", [])),
                                      "disagreements": report["typescript_python_equivalence"].get("disagreements")},
                      "passed": report["passed"]}, indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
