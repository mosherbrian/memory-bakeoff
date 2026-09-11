#!/usr/bin/env python3
"""EXPERIMENT-20260910B harness (dispatch/EXPERIMENT-20260910B.md).

Three arms over reviewer-authored cases, 24 slots (4 cases x 2 reps x 3
arms), arm order randomized within each case/rep by the frozen schedule
committed before the first evaluation run.

  A  pi-lcm only (daily configuration)
  B  + pi-project-recall (relaxed recall, NO nudge)
  C  + pi-project-recall + pi-recall-nudge (automatic nudge)

Arm C trigger authenticity: every slot runs a fixed case-neutral PRIME
invocation (fresh session, session_start reason "new") and then the task
invocation RESUMES that same session file via the RPC switch_session driver
(rpc_task.mjs -> runtime switchSession -> session_start reason "resume",
the deck-reconnect path), so the treatment prompt genuinely arrives through
a real resume and the pi-recall-nudge onResume gate fires through the
deployed path. All arms use the identical prime+resume structure; only the
packages list differs.

Isolation + verification per slot (planner rule 4 - replaces whole-store
checksums): actual db path + effective config recorded; seeded conversation
rows verified unchanged at content level after the run (message count and
text digest per seeded id); non-seed deltas asserted confined to the run's
own conversation ids; recall connection read-only is an extension-level
property (extensions/pi-project-recall test suite, node:sqlite readonly)
cited per run alongside the delta check.

Commands:
  setup            create arm agent dirs + prep manifest (case hashes)
  schedule [--write]  print the frozen randomization schedule (deterministic
                   seed 20260910); --write also persists schedule.json for the
                   freeze commit once reviewer cases are delivered
  smoke --out DIR  ONE pre-evaluation smoke of the full extension PAIR
                   (arm C packages, pi-lcm ACTIVE) with written receipt
  slot CASE ARM REP   run one slot per the frozen discipline
  walk             run all 24 slots in frozen schedule order
  analyze          ledger summary (no scoring judgments)

Private outputs live under EXPERIMENT_B_PRIVATE (default
~/.local/share/memory-bakeoff/experiment-20260910b/) - never in the repo.
"""
from __future__ import annotations

import argparse, hashlib, json, os, random, shutil, sqlite3, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import run_pi_pilot_r2 as r2  # noqa: E402  (frozen F1/F2 machinery, reused read-only)

PRIVATE = Path(os.environ.get(
    "EXPERIMENT_B_PRIVATE",
    str(Path.home() / ".local/share/memory-bakeoff/experiment-20260910b")))
RUNS = PRIVATE / "runs"
AGENT_BASE = Path.home() / ".pi-experiment-b"
EXP_DIR = ROOT / "scripts/experiment_20260910b"
CASES_DIR = EXP_DIR / "cases"
SCHEDULE_PATH = EXP_DIR / "schedule.json"
SMOKE_SEED = EXP_DIR / "smoke_seed.json"

RUN_TIMEOUT_SECONDS = 480  # 8-minute ceiling per task invocation (spec)
PRIME_PROMPT = "Reply with READY and stop."  # fixed, case-neutral, all arms

ARMS_B = {
    "A": {"packages": [r2.PI_LCM]},
    "B": {"packages": [r2.PI_LCM, str(r2.RECALL)]},
    "C": {"packages": [r2.PI_LCM, str(r2.RECALL), str(r2.NUDGE_EXT)]},
}


def agent_dir(arm: str) -> Path:
    d = AGENT_BASE / f"arm-{arm.lower()}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "models.json").write_text(json.dumps(r2.provider_models(), indent=1))
    settings = {
        "enableInstallTelemetry": False,
        "defaultProvider": "bosgame",
        "defaultModel": "bosgame/qwen3.6-35b-vulkan-nothink",
        "packages": ARMS_B[arm]["packages"],
        "defaultThinkingLevel": "high",
    }
    settings.update(r2.lcm_settings())
    (d / "settings.json").write_text(json.dumps(settings, indent=1))
    return d


