#!/usr/bin/env python3
"""R9-execution-2 operator: four pre-registered phases on kiln, each in a fresh
conversation opened with /new (R10). No stop, start or state-file edit.
Every observation goes to execution-2/log.jsonl."""
import hashlib, json, os, re, secrets, shutil, socket, subprocess, sys, time
from datetime import datetime, timezone

PKG = "/home/bmosher/memory-bake-off/campaign4/packages/R9-paired-restart-pilot"
EX = f"{PKG}/execution-2"
R8 = "/home/bmosher/memory-bake-off/campaign4/packages/R8-work-task-feasibility/director-closure"
AD = "/home/bmosher/.config/agent-deck"
SEAT = "a79067ca-1790000758"
SOCK = f"{AD}/acp-sock/{SEAT}.sock"
HIST = f"{AD}/acp-history/{SEAT}.jsonl"
STATE = f"{AD}/acp-sessions/{SEAT}.json"
WORKER_FILE = f"{AD}/acp-worker"
R10_SHA = "083f6eb7072f53a097b68451d37ac9074fdd7ccb8703f87302dfe0373dca1dbd"
ARMS = "/var/home/bmosher/r9-arms/execution-2"
END = datetime.fromisoformat("2026-09-25T15:29:01.559743+00:00").timestamp()
CLOSEOUT = 240
T = lambda n: open(f"{PKG}/templates/{n}").read()


def iso(t=None):
    return datetime.fromtimestamp(t if t is not None else time.time(), timezone.utc).isoformat()


