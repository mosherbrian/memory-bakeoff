#!/usr/bin/env python3
"""Alice second-seat of Assay's meta-guard coverage-completeness patch.

Independently checks the patch claims and the honest failure mode Assay named
(control names without `.py` produced phantom gaps): live set 0 gaps, an added
synthetic sibling flagged, a removed control's guard flagged, self-test PASS.

Read-only over the repo; all mutation in temp copies. Counts/booleans only.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
SCRIPTS = DSH3 / "scripts"
BASE = SCRIPTS / "check_checker_exit_contracts.py"
PDIR = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2"
            "/scripts/verify-20260913-assay-meta-coverage-completeness")
DIFF = PDIR / "meta-coverage-completeness.diff"
PATCHED = PDIR / "check_checker_exit_contracts.patched.py"
POWER = PDIR / "meta_coverage_completeness_power_check.py"

NOTE_HASHES = {"diff": "c19e0589", "patched": "7e289fdd", "power": "710c68b4"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(scripts_dir: Path, *args) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(scripts_dir / "check_checker_exit_contracts.py"),
                        *args], capture_output=True, text=True, cwd=str(scripts_dir))
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    out = {"hashes": {}, "checks": {}, "findings": []}
    for k, p in (("diff", DIFF), ("patched", PATCHED), ("power", POWER)):
        h = sha(p)
        out["hashes"][k] = {"sha256": h, "matches_note": h.startswith(NOTE_HASHES[k])}

    cp = subprocess.run(["git", "apply", "--check", str(DIFF)], cwd=str(DSH3),
                        capture_output=True, text=True)
    out["checks"]["apply_check_rc"] = cp.returncode
    out["checks"]["live_base"] = sha(BASE)

    def fresh_patched():
        td = tempfile.mkdtemp()
        copy = Path(td) / "scripts"
        shutil.copytree(SCRIPTS, copy)
        shutil.copy(PATCHED, copy / "check_checker_exit_contracts.py")
        return copy

    c = fresh_patched()
    rc, txt = run(c)
    out["checks"]["real_set"] = {"rc": rc, "summary": txt.strip().splitlines()[-1],
                                 "coverage_gaps_lines": [l for l in txt.splitlines()
                                                         if "uncovered guard" in l
                                                         or "missing guard" in l]}

    c = fresh_patched()
    (c / "check_zzz_synthetic.py").write_text("#!/usr/bin/env python3\nraise SystemExit(0)\n")
    rc, txt = run(c)
    out["checks"]["extra_sibling"] = {"rc": rc, "summary": txt.strip().splitlines()[-1],
                                      "gaps": [l.strip() for l in txt.splitlines()
                                               if "uncovered guard" in l]}

    c = fresh_patched()
    (c / "check_query_fork.py").unlink()
    rc, txt = run(c)
    out["checks"]["removed_guard"] = {"rc": rc, "summary": txt.strip().splitlines()[-1],
                                      "gaps": [l.strip() for l in txt.splitlines()
                                               if "missing guard" in l]}

    c = fresh_patched()
    rc, txt = run(c, "--self-test")
    out["checks"]["patched_self_test"] = {"rc": rc, "pass": rc == 0}

    # positive control: canonical base is silent on the extra sibling
    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / "scripts"
        shutil.copytree(SCRIPTS, copy)
        (copy / "check_zzz_synthetic.py").write_text("#!/usr/bin/env python3\nraise SystemExit(0)\n")
        rc, txt = run(copy)
        out["checks"]["canonical_extra_sibling"] = {
            "rc": rc, "summary": txt.strip().splitlines()[-1],
            "mentions_gap": "coverage gaps" in txt}

    ch = out["checks"]
    if ch["real_set"]["rc"] != 0 or ch["real_set"]["coverage_gaps_lines"]:
        out["findings"].append("patched real set is not gap-free")
    if ch["extra_sibling"]["rc"] != 1 or "check_zzz_synthetic.py" not in " ".join(ch["extra_sibling"]["gaps"]):
        out["findings"].append("extra sibling not flagged")
    if ch["removed_guard"]["rc"] != 1 or "check_query_fork.py" not in " ".join(ch["removed_guard"]["gaps"]):
        out["findings"].append("removed guard not flagged")
    if not ch["patched_self_test"]["pass"]:
        out["findings"].append("patched self-test failed")

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