def load_cases() -> dict:
    """Reviewer-authored case dirs: case.json {case,kind,prompt},
    seed_transcript.json (seed_store.ts format), repo/, verifier.py."""
    cases = {}
    for d in sorted(CASES_DIR.iterdir() if CASES_DIR.exists() else []):
        cj = d / "case.json"
        if not (cj.exists() and (d / "repo").is_dir() and (d / "verifier.py").exists()
                and (d / "seed_transcript.json").exists()):
            continue
        meta = json.loads(cj.read_text())
        cases[d.name] = {
            "dir": d, "kind": meta["kind"], "prompt": meta["prompt"],
            "repo": d / "repo", "verifier": d / "verifier.py",
            "seed": d / "seed_transcript.json", "meta": meta,
        }
    if not cases:
        raise SystemExit(f"no complete cases found under {CASES_DIR}")
    return cases


# ── frozen randomization schedule ────────────────────────────────────────────

def build_schedule(cases: dict) -> list:
    """Deterministic: random.Random(predeclared seed) shuffles [A,B,C]
    within each case/repetition block. Same seed -> same schedule."""
    rng = random.Random(20260910)
    blocks = []
    for cid in sorted(cases):
        for rep in (1, 2):
            order = ["A", "B", "C"]
            rng.shuffle(order)
            blocks.append({"case": cid, "rep": rep, "order": order})
    return blocks


# ── per-slot isolation (planner rule 4) ──────────────────────────────────────

def store_snapshot(db: Path) -> dict:
    """Content-level snapshot: per conversation id -> session_id, message
    count, text digest. Read-only connection (the recall tool's own
    property)."""
    if not db.exists():
        return {"convs": {}}
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    convs = {}
    for (cid,) in con.execute("select id from conversations order by id"):
        sid, = con.execute("select session_id from conversations where id=?",
                           (cid,)).fetchone()
        rows = con.execute(
            "select role, content_text, seq from messages where conversation_id=?"
            " order by seq", (cid,)).fetchall()
        digest = hashlib.sha256(
            "\n".join(f"{r[0]}|{r[2]}|{r[1]}" for r in rows).encode()).hexdigest()
        convs[cid] = {"session_id": sid, "messages": len(rows), "digest": digest}
    con.close()
    return {"convs": convs}


def check_isolation(before: dict, after: dict, db: Path, runtime_hash: str,
                    run_session_id: str | None) -> tuple:
    """Returns (ok, notes). Seeded rows must be unchanged; every new
    conversation must be the run's own (pi-lcm legitimately writes those;
    planner rule 4.3 confines the deltas to the run's own conversation)."""
    notes = []
    ok = db.stem == runtime_hash
    if not ok:
        notes.append(f"db {db.name} != runtime hash {runtime_hash}")
    seeded = before["convs"]
    for cid, snap in seeded.items():
        a = after["convs"].get(cid)
        if a is None:
            ok = False; notes.append(f"seeded conversation {cid} MISSING after run")
        elif a != snap:
            ok = False; notes.append(f"seeded conversation {cid} CHANGED {snap} -> {a}")
    new_ids = sorted(set(after["convs"]) - set(seeded))
    notes.append(f"run's own new conversations: {new_ids or 'none'}")
    for cid in new_ids:
        owner = after["convs"][cid]["session_id"]
        if run_session_id is not None and owner != run_session_id:
            ok = False
            notes.append(f"new conversation {cid} session_id {owner} != run session"
                         f" {run_session_id} (delta NOT confined to this run)")
    return ok, notes


# ── execution ────────────────────────────────────────────────────────────────

def pi_base() -> list:
    return [
        r2.PI, "--print", "--mode", "json",
        "--provider", "bosgame", "--model", "bosgame/qwen3.6-35b-vulkan-nothink",
        "--no-skills", "--no-context-files", "--no-prompt-templates", "--no-themes",
    ]


def invoke(cmd: list, worktree: Path, arm: str, store_dir: Path, out_file: Path,
           err_file: Path, timeout: int = RUN_TIMEOUT_SECONDS) -> dict:
    env = dict(
        os.environ,
        PI_CODING_AGENT_DIR=str(agent_dir(arm)),
        LCM_DB_DIR=str(store_dir),
        PI_OFFLINE="1", NO_COLOR="1",
    )
    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=worktree, env=env, capture_output=True,
                              text=True, timeout=RUN_TIMEOUT_SECONDS)
        status, code = "completed", proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        status, code = "timeout", None
        stdout = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    out_file.write_text(stdout)
    err_file.write_text(stderr)
    return {"status": status, "exit_code": code, "wall_seconds": round(time.time() - started, 2)}


