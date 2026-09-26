#!/bin/sh
# Fresh dir per run (no cleanup assumed); raw inputs, receipts and outputs kept under OUT.
R=$(cd "$(dirname "$0")/.." && pwd); OUT=${1:-$(mktemp -d /tmp/r63-t-XXXXXX)}; mkdir -p "$OUT"
python - "$R" "$OUT" <<'PY'
import sys, os, json, hashlib, importlib.util
R, OUT = sys.argv[1:3]; sys.path.insert(0, R + "/tests")
s = importlib.util.spec_from_file_location("g", R + "/gate.py"); g = importlib.util.module_from_spec(s); s.loader.exec_module(g)
from cases import CASES
D62 = R + "/../R62-context-measurement-repair/director-challenges/"
res = []; fails = 0
for i, (n, log, rep, rs, exp) in enumerate(CASES):
    d = f"{OUT}/c{i:02d}"; os.makedirs(d, exist_ok=True)
    lp, rp, xp = f"{d}/log", f"{d}/report.md", None
    for p, v, fn in ((lp, log, "log"), (rp, rep, "report.md")):
        if isinstance(v, str) and v.startswith("R62:"): v = open(D62 + v[4:] + "/" + fn, "rb").read()
        if v is not None: open(p, "wb").write(v)
    c = g.candidate(lp, "24576", rp)
    if rs:
        rec = {"schema": "r63-adjudication-v1", "label": n, "reviewer": "corvid", "log_sha256": c["log_sha256"] or "", "report_sha256": c["report_sha256"] or "",
               "candidate_outcome": c["outcome"], "decision": "reject" if rs in ("reject", "reject_irrelevant") else "approve", "guessing": rs == "approve_guess", "contradiction": False, "reason": "test", "source_evidence": {"src_contradicted":"contradicted","src_indeterminate":"indeterminate"}.get(rs,"inferred"), "ask_relevant": "no" if rs in ("ask_irrelevant","reject_irrelevant") else ("yes" if c["outcome"] == "asked_no_run" else "not_applicable")}
        if rs == "stale": rec["report_sha256"] = "0" * 64
        if rs == "wrong_outcome": rec["candidate_outcome"] = "asked_no_run"
        if rs == "self": rec["reviewer"] = "claude"
        xp = f"{d}/receipt.json"; open(xp, "w").write("{not json" if rs == "malformed" else json.dumps(rec))
    o = {"candidate": c, "gate": g.gate(c, xp)}; json.dump(o, open(f"{d}/out.json", "w"), indent=1)
    got = (c["outcome"], o["gate"]["status"], o["gate"]["final_primary"]); ok = got == tuple(exp); fails += not ok
    res.append({"case": n, "expected": list(exp), "got": list(got), "pass": ok})
json.dump(res, open(f"{OUT}/results.json", "w"), indent=1)
print(f"{len(res)-fails}/{len(res)} pass out={OUT}")
[print("FAIL", x) for x in res if not x["pass"]]
PY
