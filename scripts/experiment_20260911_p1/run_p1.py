#!/usr/bin/env python3
"""STUDY-20260911-P1 harness (dispatch/STUDY-20260911-P1.md).

Arms (planner table):
  A  pi-lcm alone (daily baseline; no Perseus, no nudge)
  B  pi-lcm + pi-perseus-recall + pi-recall-nudge, supersession OFF
     (seed-time binding_on absent: both old and current records retrievable)
  C  identical to B, supersession ON (lineage links applied at seed time)

24 slots = 4 cases x 2 reps x 3 arms, arm order randomized within each
case/rep by the frozen schedule (deterministic seed 20260911), committed
before any run. Genuine RPC switch_session resume in every B/C slot (the
nudge fires through the real path; A gets the identical prime+resume
structure with its own package set).

Per-slot records (B/C-round discipline + vault isolation):
- provenance block (STUDY sha c8a222ec..., source-identical NOT
  byte-identical vs Gen21 e9b0912c..., from_key=OLD) in every ledger row;
- vault content snapshot before/after the run (entities table, read-only
  sqlite): records + lineage state must be UNCHANGED by the run (the
  adapter recalls only);
- pi-lcm store: the run's own conversation only (no seeded history goes
  into the lcm store in this study; history lives in the vault);
- reviewer's frozen verifier.py, mention-safe, env P1_FINAL_ANSWER.

Commands:
  setup          write arm agent dirs + prep manifest (case hashes)
  schedule [--write]  frozen randomization schedule
  slot CASE ARM REP  one slot
  walk           24 slots in frozen order
  analyze        ledger dump
"""
from __future__ import annotations

import argparse, hashlib, json, os, random, shutil, sqlite3, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/experiment_20260910b"))
import run_pi_pilot_r2 as r2  # noqa: E402
import run_b as rb  # noqa: E402

EXP_DIR = ROOT / "scripts/experiment_20260911_p1"
CASES_DIR = EXP_DIR / "cases"
SCHEDULE_PATH = EXP_DIR / "schedule_p1.json"
PRIVATE = Path(os.environ.get(
    "EXPERIMENT_P1_PRIVATE",
    "/var/home/bmosher/.local/share/memory-bakeoff/experiment-20260911-p1"))
RUNS = PRIVATE / "runs"
AGENT_BASE = Path("/var/home/bmosher/.pi-experiment-p1")
PERSEUS_EXT = ROOT / "extensions/pi-perseus-recall"

BIN = Path("/var/home/bmosher/perseus-build/src/target/release/perseus-vault")
PROVENANCE = {
    "study_binary": str(BIN),
    "study_binary_sha256": "c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172",
    "study_binary_version": "perseus-vault 2.23.2 (9c82920)",
    "gen21_measured_sha256_arm64_tarball": "e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb",
    "identity": "source-identical, NOT byte-identical",
    "build_method": "build.sh with GIT_HASH=9c82920, rust 1.97.1 bookworm, "
                    "DEFAULT features (the Dockerfile lean build is FORBIDDEN "
                    "- keyword-only wearing the version string)",
    "supersede_direction": "from_key = OLD (parameters authoritative)",
}

ARMS_P1 = {
    "A": {"packages": lambda: [r2.PI_LCM], "supersession": None},
    "B": {"packages": lambda: [r2.PI_LCM, str(PERSEUS_EXT), str(r2.NUDGE_EXT)],
          "supersession": False},
    "C": {"packages": lambda: [r2.PI_LCM, str(PERSEUS_EXT), str(r2.NUDGE_EXT)],
          "supersession": True},
}


def load_cases() -> dict:
    cases = {}
    for d in sorted(CASES_DIR.iterdir() if CASES_DIR.exists() else []):
        cj = d / "case.json"
        if not (cj.exists() and (d / "repo").is_dir() and (d / "verifier.py").exists()
                and (d / "records.json").exists()):
            continue
        meta = json.loads(cj.read_text())
        cases[d.name] = {
            "dir": d, "kind": meta["kind"], "prompt": meta["prompt"],
            "repo": d / "repo", "verifier": d / "verifier.py",
            "records": json.loads((d / "records.json").read_text()),
        }
    if not cases:
        raise SystemExit(f"no complete cases found under {CASES_DIR}")
    return cases


def build_schedule(cases: dict) -> list:
    rng = random.Random(20260911)
    blocks = []
    for cid in sorted(cases):
        for rep in (1, 2):
            order = ["A", "B", "C"]
            rng.shuffle(order)
            blocks.append({"case": cid, "rep": rep, "order": order})
    return blocks


# ── vault seeding + isolation ────────────────────────────────────────────────

def sh(args):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        raise SystemExit(f"vault cmd failed {args[1:3]}: {r.stderr[-300:]}")
    return r.stdout


