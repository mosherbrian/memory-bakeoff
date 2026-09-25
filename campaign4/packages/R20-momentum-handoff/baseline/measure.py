#!/usr/bin/env python3
"""R20 momentum measures, read-only, for one fixed window.

  python measure.py START END OUTDIR      (UTC, e.g. 2026-09-24T19:00:00Z)

Sources (read only): agent-loop SQLite (consistent snapshot via the backup
API), package records under campaign4/packages (question_id bindings),
campaign4/REST.jsonl, the escalation ledger, git history of
RESEARCH-STREAMS.json, support-ticket files. Writes redacted extracts plus
metrics.json into OUTDIR. Unknown stays unknown: no full-day denominator is
invented for uncovered time.

Metric mapping (preregistered):
  executing  = a bound package between `start` and its worker claim `publish`
               (worker), or between `publish` and `verify_pass|verify_fail`
               (verify). decision_task..decide is WAITING, not executing.
  valid rest = a REST.jsonl row for the question with entered_at <= t <
               revisit_at, all R11 fields present; reported twice: R11 rule
               (any length) and R18 rule (<= 7200 s and structured next_step).
  stall      = active stream time with neither; per stream, overlaps merged.
"""
import glob, json, os, sqlite3, subprocess, sys
from datetime import datetime, timezone

C4 = "/home/bmosher/memory-bake-off/campaign4"
DB = "/home/bmosher/.local/share/agent-loop/campaign4.db"
LEDGER = "/home/bmosher/.local/share/agent-deck/escalations.jsonl"
TICKETS = "/home/bmosher/.local/share/agent-deck/support-tickets"
STREAM_Q = {"A": "Q-WORK-BENEFIT", "B": "Q-EVALUATOR-VALIDITY"}


def ts(s):
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d.timestamp() if d.tzinfo else None
    except ValueError:
        return None


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def snapshot_events(out):
    src = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    dst = sqlite3.connect(os.path.join(out, "loop-snapshot.sqlite"))
    src.backup(dst)  # one consistent read of db + wal
    ev = [dict(zip(("qid", "type", "seat", "role", "at"), r))
          for r in dst.execute("select question_id,type,actor_seat,actor_role,at from events order by at")]
    dst.close()
    os.remove(os.path.join(out, "loop-snapshot.sqlite"))  # driver_kv can hold ack capabilities: not kept
    return ev


def bindings():
    b = {}
    for f in glob.glob(f"{C4}/packages/*/*.json") + glob.glob(f"{C4}/packages/*/*/*.json"):
        try:
            r = json.load(open(f))
        except Exception:
            continue
        if isinstance(r, dict) and r.get("question_id"):
            for k in ("package_id", "qid"):
                if isinstance(r.get(k), str):
                    b.setdefault(r[k], set()).add(r["question_id"])
    return b


def stream_activity(S, E):
    """Active intervals per stream from the git history of RESEARCH-STREAMS.json.
    Before the registry existed (R11), stream A = legacy top question, active."""
    log = subprocess.run(["git", "-C", C4, "log", "--reverse", "--format=%H %ct", "--", "RESEARCH-STREAMS.json"],
                         capture_output=True, text=True).stdout.split("\n")
    changes = []
    for line in filter(None, log):
        h, t = line.split()
        try:
            d = json.loads(subprocess.run(["git", "-C", C4, "show", f"{h}:./RESEARCH-STREAMS.json"], capture_output=True, text=True).stdout)
            act = {s["stream_id"] for s in d["streams"] if s["status"] == "active"}
        except Exception:
            act = None
        changes.append((int(t), act))
    act = {"A": [], "B": []}
    cur, since = {"A"}, S  # legacy: top question counted as stream A
    for t, a in changes + [(E, None)]:
        t = max(S, min(t, E))
        for s in cur:
            if t > since:
                act[s].append((since, t))
        if a is not None:
            cur, since = a, t
        else:
            since = t
    return act, [(iso(t), sorted(a) if a else a) for t, a in changes]


