#!/usr/bin/env python3
"""Alice second-seat of cross-copy U8 v2 (`f8bd89a9…`): empty-declaration residual closed."""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path

DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
IMPL = DSH3.parent
GUARD = DSH3 / "scripts" / "check_cross_copy_drift.py"
PDIR = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2/scripts/verify-20260913-assay-crosscopy-u8")
DIFF = PDIR / "crosscopy-u8-v2.diff"

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def run(*a):
    p = subprocess.run([sys.executable, str(GUARD), *map(str, a)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr

out = {"hashes": {"guard": sha(GUARD), "diff": sha(DIFF)}, "checks": {}, "findings": []}
out["is_applied"] = out["hashes"]["guard"] == "f8bd89a90c2a08fbdd0b083c3c2df608e1cab0bac769f27c915f03930ad39eb3"
rev = subprocess.run(["git", "apply", "-R", "--check", str(DIFF)], cwd=str(DSH3), capture_output=True, text=True)
out["checks"]["reverse_apply_check_rc"] = rev.returncode

with tempfile.TemporaryDirectory() as td:
    t = Path(td)
    empty = t/"empty.txt"; empty.write_text("# no directives\n")
    shared = t/"shared.txt"; shared.write_text("shared: AGENTS.md\n")
    tree_only = t/"tree_only.txt"; tree_only.write_text("tree: implementer/repo-glm-dsh3\n")
    tree_gone = t/"tree_gone.txt"; tree_gone.write_text("tree: implementer/repo-nope\n")
    cases = {}
    for name, decl in (("empty", empty), ("shared_only", shared), ("tree_only", tree_only), ("tree_gone", tree_gone)):
        rc, o = run("--declaration", decl)
        cases[name] = {"rc": rc, "no_tree_failure": "no declared tree set" in o,
                       "undeclared": o.count("undeclared tree:"),
                       "declared_gone": "declared tree missing:" in o,
                       "findings": [l.strip() for l in o.splitlines() if "findings:" in l]}
    out["checks"]["declarations"] = cases
    rc, o = run("--declaration", shared, "--trees", IMPL/"repo", IMPL/"repo-glm-dsh2", IMPL/"repo-glm-dsh3")
    out["checks"]["explicit_trees"] = {"rc": rc, "discovery": "undeclared tree:" in o}
    st = subprocess.run([sys.executable, str(GUARD), "--self-test"], capture_output=True, text=True)
    out["checks"]["self_test"] = {"rc": st.returncode}

rc, o = run()
out["checks"]["live"] = {"rc": rc, "findings": [l.strip() for l in o.splitlines() if "findings:" in l]}

c = out["checks"]
if not out["is_applied"]: out["findings"].append("live guard != f8bd89a9")
if c["declarations"]["empty"]["rc"] != 1 or not c["declarations"]["empty"]["no_tree_failure"]:
    out["findings"].append("empty declaration still silent")
if not (c["declarations"]["shared_only"]["rc"]==1 and c["declarations"]["tree_only"]["rc"]==0
        and c["declarations"]["tree_only"]["undeclared"]==2
        and c["declarations"]["tree_gone"]["declared_gone"]):
    out["findings"].append("declaration matrix differs")
if c["explicit_trees"]["rc"] != 0 or c["explicit_trees"]["discovery"]:
    out["findings"].append("explicit --trees regression")
print(json.dumps(out, indent=1)); raise SystemExit(0)
