#!/usr/bin/env python3
"""Gen48 preflight: prove arm D and the intent-persistence ruler, with no model."""
from __future__ import annotations

import argparse, hashlib, json, os, random, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import BlockedNetwork, block_network  # noqa: E402
from memory_bakeoff.pi_state_control import harness_state as H  # noqa: E402
from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen48"
GEN47 = ROOT / "results" / "pi_state_control_gen47"
EXT = ROOT / "extensions" / "pi_state_control"
ARM_C, ARM_D = EXT / "pi_pilot_harness_state.ts", EXT / "pi_pilot_task_floor.ts"
GEN49_ORDER_SEED = 20260907
BUN = Path.home() / ".bun" / "bin" / "bun"

FLOOR_PROBE = r'''
const PI_DIST = process.env.PI_DIST!;
const { loadExtensions } = await import(`${PI_DIST}/core/extensions/loader.js`);
const TASK = process.env.PROBE_TASK!;
function transcript(turns: number) {
  const msgs: any[] = [{ role: "user", content: [{ type: "text", text: TASK }] }];
  for (let i = 0; i < turns; i++) {
    msgs.push({ role: "assistant", content: [{ type: "text", text: `step ${i}` }] });
    msgs.push({ role: "toolResult", content: [{ type: "text", text: `out ${i}` }] });
    if (i > 0) msgs.push({ role: "user", content: [{ type: "text", text: `follow up ${i}` }] });
  }
  return msgs;
}
const run = async (path: string, turnsList: number[]) => {
  const res = await loadExtensions([path], process.cwd());
  const ext = res.extensions?.[0];
  const handlers = ext?.handlers.get("context") ?? [];
  const out: any[] = [];
  for (const turns of turnsList) {
    let r: any;
    for (const fn of handlers) r = await fn({ type: "context", messages: transcript(turns) }, {});
    out.push(JSON.stringify(r?.messages ?? []));
  }
  return { errors: res.errors ?? [], out,
           tools: [...(ext?.tools?.keys() ?? [])].sort() };
};
const turnsList = JSON.parse(process.env.PROBE_TURNS!);
process.env.PI_PILOT_OUT = "/tmp/gen48-c";
const c = await run(process.env.ARM_C!, turnsList);
process.env.PI_PILOT_OUT = "/tmp/gen48-d";
const d = await run(process.env.ARM_D!, turnsList);
console.log(JSON.stringify({
  c_errors: c.errors, d_errors: d.errors, c_tools: c.tools, d_tools: d.tools,
  rows: turnsList.map((t: number, i: number) => ({
    turns: t, identical: c.out[i] === d.out[i],
    c_bytes: c.out[i].length, d_bytes: d.out[i].length,
    d_floor: d.out[i].includes("human_direction"),
    c_carries_task: c.out[i].includes(TASK),
    d_carries_task_verbatim: d.out[i].includes(TASK),
  })),
}));
'''


