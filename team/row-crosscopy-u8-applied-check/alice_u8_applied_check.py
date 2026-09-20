#!/usr/bin/env python3
"""Alice second-seat of the APPLIED cross-copy U8 vacuous fix (`dde0bbc6…`)."""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path

DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
IMPL = DSH3.parent
GUARD = DSH3 / "scripts" / "check_cross_copy_drift.py"
PDIR = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2/scripts/verify-20260913-assay-crosscopy-u8")
DIFF = PDIR / "crosscopy-u8.diff"

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def run(*a):
    p = subprocess.run([sys.executable, str(GUARD), *map(str, a)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr

out = {"hashes": {"guard": sha(GUARD), "diff": sha(DIFF)}, "checks": {}, "findings": []}
out["is_applied"] = out["hashes"]["guard"] == "dde0bbc6e5e5132ddff017d9604a420829ec0156b31a59ec32f7a9f31d13fa5d"

rev = subprocess.run(["git", "apply", "-R", "--check", str(DIFF)], cwd=str(DSH3), capture_output=True, text=True)
out["checks"]["reverse_apply_check_rc"] = rev.returncode

with tempfile.TemporaryDirectory() as td:
    t = Path(td)
    shared_only = t / "shared_only.txt"; shared_only.write_text("shared: AGENTS.md\n")
    comment_only = t / "comment_only.txt"; comment_only.write_text("# no directives\n")
    rc1, o1 = run("--declaration", shared_only)
    rc2, o2 = run("--declaration", comment_only)
    rc3, o3 = run("--declaration", shared_only, "--trees", IMPL/"repo", IMPL/"repo-glm-dsh2", IMPL/"repo-glm-dsh3")
    out["checks"]["shared_only"] = {"rc": rc1, "names_failure": "no declared tree set" in o1, "no_hold": "findings:" not in o1}
    out["checks"]["comment_only"] = {"rc": rc2, "names_failure": "no declared tree set" in o2, "findings_line": [l.strip() for l in o2.splitlines() if "findings:" in l]}
    out["checks"]["explicit_trees"] = {"rc": rc3, "discovery_line": "undeclared tree:" in o3}
    st = subprocess.run([sys.executable, str(GUARD), "--self-test"], capture_output=True, text=True)
    out["checks"]["self_test"] = {"rc": st.returncode}

rc4, o4 = run()
out["checks"]["live"] = {"rc": rc4, "findings": [l.strip() for l in o4.splitlines() if "findings:" in l]}

c = out["checks"]
if not out["is_applied"]: out["findings"].append("live guard is not the applied dde0bbc6")
if not (c["shared_only"]["rc"]==1 and c["shared_only"]["names_failure"] and c["shared_only"]["no_hold"]):
    out["findings"].append("shared-only declaration not failed loud")
if c["comment_only"]["rc"]==0:
    out["findings"].append("RESIDUAL: an empty/comment-only declaration still falls back silently (rc 0, no failure)")
if not c["explicit_trees"]["rc"]==0 and not c["explicit_trees"]["discovery_line"]:
    out["findings"].append("explicit --trees behaviour wrong")
print(json.dumps(out, indent=1))
raise SystemExit(0)
