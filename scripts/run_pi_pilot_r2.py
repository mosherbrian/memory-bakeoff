#!/usr/bin/env python3
"""R2 pilot harness: paired A/B evaluation of the pi-project-recall extension.

Arms (RESET_STATUS.md, R2 pilot specification):
  A  Brian's existing enhanced Pi-LCM setup (packages: pi-lcm), isolated config
  B  the identical setup plus extensions/pi-project-recall

Both arms share the same isolated provider/model (bosgame -> local llama-swap
on 127.0.0.1:8080, qwen3.6-35b-vulkan-nothink), the same lcm/compaction
settings mirrored from the real ~/.pi/agent/settings.json, the same per-case
worktree snapshot and the same seeded prior-session store. Only the packages
list differs. The store is copied fresh for every run; nothing crosses runs.

Commands:
  setup              create isolated agent dirs (both arms) + prep manifest
  smoke <arm>        unrelated kettle smoke task (feature-active check)
  run <case> <arm> <rep>   one evaluation run (rep in {1,2})
  walk               the frozen evaluation order: per case rep1 A,B then rep2 B,A
  score <rundir>     re-derive a row from an existing run dir

Private outputs (stdout, stderr, stores, sessions, worktrees) live under
~/.local/share/memory-bakeoff/reset-20260907/r2/ - never in the repository.
"""
from __future__ import annotations

import argparse, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path.home() / ".local/share/memory-bakeoff/reset-20260907/r2"
RUNS = PRIVATE / "runs"
AGENT_BASE = Path.home() / ".pi-pilot-r2"
PI = "/var/home/bmosher/.bun/bin/pi"
PI_LCM = "/var/home/bmosher/projects/pi-lcm-bun"
RECALL = ROOT / "extensions/pi-project-recall"
CASES_DIR = ROOT / "scripts/r2_pilot/cases"
FIXTURES = ROOT / "fixtures/intent_persistence_gen48"

RUN_TIMEOUT_SECONDS = 480  # 8-minute ceiling per the specification
PREP_EPOCH_NOTE = "transcripts authored 2026-09-09 before any treatment outcome"

RESUME_PREFIX = "I'm returning to this project after a break. "

CASES = {
    "c1": {
        "fixture": "IP1",
        "transcript": "c1_sluice.json",
        "prompt": RESUME_PREFIX
        + "The controller firmware changed: it now reports 8 steps per millimetre instead of 4. "
        + "Update the package so gate positions are correct again.",
    },
    "c2": {
        "fixture": "IP2",
        "transcript": "c2_ferry.json",
        "prompt": RESUME_PREFIX
        + "Add a 12:00 sailing, and make next_sailing return None instead of wrapping around to "
        + "the first sailing when there is nothing later in the day.",
    },
    "c3": {
        "fixture": "IP3",
        "transcript": "c3_tally.json",
        "prompt": RESUME_PREFIX
        + "Two things. First, `totals` should ignore items whose hold is missing or empty rather "
        + "than counting them under a blank key. Second, `summary` must list holds in alphabetical "
        + "order, because the printed manifest is compared line by line against the port's own copy.",
    },
    "c4": {
        "fixture": "IP4",
        "transcript": "c4_lockgate.json",
        "prompt": RESUME_PREFIX
        + "`clamp` should also refuse negative openings: anything below zero must come back as "
        + "zero. Keep the existing upper bound behaviour exactly as it is.",
    },
}

ARMS = {
    "A": {"packages": [PI_LCM]},
    "B": {"packages": [PI_LCM, str(RECALL)]},
}

# The unrelated smoke task (adapted from the Gen49 harness smoke fixture).
SMOKE_FILES = {
    "kettle/__init__.py": "",
    "kettle/greet.py": 'def greet(name: str) -> str:\n    """Return a greeting for the caller."""\n    return "hello"\n',
    "README.md": "# kettle\n\nA tiny greeting helper.\n",
}
SMOKE_PROMPT = (
    "In this repository, `kettle/greet.py` has a function `greet(name)` that ignores its "
    "argument and always returns \"hello\". Read the file, then edit it so it returns "
    "\"hello NAME\" for the name it is given. When you have made the edit, say DONE."
)


