#!/usr/bin/env python3
"""Alice second-seat of the adopted guard 18 (`check_record_text_identity.py`)."""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
G = DSH3 / "scripts" / "check_record_text_identity.py"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cwd, *a):
    p = subprocess.run([sys.executable, str(G), *map(str, a)], capture_output=True, text=True, cwd=str(cwd))
    return p.returncode, p.stdout + p.stderr

out = {"hash": sha(G), "checks": {}, "findings": []}
out["is_guard18"] = out["hash"].startswith("0b8fd3aa")
st = subprocess.run([sys.executable, str(G), "--self-test"], capture_output=True, text=True, cwd=str(DSH3))
out["checks"]["self_test_rc"] = st.returncode

with tempfile.TemporaryDirectory() as td:
    t = Path(td)
    (t/"DOC.json").write_text('{"c":"- [M005] The staging Redis database number is 9."}')
    canon = t/"corpus.py"
    canon.write_text('R("M005", "The staging Redis database number is 6.", x)\n')
    rc_drift, o_drift = run(t, t, "--canonical", canon)
    rc_missing, o_missing = run(t, t, "--canonical", t/"nope.py")
    (t/"dircanon").mkdir()
    rc_dir, o_dir = run(t, t, "--canonical", t/"dircanon")
    rc_no, o_no = run(t, t, "--canonical", canon, "--no-unindexed")
    out["checks"]["drift_cli"] = {"rc": rc_drift, "marker": "record-text drift: M005" in o_drift,
                                  "traceback": "Traceback" in o_drift}
    out["checks"]["missing_canon"] = {"rc": rc_missing, "structured": "prerequisite" in o_missing,
                                      "traceback": "Traceback" in o_missing}
    out["checks"]["dir_canon"] = {"rc": rc_dir, "structured": "prerequisite" in o_dir,
                                  "traceback": "Traceback" in o_dir}
    out["checks"]["no_unindexed"] = {"rc": rc_no, "unindexed_named": "unindexed record text" in o_no}
c = out["checks"]
if not out["is_guard18"]: out["findings"].append("live guard hash != 0b8fd3aa")
if c["self_test_rc"] != 0: out["findings"].append("self-test failed")
if not (c["drift_cli"]["rc"]==1 and c["drift_cli"]["marker"] and not c["drift_cli"]["traceback"]):
    out["findings"].append("drift CLI not loud/clean")
if not (c["missing_canon"]["rc"]==1 and c["missing_canon"]["structured"] and not c["missing_canon"]["traceback"]):
    out["findings"].append("missing canonical not structured")
if not (c["dir_canon"]["rc"]==1 and c["dir_canon"]["structured"] and not c["dir_canon"]["traceback"]):
    out["findings"].append("directory canonical not structured")
if c["no_unindexed"]["unindexed_named"]:
    out["findings"].append("--no-unindexed still names unindexed")
print(json.dumps(out, indent=1)); raise SystemExit(0)
