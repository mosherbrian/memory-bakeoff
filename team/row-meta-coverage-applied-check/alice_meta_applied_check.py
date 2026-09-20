#!/usr/bin/env python3
"""Alice second-seat of the APPLIED meta-guard completeness check (`6cd289e7…`).

Corvid's applied version differs from Assay's reviewed patch; this verifies the
live implementation both ways (live guard outside the declared set; declared
control whose file is gone), the added `_build_checks`-vs-declared drift guard,
and that the INCOMPLETE path never prints `N/N hold`.

Read-only over the repo; all mutation in temp copies. Counts/booleans only.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
SCRIPTS = DSH3 / "scripts"
META = "check_checker_exit_contracts.py"
EXPECTED = "6cd289e7"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(scripts_dir: Path, *args) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(scripts_dir / META), *args],
                       capture_output=True, text=True, cwd=str(scripts_dir))
    return p.returncode, p.stdout + p.stderr


def copy_scripts() -> Path:
    td = tempfile.mkdtemp()
    dest = Path(td) / "scripts"
    shutil.copytree(SCRIPTS, dest)
    return dest


def main() -> int:
    out = {"hash": sha(SCRIPTS / META), "checks": {}, "findings": []}
    out["is_applied"] = out["hash"].startswith(EXPECTED)

    rc, txt = run(SCRIPTS, "--self-test")
    out["checks"]["self_test"] = {"rc": rc, "pass": rc == 0}

    rc, txt = run(SCRIPTS)
    out["checks"]["live"] = {"rc": rc, "last": txt.strip().splitlines()[-1]}

    c = copy_scripts()
    (c / "check_zzz_synthetic.py").write_text("#!/usr/bin/env python3\nraise SystemExit(0)\n")
    rc, txt = run(c)
    out["checks"]["live_extra"] = {
        "rc": rc, "last": txt.strip().splitlines()[-1],
        "gap_lines": [l.strip() for l in txt.splitlines() if "NO CONTROL" in l],
        "prints_hold": "hold" in txt,
    }

    c = copy_scripts()
    (c / "check_query_fork.py").unlink()
    rc, txt = run(c)
    out["checks"]["declared_gone"] = {
        "rc": rc, "last": txt.strip().splitlines()[-1],
        "gap_lines": [l.strip() for l in txt.splitlines()
                      if "CONTROL WITHOUT A LIVE GUARD" in l],
        "prints_hold": "hold" in txt,
    }

    c = copy_scripts()
    src = (c / META).read_text()
    needle = '        "check_query_fork": (_fork_good, _fork_bad, r"FORK "),\n'
    (c / META).write_text(src.replace(needle, ""))
    rc, txt = run(c)
    out["checks"]["declared_vs_build_drift"] = {
        "rc": rc, "last": txt.strip().splitlines()[-1],
        "is_internal_error": "INTERNAL ERROR" in txt,
    }

    ch = out["checks"]
    if not out["is_applied"]:
        out["findings"].append("live meta-guard is not the applied 6cd289e7")
    if not ch["live"]["rc"] == 0 or "16/16 hold" not in ch["live"]["last"]:
        out["findings"].append("live run not 16/16 rc 0")
    if not any("check_zzz_synthetic" in l for l in ch["live_extra"]["gap_lines"]) \
            or ch["live_extra"]["prints_hold"]:
        out["findings"].append("extra-live-guard direction wrong")
    if not any("check_query_fork" in l for l in ch["declared_gone"]["gap_lines"]) \
            or ch["declared_gone"]["prints_hold"]:
        out["findings"].append("declared-control-gone direction wrong")
    if not ch["declared_vs_build_drift"]["is_internal_error"]:
        out["findings"].append("declared-vs-build drift not caught")

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