def provider_models() -> dict:
    """Provider catalog mirroring the working Gen49 definition of the local
    llama-swap endpoint, under the recorded provider name bosgame, plus the
    pi-lcm compaction provider fast/npu-summarise as in the real settings."""
    return {"providers": {
        "bosgame": {
            "baseUrl": "http://127.0.0.1:8080/v1",
            "api": "openai-completions",
            "apiKey": "none",
            "compat": {"sendSessionAffinityHeaders": True},
            "models": [{
                "id": "qwen3.6-35b-vulkan-nothink", "contextWindow": 131072, "maxTokens": 8192,
                "compat": {"supportsDeveloperRole": False, "supportsReasoningEffort": False},
            }],
        },
        "fast": {
            "baseUrl": "http://127.0.0.1:8310/v1",
            "api": "openai-completions",
            "apiKey": "none",
            "models": [{
                "id": "npu-summarise", "contextWindow": 32768, "maxTokens": 4096,
                "compat": {"supportsDeveloperRole": False, "supportsReasoningEffort": False},
            }],
        },
    }}


def lcm_settings() -> dict:
    """Mirror of the real ~/.pi/agent/settings.json lcm/compaction values
    (RESET_STATUS.md R2 configuration row); identical in both arms."""
    return {
        "lcm": {
            "compactionModels": [{"provider": "fast", "id": "npu-summarise"}],
            "minMessagesForCompaction": 15,
            "prewarm": True,
            "prewarmContinuous": False,
            "prewarmStableBlock": False,
            "debugMode": True,
        },
        "compaction": {"enabled": True, "reserveTokens": 65536, "keepRecentTokens": 19660},
    }


def agent_dir(arm: str) -> Path:
    d = AGENT_BASE / f"arm-{arm.lower()}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "models.json").write_text(json.dumps(provider_models(), indent=1))
    settings = {
        "enableInstallTelemetry": False,
        "defaultProvider": "bosgame",
        "defaultModel": "bosgame/qwen3.6-35b-vulkan-nothink",
        "packages": ARMS[arm]["packages"],
        "defaultThinkingLevel": "high",
    }
    settings.update(lcm_settings())
    (d / "settings.json").write_text(json.dumps(settings, indent=1))
    return d


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def cmd_setup(args) -> None:
    for arm in ARMS:
        d = agent_dir(arm)
        print(f"agent dir {d}")
    PRIVATE.mkdir(parents=True, exist_ok=True)
    manifest = {
        "prepared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": PREP_EPOCH_NOTE,
        "harness": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__))},
        "cases": {},
    }
    for cid, case in CASES.items():
        t = CASES_DIR / case["transcript"]
        v = FIXTURES / case["fixture"] / "verifier.py"
        manifest["cases"][cid] = {
            "fixture": case["fixture"],
            "prompt": case["prompt"],
            "transcript": {"path": str(t), "sha256": sha256_file(t)},
            "verifier": {"path": str(v), "sha256": sha256_file(v)},
        }
    (PRIVATE / "PREP_MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print(f"prep manifest: {PRIVATE/'PREP_MANIFEST.json'}")


def hash_cwd(path: str) -> str:
    # Resolve to the physical path first: node's process.cwd() (getcwd)
    # returns the symlink-resolved path, and both pi-lcm and the extension
    # hash that string. Hashing the /home symlink spelling was the R3 blocker.
    return hashlib.sha256(os.path.realpath(path).encode()).hexdigest()[:16]


def node_cwd_hash(worktree: Path) -> str:
    """The store-name hash a node process actually computes from
    process.cwd() inside the worktree - the authoritative runtime key."""
    out = subprocess.run(
        ["node", "-e",
         "console.log(require('node:crypto').createHash('sha256')"
         ".update(process.cwd()).digest('hex').slice(0,16))"],
        cwd=worktree, capture_output=True, text=True, check=True, timeout=30)
    return out.stdout.strip()


def verify_store_reachable(worktree: Path, db: Path) -> None:
    """Fail fast (wiring-recurrence) if the seeded filename is not the one
    the runtime will open - receipts, not claims."""
    runtime = node_cwd_hash(worktree)
    if runtime != db.stem:
        raise SystemExit(
            f"wiring-recurrence: seeded {db.name} but the runtime hashes "
            f"{runtime}; aborting before any pi invocation")


def reset_worktree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(["git", "-c", "user.email=p@example.invalid", "-c", "user.name=p",
                    "commit", "-qm", "run"], cwd=target, check=True)


def seed_store(transcript: Path, db: Path, cwd: str) -> None:
    db.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["node", str(ROOT / "scripts/r2_pilot/seed_store.ts"),
                    str(transcript), str(db), cwd],
                   check=True, capture_output=True, text=True, timeout=60)


def pi_command(prompt: str) -> list:
    return [
        PI, "--print", "--mode", "json",
        "--provider", "bosgame", "--model", "bosgame/qwen3.6-35b-vulkan-nothink",
        "--no-skills", "--no-context-files", "--no-prompt-templates", "--no-themes",
        "--session-dir", "SESSION_DIR_PLACEHOLDER",
        prompt,
    ]