def seed_vault(spec: dict, root: Path, arm: str) -> Path:
    """Write the spec's records; apply lineage links ONLY for arm C
    (seed-time binding_on). B/C vaults are otherwise identical."""
    db, key = root / "vault.sqlite", root / "vault.key"
    sh([BIN, "keygen", "--key-file", key])
    ws = hashlib.sha256(b"study-p1-" + root.name.encode()).hexdigest()
    for rec in spec["records"]:
        sh([BIN, "write", "--db", db, "--encryption-key", key,
            "--category", rec["category"], "--key", rec["key"],
            "--body", json.dumps(rec["body"], sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False),
            "--workspace-hash", ws])
    if ARMS_P1[arm]["supersession"]:
        proc = subprocess.Popen([str(BIN), "serve", "--db", str(db),
                                 "--encryption-key", str(key)],
                                text=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                bufsize=1)
        try:
            def rpc(method, params):
                rpc.i = getattr(rpc, "i", 0) + 1
                proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": rpc.i,
                                             "method": method, "params": params}) + "\n")
                proc.stdin.flush()
                return json.loads(proc.stdout.readline())["result"]
            rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                               "clientInfo": {"name": "p1-seed", "version": "0"}})
            for link in spec["links"]:
                out = rpc("tools/call", {"name": "perseus_vault_supersede",
                                         "arguments": {
                                             "from_category": "decision",
                                             "from_key": link["from_key"],
                                             "to_category": "decision",
                                             "to_key": link["to_key"],
                                             "relationship": link["relationship"],
                                             "reason": link["reason"]}})
                print(f"  supersede: {link['from_key']} -> {link['to_key']} "
                      f"({json.dumps(out)[:100]})")
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    return db


