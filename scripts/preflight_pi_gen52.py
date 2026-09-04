#!/usr/bin/env python3
"""Gen52 pre-live gate. No model, no GPU, no network.

Proves, before any IP1-IP4 provider response, that arm E is arm C plus one
dormant termination policy: identical model-facing behaviour until it stops,
exact trigger semantics, the hidden verifier still excluded, and no tool killed
while it is still running.
"""
from __future__ import annotations

import argparse, hashlib, json, os, random, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import block_network            # noqa: E402
from memory_bakeoff.pi_state_control import pilot as P              # noqa: E402
from memory_bakeoff.pi_state_control import raw_evidence as R       # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen52"
EXT = ROOT / "extensions" / "pi_state_control"
ARM_C, ARM_E = EXT / "pi_pilot_harness_state.ts", EXT / "pi_pilot_quiescent.ts"
RUNNER = ROOT / "scripts" / "run_pi_pilot_gen52.py"
GEN52_ORDER_SEED = 20260909
GEN48 = ROOT / "results" / "pi_state_control_gen48"
ARM_NAMES = ["pi_harness_state_control_v1", "pi_harness_state_control_quiescent_k3_v1"]
BUN = Path.home() / ".bun" / "bin" / "bun"
PI_DIST = Path("/tmp/pi73/node_modules/@mariozechner/pi-coding-agent/dist")

PROBE = r'''
const PI_DIST = process.env.PI_DIST!;
const { loadExtensions } = await import(`${PI_DIST}/core/extensions/loader.js`);
const WORKTREE = process.env.PI_PILOT_WORKTREE!;
const { execFileSync } = await import("node:child_process");
const { writeFileSync } = await import("node:fs");

const load = async (path: string) => {
  const res = await loadExtensions([path], process.cwd());
  const ext = res.extensions?.[0];
  if (!ext) throw new Error(`no extension from ${path}`);
  return {
    context: (ext.handlers.get("context") ?? [])[0],
    call: (ext.handlers.get("tool_call") ?? [])[0],
    result: (ext.handlers.get("tool_result") ?? [])[0],
    request: (ext.handlers.get("before_provider_request") ?? [])[0],
  };
};

/** A scripted trace: each step is a tool call, its result, and an optional edit. */
async function drive(path: string, steps: any[]) {
  const h = await load(path);
  const aborts: number[] = [];
  const ctx = { abort: () => aborts.push(steps.length) };
  const composed: string[] = [];
  let index = 0;
  for (const step of steps) {
    for (const call of step.batch ?? [step]) {
      index += 1;
      await h.call?.({ toolName: call.tool, input: call.input ?? {} }, ctx);
    }
    for (const call of step.batch ?? [step]) {
      if (call.writes) writeFileSync(`${WORKTREE}/${call.writes.path}`, call.writes.text);
      await h.result?.({ toolName: call.tool, input: call.input ?? {},
                         result: { exitCode: call.exit ?? 0, output: call.output ?? "" },
                         isError: Boolean(call.exit) }, ctx);
    }
    if (step.request) {
      await h.request?.({ payload: { messages: [{ role: "user", content: "x" }] } }, ctx);
    }
    if (step.compose) {
      const out = await h.context?.({ messages: [
        { role: "user", content: [{ type: "text", text: "task" }] },
        { role: "assistant", content: [{ type: "text", text: `step ${index}` }] },
      ] }, ctx);
      composed.push(JSON.stringify(out));
    }
  }
  return { aborts: aborts.length, composed };
}

const scenario = JSON.parse(process.env.PROBE_STEPS!);
const out: any = {};
for (const [name, spec] of Object.entries<any>(scenario)) {
  out[name] = await drive(spec.arm === "E" ? process.env.ARM_E! : process.env.ARM_C!, spec.steps);
}
console.log(JSON.stringify(out));
'''

CHECK = "cd . && python -m pytest tests/ -q"
HIDDEN = "python /outside/verifier.py"


def worktree() -> Path:
    path = Path(tempfile.mkdtemp(prefix="gen52-probe-"))
    (path / "a.py").write_text("x = 1\n")
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "-c", "user.email=p@x.invalid", "-c", "user.name=p",
                    "commit", "-qm", "base"], cwd=path, check=True)
    return path


def step(tool="bash", command="", exit_code=0, writes=None, compose=False, request=False, batch=None):
    entry = {"tool": tool, "input": {"command": command} if command else {}, "exit": exit_code}
    if writes:
        entry["writes"] = writes
    if batch:
        entry = {"batch": batch}
    entry["compose"] = compose
    entry["request"] = request
    return entry


def mutation(name="a.py", text="x = 2\n"):
    return step(tool="edit", writes={"path": name, "text": text})


