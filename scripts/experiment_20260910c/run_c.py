#!/usr/bin/env python3
"""EXPERIMENT-20260910C harness (dispatch/EXPERIMENT-20260910C.md).

Verify-after-recall nudge mitigation, config-only: the SAME frozen B-round
cases, seeds, model, harness machinery and per-slot records; the ONLY
variable is the nudge text delivered by pi-recall-nudge, overridden via
`recallNudge.nudge` in each arm's isolated agent-dir settings (extension
code byte-frozen).

  O (nudge-orig)    the F2 sentence, byte-identical to the default
  V (nudge-verify)  F2 sentence + one appended verify-against-current clause

16 slots = 2 arms x 4 cases x 2 reps, arm order randomized within each
case/rep by the fresh frozen schedule (seed 20260911), committed before any
run. Genuine RPC switch_session resume in every slot (B-round machinery,
rpc_task.mjs, reused unchanged).

Commands:
  setup            write arm agent dirs + CONFIG_RECEIPTS.json (effective
                   configs AS LOADED via the extension's own loadConfig,
                   nudge strings hash-pinned) into this dir for the freeze
  schedule [--write]  fresh C-round schedule (deterministic seed 20260911)
  slot CASE ARM REP   one slot (ARM in {O,V})
  walk             16 slots in frozen schedule order
  analyze          ledger dump
"""
from __future__ import annotations

import argparse, hashlib, json, os, random, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/experiment_20260910b"))
import run_pi_pilot_r2 as r2  # noqa: E402
import run_b as rb  # noqa: E402  (B-round machinery, reused read-only)

EXP_DIR = ROOT / "scripts/experiment_20260910c"
PRIVATE = Path(os.environ.get(
    "EXPERIMENT_C_PRIVATE",
    "/var/home/bmosher/.local/share/memory-bakeoff/experiment-20260910c"))
RUNS = PRIVATE / "runs"
AGENT_BASE = Path("/var/home/bmosher/.pi-experiment-c")
CASES_DIR = rb.CASES_DIR  # the SAME frozen B-round cases
SCHEDULE_PATH = EXP_DIR / "schedule_c.json"

# The mitigation under test (dispatch, minimal-diff by design): the F2
# sentence with its final period replaced by " — " + one appended
# verify-against-current clause (verbatim from the dispatch text).
F2_SENTENCE = (
    "Before you edit anything, use the project_recall tool to check this "
    "project's past sessions for decisions or constraints relevant to the task.")
NUDGE_ORIG = F2_SENTENCE
NUDGE_VERIFY = (
    "Before you edit anything, use the project_recall tool to check this "
    "project's past sessions for decisions or constraints relevant to the task — "
    "then verify they still hold against the project's current files and "
    "instructions before acting on them.")
assert NUDGE_VERIFY.startswith(F2_SENTENCE[:-1]) and len(NUDGE_VERIFY) > len(F2_SENTENCE)

ARMS_C = {
    "O": {"nudge": NUDGE_ORIG},
    "V": {"nudge": NUDGE_VERIFY},
}


def agent_dir(arm: str) -> Path:
    """C-round arm agent dir: B-round arm-C settings + recallNudge.nudge
    override. Identical in both arms except the nudge string (the single
    experimental variable)."""
    d = AGENT_BASE / f"arm-{arm.lower()}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "models.json").write_text(json.dumps(r2.provider_models(), indent=1))
    settings = {
        "enableInstallTelemetry": False,
        "defaultProvider": "bosgame",
        "defaultModel": "bosgame/qwen3.6-35b-vulkan-nothink",
        "packages": rb.ARMS_B["C"]["packages"],  # same pair as B-round arm C
        "defaultThinkingLevel": "high",
        "recallNudge": {"enabled": True, "nudge": ARMS_C[arm]["nudge"],
                        "onResume": True, "everyPrompt": False,
                        "everyNPrompts": 0, "delivery": "message"},
    }
    settings.update(r2.lcm_settings())
    (d / "settings.json").write_text(json.dumps(settings, indent=1))
    return d


# The B-round machinery (invoke/invoke_task) resolves arm agent dirs through
# rb.agent_dir; point it at the C-round dirs/settings. run_b.py itself stays
# untouched (B-round frozen artifacts unaffected).
rb.agent_dir = agent_dir


def load_cases() -> dict:
    return rb.load_cases()


def build_schedule(cases: dict) -> list:
    """Fresh C-round schedule: deterministic seed 20260911, shuffles [O,V]
    within each case/rep block (8 blocks)."""
    rng = random.Random(20260911)
    blocks = []
    for cid in sorted(cases):
        for rep in (1, 2):
            order = ["O", "V"]
            rng.shuffle(order)
            blocks.append({"case": cid, "rep": rep, "order": order})
    return blocks