def invoke_task(arm: str, worktree: Path, session_file: Path, prompt: str,
                run_dir: Path, store_dir: Path) -> dict:
    """Task invocation for ALL arms via the RPC driver (rpc_task.mjs):
    genuine switch_session resume (session_start reason 'resume' — the same
    runtime path the deck uses on reconnect) then the task prompt. Plain
    `--print --session` reports reason 'startup' and cannot arm the nudge
    gate (pi 0.84.4 CLI initial-runtime default); verified by the failed
    prep smoke of 2026-09-11T04:03Z and pi source
    dist/core/agent-session-runtime.js:141."""
    prompt_file = run_dir / "task-prompt.txt"
    prompt_file.write_text(prompt)
    events_file = run_dir / "stdout.txt"
    err_file = run_dir / "stderr.txt"
    # The driver streams pi's RPC events into events_file itself; invoke()'s
    # captured-subprocess output would clobber it, so it goes to its own file
    # (normally empty - the driver is silent on its own stdout).
    driver_out = run_dir / "driver-stdout.txt"
    cmd = ["node", str(EXP_DIR / "rpc_task.mjs"), str(session_file),
           str(prompt_file), str(events_file)]
    result = invoke(cmd, worktree, arm, store_dir, driver_out, err_file,
                    timeout=RUN_TIMEOUT_SECONDS + 25)
    if result["status"] == "completed":
        if result["exit_code"] == 3:
            result["status"] = "timeout"
        elif result["exit_code"] not in (0, None):
            result["status"] = f"rpc-exit-{result['exit_code']}"
    return result


def session_event_id(stdout: str) -> str | None:
    """The session id pi reported in its first 'session' event, if any."""
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") == "session" and e.get("id"):
                return e["id"]
    return None