def execute(arm: str, worktree: Path, prompt: str, out: Path, store_dir: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    sessions = out / "sessions"
    sessions.mkdir(exist_ok=True)
    command = [c.replace("SESSION_DIR_PLACEHOLDER", str(sessions)) for c in pi_command(prompt)]
    env = dict(
        os.environ,
        PI_CODING_AGENT_DIR=str(agent_dir(arm)),
        LCM_DB_DIR=str(store_dir),
        PI_OFFLINE="1",
        NO_COLOR="1",
    )
    started = time.time()
    try:
        proc = subprocess.run(command, cwd=worktree, env=env,
                              capture_output=True, text=True, timeout=RUN_TIMEOUT_SECONDS)
        status, code, stdout, stderr = "completed", proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        status, code = "timeout", None
        stdout = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    elapsed = time.time() - started
    (out / "stdout.txt").write_text(stdout)
    (out / "stderr.txt").write_text(stderr)
    return {"status": status, "exit_code": code, "wall_seconds": round(elapsed, 2)}


def parse_events(stdout: str) -> dict:
    """Parse --mode json output (newline-delimited events): tool calls from
    tool_execution_start.toolName, usage summed over message_end.message.usage."""
    events = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    tool_calls = [e["toolName"] for e in events if e.get("type") == "tool_execution_start"]
    usage = {"input": 0, "output": 0, "cacheRead": 0, "totalTokens": 0, "messages": 0}
    for e in events:
        if e.get("type") == "message_end":
            u = (e.get("message") or {}).get("usage") or {}
            if u:
                usage["input"] += u.get("input", 0)
                usage["output"] += u.get("output", 0)
                usage["cacheRead"] += u.get("cacheRead", 0)
                usage["totalTokens"] += u.get("totalTokens", 0)
                usage["messages"] += 1
    return {"event_count": len(events), "tool_calls": tool_calls, "usage": usage}


def run_verifier(fixture: str, worktree: Path) -> dict:
    v = FIXTURES / fixture / "verifier.py"
    try:
        proc = subprocess.run([sys.executable, str(v)], cwd=worktree,
                              capture_output=True, text=True, timeout=60)
        ok = "VERIFIER OK" in proc.stdout
        return {"verifier": "pass" if ok else "fail",
                "verifier_stdout": proc.stdout.strip()[:500],
                "verifier_stderr": proc.stderr.strip()[-500:]}
    except Exception as exc:  # noqa: BLE001
        return {"verifier": "error", "verifier_stderr": str(exc)[:500]}


def tree_digest(path: Path) -> str:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    return subprocess.run(["git", "write-tree"], cwd=path, capture_output=True,
                          text=True, check=True).stdout.strip()


def do_run(name: str, arm: str, rep: int | None, smoke: bool) -> dict:
    if smoke:
        run_dir = RUNS / f"smoke-{name}"
        source = RUNS / "_smoke_src"
        source.mkdir(parents=True, exist_ok=True)
        for rel, content in SMOKE_FILES.items():
            f = source / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(content)
        prompt = SMOKE_PROMPT
        fixture = None
        transcript = None
    else:
        case = CASES[name]
        run_dir = RUNS / f"{name}-{arm.lower()}-rep{rep}"
        source = FIXTURES / case["fixture"] / "repo"
        prompt = case["prompt"]
        fixture = case["fixture"]
        transcript = CASES_DIR / case["transcript"]

    worktree = run_dir / "repo"
    prep_started = time.time()
    reset_worktree(source, worktree)
    store_dir = run_dir / "lcm"
    resolved = str(worktree.resolve())
    db = store_dir / f"{hash_cwd(resolved)}.db"
    if transcript is not None:
        seed_store(transcript, db, resolved)
        verify_store_reachable(worktree, db)
    elif smoke:
        # No seeded history for the smoke task: it is unrelated by design.
        pass
    prep_seconds = round(time.time() - prep_started, 2)

    result = execute(arm, worktree, prompt, run_dir, store_dir)
    parsed = parse_events((run_dir / "stdout.txt").read_text())
    row = {
        "run": run_dir.name, "case": "smoke" if smoke else name, "arm": arm,
        "rep": rep, "config_ref": f"~/.pi-pilot-r2/arm-{arm.lower()}/settings.json",
        **result, **parsed, "prep_seconds": prep_seconds,
        "digest_initial": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=worktree,
                                         capture_output=True, text=True).stdout.strip(),
    }
    if fixture is not None:
        row.update(run_verifier(fixture, worktree))
        row["digest_final"] = tree_digest(worktree)
        row["store_db"] = str(db)
    ledger = PRIVATE / "ledger.jsonl"
    with ledger.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    print(json.dumps({k: row[k] for k in ("run", "status", "wall_seconds", "verifier")
                      if k in row}))
    return row