def log(event, **kw):
    rec = {"at": iso(), "event": event, **kw}
    with open(f"{EX}/log.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec)[:600], flush=True)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sock(text, timeout=10):
    s = socket.socket(socket.AF_UNIX)
    s.settimeout(timeout)
    s.connect(SOCK)
    s.sendall((json.dumps({"text": text}) + "\n").encode())
    buf = b""
    while not buf.endswith(b"\n"):
        c = s.recv(65536)
        if not c:
            break
        buf += c
    s.close()
    return json.loads(buf)


def socket_pid():
    """Bind the named socket to its worker. This sandbox cannot read another
    process's fd links, so use the director's verified join (R10
    activation-reconciliation.json: inode 554033536 held by pid 4141367 via
    fd 4, start 1790346647.69) and require that the socket inode and that
    process (same start time) are both unchanged now."""
    rec = json.load(open("/home/bmosher/memory-bake-off/campaign4/packages/R10-runtime-new-session/activation-reconciliation.json"))
    inodes = [l.split()[6] for l in open("/proc/net/unix") if l.rstrip().endswith(SOCK) and len(l.split()) >= 8]
    pid = rec["worker_pid"]
    try:
        same_proc = abs(proc_start(pid) - rec["process_start"]) < 1
    except OSError:
        same_proc = False
    return (pid if inodes == rec["socket_inodes"] and same_proc else None), inodes


def proc_start(pid):
    clk = os.sysconf("SC_CLK_TCK")
    boot = float([l for l in open("/proc/stat") if l.startswith("btime")][0].split()[1])
    return boot + int(open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()[19]) / clk


def outbox_ok():
    import sqlite3
    st = json.loads(subprocess.run(["/home/bmosher/.local/bin/agent-loop", "status", "--config",
                                    "/home/bmosher/.config/agent-loop/campaign4.json", "--json"],
                                   capture_output=True, text=True).stdout)
    step = {p["qid"]: p["step"] for p in st["packages"]}
    executing = [p["qid"] for p in st["packages"] if p["step"] in ("worker", "verify")
                 and p["principals"]["worker"]["seat"] == "kiln"]
    c = sqlite3.connect("file:/home/bmosher/.local/share/agent-loop/campaign4.db?mode=ro", uri=True)
    kv = dict(c.execute("select key,value from driver_kv"))
    rows = []
    for k, v in kv.items():
        if k.startswith("outbox-pending:"):
            r = json.loads(v)
            if kv.get("route:" + r["target"]) == SEAT:
                pk = r["payload"].get("package")
                claim = os.path.exists(f"/home/bmosher/.local/share/agent-loop/campaign4/claims/{r['execution']}.json")
                acked = kv.get(f"deadline:{pk}:{r['target']}:stop") == "delivered-acked"
                rows.append((r["execution"], step.get(pk), claim, acked))
    unresolved = [r for r in rows if not ((r[1] == "closed" and r[2]) or (r[1] == "timed-out" and r[3]))]
    return executing, len(rows), unresolved


def precheck(label):
    pid, inodes = socket_pid()
    feats = json.load(open(STATE)).get("features", [])
    p = sock("/ping")
    executing, n, unresolved = outbox_ok()
    ok = (sha(WORKER_FILE) == R10_SHA and pid is not None and proc_start(pid) > os.stat(WORKER_FILE).st_mtime
          and "new" in feats and p == {"ok": True, "status": "idle"} and not executing and not unresolved)
    log("precheck", label=label, worker_pid=pid, socket_inodes=inodes, features=feats, ping=p,
        kiln_executing=executing, kiln_outbox_rows=n, unresolved=unresolved, ok=ok)
    if not ok:
        raise SystemExit(f"precheck failed at {label}")
    return pid


def hist_len():
    return sum(1 for _ in open(HIST))


def hist_from(n):
    return [json.loads(l) for l in list(open(HIST))[n:]]


def new_session(label, seen):
    n = hist_len()
    r = sock("/new", 60)
    st = r.get("status", "")
    m = re.fullmatch(r"new (ses_\w+)( - .*)?", st)
    sid = m.group(1) if m else None
    b = [h for h in hist_from(n) if h.get("text", "").startswith("[new session]")]
    ok = bool(r.get("ok")) and sid is not None and "REFUSED" not in st and sid not in seen and len(b) == 1 \
        and b[0]["text"].split(" -> ")[1].startswith(sid)
    log("new", label=label, reply=r, sid=sid, boundary=b, ok=ok)
    if not ok:
        raise SystemExit(f"/new failed at {label}: {r}")
    seen.add(sid)
    return sid


def turn(text, deadline, unit):
    when = datetime.fromtimestamp(deadline, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    open(f"{EX}/active-{unit}", "w").write(iso())
    rc = subprocess.run(["systemd-run", "--user", f"--unit={unit}", f"--on-calendar={when}",
                         "--timer-property=AccuracySec=1s", sys.executable, os.path.abspath(__file__), "cancel", unit],
                        capture_output=True, text=True)
    log("timer-armed", unit=unit, at=when, rc=rc.returncode, err=rc.stderr.strip()[-200:])
    n = hist_len()
    t0 = time.time()
    r = sock(text)
    log("sent", unit=unit, reply=r, chars=len(text))
    time.sleep(3)
    while True:
        try:
            p = sock("/ping", 5)
        except OSError as e:
            p = {"status": f"error {e}"}
        if p.get("status") == "idle":
            break
        if time.time() > deadline + 60:
            log("overrun", unit=unit, ping=p)
            break
        time.sleep(5)
    os.remove(f"{EX}/active-{unit}")
    subprocess.run(["systemctl", "--user", "stop", f"{unit}.timer"], capture_output=True)
    cancelled = os.path.exists(f"{EX}/{unit}.cancelled")
    recs = hist_from(n)
    reply = "\n".join(h["text"] for h in recs if h.get("role") == "assistant")
    promise = sum(1 for h in recs if h.get("role") == "user" and h is not recs[0])
    log("turn-end", unit=unit, seconds=round(time.time() - t0, 1), cancelled_by_timer=cancelled,
        records=len(recs), extra_user_prompts=promise)
    open(f"{EX}/{unit}-records.jsonl", "w").write("".join(json.dumps(h) + "\n" for h in recs))
    return reply, cancelled


def confirm_fresh(sid, label):
    eng = subprocess.run(["opencode", "session", "list"], capture_output=True, text=True, timeout=60).stdout
    st = json.load(open(STATE)).get("sessionId")
    log("fresh-confirm", label=label, sid=sid, engine_store=sid in eng, state_sessionId=st, state_matches=st == sid)


def make_arm(arm):
    d = f"{ARMS}/{arm}"
    os.makedirs(f"{d}/notes")
    shutil.copy2(f"{R8}/broken.sh", f"{d}/fleet-poller.sh")
    for f in ("test-fleet-poller.sh", "rowcheck", "acp-worker"):
        shutil.copy2(f"{R8}/{f}", f"{d}/{f}")
    log("arm-created", arm=arm, dir=d, sha={f: sha(f"{d}/{f}") for f in sorted(os.listdir(d)) if os.path.isfile(f"{d}/{f}")})
    return d


def run_test(arm, d, label):
    cmd = f"cd {d} && ROWCHECK_BIN={d}/rowcheck ACP_WORKER={d}/acp-worker bash {d}/test-fleet-poller.sh {d}/fleet-poller.sh"
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=300)
    open(f"{EX}/{arm}-{label}-test.out", "w").write(r.stdout + r.stderr)
    diff = subprocess.run(["diff", "-u", f"{R8}/broken.sh", f"{d}/fleet-poller.sh"], capture_output=True, text=True).stdout
    open(f"{EX}/{arm}-{label}-fleet-poller.diff", "w").write(diff)
    log("test", arm=arm, label=label, rc=r.returncode, last=(r.stdout.strip().splitlines() or [""])[-1],
        skips=sum("SKIP" in l for l in r.stdout.splitlines()),
        unchanged={f: sha(f"{d}/{f}") == sha(f"{R8}/{f}") for f in ("test-fleet-poller.sh", "rowcheck", "acp-worker")},
        files=sorted(os.listdir(d)), notes=sorted(os.listdir(f"{d}/notes")))


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace("{" + k + "}", v)
    return tpl


def deadline_for(left):
    return min(time.time() + 600, END - CLOSEOUT - (left - 1) * 620)


def main():
    os.makedirs(EX, exist_ok=True)
    precheck("start")
    seen = {json.load(open(STATE)).get("sessionId")} - {None}
    seen |= set(re.findall(r"ses_\w+", subprocess.run(["opencode", "session", "list"], capture_output=True, text=True, timeout=60).stdout))
    bit = secrets.randbits(1)
    order = ["T", "C"] if bit == 0 else ["C", "T"]
    log("order", random_bit=bit, order=order)
    left = 4
    for arm in order:
        d = make_arm(arm)
        run_test(arm, d, "pre")
        precheck(f"{arm}-p1")
        sid = new_session(f"{arm}-p1", seen)
        dl = deadline_for(left); left -= 1
        reply, cut = turn(fill(T("phase1-task.txt"), ARM=arm, ARM_DIR=d, PHASE_MIN=str(round((dl - time.time()) / 60)),
                               DEADLINE_UTC=iso(dl)), dl, f"r9e2-{arm}-p1")
        confirm_fresh(sid, f"{arm}-p1")
        open(f"{EX}/{arm}-p1-reply.txt", "w").write(reply)
        summary = ""
        if arm == "T":
            if not cut and time.time() < dl - 20:
                rep, cut2 = turn(T("summary-request.txt"), dl, f"r9e2-{arm}-p1s")
                m = re.search(r"SUMMARY START\s*(.*?)\s*SUMMARY END", rep, re.S)
                summary = (m.group(1) if m else rep).strip()
                words = summary.split()
                if len(words) > 300:
                    summary = " ".join(words[:300])
                log("summary", words=len(words), truncated=len(words) > 300, marked=bool(m), cut=cut2)
                open(f"{EX}/T-summary.txt", "w").write(summary)
            else:
                log("summary", words=0, note="phase 1 cut or out of time; treatment not delivered")
        precheck(f"{arm}-p2")
        sid = new_session(f"{arm}-p2", seen)
        dl = deadline_for(left); left -= 1
        block = fill(T("summary-block.txt"), SUMMARY_TEXT=summary) if (arm == "T" and summary) else ""
        p2 = fill(T("phase2-resume.txt"), ARM=arm, ARM_DIR=d, PHASE_MIN=str(round((dl - time.time()) / 60)),
                  DEADLINE_UTC=iso(dl), SUMMARY_BLOCK=block)
        open(f"{EX}/{arm}-p2-prompt.txt", "w").write(p2)
        reply, cut = turn(p2, dl, f"r9e2-{arm}-p2")
        confirm_fresh(sid, f"{arm}-p2")
        open(f"{EX}/{arm}-p2-reply.txt", "w").write(reply)
        run_test(arm, d, "post")
    log("closeout", ping=sock("/ping"), state=json.load(open(STATE)).get("sessionId"))


if __name__ == "__main__":
    if sys.argv[1:2] == ["cancel"]:
        unit = sys.argv[2]
        if os.path.exists(f"{EX}/active-{unit}"):
            p = sock("/ping", 5)
            if p.get("status", "").startswith("busy"):
                open(f"{EX}/{unit}.cancelled", "w").write(json.dumps({"at": iso(), "ping": p, "cancel": sock("/cancel")}))
    else:
        main()
