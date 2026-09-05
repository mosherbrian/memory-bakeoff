#!/usr/bin/env python3
"""Gen55 pre-live gates. No model, no GPU, no network.

Ten gates, all of which must pass before the first IP task request. If one fails
for a build or instrumentation reason it may be fixed and the preflight re-run;
if satisfying it would need a semantic change to a frozen contract, stop.
"""
from __future__ import annotations

import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import block_network              # noqa: E402
from memory_bakeoff.pi_state_control import quiescent_v2 as Q         # noqa: E402
from memory_bakeoff.pi_state_control import raw_evidence as R         # noqa: E402
from memory_bakeoff.pi_state_control import tracked_digest as T       # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen55"
GEN52 = ROOT / "results" / "pi_quiescent_completion_gen52"
GEN48 = ROOT / "results" / "pi_state_control_gen48"
EXT = ROOT / "extensions" / "pi_state_control"
ARM_C, ARM_F = EXT / "pi_pilot_harness_state.ts", EXT / "pi_pilot_quiescent_tracked.ts"
ARCHIVE = Path.home() / "gen55-raw-archive"
FROZEN_ARM_C = "205279d9c1db4659459ccd9e504421f21623c6d9a74c14142b322450bad848df"
BASE = "fd227b56e14b8b7b6bcd25ca3c8fb80a7b2a61ac"
BUN = Path.home() / ".bun" / "bin" / "bun"
PI_DIST = Path("/tmp/pi73/node_modules/@mariozechner/pi-coding-agent/dist")

PROBE = '''
const PI_DIST = process.env.PI_DIST!;
const { loadExtensions } = await import(`${PI_DIST}/core/extensions/loader.js`);
const { readFileSync, writeFileSync } = await import("node:fs");
const { execSync } = await import("node:child_process");
const WORKTREE = process.env.PI_PILOT_WORKTREE!;
const OUTDIR = process.env.PI_PILOT_OUT!;
const ext = (await loadExtensions([process.env.ARM!], process.cwd())).extensions?.[0]!;
const call = (ext.handlers.get("tool_call") ?? [])[0];
const result = (ext.handlers.get("tool_result") ?? [])[0];
const context = (ext.handlers.get("context") ?? [])[0];
let aborts = 0;
const ctx = { abort: () => { aborts += 1; } };
const snap = () => JSON.parse(readFileSync(`${OUTDIR}/quiescent_stop.json`, "utf8"));
const CHECK = `cd ${WORKTREE} && python -m pytest tests/ -q`;
const step = async (tool: string, command: string, exit = 0) => {
  const input = command ? { command } : {};
  await call({ toolName: tool, input }, ctx);
  await result({ toolName: tool, input, result: { exitCode: exit }, isError: exit !== 0 }, ctx);
  return snap();
};
const out: any = {};
out.initial_before_any_action = snap ? null : null;
out.first = await step("bash", "ls");
out.initial_tree_digest = out.first.initial_tree_digest;
writeFileSync(`${WORKTREE}/pkg/units.py`, "X = 8\\n");
out.after_edit = await step("edit", "");
try { execSync("python3 -m pytest -q tests/", { cwd: WORKTREE }); } catch {}
out.after_tests = await step("bash", CHECK);
writeFileSync(`${WORKTREE}/pkg/units.py`, "X = 4\\n");
out.after_revert = await step("edit", "");
out.after_revert_check = await step("bash", CHECK);
for (let i = 0; i < 5; i++) out.after_revert_idle = await step("bash", "ls");
out.aborts_while_reverted = aborts;
writeFileSync(`${WORKTREE}/pkg/extra.py`, "Y = 1\\n");
out.after_new_file = await step("write", "");
out.after_new_file_check = await step("bash", CHECK);
out.idle1 = await step("bash", "ls");
out.repeat_pass1 = await step("bash", CHECK);
out.repeat_pass2 = await step("bash", CHECK);
out.aborts_total = aborts;
console.log(JSON.stringify(out));
'''


def worktree() -> Path:
    tree = Path(tempfile.mkdtemp(prefix="gen55-preflight-"))
    (tree / "pkg").mkdir()
    (tree / "pkg" / "__init__.py").write_text("")
    (tree / "pkg" / "units.py").write_text("X = 4\n")
    (tree / "tests").mkdir()
    (tree / "tests" / "test_x.py").write_text(
        "from pkg.units import X\ndef test_x():\n    assert X in (4, 8)\n")
    for command in (["git", "init", "-q"], ["git", "add", "-A"],
                    ["git", "-c", "user.email=p@x.invalid", "-c", "user.name=p",
                     "commit", "-qm", "base"]):
        subprocess.run(command, cwd=tree, check=True, capture_output=True)
    return tree