# ── slots (B-round per-slot discipline, arm set replaced) ────────────────────

def do_slot(case: dict, cid: str, arm: str, rep: int) -> dict:
    run_dir = RUNS / f"{cid}-{arm.lower()}-rep{rep}"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    worktree = run_dir / "repo"
    r2.reset_worktree(case["repo"], worktree)
    store_dir = run_dir / "lcm"
    resolved = str(worktree.resolve())
    db = store_dir / f"{r2.hash_cwd(resolved)}.db"
    r2.seed_store(case["seed"], db, resolved)
    r2.verify_store_reachable(worktree, db)
    settings_sha = r2.sha256_file(agent_dir(arm) / "settings.json")
    before = rb.store_snapshot(db)

    sessions = run_dir / "sessions"
    sessions.mkdir()
    prime_cmd = rb.pi_base() + ["--session-dir", str(sessions), rb.PRIME_PROMPT]
    prime = rb.invoke(prime_cmd, worktree, arm, store_dir,
                      run_dir / "prime-stdout.txt", run_dir / "prime-stderr.txt")
    prime_parsed = r2.parse_events((run_dir / "prime-stdout.txt").read_text())
    session_file, session_id = rb.find_session_file(
        sessions, (run_dir / "prime-stdout.txt").read_text())

    task = rb.invoke_task(arm, worktree, session_file, case["prompt"],
                          run_dir, store_dir)
    task_parsed = r2.parse_events((run_dir / "stdout.txt").read_text())
    stderr = (run_dir / "stderr.txt").read_text()
    stdout = (run_dir / "stdout.txt").read_text()

    after = rb.store_snapshot(db)
    iso_ok, iso_notes = rb.check_isolation(before, after, db,
                                           r2.node_cwd_hash(worktree), session_id)
    new_ids = sorted(set(after["convs"]) - set(before["convs"]))

    v = case["verifier"]
    final_answer_path = run_dir / "final-answer.txt"
    final_answer_path.write_text(rb.final_answer_text(stdout))
    v_env = dict(os.environ,
                 EXPERIMENT_B_FINAL_ANSWER=str(final_answer_path),
                 EXPERIMENT_B_PRISTINE_DIR=str(case["repo"]))
    try:
        proc = subprocess.run([sys.executable, str(v)], cwd=worktree,
                              capture_output=True, text=True, timeout=60,
                              env=v_env)
        verdict = "pass" if "VERIFIER OK" in proc.stdout else "fail"
        v_stdout = proc.stdout.strip()[:400]
    except Exception as exc:  # noqa: BLE001
        verdict, v_stdout = "error", str(exc)[:400]

    # C-round in-stream evidence (decision rules 1/6): was the current-info
    # supersession consulted, and do stale commands appear in deliverables?
    supersession_consulted = "decommissioned" in stdout
    stale_in_deliverables = None
    if case["kind"] == "control-stale":
        deploy = run_dir / "repo/DEPLOY.txt"
        if deploy.exists():
            text = deploy.read_text(errors="replace")
            stale_in_deliverables = ("staging-box-old" in text
                                     or "deploy_via_ansible" in text)
        else:
            stale_in_deliverables = True  # missing deliverable = R1 fail anyway

    row = {
        "run": run_dir.name, "case": cid, "kind": case["kind"], "arm": arm,
        "rep": rep,
        "arm_nudge_sha256": hashlib.sha256(ARMS_C[arm]["nudge"].encode()).hexdigest(),
        "prompt_sha256": hashlib.sha256(case["prompt"].encode()).hexdigest(),
        "config_ref": f"~/.pi-experiment-c/arm-{arm.lower()}/settings.json",
        "settings_sha256": settings_sha,
        "packages": rb.ARMS_B["C"]["packages"],
        "session_file": str(session_file), "session_id": session_id,
        "prime": {"status": prime["status"], "wall_seconds": prime["wall_seconds"],
                  "usage": prime_parsed["usage"]},
        "task": {"status": task["status"], "exit_code": task["exit_code"],
                 "wall_seconds": task["wall_seconds"]},
        "usage": task_parsed["usage"],
        "tool_calls": task_parsed["tool_calls"],
        "recall_calls": sum(1 for t in task_parsed["tool_calls"] if t == "project_recall"),
        "relaxation_marks": stdout.count("RELAXATION-SOURCED"),
        "nudge": rb.nudge_evidence(stderr, stdout),
        "verifier": verdict, "verifier_stdout": v_stdout,
        "supersession_consulted_in_stream": supersession_consulted,
        "stale_in_deliverables": stale_in_deliverables,
        "isolation_ok": iso_ok, "isolation_notes": iso_notes,
        "reachability": {
            "wiring": "seeded db stem == runtime cwd hash (verify_store_reachable)",
            "store_opened_by_runtime": bool(new_ids),
            "seed_ids_surfaced_in_output": any(s in stdout for s in before["convs"]),
        },
        "store_db": str(db),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    ledger = PRIVATE / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    print(json.dumps({k: row[k] for k in
                      ("run", "verifier", "recall_calls", "isolation_ok",
                       "supersession_consulted_in_stream", "stale_in_deliverables")}))
    print(json.dumps(row["nudge"]))
    return row


# ── commands ─────────────────────────────────────────────────────────────────

def effective_loaded_config(arm: str) -> dict:
    """The config AS LOADED, via the extension's own loadConfig (receipt
    basis; also proves no CONFIG REJECTED problems)."""
    script = (f'import {{loadConfig}} from "{r2.NUDGE_EXT}/index.ts"; '
              f'console.log(JSON.stringify(loadConfig("{agent_dir(arm)}")))')
    out = subprocess.run(["bun", "-e", script],
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise SystemExit(f"loadConfig receipt failed for arm {arm}: {out.stderr[:300]}")
    return json.loads(out.stdout.strip().splitlines()[-1])


def cmd_setup(args) -> None:
    for arm in ARMS_C:
        print(f"agent dir {agent_dir(arm)}")
    receipts = {"prepared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "note": "config-only mitigation; extension code byte-frozen",
                "arms": {}}
    for arm, spec in ARMS_C.items():
        loaded = effective_loaded_config(arm)
        problems = loaded.get("problems")
        nudge_loaded = loaded["config"]["nudge"] if "config" in loaded else loaded.get("nudge")
        receipts["arms"][arm] = {
            "nudge_expected": spec["nudge"],
            "nudge_sha256_expected": hashlib.sha256(spec["nudge"].encode()).hexdigest(),
            "nudge_as_loaded": nudge_loaded,
            "nudge_sha256_as_loaded": hashlib.sha256(str(nudge_loaded).encode()).hexdigest(),
            "load_problems": problems,
            "settings_sha256": r2.sha256_file(agent_dir(arm) / "settings.json"),
            "loadConfig_output": loaded,
        }
        assert nudge_loaded == spec["nudge"], f"arm {arm}: loaded nudge != expected"
        assert not problems, f"arm {arm}: config problems {problems}"
    (EXP_DIR / "CONFIG_RECEIPTS.json").write_text(json.dumps(receipts, indent=1) + "\n")
    print(f"config receipts: {EXP_DIR / 'CONFIG_RECEIPTS.json'}")


def cmd_schedule(args) -> None:
    blocks = build_schedule(load_cases())
    if args.write:
        SCHEDULE_PATH.write_text(json.dumps(blocks, indent=1) + "\n")
        print(f"wrote {SCHEDULE_PATH} (for the freeze commit)")
    print(json.dumps(blocks, indent=1))


def cmd_slot(args) -> None:
    do_slot(load_cases()[args.case], args.case, args.arm, args.rep)


def cmd_walk(args) -> None:
    cases = load_cases()
    for b in json.loads(SCHEDULE_PATH.read_text()):
        for arm in b["order"]:
            do_slot(cases[b["case"]], b["case"], arm, b["rep"])


def cmd_analyze(args) -> None:
    rows = [json.loads(l) for l in (PRIVATE / "ledger.jsonl").read_text().splitlines() if l.strip()]
    for r in rows:
        print(json.dumps({k: r.get(k) for k in
                          ("run", "verifier", "recall_calls", "relaxation_marks",
                           "supersession_consulted_in_stream", "stale_in_deliverables",
                           "isolation_ok")}))
        print("  nudge:", json.dumps(r.get("nudge")))
    print(f"total rows: {len(rows)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    p = sub.add_parser("schedule"); p.add_argument("--write", action="store_true")
    p = sub.add_parser("slot"); p.add_argument("case"); p.add_argument("arm", choices=list(ARMS_C))
    p.add_argument("rep", type=int, choices=[1, 2])
    sub.add_parser("walk")
    sub.add_parser("analyze")
    args = ap.parse_args()
    {"setup": cmd_setup, "schedule": cmd_schedule, "slot": cmd_slot,
     "walk": cmd_walk, "analyze": cmd_analyze}[args.cmd](args)


if __name__ == "__main__":
    main()
