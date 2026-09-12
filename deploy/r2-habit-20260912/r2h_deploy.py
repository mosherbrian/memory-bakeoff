#!/usr/bin/env python3
"""
r2h_deploy.py — Brian's work-machine deploy package for the R2 explicit-prompt
habit arm (v2 design: team/PROPOSAL-R2-explicit-prompt-habit.md, FINAL GO
2026-09-12). Self-contained: Python 3 stdlib only, no network calls, no
telemetry, no fleet contact of any kind. Everything it collects stays on this
machine until you choose to send the bundle somewhere.

Commands:
  check           environment check (pi, agent dir, settings, stores, env vars)
  install-check   verify both extensions are installed and registered
  smoke           day-0 smoke cycle -> smoke receipt (before day 1 counts)
  flip            daily arm helper: prints the shell line for today's arm
                  (use:  eval "$(python3 r2h_deploy.py flip)")
  status          show progress through the 10 counted days
  close           build the return bundle (receipts + session slices +
                  arm-stripped slice + redaction log template; store hashes
                  only, never the store itself)

State lives in ~/.r2h (override: R2H_STATE). The pi agent dir is
~/.pi/agent (override: PI_CODING_AGENT_DIR). The schedule below is frozen
(see SCHEDULE.txt / FREEZE.md in this directory); do not edit it.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

SEED = "9e2aac78cbc3243967a557cd10fddf7a2382046516e90e9e6ce196f0c38371e7"
N_DAYS = 10
SCHEDULE = {1:"ON",2:"ON",3:"OFF",4:"ON",5:"ON",6:"OFF",7:"ON",8:"OFF",9:"OFF",10:"OFF"}

def derive_schedule(seed=SEED, n=N_DAYS):
    pairs = sorted((hashlib.sha256(f"{seed}:day{i}:perm".encode()).hexdigest(), i)
                   for i in range(1, n + 1))
    return {d: ("ON" if r < n // 2 else "OFF") for r, (_, d) in enumerate(pairs)}

assert derive_schedule() == SCHEDULE, "embedded schedule does not derive from seed"

DEFAULT_PROMPT = ("Summarize what past sessions in this project established "
                  "about decisions or constraints relevant to continuing work here.")
SMOKE_TIMEOUT = 480  # seconds; the pilot line's per-run ceiling

def state_dir() -> Path:
    p = Path(os.environ.get("R2H_STATE", Path.home() / ".r2h")); p.mkdir(parents=True, exist_ok=True); return p
def agent_dir() -> Path:
    return Path(os.environ.get("PI_CODING_AGENT_DIR", Path.home() / ".pi" / "agent"))
def state() -> dict:
    f = state_dir() / "state.json"
    return json.loads(f.read_text()) if f.exists() else {"days_flipped": 0, "log": []}
def save_state(s): (state_dir() / "state.json").write_text(json.dumps(s, indent=1))
def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()
def store_for_cwd(cwd: str) -> Path:
    return agent_dir() / "lcm" / (hashlib.sha256(cwd.encode()).hexdigest()[:16] + ".db")
def log(s, ev): s["log"].append({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": ev}); save_state(s)

def cmd_check(a):
    s = state(); rows, ok = [], True
    def row(name, good, detail): nonlocal ok; rows.append((name, good, detail)); ok = ok and good
    pi = shutil.which("pi")
    if pi:
        v = subprocess.run(["pi", "--version"], capture_output=True, text=True, timeout=30)
        row("pi binary", True, f"{pi} ({(v.stdout or v.stderr).strip()[:60]})")
    else: row("pi binary", False, "not on PATH")
    ad = agent_dir(); row("pi agent dir", ad.is_dir(), str(ad))
    st = ad / "settings.json"
    if st.exists():
        try:
            cfg = json.loads(st.read_text())
            row("settings.json parses", True, f"{len(cfg.get('packages', []))} package(s)")
        except Exception as e: row("settings.json parses", False, str(e))
    else: row("settings.json", False, "missing")
    lcm = ad / "lcm"
    ndb = len(list(lcm.glob("*.db"))) if lcm.is_dir() else 0
    row("pi-lcm store dir", lcm.is_dir() and ndb > 0, f"{ndb} store(s) in {lcm}")
    my_store = store_for_cwd(os.getcwd())
    row("store for cwd", my_store.exists(), f"{my_store}" + (f" ({my_store.stat().st_size} bytes)" if my_store.exists() else " — no prior conversations here yet"))
    row("PI_PROJECT_RECALL", os.environ.get("PI_PROJECT_RECALL") != "0", "unset/unless 0 = tool active (required)")
    row("PI_RECALL_NUDGE", os.environ.get("PI_RECALL_NUDGE") is None, "unset = nudge active (flip manages this)")
    for name, good, detail in rows: print(f"  {'PASS' if good else 'FAIL'}  {name}: {detail}")
    print(f"\ncheck: {'ALL PASS' if ok else 'FAILURES PRESENT — fix before day 0 smoke'}")
    log(s, f"check {'pass' if ok else 'fail'}")

def cmd_install_check(a):
    st = agent_dir() / "settings.json"
    try: pkgs = json.loads(st.read_text()).get("packages", [])
    except Exception as e: print(f"FAIL  cannot read {st}: {e}"); return 1
    want = [("pi-project-recall", ("project_recall",)), ("pi-recall-nudge", ("recall-nudge",))]
    ok = True
    for name, markers in want:
        hit = next((p for p in pkgs if name in str(p)), None)
        if not hit: print(f"FAIL  {name}: no packages entry mentioning it"); ok = False; continue
        idx = Path(hit) / "index.ts"
        if not idx.exists(): print(f"FAIL  {name}: {hit} has no index.ts"); ok = False; continue
        src = idx.read_text(errors="replace")
        miss = [m for m in markers if m not in src]
        print(f"{'PASS' if not miss else 'FAIL'}  {name}: registered at {hit}" + (f", MISSING markers: {miss}" if miss else ""))
        ok = ok and not miss
    print("\ninstall-check: " + ("BOTH EXTENSIONS INSTALLED AND REGISTERED" if ok else "INCOMPLETE — see above"))
    log(state(), f"install-check {'pass' if ok else 'fail'}")
    return 0 if ok else 1

def _newest_session_since(t0: float):
    sess = agent_dir() / "sessions"; best, bmt = None, t0
    if not sess.is_dir(): return None
    for f in sess.rglob("*.jsonl"):
        try: mt = f.stat().st_mtime
        except OSError: continue
        if mt >= bmt: best, bmt = f, mt
    return best

def cmd_smoke(a):
    s = state()
    cwd = os.getcwd(); store = store_for_cwd(cwd)
    if not store.exists(): print(f"WARN  no pi-lcm store for {cwd} — recall would have nothing prior to deliver; run the smoke in a real project with history.")
    pre = sha256_file(store) if store.exists() else None
    print(f"store sha256 (pre):  {pre or 'n/a'}")
    cmd = a.pi_cmd.split() + (["--continue"] if a.resume == "continue" else []) + \
          (["--session", a.session] if a.session else []) + ["-p", a.prompt]
    print("running:", " ".join(cmd), f"(timeout {SMOKE_TIMEOUT}s)")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=SMOKE_TIMEOUT)
    dur = time.time() - t0
    out = r.stdout or ""; err = r.stderr or ""
    post = sha256_file(store) if store.exists() else None
    print(f"store sha256 (post): {post or 'n/a'}  (exit={r.returncode}, {dur:.0f}s)")
    sess = _newest_session_since(t0 - 5)
    raw = sess.read_text(errors="replace") if sess else ""
    hay = out + "\n" + err + "\n" + raw
    checks = {
        "pi_ran": r.returncode == 0 and bool(out.strip() or raw.strip()),
        "nudge_delivered": ("recall-nudge" in raw),
        "recall_registered": ("project_recall" in hay),
        "recall_invoked": hay.count("project_recall") > 1 or "toolExecution" in hay and "project_recall" in hay,
        "store_named": bool(post and store.name in hay),
        "prior_id_surfaced": bool(re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", hay.replace(str(sess), ""))),
        "store_unmodified": (pre == post),
    }
    hard = checks["pi_ran"] and checks["nudge_delivered"] and checks["recall_registered"] and checks["store_unmodified"]
    warn = [k for k in ("recall_invoked", "store_named", "prior_id_surfaced") if not checks[k]]
    verdict = "PASS" if hard else "FAIL"
    sdir = state_dir() / "smoke"; sdir.mkdir(exist_ok=True)
    rec = {"verdict": verdict, "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "cwd": cwd, "cmd": cmd, "exit": r.returncode, "duration_s": round(dur, 1),
           "store": str(store), "store_sha_pre": pre, "store_sha_post": post,
           "session_file": str(sess) if sess else None, "checks": checks,
           "warnings": warn + ["prior_id/store_named depend on query match — a WARN here is the F2 c1/c3 failure mode, report it, do not retry"],
           "note": "string-level evidence from the persisted session file (state, not receipts)"}
    (sdir / "smoke-receipt.json").write_text(json.dumps(rec, indent=1))
    (sdir / "smoke-receipt.txt").write_text(json.dumps(rec, indent=1) + f"\n\n--- pi stdout (first 2000 chars) ---\n{out[:2000]}\n")
    for k, v in checks.items(): print(f"  {'PASS' if v else 'MISS'}  {k}")
    print(f"\nsmoke verdict: {verdict}" + (f"  (warnings: {', '.join(warn)})" if warn else ""))
    print(f"receipt: {sdir/'smoke-receipt.json'}  — send this back before day 1 counts.")
    log(s, f"smoke {verdict}"); s["day0_ts"] = rec["ts"]; save_state(s)
    return 0 if hard else 1

def cmd_flip(a):
    s = state()
    day = s["days_flipped"] + 1
    if day > N_DAYS:
        print(f"# schedule complete ({N_DAYS}/{N_DAYS} days). Run: python3 {Path(__file__).name} close", file=sys.stderr)
        return 0
    arm = SCHEDULE[day]
    print("unset PI_RECALL_NUDGE" if arm == "ON" else "export PI_RECALL_NUDGE=0")
    print(f"# R2H day {day}/{N_DAYS}: {arm} — this shell only. Work normally.", file=sys.stderr)
    s["days_flipped"] = day; log(s, f"flip day{day} {arm}")
    return 0

def cmd_status(a):
    s = state(); d = s["days_flipped"]
    arms = " ".join(f"d{i}:{SCHEDULE[i]}" for i in range(1, N_DAYS + 1))
    print(f"days flipped: {d}/{N_DAYS}\nschedule: {arms}\nlog entries: {len(s['log'])}")
    return 0

def _strip_arm(path: Path, dest: Path) -> int:
    dropped = 0
    with open(path, errors="replace") as src, open(dest, "w") as out:
        for line in src:
            if "recall-nudge" in line: dropped += 1; continue
            out.write(line)
    return dropped

def cmd_close(a):
    s = state(); sdir = state_dir()
    t0 = s.get("day0_ts") or (s["log"][0]["ts"] if s["log"] else datetime.now(timezone.utc).isoformat())
    def within(p):
        try: mt = p.stat().st_mtime
        except OSError: return False
        return mt >= time.mktime(time.strptime(t0[:19], "%Y-%m-%dT%H:%M:%S")) - 86400
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    b = sdir / f"bundle-{ts}"; raw = b / "raw"; b.mkdir(parents=True); raw.mkdir()
    munged = re.sub(r"[^A-Za-z0-9._-]", "-", os.getcwd().strip("/"))
    manifest, missing = [], []
    sess_root = agent_dir() / "sessions"
    picked = [f for f in sess_root.rglob("*.jsonl") if within(f) and munged in str(f)] if sess_root.is_dir() else []
    if not picked and sess_root.is_dir(): picked = [f for f in sess_root.rglob("*.jsonl") if within(f)]
    for f in picked:
        d = raw / f"{len(manifest):03d}-{f.name}"; shutil.copy2(f, d)
        manifest.append({"file": d.name, "sha256": sha256_file(d), "why": f"session slice (project match: {munged in str(f)})"})
    stripped = b / "stripped"; stripped.mkdir()
    ndrop = 0
    for i, f in enumerate(picked):
        ndrop += _strip_arm(raw / f"{i:03d}-{f.name}", stripped / f"{i:03d}-{f.name}")
    for pat, why in ((("notifications.jsonl",), "pi notifications log"), (("traces",), "pi traces")):
        found = [p for p in agent_dir().rglob(pat[0]) if p.is_file() and within(p)]
        for f in found[:50]:
            d = raw / f"agent-{f.name}"; shutil.copy2(f, d)
            manifest.append({"file": d.name, "sha256": sha256_file(d), "why": why})
        if not found: missing.append(f"{pat[0]}: none found under {agent_dir()} in window (recorded, not fabricated)")
    lcm = agent_dir() / "lcm"; stores = []
    if lcm.is_dir():
        for f in sorted(lcm.glob("*.db")):
            st = f.stat(); stores.append({"file": f.name, "sha256": sha256_file(f), "bytes": st.st_size, "mtime": st.st_mtime})
    (b / "stores-HASHES-ONLY.json").write_text(json.dumps(stores, indent=1))
    for f in [sdir / "state.json", sdir / "smoke" / "smoke-receipt.json"]:
        if f.exists():
            d = raw / f"deploy-{f.name}"; shutil.copy2(f, d)
            manifest.append({"file": d.name, "sha256": sha256_file(d), "why": "deploy state / smoke receipt"})
    (b / "REDACTION-LOG.md").write_text(
        "# Redaction log (required if you removed anything)\n\n"
        "Delete or edit any file in raw/ or stripped/ you wish, then add one line here\n"
        "per removal: <file> — <what it contained, one sentence>. Undeclared removals\n"
        "make the denominators uninterpretable; declared ones are honored and reported.\n\n"
        "- (none)\n")
    manifest.append({"file": "stripped/", "note": f"arm-stripped copies of the {len(picked)} session slice(s); {ndrop} line(s) containing 'recall-nudge' removed — this is the slice the blind rater sees",
                     "sha256": sha256_file(b / "stripped" / f"000-{picked[0].name}") if picked and (b / "stripped" / f"000-{picked[0].name}").exists() else "empty"})
    (b / "manifest.json").write_text(json.dumps({
        "bundle": b.name, "created": ts, "arm_design": "PROPOSAL-R2-explicit-prompt-habit.md v2",
        "schedule_seed_sha256": hashlib.sha256((SEED + "\n").encode()).hexdigest(),
        "days_flipped": s["days_flipped"], "flip_log": s["log"],
        "expected_but_absent": missing, "store_dbs_included": False,
        "network_calls": "none — this script never opens a socket",
        "files": manifest}, indent=1))
    print(f"bundle: {b}\n  raw session slices: {len(picked)}   arm-stripped: {ndrop} line(s) removed"
          f"\n  stores: hashes only ({len(stores)} files)   absent-expected: {len(missing)}"
          f"\n  Next: review, redact if you like (log it), send the bundle anywhere you choose.")

def main():
    p = argparse.ArgumentParser(description="R2 explicit-prompt habit arm — work-machine deploy")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check"); sub.add_parser("install-check")
    sm = sub.add_parser("smoke")
    sm.add_argument("--prompt", default=DEFAULT_PROMPT); sm.add_argument("--resume", choices=["continue", "none"], default="continue")
    sm.add_argument("--session"); sm.add_argument("--pi-cmd", default="pi")
    sub.add_parser("flip"); sub.add_parser("status"); sub.add_parser("close")
    a = p.parse_args()
    {"check": cmd_check, "install-check": cmd_install_check, "smoke": cmd_smoke,
     "flip": cmd_flip, "status": cmd_status, "close": cmd_close}[a.cmd](a)

if __name__ == "__main__":
    main()