def find_session_file(sessions_dir: Path, stdout: str) -> tuple:
    """Locate (session file, session id) pi created in this invocation."""
    sid = session_event_id(stdout)
    if sid is None:
        raise SystemExit("invocation emitted no session id")
    for f in sorted(sessions_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
        if sid in f.name or f.read_text(errors="replace")[:2000].find(sid) >= 0:
            return f, sid
    raise SystemExit(f"session file for {sid} not found under {sessions_dir}")


def nudge_evidence(stderr: str, stdout: str) -> dict:
    return {
        "registered": "pi-recall-nudge: registered" in stderr,
        "resume_armed": "resumption pending (session_start reason=" in stderr,
        "resume_reason": (stderr.split("resumption pending (session_start reason=")[1]
                          .split(")")[0] if "resumption pending (session_start reason=" in stderr else None),
        "injected": "pi-recall-nudge: injecting nudge" in stderr,
        "inject_line": next((l.strip() for l in stderr.splitlines()
                             if "injecting nudge" in l), None),
        "custom_message_in_transcript": '"customType":"recall-nudge"' in stdout.replace(" ", ""),
    }


def final_answer_text(stdout: str) -> str:
    """Last assistant message text from the event stream (verifiers score
    the agent's final answer; H2's work product IS the plan)."""
    best = ""
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") != "message_end":
            continue
        msg = e.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            best = content
        elif isinstance(content, list):
            best = "\n".join(b.get("text", "") for b in content
                             if isinstance(b, dict) and b.get("type") == "text")
    return best


def do_slot(case: dict, cid: str, arm: str, rep: int, tag: str = "") -> dict:
    run_dir = RUNS / f"{cid}-{arm.lower()}-rep{rep}{'-' + tag if tag else ''}"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    worktree = run_dir / "repo"
    r2.reset_worktree(case["repo"], worktree)
    store_dir = run_dir / "lcm"
    resolved = str(worktree.resolve())
    db = store_dir / f"{r2.hash_cwd(resolved)}.db"
    r2.seed_store(case["seed"], db, resolved)
    r2.verify_store_reachable(worktree, db)  # wiring receipt: raises on mismatch
    settings_sha = r2.sha256_file(agent_dir(arm) / "settings.json")
    before = store_snapshot(db)

    sessions = run_dir / "sessions"
    sessions.mkdir()
    prime_cmd = pi_base() + ["--session-dir", str(sessions), PRIME_PROMPT]
    prime = invoke(prime_cmd, worktree, arm, store_dir,
                   run_dir / "prime-stdout.txt", run_dir / "prime-stderr.txt")
    prime_parsed = r2.parse_events((run_dir / "prime-stdout.txt").read_text())
    session_file, session_id = find_session_file(
        sessions, (run_dir / "prime-stdout.txt").read_text())

    task = invoke_task(arm, worktree, session_file, case["prompt"], run_dir, store_dir)
    task_parsed = r2.parse_events((run_dir / "stdout.txt").read_text())
    stderr = (run_dir / "stderr.txt").read_text()
    stdout = (run_dir / "stdout.txt").read_text()

    after = store_snapshot(db)
    iso_ok, iso_notes = check_isolation(before, after, db,
                                        r2.node_cwd_hash(worktree), session_id)
    new_ids = sorted(set(after["convs"]) - set(before["convs"]))

    v = case["verifier"]
    final_answer_path = run_dir / "final-answer.txt"
    final_answer_path.write_text(final_answer_text(stdout))
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

    row = {
        "run": run_dir.name, "case": cid, "kind": case["kind"], "arm": arm, "rep": rep,
        "prompt_sha256": hashlib.sha256(case["prompt"].encode()).hexdigest(),
        "prime_prompt": PRIME_PROMPT,
        "config_ref": f"~/.pi-experiment-b/arm-{arm.lower()}/settings.json",
        "settings_sha256": settings_sha,
        "packages": ARMS_B[arm]["packages"],
        "session_file": str(session_file), "session_id": session_id,
        "prime": {"status": prime["status"], "wall_seconds": prime["wall_seconds"],
                  "usage": prime_parsed["usage"]},
        "task": {"status": task["status"], "exit_code": task["exit_code"],
                 "wall_seconds": task["wall_seconds"]},
        "usage": task_parsed["usage"],
        "tool_calls": task_parsed["tool_calls"],
        "recall_calls": sum(1 for t in task_parsed["tool_calls"] if t == "project_recall"),
        "relaxation_marks": stdout.count("RELAXATION-SOURCED"),
        "nudge": nudge_evidence(stderr, stdout),
        "verifier": verdict, "verifier_stdout": v_stdout,
        "isolation_ok": iso_ok, "isolation_notes": iso_notes,
        # planner rule 4 records: (1) actual db + effective config above;
        # (2) seeded-unchanged + delta confinement in isolation_*; (3) the
        # recall connection is read-only by extension design (node:sqlite
        # readonly:true, extensions/pi-project-recall test suite) and the
        # delta check above confines writes; (4) reachability receipt below.
        "reachability": {
            "wiring": "seeded db stem == runtime cwd hash (verify_store_reachable)",
            "store_opened_by_runtime": bool(new_ids),
            "seed_ids_surfaced_in_output": any(s in stdout for s in before["convs"]),
            "note": ("arm A has no recall tool; through-tool retrieval is n/a "
                     "by design - runtime-opened store evidenced by the run's "
                     "own conversation written into the seeded db"),
        },
        "store_db": str(db),
        "digest_initial": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=worktree,
                                         capture_output=True, text=True).stdout.strip(),
        "digest_final": r2.tree_digest(worktree),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    ledger = PRIVATE / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    print(json.dumps({k: row[k] for k in
                      ("run", "verifier", "recall_calls", "isolation_ok")}))
    print(json.dumps(row["nudge"]))
    return row


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_setup(args) -> None:
    cases = load_cases()
    for arm in ARMS_B:
        print(f"agent dir {agent_dir(arm)}")
    PRIVATE.mkdir(parents=True, exist_ok=True)
    manifest = {
        "prepared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "harness": {"path": str(Path(__file__).resolve()),
                    "sha256": r2.sha256_file(Path(__file__))},
        "cases": {cid: {
            "kind": c["kind"], "prompt": c["prompt"],
            "case_json": r2.sha256_file(c["dir"] / "case.json"),
            "seed": r2.sha256_file(c["seed"]),
            "verifier": r2.sha256_file(c["verifier"]),
            "repo_digest": tree_digest_flat(c["repo"]),
        } for cid, c in cases.items()},
        "schedule": json.loads(SCHEDULE_PATH.read_text()) if SCHEDULE_PATH.exists() else None,
    }
    (PRIVATE / "PREP_MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print(f"prep manifest: {PRIVATE / 'PREP_MANIFEST.json'}")


def tree_digest_flat(path: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(str(f.relative_to(path)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def cmd_schedule(args) -> None:
    cases = load_cases()
    blocks = build_schedule(cases)
    if args.write:
        SCHEDULE_PATH.write_text(json.dumps(blocks, indent=1) + "\n")
        print(f"wrote {SCHEDULE_PATH} (for the freeze commit)")
    print(json.dumps(blocks, indent=1))


def cmd_slot(args) -> None:
    cases = load_cases()
    do_slot(cases[args.case], args.case, args.arm, args.rep, tag=args.tag)


def cmd_walk(args) -> None:
    cases = load_cases()
    blocks = json.loads(SCHEDULE_PATH.read_text())
    for b in blocks:
        for arm in b["order"]:
            do_slot(cases[b["case"]], b["case"], arm, b["rep"])


def cmd_analyze(args) -> None:
    rows = [json.loads(l) for l in (PRIVATE / "ledger.jsonl").read_text().splitlines() if l.strip()]
    for r in rows:
        print(json.dumps({k: r.get(k) for k in
                          ("run", "verifier", "recall_calls", "relaxation_marks",
                           "isolation_ok")}))
        print("  nudge:", json.dumps(r.get("nudge")))
    print(f"total rows: {len(rows)}")


def cmd_smoke(args) -> None:
    """ONE pre-evaluation smoke of the extension PAIR under daily-like
    settings (arm C packages, pi-lcm ACTIVE so normal writes occur), through
    the genuine prime+resume path, with receipt. Not an evaluation slot."""
    out = Path(args.out).expanduser().resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    src = out / "_src"
    src.mkdir(parents=True)
    for rel, content in r2.SMOKE_FILES.items():
        f = src / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    worktree = out / "repo"
    r2.reset_worktree(src, worktree)
    store_dir = out / "lcm"
    resolved = str(worktree.resolve())
    db = store_dir / f"{r2.hash_cwd(resolved)}.db"
    r2.seed_store(SMOKE_SEED, db, resolved)
    r2.verify_store_reachable(worktree, db)
    before = store_snapshot(db)

    sessions = out / "sessions"
    sessions.mkdir()
    settings_sha = r2.sha256_file(agent_dir("C") / "settings.json")
    prime = invoke(pi_base() + ["--session-dir", str(sessions), PRIME_PROMPT],
                   worktree, "C", store_dir,
                   out / "prime-stdout.txt", out / "prime-stderr.txt")
    session_file, session_id = find_session_file(
        sessions, (out / "prime-stdout.txt").read_text())
    task_prompt = (
        "In this repository, `kettle/greet.py` has a function `greet(name)` that ignores "
        "its argument and always returns \"hello\". Read the file, then edit it so it returns "
        "\"hello NAME\" for the name it is given. When you have made the edit, say DONE.")
    task = invoke_task("C", worktree, session_file, task_prompt, out, store_dir)
    parsed = r2.parse_events((out / "stdout.txt").read_text())
    stderr = (out / "stderr.txt").read_text()
    stdout = (out / "stdout.txt").read_text()
    after = store_snapshot(db)
    iso_ok, iso_notes = check_isolation(before, after, db,
                                        r2.node_cwd_hash(worktree), session_id)

    nud = nudge_evidence(stderr, stdout)
    prime_stderr = (out / "prime-stderr.txt").read_text()
    prime_nud = nudge_evidence(prime_stderr, (out / "prime-stdout.txt").read_text())

    # [7] deterministic reachability probe (Stage-A pattern): one separate
    # short arm-C invocation through the real recall path. The TASK run's
    # recall results are model-query-dependent (recorded as observables
    # below); the probe isolates the mechanism.
    probe_prompt = ('Use the project_recall tool now with query "SMOKE-B-7f3b" '
                    'and scope "all". Reply with what it returns. Do not edit any files.')
    probe = invoke(pi_base() + ["--session-dir", str(sessions), probe_prompt],
                   worktree, "C", store_dir,
                   out / "probe-stdout.txt", out / "probe-stderr.txt")
    probe_stdout = (out / "probe-stdout.txt").read_text(errors="replace")
    probe_ok = ("SMOKE-B-7f3b" in probe_stdout and "seed-smoke-prior" in probe_stdout)

    lines = [
        f"pair smoke (arm C packages; pi-lcm ACTIVE): prime {prime['status']} "
        f"{prime['wall_seconds']}s | task {task['status']} {task['wall_seconds']}s",
        f"worktree (resolved): {resolved}",
        f"store: {db} | runtime hash match: {db.stem == r2.node_cwd_hash(worktree)}",
        f"config: ~/.pi-experiment-b/arm-c/settings.json sha256 {settings_sha}",
        f"packages: {ARMS_B['C']['packages']}",
        f"session: prime id {session_id} -> resumed via RPC switch_session "
        f"(runtime switchSession -> session_start reason resume) {session_file.name}",
        "",
        f"[1] genuine resume: task session resumed through the RPC switch_session path",
        f"    extension saw session_start reason: {nud['resume_reason']!r} "
        f"(receipt line: resumption pending ... reason=...) -> {nud['resume_armed']}",
        f"[2] nudge fired on the task prompt only: injected={nud['injected']} "
        f"line={nud['inject_line']!r}",
        f"    prime (fresh session, reason new) injected: {prime_nud['injected']} "
        f"(must be False)",
        f"    [recall-nudge] custom message in transcript: {nud['custom_message_in_transcript']}",
        f"[3] pair registered: project_recall registered line: "
        f"{'registered project_recall' in stderr} | pi-recall-nudge registered: {nud['registered']}",
        f"[4] pi-lcm ACTIVE (normal writes): {iso_notes}",
        f"[5] isolation (planner rule 4): seeded rows unchanged + deltas confined: {iso_ok}",
        f"    recall tool connection read-only: extension-level property, "
        f"extensions/pi-project-recall test suite (node:sqlite readonly:true)",
        f"[6] observables: project_recall calls "
        f"{sum(1 for t in parsed['tool_calls'] if t == 'project_recall')}"
        f" | RELAXATION-SOURCED marks {stdout.count('RELAXATION-SOURCED')}",
        f"    task usage totalTokens: {parsed['usage']['totalTokens']}",
        f"[7] reachability (Stage-A pattern, dedicated probe {probe['status']} "
        f"{probe['wall_seconds']}s): SMOKE-B-7f3b + seed-smoke-prior surfaced"
        f" through the real recall path: {probe_ok}",
        f"    task-run observables (model-dependent, not gates): marker in task"
        f" output: {'SMOKE-B-7f3b' in stdout} | seeded id in task output: "
        f"{'seed-smoke-prior' in stdout}",
    ]
    verdict_ok = (nud["resume_armed"] and nud["resume_reason"] in ("resume", "fork")
                  and nud["injected"] and not prime_nud["injected"]
                  and nud["custom_message_in_transcript"] and nud["registered"]
                  and "registered project_recall" in stderr and iso_ok
                  and probe_ok)
    lines += ["", "PAIR SMOKE RECEIPT: PASS" if verdict_ok else "PAIR SMOKE RECEIPT: FAIL"]
    (out / "SMOKE_RECEIPT.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    p = sub.add_parser("schedule"); p.add_argument("--write", action="store_true")
    p = sub.add_parser("slot"); p.add_argument("case"); p.add_argument("arm", choices=list(ARMS_B))
    p.add_argument("rep", type=int, choices=[1, 2]); p.add_argument("--tag", default="")
    sub.add_parser("walk")
    sub.add_parser("analyze")
    p = sub.add_parser("smoke"); p.add_argument("--out", required=True)
    args = ap.parse_args()
    {"setup": cmd_setup, "schedule": cmd_schedule, "slot": cmd_slot,
     "walk": cmd_walk, "analyze": cmd_analyze, "smoke": cmd_smoke}[args.cmd](args)


if __name__ == "__main__":
    main()
