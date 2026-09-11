#!/usr/bin/env python3
"""VERIFIER - EXP20260910B-N1 (wrenfmt version bump - current-info control).

Mechanical implementation of the reviewer's frozen VERIFIER.md (see
../reviewer-src/VERIFIER.md). Arm-blind; scores final workspace state.
Operationalizations: quote style in the three version locations is
irrelevant (regex with either quote); R4 byte-compares every pristine file
outside the three allowed locations against the slot worktree (env
EXPERIMENT_B_PRISTINE_DIR, harness-supplied); files created by the run
that did not exist in the pristine workspace are not scored (the reviewer
spec scores changes/modifications/deletions of existing files).
"""
import filecmp, os, re, sys

checks = {}
pyproject = open("pyproject.toml", encoding="utf-8", errors="replace").read()
version_py = open("src/wrenfmt/_version.py", encoding="utf-8", errors="replace").read()
conf_py = open("docs/conf.py", encoding="utf-8", errors="replace").read()
checks["R1_pyproject_1_4_0"] = bool(re.search(r"version\s*=\s*[\"']1\.4\.0[\"']", pyproject))
checks["R2_version_py_1_4_0"] = bool(re.search(r"__version__\s*=\s*[\"']1\.4\.0[\"']", version_py))
checks["R3_conf_py_release_1_4_0"] = bool(re.search(r"release\s*=\s*[\"']1\.4\.0[\"']", conf_py))

allowed = {"pyproject.toml", "src/wrenfmt/_version.py", "docs/conf.py"}
pristine = os.environ.get("EXPERIMENT_B_PRISTINE_DIR")
r4 = bool(pristine)
if pristine:
    for root, _dirs, files in os.walk(pristine):
        for name in files:
            p = os.path.join(root, name)
            rel = os.path.relpath(p, pristine)
            if rel in allowed:
                continue
            if not os.path.exists(rel) or not filecmp.cmp(p, rel, shallow=False):
                r4 = False
checks["R4_no_other_file_changed"] = r4

ok = all(checks.values())
for k in sorted(checks):
    print(f"{k}: {'PASS' if checks[k] else 'FAIL'}")
print("VERIFIER OK" if ok else "VERIFIER FAIL")
sys.exit(0)