def bun_probe(task_text: str, turns: list[int]) -> dict:
    work = Path("/tmp/gen48-probe"); work.mkdir(parents=True, exist_ok=True)
    (work / "probe.ts").write_text(FLOOR_PROBE)
    env = {**os.environ,
           "PI_DIST": str(Path.home() / ".bun/install/global/node_modules/@mariozechner/pi-coding-agent/dist"),
           "ARM_C": str(ARM_C.resolve()), "ARM_D": str(ARM_D.resolve()),
           "PROBE_TASK": task_text, "PROBE_TURNS": json.dumps(turns)}
    proc = subprocess.run([str(BUN), "run", str(work / "probe.ts")], capture_output=True,
                          text=True, env=env, cwd=str(work))
    if proc.returncode != 0:
        return {"error": proc.stderr[-400:]}
    return json.loads(proc.stdout)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((OUT / "task_manifest.json").read_text())
    checks: dict = {}

    task_text = manifest["tasks"]["IP2"]["prompt"]
    probe = bun_probe(task_text, [1, 2, 3, 4, 6, 10, 40, 100])
    rows = probe.get("rows", [])
    pre = [r for r in rows if r["c_carries_task"]]
    post = [r for r in rows if not r["c_carries_task"]]

    checks["arm_equality_before_activation"] = {
        "requests_checked": len(pre),
        "all_identical": bool(pre) and all(r["identical"] for r in pre),
        "no_early_floor": not any(r["d_floor"] for r in pre),
    }
    checks["floor_activation"] = {
        "activates_exactly_when_the_window_drops_the_task": bool(post) and all(r["d_floor"] for r in post),
        "never_deactivates": all(r["d_floor"] for r in post),
        "verbatim_after_activation": all(r["d_carries_task_verbatim"] for r in post),
        "c_never_carries_it_after": not any(r["c_carries_task"] for r in post),
        "floor_bytes_added": (post[0]["d_bytes"] - post[0]["c_bytes"]) if post else None,
        "checked_up_to_turns": max((r["turns"] for r in rows), default=0),
    }
    checks["same_tool_surface"] = {
        "c_tools": probe.get("c_tools"), "d_tools": probe.get("d_tools"),
        "identical": probe.get("c_tools") == probe.get("d_tools"),
        "neither_offers_state_control_tools": not (probe.get("c_tools") or probe.get("d_tools")),
    }
    checks["load_errors"] = {"c": probe.get("c_errors"), "d": probe.get("d_errors"),
                             "none": not probe.get("c_errors") and not probe.get("d_errors")}

    # D is generated from C, so the derivation cannot drift; prove it on an event log
    events = [
        {"type": "tool_call", "id": "e000001", "tool": "read", "args": {"path": "a.py"}},
        {"type": "tool_call", "id": "e000002", "tool": "read", "args": {"path": "b.py"}},
        {"type": "tool_call", "id": "e000003", "tool": "edit", "args": {"path": "a.py"}},
        {"type": "tool_result", "id": "e000004", "command": "python -m pytest", "exit_code": 0,
         "tree_digest": "t1"},
        {"type": "session_end", "id": "e000005"},
    ]
    checks["derivation_unchanged"] = {
        "replay_digest": H.replay_digest(events),
        "d_generated_from_c": "generated from" in ARM_D.read_text().lower(),
        "same_derivation_version": "harness-state-v1" in ARM_D.read_text(),
    }

    checks["tasks"] = {
        "count": len(manifest["tasks"]),
        "all_fail_before_and_pass_after": manifest["all_tasks_fail_before_and_pass_after"],
        "incomplete_visible_check_is_real": manifest["incomplete_visible_check_is_real"],
        "prompts_within_cap": all(t["prompt_bytes"] <= 4096 for t in manifest["tasks"].values()),
        "every_task_has_two_public_requirements": all(
            set(t["requirements"]) == {"A", "B"} for t in manifest["tasks"].values()),
        "ip1_visible_check_contradicts_the_new_instruction": (
            manifest["tasks"]["IP1"]["solvable"]["visible_check_passes_after_reference_fix"] is False),
        "note": ("IP1's shipped test encodes the OLD firmware ratio, so a correct fix makes it "
                 "fail until the agent updates it. That is realistic and deliberate, and it means "
                 "IP1 cannot reach control-valid done without touching the visible test - recorded "
                 "here so it is not discovered as a surprise later"),
    }

    verifier_paths = [ROOT / t["verifier_path"] for t in manifest["tasks"].values()]
    repo_paths = [ROOT / t["repo_path"] for t in manifest["tasks"].values()]
    checks["task_isolation"] = {
        "verifier_never_inside_repo": all(
            not v.resolve().is_relative_to(r.resolve()) for v, r in zip(verifier_paths, repo_paths)),
        "verifier_not_named_in_any_prompt": not any(
            "verifier" in t["prompt"].lower() for t in manifest["tasks"].values()),
        "no_fixture_mentions_the_verifier": not any(
            "verifier" in p.read_text(errors="ignore")
            for r in repo_paths for p in r.rglob("*") if p.is_file()),
    }

    checks["arm_c_unchanged_from_gen47"] = {
        "gen47_recorded": json.loads((GEN47 / "preflight_bindings.json").read_text())["extension_hashes"]["arm_c_now"],
        "current": sha(ARM_C),
        "identical": sha(ARM_C) == json.loads(
            (GEN47 / "preflight_bindings.json").read_text())["extension_hashes"]["arm_c_now"],
    }
    checks["arm_d_hash"] = sha(ARM_D)

    import socket
    block_network()
    try:
        socket.create_connection(("127.0.0.2", 8080), timeout=0.2)
        checks["no_network"] = {"outbound_blocked": False}
    except (BlockedNetwork, OSError) as exc:
        checks["no_network"] = {"outbound_blocked": True, "detail": str(exc)[:120]}

    passed = (
        checks["arm_equality_before_activation"]["all_identical"]
        and checks["arm_equality_before_activation"]["no_early_floor"]
        and checks["floor_activation"]["activates_exactly_when_the_window_drops_the_task"]
        and checks["floor_activation"]["verbatim_after_activation"]
        and checks["same_tool_surface"]["identical"]
        and checks["load_errors"]["none"]
        and checks["tasks"]["all_fail_before_and_pass_after"]
        and checks["tasks"]["incomplete_visible_check_is_real"]
        and checks["tasks"]["prompts_within_cap"]
        and all(checks["task_isolation"].values())
        and checks["arm_c_unchanged_from_gen47"]["identical"]
        and checks["no_network"]["outbound_blocked"]
    )
    checks["passed"] = passed

    pairs = [{"task": t, "repetition": r} for t in sorted(manifest["tasks"]) for r in (1, 2, 3)]
    rng = random.Random(GEN49_ORDER_SEED)
    rng.shuffle(pairs)
    order = []
    for index, pair in enumerate(pairs):
        arms = ["pi_harness_state_control_v1", "pi_harness_state_control_task_floor_v1"]
        if index % 2:
            arms.reverse()
        for position, arm in enumerate(arms):
            order.append({"index": len(order) + 1, "task": pair["task"],
                          "repetition": pair["repetition"], "arm": arm,
                          "position_in_pair": position + 1})

    (OUT / "preflight.json").write_text(json.dumps(checks, indent=2, sort_keys=True, default=str) + "\n")
    (OUT / "gen49_order_manifest.json").write_text(json.dumps(
        {"seed": GEN49_ORDER_SEED,
         "arms": ["pi_harness_state_control_v1", "pi_harness_state_control_task_floor_v1"],
         "runs": len(order), "order": order}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"passed": passed,
                      "equality_before": checks["arm_equality_before_activation"],
                      "floor": checks["floor_activation"],
                      "arm_c_unchanged": checks["arm_c_unchanged_from_gen47"]["identical"]}, indent=1))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