def run_probe(scenarios: dict, tree: Path) -> dict:
    # Both the probe script and the harness output live OUTSIDE the worktree.
    # They must: the tree digest is computed over the worktree, so a log file
    # written inside it would change the digest on every tool result and void
    # every receipt. Production already keeps `PI_PILOT_OUT` outside; this is
    # the same requirement, and the probe caught it the hard way.
    side = tree.parent / f"{tree.name}-side"
    side.mkdir(exist_ok=True)
    probe = side / "probe.ts"
    probe.write_text(PROBE)
    env = dict(os.environ, PI_DIST=str(PI_DIST), ARM_C=str(ARM_C), ARM_E=str(ARM_E),
               PI_PILOT_WORKTREE=str(tree), PI_PILOT_OUT=str(side / "out"),
               PROBE_STEPS=json.dumps(scenarios), PI_OFFLINE="1")
    done = subprocess.run([str(BUN), str(probe)], cwd=tree, env=env,
                          capture_output=True, text=True, timeout=180)
    if done.returncode != 0:
        raise SystemExit(f"probe failed: {done.stderr[-2000:]}")
    parsed = json.loads(done.stdout.strip().splitlines()[-1])
    summary = side / "out" / "quiescent_stop.json"
    for value in parsed.values():
        value["stop_summary"] = json.loads(summary.read_text()) if summary.exists() else None
    return parsed


