#!/bin/sh
# R57 grading wrapper: the pinned R56 runner is not edited. After each arm, run this to grade every mapped arm with the
# R57 grader and to surface manual flags. sh grade-arms.sh OPROOT  -> OPROOT/<op>/grade-r57.json and a summary line per arm.
OPROOT=${1:-/tmp/campaign4-r56-op}; G=/var/home/bmosher/memory-bake-off/campaign4/packages/R57-context-endpoint-repair/grade.py
python - "$OPROOT" "$G" <<'PY'
import json, sys, subprocess
root, g = sys.argv[1], sys.argv[2]
for line in open(f"{root}/map.jsonl"):
    m = json.loads(line); out = subprocess.run([sys.executable, g, f"{m['op']}/log", m["target"], f"{m['cwd']}/report.md"], capture_output=True, text=True).stdout
    open(f"{m['op']}/grade-r57.json", "w").write(out); d = json.loads(out)
    print(m["label"], d["outcome"], "primary" if d["primary"] else "-", "MANUAL" if d["manual"] else "", sep="  ")
PY
