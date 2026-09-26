#!/bin/sh
# Fresh temp dir per run; writes raw inputs + grader outputs under OUT; prints pass/fail summary.
R=$(cd "$(dirname "$0")/.." && pwd); OUT=${1:-$(mktemp -d /tmp/r62-t-XXXXXX)}; mkdir -p "$OUT"
cd "$R/tests" && python - "$R" "$OUT" <<'PY'
import sys, os, json, importlib.util
R, OUT = sys.argv[1:3]; sys.path.insert(0, R + "/tests")
spec = importlib.util.spec_from_file_location("g", R + "/grade.py"); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
from cases import CASES
fails = 0; res = []
for i, (n, log, t, rep, eo, er) in enumerate(CASES):
    d = f"{OUT}/c{i:02d}"; os.makedirs(d, exist_ok=True)
    lp = f"{d}/log"; rp = f"{d}/report.md"
    if log is not None: open(lp, "w").write(log)
    if rep is not None: open(rp, "w").write(rep)
    o = g.grade(lp if log is not None else f"{d}/absent-log", t, rp if rep is not None else None)
    json.dump(o, open(f"{d}/grade.json", "w"), indent=1)
    ok = o["outcome"] == eo and o["rule"] == er; fails += not ok
    res.append({"case": n, "expected": [eo, er], "got": [o["outcome"], o["rule"]], "pass": ok})
json.dump(res, open(f"{OUT}/results.json", "w"), indent=1)
print(f"{len(CASES)-fails}/{len(CASES)} pass, out={OUT}")
for x in res:
    if not x["pass"]: print("FAIL", x)
sys.exit(1 if fails else 0)
PY
