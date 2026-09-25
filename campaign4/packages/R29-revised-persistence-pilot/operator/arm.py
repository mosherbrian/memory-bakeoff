"""R29 per-arm operator step: preflight (kiln idle, no open production or private kiln/corvid work),
R10 /new over the existing kiln socket, then ONE private dispatch. Writes preflight/new/dispatch receipts.
Usage: python arm.py PAIR-ARM   (e.g. A-T). Refuses on any failed preflight; never retries."""
import json, socket, subprocess, sys, hashlib
from datetime import datetime, timezone, timedelta

R = "/home/bmosher/memory-bake-off/campaign4/packages/R29-revised-persistence-pilot"
BIN = "/home/bmosher/.local/bin/agent-loop.prev-r23-47f69dfd"
CFG = "/home/bmosher/.config/agent-loop/campaign4-r29.json"
PROD_BIN, PROD_CFG = "/home/bmosher/.local/bin/agent-loop", "/home/bmosher/.config/agent-loop/campaign4.json"
KILN = "a79067ca-1790000758"
SOCK = f"/home/bmosher/.config/agent-deck/acp-sock/{KILN}.sock"
STATE = f"/home/bmosher/.config/agent-deck/acp-sessions/{KILN}.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sock(text, timeout=60):
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
    return json.loads(buf)


def open_pkgs(bin_, cfg):
    out = subprocess.run([bin_, "status", "--config", cfg, "--json"], capture_output=True, text=True).stdout
    d = json.loads(out)
    ps = d if isinstance(d, list) else (d.get("packages") or [])
    return [p for p in ps if p.get("step") not in ("closed", "timed-out")]


def main():
    pa = sys.argv[1]
    pair, arm = pa.split("-")
    order = json.load(open(f"{R}/release.json"))["order"]
    assert pa in order
    frozen = json.load(open(f"{R}/operator/frozen-hashes.json"))
    drift = [f for f, h in frozen.items() if hashlib.sha256(open(f, "rb").read()).hexdigest() != h
             and "/r29-arms/" not in f]
    ping = sock("/ping", 10)
    pre = {"at": now(), "arm": pa, "ping": ping, "state_before": json.load(open(STATE)),
           "production_open": open_pkgs(PROD_BIN, PROD_CFG), "private_open": open_pkgs(BIN, CFG),
           "frozen_drift": drift,
           "private_run": subprocess.run(["systemctl", "--user", "is-active", "agent-loop-r29-private-run.service"],
                                         capture_output=True, text=True).stdout.strip()}
    pre["ok"] = (ping.get("ok") and ping.get("status") == "idle" and not pre["production_open"]
                 and not pre["private_open"] and not drift and pre["private_run"] == "active")
    json.dump(pre, open(f"{R}/operator/preflight-{pa}.json", "w"), indent=1)
    if not pre["ok"]:
        sys.exit(f"preflight failed: see operator/preflight-{pa}.json")
    new = {"at": now(), "state_session_before": pre["state_before"]["sessionId"], "reply": sock("/new", 120)}
    new["state_session_after"] = json.load(open(STATE))["sessionId"]
    json.dump(new, open(f"{R}/operator/new-{pa}.json", "w"), indent=1)
    if not new["reply"].get("ok"):
        sys.exit("/new failed")
    qid = f"R29-{pair}-{arm}"
    cmd = [BIN, "dispatch", "--config", CFG, "--qid", qid, "--worker", "kiln", "--verifier", "corvid",
           "--duration", "10m", "--verify-window", "5m", "--task", f"@{R}/tasks/{pa}-worker.md",
           "--verify-task", f"@{R}/tasks/{pa}-verifier.md"]
    t = datetime.now(timezone.utc)
    p = subprocess.run(cmd, capture_output=True, text=True)
    rec = {"package_id": qid, "qid": qid, "question_id": "Q-WORK-BENEFIT", "stream_id": "A", "pair": pair, "arm": arm,
           "config": CFG, "bin": BIN, "dispatched_at": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "worker_deadline": (t + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "argv": cmd, "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
           "new_session": new["reply"].get("status")}
    json.dump(rec, open(f"{R}/dispatch/{qid}.json", "w"), indent=1)
    print(json.dumps({k: rec[k] for k in ("qid", "exit", "dispatched_at", "worker_deadline", "new_session")}))
    print(p.stdout, p.stderr)


if __name__ == "__main__":
    main()