def vault_snapshot(db: Path) -> dict:
    """Content-level vault state (read-only sqlite): per record key ->
    (status, valid_to, retrieval_count). Supersession state is visible as
    status/valid_to; retrieval_count changes are read-side and recorded."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute("SELECT key, status, valid_to_unix_ms, retrieval_count "
                       "FROM entities ORDER BY key").fetchall()
    con.close()
    return {r[0]: {"status": r[1], "valid_to": r[2], "retrievals": r[3]} for r in rows}


def check_vault(before: dict, after: dict) -> tuple:
    notes, ok = [], True
    for k, v in before.items():
        a = after.get(k)
        if a is None:
            ok = False; notes.append(f"record {k} MISSING after run")
        elif (a["status"], a["valid_to"]) != (v["status"], v["valid_to"]):
            ok = False
            notes.append(f"record {k} lineage state CHANGED {v} -> {a}")
    new = sorted(set(after) - set(before))
    if new:
        ok = False; notes.append(f"records ADDED during run: {new}")
    return ok, notes


# ── arm agent dirs ───────────────────────────────────────────────────────────

def agent_dir(arm: str, vault_db: Path | None) -> Path:
    d = AGENT_BASE / f"arm-{arm.lower()}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "models.json").write_text(json.dumps(r2.provider_models(), indent=1))
    settings = {
        "enableInstallTelemetry": False,
        "defaultProvider": "bosgame",
        "defaultModel": "bosgame/qwen3.6-35b-vulkan-nothink",
        "packages": ARMS_P1[arm]["packages"](),
        "defaultThinkingLevel": "high",
    }
    if arm in ("B", "C"):
        settings["recallNudge"] = {
            "enabled": True, "nudge": r2.F2_NUDGE, "onResume": True,
            "everyPrompt": False, "everyNPrompts": 0, "delivery": "message"}
        settings["perseusRecall"] = {
            "bin": str(BIN), "db": str(vault_db),
            "keyFile": str(vault_db.parent / "vault.key"),
            "workspaceHash": hashlib.sha256(
                b"study-p1-" + vault_db.parent.name.encode()).hexdigest(),
            "limit": 5}
    settings.update(r2.lcm_settings())
    (d / "settings.json").write_text(json.dumps(settings, indent=1))
    return d


# ── slot ─────────────────────────────────────────────────────────────────────

def do_slot(case: dict, cid: str, arm: str, rep: int) -> dict:
    run_dir = RUNS / f"{cid}-{arm.lower()}-rep{rep}"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    worktree = run_dir / "repo"
    r2.reset_worktree(case["repo"], worktree)
    vault_root = run_dir / "vault"
    vault_root.mkdir()
    db = seed_vault(case["records"], vault_root, arm)
    ad = agent_dir(arm, db if arm in ("B", "C") else None)
    rb.agent_dir = lambda a: ad
    settings_sha = r2.sha256_file(ad / "settings.json")
    vault_before = vault_snapshot(db)
    store_dir = run_dir / "lcm"  # pi-lcm ACTIVE; no seeded history in-lcm

    sessions = run_dir / "sessions"
    sessions.mkdir()
    prime = rb.invoke(rb.pi_base() + ["--session-dir", str(sessions), rb.PRIME_PROMPT],
                      worktree, arm, store_dir,
                      run_dir / "prime-stdout.txt", run_dir / "prime-stderr.txt")
    prime_parsed = r2.parse_events((run_dir / "prime-stdout.txt").read_text())
    session_file, session_id = rb.find_session_file(
        sessions, (run_dir / "prime-stdout.txt").read_text())

    task = rb.invoke_task(arm, worktree, session_file, case["prompt"], run_dir, store_dir)
    task_parsed = r2.parse_events((run_dir / "stdout.txt").read_text())
    stderr = (run_dir / "stderr.txt").read_text()
    stdout = (run_dir / "stdout.txt").read_text()

    vault_after = vault_snapshot(db)
    v_ok, v_notes = check_vault(vault_before, vault_after)

    final_answer_path = run_dir / "final-answer.txt"
    final_answer_path.write_text(rb.final_answer_text(stdout))
    v_env = dict(os.environ, P1_FINAL_ANSWER=str(final_answer_path))
    try:
        proc = subprocess.run([sys.executable, str(case["verifier"])], cwd=worktree,
                              capture_output=True, text=True, timeout=60, env=v_env)
        verdict = "pass" if "VERIFIER OK" in proc.stdout else "fail"
        v_stdout = proc.stdout.strip()[:400]
    except Exception as exc:  # noqa: BLE001
        verdict, v_stdout = "error", str(exc)[:400]

    row = {
        "run": run_dir.name, "case": cid, "kind": case["kind"], "arm": arm, "rep": rep,
        "supersession": ARMS_P1[arm]["supersession"],
        "provenance": PROVENANCE,
        "prompt_sha256": hashlib.sha256(case["prompt"].encode()).hexdigest(),
        "config_ref": f"~/.pi-experiment-p1/arm-{arm.lower()}/settings.json",
        "settings_sha256": settings_sha,
        "packages": ARMS_P1[arm]["packages"](),
        "vault_db": str(db),
        "vault_before": vault_before,
        "session_id": session_id,
        "prime": {"status": prime["status"], "wall_seconds": prime["wall_seconds"],
                  "usage": prime_parsed["usage"]},
        "task": {"status": task["status"], "exit_code": task["exit_code"],
                 "wall_seconds": task["wall_seconds"]},
        "usage": task_parsed["usage"],
        "tool_calls": task_parsed["tool_calls"],
        "recall_calls": sum(1 for t in task_parsed["tool_calls"] if t == "project_recall"),
        "nudge": rb.nudge_evidence(stderr, stdout),
        "verifier": verdict, "verifier_stdout": v_stdout,
        "vault_isolation_ok": v_ok, "vault_isolation_notes": v_notes,
        "seed_record_keys_surfaced": sorted(
            k for k in vault_before if vault_before[k]["status"] != "retired"
            and k.replace("record-", "").replace("-d2-current", "") in stdout),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    ledger = PRIVATE / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    print(json.dumps({k: row[k] for k in
                      ("run", "verifier", "recall_calls", "vault_isolation_ok")}))
    print(json.dumps(row["nudge"]))
    return row


def cmd_setup(args) -> None:
    cases = load_cases()
    PRIVATE.mkdir(parents=True, exist_ok=True)
    for arm in ARMS_P1:
        print(f"agent dir pattern {AGENT_BASE}/arm-{arm.lower()} (per-slot vault ptr)")
    manifest = {
        "prepared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provenance": PROVENANCE,
        "binary_sha_check": hashlib.sha256(BIN.read_bytes()).hexdigest(),
        "cases": {cid: {
            "kind": c["kind"],
            "records": [r["key"] for r in c["records"]["records"]],
            "links": [(l["from_key"], l["to_key"]) for l in c["records"]["links"]],
            "case_json": r2.sha256_file(c["dir"] / "case.json"),
            "records_json": r2.sha256_file(c["dir"] / "records.json"),
            "verifier_py": r2.sha256_file(c["verifier"]),
        } for cid, c in cases.items()},
        "schedule": json.loads(SCHEDULE_PATH.read_text()) if SCHEDULE_PATH.exists() else None,
    }
    assert manifest["binary_sha_check"] == PROVENANCE["study_binary_sha256"]
    (PRIVATE / "PREP_MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print(f"prep manifest: {PRIVATE / 'PREP_MANIFEST.json'}")


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
                          ("run", "verifier", "recall_calls", "vault_isolation_ok",
                           "supersession")}))
        print("  nudge:", json.dumps(r.get("nudge")))
    print(f"total rows: {len(rows)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    p = sub.add_parser("schedule"); p.add_argument("--write", action="store_true")
    p = sub.add_parser("slot"); p.add_argument("case")
    p.add_argument("arm", choices=list(ARMS_P1)); p.add_argument("rep", type=int, choices=[1, 2])
    sub.add_parser("walk")
    sub.add_parser("analyze")
    args = ap.parse_args()
    {"setup": cmd_setup, "schedule": cmd_schedule, "slot": cmd_slot,
     "walk": cmd_walk, "analyze": cmd_analyze}[args.cmd](args)


if __name__ == "__main__":
    main()