def cmd_walk(args) -> None:
    order = []
    for cid in CASES:
        order += [(cid, "A", 1), (cid, "B", 1), (cid, "B", 2), (cid, "A", 2)]
    for cid, arm, rep in order:
        do_run(cid, arm, rep, smoke=False)


def cmd_receipt(args) -> None:
    """Stage A reachability receipt: one probe run through the REAL path
    (real pi invocation, arm B packages, seeded prior-session store). Not an
    evaluation slot; consumes no F1/F2 budget. Writes RECEIPT.txt with the
    verbatim evidence lines into --out."""
    out = Path(args.out).expanduser().resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    source = out / "_src"
    source.mkdir()
    for rel, content in SMOKE_FILES.items():
        f = source / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    worktree = out / "repo"
    reset_worktree(source, worktree)
    store_dir = out / "lcm"
    resolved = str(worktree.resolve())
    db = store_dir / f"{hash_cwd(resolved)}.db"
    seed_store(RECEIPT_TRANSCRIPT, db, resolved)
    verify_store_reachable(worktree, db)

    result = execute("B", worktree, RECEIPT_PROMPT, out, store_dir)
    parsed = parse_events((out / "stdout.txt").read_text())

    lines = [f"receipt run: status={result['status']} wall={result['wall_seconds']}s "
             f"exit={result.get('exit_code')} events={parsed['event_count']}",
             f"worktree (resolved): {resolved}"]

    # (a) filename identity: exactly one db, named by the runtime hash, and
    # pi-lcm wrote the run's conversation into it (wal/shm + new conv row).
    dbs = sorted(p.name for p in store_dir.glob("*.db"))
    runtime_hash = node_cwd_hash(worktree)
    sidecars = sorted(p.name for p in store_dir.iterdir() if p.suffix in ("-wal", "-shm"))
    import sqlite3
    convs = []
    if db.exists():
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        convs = con.execute("select id, session_id from conversations").fetchall()
        con.close()
    lines.append(f"db files: {dbs} | runtime hash: {runtime_hash} | sidecars: {sidecars}")
    lines.append(f"conversations in seeded store: {convs}")
    a_ok = (dbs == [db.name] and db.stem == runtime_hash and sidecars
            and len(convs) >= 2 and any(c[0] == "seed-receipt-prior" for c in convs)
            and any(c[0] != "seed-receipt-prior" for c in convs))

    # (b) content surfacing: a project_recall call whose result carries the
    # seeded probe string and the seeded conversation id.
    stdout = (out / "stdout.txt").read_text(errors="replace")
    b_ok = False
    for line in stdout.splitlines():
        if "RECEIPT-PROBE-7f3a" in line and "seed-receipt-prior" in line:
            lines.append(f"evidence: {line.strip()[:600]}")
            b_ok = True
    recall_calls = [t for t in parsed["tool_calls"] if t == "project_recall"]
    lines.append(f"project_recall calls in transcript: {len(recall_calls)}")

    verdict = "REACHABILITY RECEIPT: PASS" if (a_ok and b_ok) else \
              "REACHABILITY RECEIPT: FAIL"
    lines.append(verdict)
    (out / "RECEIPT.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


RECEIPT_TRANSCRIPT = CASES_DIR / "receipt_probe.json"
RECEIPT_PROMPT = (
    "Use the project_recall tool now with query \"RECEIPT-PROBE-7f3a\" and scope \"all\". "
    "Reply with the timestamps, session ids and text of whatever it returns. "
    "Do not edit any files."
)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    p = sub.add_parser("smoke"); p.add_argument("arm", choices=["A", "B"])
    p = sub.add_parser("run"); p.add_argument("case", choices=list(CASES))
    p.add_argument("arm", choices=["A", "B"]); p.add_argument("rep", type=int, choices=[1, 2])
    sub.add_parser("walk")
    p = sub.add_parser("score"); p.add_argument("rundir")
    p = sub.add_parser("receipt"); p.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.cmd == "setup":
        cmd_setup(args)
    elif args.cmd == "smoke":
        do_run(f"task-{args.arm.lower()}", args.arm, None, smoke=True)
    elif args.cmd == "run":
        do_run(args.case, args.arm, args.rep, smoke=False)
    elif args.cmd == "walk":
        cmd_walk(args)
    elif args.cmd == "score":
        print("rescoring from run dir:", args.rundir)
    elif args.cmd == "receipt":
        cmd_receipt(args)


if __name__ == "__main__":
    main()