def merge(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def minus(base, cut):
    res = []
    for a, b in base:
        segs = [(a, b)]
        for c, d in cut:
            segs = [x for s in segs for x in ((s[0], min(s[1], c)), (max(s[0], d), s[1])) if x[1] > x[0]]
        res += segs
    return res


def length(iv):
    return sum(b - a for a, b in iv)


def main():
    S, E, out = ts(sys.argv[1]), ts(sys.argv[2]), sys.argv[3]
    os.makedirs(out, exist_ok=True)
    ev = snapshot_events(out)
    win = [e for e in ev if S <= ts(e["at"]) < E]
    json.dump(win, open(os.path.join(out, "events-window.json"), "w"), indent=0)
    b = bindings()
    # sensitivity only: SENS_BIND=qid,qid binds unlabelled packages to stream A's question
    for q in filter(None, os.environ.get("SENS_BIND", "").split(",")):
        b.setdefault(q, set()).add(STREAM_Q["A"])
    first_ev = min((ts(e["at"]) for e in win), default=None)
    # executing intervals per question
    per = {}
    for e in ev:
        per.setdefault(e["qid"], []).append(e)
    execq = {q: [] for q in STREAM_Q.values()}
    pk_meta = {}
    for qid, es in per.items():
        qs = b.get(qid, set())
        t = {x["type"]: ts(x["at"]) for x in es}
        pk_meta[qid] = {"questions": sorted(qs), **{k: iso(v) for k, v in t.items()}}
        spans = []
        if "start" in t:
            spans.append((t["start"], t.get("publish") or t.get("interrupt") or E))
        if "publish" in t:
            vend = t.get("verify_pass") or t.get("verify_fail") or t.get("interrupt") or E
            spans.append((t["publish"], vend))
        if len(qs) == 1:
            q = next(iter(qs))
            if q in execq:
                execq[q] += [(max(a, S), min(c, E)) for a, c in spans if c > S and a < E]
    # rests
    rests = {q: {"r11": [], "r18": []} for q in STREAM_Q.values()}
    for line in open(f"{C4}/REST.jsonl"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        q = r.get("question_id")
        if q not in rests:
            continue
        e_, v_ = ts(r.get("entered_at")), ts(r.get("revisit_at"))
        if not all(r.get(k) for k in ("reason", "owner", "entered_at", "revisit_at")) or e_ is None or v_ is None or v_ <= e_:
            continue
        iv = (max(e_, S), min(v_, E))
        if iv[1] > iv[0]:
            rests[q]["r11"].append(iv)
            st = r.get("next_step") or {}
            if v_ - e_ <= 7200 and all(st.get(k) for k in ("action_id", "owner", "deadline", "objective")):
                rests[q]["r18"].append(iv)
    act, reg_changes = stream_activity(S, E)
    stall = {}
    for s, q in STREAM_Q.items():
        a = merge(act[s]); x = merge(execq[q])
        for rule in ("r11", "r18"):
            gaps = minus(minus(a, x), merge(rests[q][rule]))
            cov_gap = minus(gaps, [(S, first_ev)]) if first_ev else gaps
            stall[f"{s}-{rule}"] = {"active_min": round(length(a) / 60), "executing_min": round(length(x) / 60),
                                    "stall_min_total": round(length(gaps) / 60),
                                    "stall_min_after_first_loop_event": round(length(cov_gap) / 60),
                                    "gaps": [(iso(g[0]), iso(g[1])) for g in gaps if g[1] - g[0] >= 300]}
    # dropped handoffs
    started = sorted({e["qid"] for e in win if e["type"] == "start"})
    status = json.loads(subprocess.run(["/home/bmosher/.local/bin/agent-loop", "status", "--config",
                                        "/home/bmosher/.config/agent-loop/campaign4.json", "--json"], capture_output=True, text=True).stdout)
    step = {p["qid"]: p for p in status["packages"]}
    timed = sorted(q for q in started if step.get(q, {}).get("step") == "timed-out")
    interrupted = sorted({e["qid"] for e in win if e["type"] == "interrupt"})
    no_publish = sorted(q for q in started if not any(x["type"] == "publish" for x in per[q]) and step.get(q, {}).get("step") not in ("worker", "verify"))
    dropped = sorted(set(timed) | set(no_publish))
    # terminal decision -> next dispatch same stream
    lat = []
    for q in STREAM_Q.values():
        seq = sorted((ts(x["at"]), x["type"], qid) for qid, es in per.items() if b.get(qid) == {q} for x in es if x["type"] in ("decide", "start"))
        for i, (t, typ, qid) in enumerate(seq):
            if typ == "decide" and S <= t < E:
                nxt = next(((t2, q2) for t2, typ2, q2 in seq[i + 1:] if typ2 == "start"), None)
                lat.append({"question": q, "decided": qid, "at": iso(t), "next": nxt[1] if nxt else None,
                            "minutes": round((nxt[0] - t) / 60, 1) if nxt else None, "censored": nxt is None})
    # escalations
    esc = []
    for line in open(LEDGER):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if "id" in r and S <= r.get("t", 0) < E:
            esc.append({"id": r["id"], "kind": r.get("kind"), "source": r.get("source"), "t": iso(r["t"]), "key": r.get("key")})
    kinds = {}
    for r in esc:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    tickets = sorted(os.path.basename(f) for f in glob.glob(f"{TICKETS}/T-*.md") if S <= os.path.getmtime(f) < E)
    json.dump(esc, open(os.path.join(out, "escalations-window.json"), "w"), indent=0)
    m = {"window": [iso(S), iso(E)], "coverage": {
            "first_loop_event_in_window": iso(first_ev) if first_ev else None,
            "uncovered_start_minutes": round((first_ev - S) / 60) if first_ev else None,
            "note": "loop events are only written for packages; minutes before the first event are uncovered by loop records. REST rows and registry history still cover them.",
            "registry_changes": reg_changes},
         "a_stall": stall,
         "b_dropped": {"packages_started": len(started), "dropped_unique": len(dropped), "timed_out": timed,
                       "ended_without_claim": no_publish, "interrupt_events": len(interrupted),
                       "per_10_packages": round(10 * len(dropped) / len(started), 1) if started else None},
         "c_decision_to_next_dispatch": lat,
         "d_escalations": {"ledger_rows": len(esc), "by_kind": kinds, "brian_ticket_files": tickets,
                           "note": "ledger rows are the durable record of notices to Claude; channel delivery is not recorded. Brian pages: ticket files only; the two synthetic Signal pages at ~15:52Z (old poller test harness) are excluded as test pages and noted."},
         "e_stamp_honesty": "N/A: no structured next-step commitments with start evidence existed before R18 (18:38Z). R18 rest receipts from 18:38Z are the only commitments in the window.",
         "packages": pk_meta}
    json.dump(m, open(os.path.join(out, "metrics.json"), "w"), indent=1)
    print(json.dumps({k: m[k] for k in ("coverage", "b_dropped", "d_escalations")}, indent=1)[:3000])
    print(json.dumps(m["a_stall"], indent=1)[:2500])


if __name__ == "__main__":
    main()
