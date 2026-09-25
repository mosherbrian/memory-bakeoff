#!/usr/bin/env python3
"""R20 baseline-v2 step 1: freeze redacted, window-bounded source snapshots.
  python snapshot.py END SNAPDIR
Everything after END is excluded at capture. Capture time and source hashes
go to SNAPDIR/provenance.json. No message bodies, no driver_kv (it can hold
acknowledgement capabilities)."""
import glob, hashlib, json, os, sqlite3, subprocess, sys, tempfile, time
from datetime import datetime, timezone

C4 = "/home/bmosher/memory-bake-off/campaign4"
DB = "/home/bmosher/.local/share/agent-loop/campaign4.db"
LEDGER = "/home/bmosher/.local/share/agent-deck/escalations.jsonl"
TICKETS = "/home/bmosher/.local/share/agent-deck/support-tickets"


def ts(s):
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d.timestamp() if d.tzinfo else None
    except ValueError:
        return None


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    E, out = ts(sys.argv[1]), sys.argv[2]
    os.makedirs(out, exist_ok=True)
    prov = {"captured_at": datetime.now(timezone.utc).isoformat(), "window_end": sys.argv[1], "sources": {}}
    # loop events: one consistent read through the backup API, bodies dropped
    with tempfile.TemporaryDirectory() as td:
        dst = sqlite3.connect(os.path.join(td, "s.sqlite"))
        sqlite3.connect(f"file:{DB}?mode=ro", uri=True).backup(dst)
        ev = [dict(zip(("qid", "type", "seat", "role", "at"), r)) for r in
              dst.execute("select question_id,type,actor_seat,actor_role,at from events order by at, event_id")]
        dst.close()
    ev = [e for e in ev if ts(e["at"]) < E]
    json.dump(ev, open(f"{out}/events.json", "w"), indent=0)
    prov["sources"]["agent-loop events"] = {"path": DB, "rows_before_end": len(ev), "method": "sqlite backup API, events table only"}
    # REST rows entered before END (the file has no write time; entered_at is the only order key)
    rows = [json.loads(l) for l in open(f"{C4}/REST.jsonl") if l.strip()]
    keep = [r for r in rows if (ts(r.get("entered_at")) or 1e18) < E]
    open(f"{out}/rest.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in keep))
    prov["sources"]["REST.jsonl"] = {"sha256_at_capture": sha(f"{C4}/REST.jsonl"), "rows": len(rows), "rows_entered_before_end": len(keep)}
    # registry history up to END
    log = subprocess.run(["git", "-C", C4, "log", "--reverse", "--format=%H %ct", "--", "RESEARCH-STREAMS.json"], capture_output=True, text=True).stdout.split()
    reg = []
    for h, t in zip(log[::2], log[1::2]):
        if int(t) < E:
            d = json.loads(subprocess.run(["git", "-C", C4, "show", f"{h}:./RESEARCH-STREAMS.json"], capture_output=True, text=True).stdout)
            reg.append({"commit": h, "t": int(t), "active": sorted(s["stream_id"] for s in d["streams"] if s["status"] == "active")})
    json.dump(reg, open(f"{out}/registry.json", "w"), indent=1)
    # question bindings from package records (path + hash of each record used)
    b = []
    for f in sorted(glob.glob(f"{C4}/packages/*/*.json") + glob.glob(f"{C4}/packages/*/*/*.json")):
        try:
            r = json.load(open(f))
        except Exception:
            continue
        if isinstance(r, dict) and r.get("question_id"):
            for k in ("package_id", "qid"):
                if isinstance(r.get(k), str):
                    b.append({"package": r[k], "question_id": r["question_id"], "stream_id": r.get("stream_id"),
                              "record": os.path.relpath(f, C4), "sha256": sha(f)})
    json.dump(b, open(f"{out}/bindings.json", "w"), indent=0)
    # escalation ledger metadata before END (no text)
    esc = []
    for l in open(LEDGER):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("t", 1e18) < E:
            esc.append({k: r.get(k) for k in ("id", "kind", "source", "t", "key", "ack", "resolve") if k in r})
    json.dump(esc, open(f"{out}/escalations.json", "w"), indent=0)
    prov["sources"]["escalations.jsonl"] = {"sha256_at_capture": sha(LEDGER), "rows_before_end": len(esc)}
    tk = [{"file": os.path.basename(f), "mtime": os.path.getmtime(f)} for f in glob.glob(f"{TICKETS}/T-*.md") if os.path.getmtime(f) < E]
    json.dump(tk, open(f"{out}/tickets.json", "w"), indent=0)
    prov["files_sha256"] = {os.path.basename(f): sha(f) for f in sorted(glob.glob(f"{out}/*.json*"))}
    json.dump(prov, open(f"{out}/provenance.json", "w"), indent=1)
    print(json.dumps(prov, indent=1)[:1500])


if __name__ == "__main__":
    main()