def main() -> int:
    block_network()
    OUT.mkdir(parents=True, exist_ok=True)

    ordinary = [step(command="ls"), step(command="cat a.py")]
    passing = step(command=CHECK)

    scenarios = {
        # K semantics: a pass after a mutation, then 1, 2, 3 ordinary completions.
        "k1": {"arm": "E", "steps": [*ordinary, mutation(), passing, step(command="ls")]},
        "k2": {"arm": "E", "steps": [*ordinary, mutation(), passing, step(command="ls"), step(command="ls")]},
        "k3": {"arm": "E", "steps": [*ordinary, mutation(), passing,
                                     step(command="ls"), step(command="ls"), step(command="ls")]},
        # a mutation after the pass resets the count
        "mutation_resets": {"arm": "E", "steps": [mutation(), passing, step(command="ls"),
                                                  mutation("a.py", "x = 3\n"),
                                                  step(command="ls"), step(command="ls"), step(command="ls")]},
        # a failing visible check clears eligibility
        "fail_resets": {"arm": "E", "steps": [mutation(), passing,
                                              step(command=CHECK, exit_code=1),
                                              step(command="ls"), step(command="ls"), step(command="ls")]},
        # a pass before any mutation is not eligible at all
        "pass_before_mutation": {"arm": "E", "steps": [passing, step(command="ls"),
                                                       step(command="ls"), step(command="ls")]},
        # a new pass after a later mutation re-arms
        "rearm": {"arm": "E", "steps": [mutation(), passing, mutation("a.py", "x = 4\n"),
                                        step(command="ls"), step(command="ls"), step(command="ls"),
                                        passing, step(command="ls"), step(command="ls"), step(command="ls")]},
        # the hidden verifier is not a visible check
        "hidden_excluded": {"arm": "E", "steps": [mutation(), step(command=HIDDEN),
                                                  step(command="ls"), step(command="ls"), step(command="ls")]},
        # a batch still running when the trigger is reached is not killed
        "batch_overshoot": {"arm": "E", "steps": [
            mutation(), passing, step(command="ls"),
            {"batch": [{"tool": "bash", "input": {"command": "ls"}, "exit": 0},
                       {"tool": "bash", "input": {"command": "ls"}, "exit": 0},
                       {"tool": "bash", "input": {"command": "ls"}, "exit": 0}],
             "compose": False, "request": False}]},
        # model-facing identity: the same trace through C and through E
        "identity_C": {"arm": "C", "steps": [step(command="ls", compose=True), mutation(),
                                             {**passing, "compose": True}, step(command="ls", compose=True)]},
        "identity_E": {"arm": "E", "steps": [step(command="ls", compose=True), mutation(),
                                             {**passing, "compose": True}, step(command="ls", compose=True)]},
    }

    results = {}
    for name, spec in scenarios.items():
        tree = worktree()
        results[name] = run_probe({name: spec}, tree)[name]

    triggered = {name: bool(value["aborts"]) for name, value in results.items()}
    identity = results["identity_C"]["composed"] == results["identity_E"]["composed"]

    report = {
        "contract": "quiescent-completion-toolcall-k3-v1",
        "k": 3,
        "k_source": "Gen51 offline calibration, smallest tested K with zero observed progress truncations",
        "arm_hashes": {
            "pi_harness_state_control_v1": hashlib.sha256(ARM_C.read_bytes()).hexdigest(),
            "pi_harness_state_control_quiescent_k3_v1": hashlib.sha256(ARM_E.read_bytes()).hexdigest()},
        "e_generated_from_c": "GENERATED from" in ARM_E.read_text(),
        "trigger_semantics": {
            "k1_does_not_stop": triggered["k1"] is False,
            "k2_does_not_stop": triggered["k2"] is False,
            "k3_stops": triggered["k3"] is True,
            "mutation_resets_the_count": triggered["mutation_resets"] is False,
            "failing_visible_check_resets": triggered["fail_resets"] is False,
            "pass_before_any_mutation_is_ineligible": triggered["pass_before_mutation"] is False,
            "new_pass_after_mutation_rearms": triggered["rearm"] is True,
        },
        "hidden_verifier_excluded": triggered["hidden_excluded"] is False,
        "no_in_flight_tool_killed": {
            "batch_stop_deferred_to_batch_drain": triggered["batch_overshoot"] is True,
            "aborted_exactly_once": results["batch_overshoot"]["aborts"] == 1,
            # The trigger was reached while a sibling call was still outstanding,
            # and the stop waited for it. `trigger_tool_index` cannot show this on
            # its own: it counts calls, and a batch issues all of its calls before
            # any of them returns. The overshoot count is the evidence.
            "stop_deferred_until_batch_drained": ((results["batch_overshoot"]["stop_summary"] or {})
                                                  .get("same_batch_overshoot_calls") or 0) >= 1,
            "same_batch_overshoot_calls": (results["batch_overshoot"]["stop_summary"] or {}).get(
                "same_batch_overshoot_calls"),
        },
        "stop_summaries": {name: results[name]["stop_summary"]
                           for name in ("k3", "rearm", "batch_overshoot", "k2")},
        "model_facing_identity": {
            "composed_context_identical": identity,
            "compositions_compared": len(results["identity_C"]["composed"]),
        },
        "raw_evidence_retention": {
            "contract_sha256": R.contract()["contract_sha256"],
            # Gate 6: the retention path must be invisible to the model and must
            # not touch the task worktree while the run is in progress.
            "archive_root": str(Path.home() / "gen52-raw-archive"),
            "archive_is_outside_the_repository":
                not str(Path.home() / "gen52-raw-archive").startswith(str(ROOT)),
            "archive_is_outside_every_worktree":
                not str(Path.home() / "gen52-raw-archive").startswith(str(Path.home() / "pilot-gen45-work")),
            "archiving_happens_after_the_pi_process_exits":
                RUNNER.read_text().index("archive_stream") > RUNNER.read_text().index("subprocess.run(pi_command"),
            "no_extension_writes_into_the_archive":
                "gen52-raw-archive" not in ARM_C.read_text() and "gen52-raw-archive" not in ARM_E.read_text(),
        },
        "order_seed": GEN52_ORDER_SEED,
        "raw_triggers": triggered,
    }
    report["passed"] = (
        report["e_generated_from_c"]
        and all(report["trigger_semantics"].values())
        and report["hidden_verifier_excluded"]
        and report["no_in_flight_tool_killed"]["batch_stop_deferred_to_batch_drain"]
        and report["no_in_flight_tool_killed"]["aborted_exactly_once"]
        and report["no_in_flight_tool_killed"]["stop_deferred_until_batch_drained"]
        and report["model_facing_identity"]["composed_context_identical"]
        and all(value for key, value in report["raw_evidence_retention"].items()
                if isinstance(value, bool)))
    # The ruler is Gen48's, byte-for-byte. Nothing here may create a new one.
    manifest = json.loads((GEN48 / "task_manifest.json").read_text())
    report["ruler"] = {"source": "results/pi_state_control_gen48/task_manifest.json",
                       "manifest_digest": manifest["manifest_digest"],
                       "tasks": sorted(manifest["tasks"]),
                       "unchanged": sorted(manifest["tasks"]) == ["IP1", "IP2", "IP3", "IP4"]}
    report["passed"] = report["passed"] and report["ruler"]["unchanged"]

    pairs = [{"task": task, "repetition": rep}
             for task in sorted(manifest["tasks"]) for rep in (1, 2, 3)]
    random.Random(GEN52_ORDER_SEED).shuffle(pairs)
    order = []
    for index, pair in enumerate(pairs):
        arms = list(ARM_NAMES)
        if index % 2:
            arms.reverse()
        for position, arm in enumerate(arms):
            order.append({"index": len(order) + 1, "task": pair["task"],
                          "repetition": pair["repetition"], "arm": arm,
                          "position_in_pair": position + 1})
    (OUT / "gen52_order_manifest.json").write_text(json.dumps(
        {"seed": GEN52_ORDER_SEED, "arms": ARM_NAMES, "runs": len(order), "order": order},
        indent=2, sort_keys=True) + "\n")

    (OUT / "preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in ("trigger_semantics", "hidden_verifier_excluded",
                                             "no_in_flight_tool_killed", "model_facing_identity",
                                             "passed")}, indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
