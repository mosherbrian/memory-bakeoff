#!/usr/bin/env python3
"""R20 baseline-v2 step 2: metrics from a frozen snapshot ONLY (no live reads).
  python measure_v2.py START END SNAPDIR > metrics.json

Window-bounded: an event at or after END never counts; packages still open at
END are right-censored. Where the snapshot cannot establish a measure it says
UNKNOWN; approximations are labelled diagnostics, not stalls and not bounds."""
import json, os, sys
from datetime import datetime, timezone

STREAM_Q = {"A": "Q-WORK-BENEFIT", "B": "Q-EVALUATOR-VALIDITY"}


def ts(s):
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d.timestamp() if d.tzinfo else None
    except ValueError:
        return None


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def measure(S, E, snap):
    L = lambda n: json.load(open(os.path.join(snap, n)))
    ev = [e for e in L("events.json") if ts(e["at"]) < E]  # belt and braces: never read past END
    bind = {}
    for r in L("bindings.json"):
        bind.setdefault(r["package"], set()).add(r["question_id"])
    per = {}
    for e in ev:
        per.setdefault(e["qid"], []).append(e)
    first = {q: {x["type"]: ts(x["at"]) for x in reversed(es)} for q, es in per.items()}  # earliest per type
    win_started = sorted(q for q, t in first.items() if "start" in t and S <= t["start"] < E)
    # (b) timeout-only: an `interrupt` event (the loop's worker timeout) inside the window
    timeouts = sorted(q for q in win_started if "interrupt" in first[q] and first[q]["interrupt"] < E)
    pending = sorted(q for q in win_started if not any(k in first[q] for k in ("publish", "interrupt", "decide")))
    b = {"packages_started_in_window": len(win_started), "timeout_only": timeouts,
         "timeout_only_per_10": round(10 * len(timeouts) / len(win_started), 2) if win_started else None,
         "right_censored_open_at_end": pending,
         "ended_without_claim": "UNKNOWN: needs the worker's runtime turn-end evidence per phase, which this snapshot does not include; not inferred from later timeouts"}
    # (c) decision -> next start in the same stream (explicit single-question bindings only)
    lat = []
    for q in STREAM_Q.values():
        seq = sorted((t, typ, qid) for qid, tt in first.items() if bind.get(qid) == {q} for typ, t in tt.items() if typ in ("decide", "start"))
        for i, (t, typ, qid) in enumerate(seq):
            if typ == "decide" and S <= t < E:
                nxt = next(((t2, q2) for t2, y2, q2 in seq[i + 1:] if y2 == "start"), None)
                lat.append({"question": q, "decided": qid, "at": iso(t), "next": nxt[1] if nxt else None,
                            "minutes": round((nxt[0] - t) / 60, 1) if nxt else None, "censored_at_end": nxt is None})
    # (a) diagnostic only
    reg = L("registry.json")
    act = {"A": [], "B": []}
    cur, since = {"A"}, S
    for r in reg + [{"t": E, "active": None}]:
        t = max(S, min(r["t"], E))
        for s in cur:
            if t > since:
                act[s].append((since, t))
        if r["active"] is not None:
            cur = set(r["active"])
        since = t
    rest_rows = [json.loads(l) for l in open(os.path.join(snap, "rest.jsonl")) if l.strip()]
    diag = {}
    for s, q in STREAM_Q.items():
        x = []
        for qid, t in first.items():
            if bind.get(qid) == {q} and "start" in t:
                x.append((t["start"], min(t.get("publish") or t.get("interrupt") or E, E)))
                if "publish" in t:
                    x.append((t["publish"], min(t.get("verify_pass") or t.get("verify_fail") or E, E)))
        rows = [(ts(r.get("entered_at")), ts(r.get("revisit_at"))) for r in rest_rows if r.get("question_id") == q]
        rows = [(max(a, S), min(c, E)) for a, c in rows if a and c and c > a and c > S and a < E]
        overlaps = sum(1 for i in range(len(rows)) for j in range(i + 1, len(rows)) if rows[i][0] < rows[j][1] and rows[j][0] < rows[i][1])
        gaps = minus(minus(merge(act[s]), merge(x)), merge(rows))
        diag[s] = {"active_min": round(length(merge(act[s])) / 60), "loop_executing_min": round(length(merge(x)) / 60),
                   "uncovered_by_loop_or_any_rest_row_min": round(length(gaps) / 60),
                   "rest_rows_in_window": len(rows), "overlapping_rest_row_pairs": overlaps,
                   "longest_uncovered": max(((iso(a), iso(c)) for a, c in gaps), key=lambda g: ts(g[1]) - ts(g[0]), default=None)}
    a = {"primary_stall_minutes": "UNKNOWN",
         "why": "the snapshot lacks out-of-loop work records and the live checker's historical latest-row/receipt verdicts; the union below over-credits rest (any row counts, superseded rows included) and under-credits work (out-of-loop packages absent), so it is neither an upper nor a lower bound",
         "diagnostic_union": diag}
    esc = [r for r in L("escalations.json") if "id" in r and S <= r["t"] < E]
    kinds = {}
    for r in esc:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    d = {"ledger_notices_in_window": len(esc), "by_kind": kinds,
         "confirmed_delivery": "UNKNOWN: notify-claude records no receipt; the ledger is attempted notice, not delivery",
         "stall_escalations": "UNKNOWN as a confirmed count; ledger shows notices only",
         "brian_ticket_files": sorted(t["file"] for t in L("tickets.json") if S <= t["mtime"] < E),
         "excluded_test_pages": "two synthetic Signal pages ~15:52Z from the old poller harness (not in ticket files)"}
    return {"window": [iso(S), iso(E)], "first_loop_event": iso(min(ts(e["at"]) for e in ev if ts(e["at"]) >= S)) if any(ts(e["at"]) >= S for e in ev) else None,
            "a_stall": a, "b_dropped": b, "c_decision_to_next_dispatch": lat, "d_escalations": d,
            "e_stamp_honesty": "N/A before activation"}


if __name__ == "__main__":
    print(json.dumps(measure(ts(sys.argv[1]), ts(sys.argv[2]), sys.argv[3]), indent=1))