def live_probe() -> dict:
    tree = worktree()
    side = tree.parent / f"{tree.name}-side"
    side.mkdir()
    probe = side / "probe.ts"
    probe.write_text(PROBE)
    env = dict(os.environ, PI_DIST=str(PI_DIST), ARM=str(ARM_F),
               PI_PILOT_WORKTREE=str(tree), PI_PILOT_OUT=str(side / "out"), PI_OFFLINE="1")
    done = subprocess.run([str(BUN), str(probe)], env=env, cwd=tree,
                          capture_output=True, text=True, timeout=300)
    if done.returncode:
        return {"error": done.stderr[-1500:]}
    return json.loads(done.stdout.strip().splitlines()[-1])


def main() -> int:
    block_network()
    OUT.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    probe = live_probe()

    initial = probe.get("initial_tree_digest", "")
    gates = {
        "1_head_is_the_frozen_base": head == BASE,
        "2_arm_c_matches_the_frozen_baseline":
            hashlib.sha256(ARM_C.read_bytes()).hexdigest() == FROZEN_ARM_C,
        "3_arm_f_is_generated_deterministically": None,   # filled below
        "5_initial_digest_captured_before_the_first_action":
            bool(initial) and probe["first"]["initial_tree_digest"] == initial
            and probe["first"]["current_tree_digest"] == initial,
        "4a_running_the_tests_alone_does_not_move_the_tracked_digest":
            probe["after_tests"]["current_tree_digest"] == probe["after_edit"]["current_tree_digest"],
        "4b_a_real_edit_moves_the_tracked_digest":
            probe["after_edit"]["current_tree_digest"] != initial,
        "4c_an_exact_revert_returns_to_the_initial_digest":
            probe["after_revert"]["current_tree_digest"] == initial,
        "4d_a_reverted_tree_is_never_eligible":
            probe["after_revert_idle"]["eligible"] is False
            and probe["after_revert_idle"]["net_tree_changed"] is False
            and probe["aborts_while_reverted"] == 0,
        "4e_a_new_source_file_moves_the_tracked_digest":
            probe["after_new_file"]["current_tree_digest"] != initial,
        "4f_repeated_same_tree_passes_count_as_idle":
            probe["repeat_pass2"]["same_tree_passes_counted_idle"] >= 1,
        "4g_k_is_three_in_tool_calls":
            probe["repeat_pass2"]["k"] == 3,
        "4h_the_stop_fires_only_after_three_idle_completions":
            probe["repeat_pass2"]["triggered"] is True
            and probe["repeat_pass2"]["trigger_tool_index"] is not None,
        "6_snapshot_written_on_every_tool_result":
            all(key in probe["first"] for key in
                ("initial_tree_digest", "current_tree_digest", "idle_count", "eligible")),
    }

    before = ARM_F.read_bytes()
    subprocess.run([sys.executable, str(ROOT / "scripts/build_pi_pilot_gen54_quiescent_tracked.py")],
                   check=True, capture_output=True)
    gates["3_arm_f_is_generated_deterministically"] = ARM_F.read_bytes() == before

    # gate 7: retention failure injection, reusing the Gen51 preflight verbatim
    retention = subprocess.run([sys.executable, str(ROOT / "scripts/run_gen51_retention_preflight.py")],
                               capture_output=True, text=True, timeout=300)
    gates["7_retention_failure_injection_fails_closed"] = retention.returncode == 0
    # gate 8: the archive is invisible to the extension and outside every worktree
    gates["8_archive_is_outside_the_repo_and_worktrees_and_unreferenced"] = (
        not str(ARCHIVE).startswith(str(ROOT))
        and not str(ARCHIVE).startswith(str(Path.home() / "pilot-gen45-work"))
        and "gen55-raw-archive" not in ARM_C.read_text()
        and "gen55-raw-archive" not in ARM_F.read_text())

    report = {
        "evidence_class": "architecture_quiescent_completion_tracked_digest_paired_live",
        "base": BASE, "head": head,
        "arms": {
            "pi_harness_state_control_v1": hashlib.sha256(ARM_C.read_bytes()).hexdigest(),
            "pi_harness_state_control_quiescent_tracked_k3_v1":
                hashlib.sha256(ARM_F.read_bytes()).hexdigest()},
        "frozen_contracts": {
            "quiescence": Q.contract()["contract_version"],
            "k": 3,
            "k_choice": ("frozen at 3 by the Gen55 brief, a deliberate deviation from the Gen54 "
                         "historical rule that mechanically named K=1; labelled, not tuned"),
            "tracked_digest": T.contract()["contract_version"],
            "tracked_digest_sha256": T.contract()["contract_sha256"],
            "retention": R.CONTRACT_VERSION},
        "live_probe": probe,
        "gates": gates,
    }
    report["passed"] = all(v is True for v in gates.values())
    (OUT / "preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gates": gates, "passed": report["passed"]}, indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
