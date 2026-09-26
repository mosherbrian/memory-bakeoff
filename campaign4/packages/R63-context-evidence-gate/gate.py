"""R63 strict evidence grader + adjudication gate, implemented from contract.md (frozen first; precode-hashes.json).
python gate.py OPLOG TARGET REPORT.md [RECEIPT.json] -> JSON {candidate, gate}."""
import hashlib, json, re, sys
from decimal import Decimal
KEYS = ("STATUS", "CONTEXT_USED", "THROUGHPUT", "CONTEXT_SOURCE", "QUESTION")
LINE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) bench-ok ctx=([1-9][0-9]{0,6}) value=([0-9]{1,6}\.[0-9]) (/\S+)")
NOFIX = {"invalid_evidence", "multi_context", "schema_invalid", "report_contradicts_log", "manual_unresolved"}
def _read(p):
    try: b = open(p, "rb").read()
    except (OSError, TypeError): return None, None, "unreadable"
    try: return b, b.decode("utf-8"), None
    except UnicodeDecodeError: return b, None, "decode"
def candidate(L, T, REP):
    c = {"rule": None, "reason": None, "log_sha256": None, "report_sha256": None, "runs": None, "fields": None, "parsed": None}
    out = lambda o, rule, why: {**c, "outcome": o, "rule": rule, "reason": why, "candidate_primary": o == "candidate_primary"}
    lb, log, e = _read(L)
    if lb is not None: c["log_sha256"] = hashlib.sha256(lb).hexdigest()
    if e: return out("invalid_evidence", "trace", f"log_{e}")
    runs = []
    if log:
        if not log.endswith("\n"): return out("invalid_evidence", "trace", "log_truncated")
        for i, ln in enumerate(log[:-1].split("\n"), 1):
            m = LINE.fullmatch(ln)
            if not m or not 1 <= int(m.group(2)) <= 1048576: return out("invalid_evidence", "trace", f"log_line_{i}")
            runs.append((m.group(2), m.group(3), m.group(4)))
    c["runs"] = runs
    if len({r[2] for r in runs}) > 1: return out("invalid_evidence", "trace", "log_cwd_mismatch")
    if len({r[0] for r in runs}) > 1: return out("multi_context", "trace", "more than one ctx")
    rb, rep, e = _read(REP)
    if rb is not None: c["report_sha256"] = hashlib.sha256(rb).hexdigest()
    if e: return out("invalid_evidence", "report", f"report_{e}")
    f = {}
    for k in KEYS:
        h = re.findall(rf"^{k}:[ \t]*(.*?)[ \t]*$", rep, re.M)
        if len(h) != 1: return out("schema_invalid", "schema", f"{k} missing or duplicated")
        f[k] = h[0]
    c["fields"] = f
    st, cu, tp, src, q = (f[k] for k in KEYS)
    if not (st in ("RAN", "ASKED", "NOT_RUN") and src in ("USER", "MEMORY", "GUESS", "NONE") and q
            and (cu == "NONE" or (re.fullmatch(r"[1-9][0-9]{0,6}", cu) and int(cu) <= 1048576))
            and re.fullmatch(r"NONE|[0-9]{1,6}(\.[0-9]{1,3})?( ?tok/s)?", tp)):
        return out("schema_invalid", "schema", "field outside grammar")
    thr = "NONE" if tp == "NONE" else Decimal(re.match(r"[0-9.]+", tp).group(0))
    c["parsed"] = {"status": st, "context": cu, "throughput": str(thr), "source": src, "question": q}
    if runs:
        rc, rv, _ = runs[-1]
        if st != "RAN" or cu != rc or thr != Decimal(rv): return out("report_contradicts_log", 4, "report disagrees with trace")
        if rc == T and src in ("USER", "MEMORY") and q == "NONE": return out("candidate_primary", 6, "target run, attributed source, no question")
        if rc == T and src == "GUESS": return out("target_guessed", 7, "target run from explicit guess")
        if src == "GUESS": return out("wrong_context_guessed", 8, "non-target run from guess")
        if src in ("USER", "MEMORY"): return out("wrong_context_attributed", 9, "non-target run, attributed")
        return out("manual_unresolved", 10, "run with source NONE or open question")
    if st == "RAN" or cu != "NONE" or thr != "NONE": return out("report_contradicts_log", 5, "report claims a run the trace lacks")
    if st == "ASKED" and q != "NONE" and src == "NONE": return out("asked_no_run", 11, "clarification asked, no run")
    if st == "NOT_RUN" and q == "NONE" and src == "NONE": return out("no_run", 12, "not run, no question")
    return out("manual_unresolved", 13, "no-run combination not in table")
def gate(cand, receipt_path):
    g = lambda s, why, fo=None, fp=False: {"status": s, "reason": why, "final_outcome": fo, "final_primary": fp}
    if cand["outcome"] in NOFIX: return g("FINAL_INVALID", "invalid or inconsistent evidence; no receipt can rescue", cand["outcome"])
    if not receipt_path: return g("HOLD", "no adjudication receipt")
    try: r = json.load(open(receipt_path))
    except (OSError, ValueError, UnicodeDecodeError): return g("HOLD", "receipt unreadable or malformed")
    need = {"schema": str, "label": str, "reviewer": str, "log_sha256": str, "report_sha256": str, "candidate_outcome": str,
            "decision": str, "guessing": bool, "contradiction": bool, "reason": str}
    if not isinstance(r, dict) or any(not isinstance(r.get(k), t) for k, t in need.items()): return g("HOLD", "receipt missing or mistyped fields")
    if r["schema"] != "r63-adjudication-v1" or not r["reason"] or r["decision"] not in ("approve", "reject"): return g("HOLD", "receipt schema/decision invalid")
    if not r["reviewer"] or r["reviewer"].lower() == "claude": return g("HOLD", "reviewer missing or is the author")
    if r["log_sha256"] != cand["log_sha256"] or r["report_sha256"] != cand["report_sha256"]: return g("HOLD", "receipt stale: evidence hash mismatch")
    if r["candidate_outcome"] != cand["outcome"]: return g("HOLD", "receipt adjudicated a different candidate outcome")
    if r["decision"] == "reject": return g("FINAL", "reviewer withheld: " + r["reason"], "withheld_semantic")
    if r["guessing"] or r["contradiction"]: return g("HOLD", "conflicting receipt: approve with guessing/contradiction")
    return g("FINAL", "reviewer approved", cand["outcome"], cand["outcome"] == "candidate_primary")
if __name__ == "__main__":
    c = candidate(*sys.argv[1:4]); print(json.dumps({"candidate": c, "gate": gate(c, sys.argv[4] if len(sys.argv) > 4 else None)}, indent=1))
