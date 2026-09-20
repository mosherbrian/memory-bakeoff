#!/usr/bin/env python3
"""Alice second-seat of the applied exit-contract coverage patch (meta-guard).

Reproduces Corvid's apply receipt claims independently and probes the one gap
the patch does not guard: the driver has no completeness check against the live
`check_*.py` set, so a newly added sibling is silently uncovered while the
driver still reports "all hold".

Read-only over the repo; all mutation happens in temp copies. Counts only.
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
META = SCRIPTS / "check_checker_exit_contracts.py"
SELF = "check_checker_exit_contracts"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_meta(scripts_dir: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(scripts_dir / META.name)],
                       capture_output=True, text=True, cwd=str(scripts_dir))
    return p.returncode, p.stdout + p.stderr


def hold_line(text: str) -> str:
    for ln in text.strip().splitlines()[::-1]:
        if "hold" in ln:
            return ln.strip()
    return "(no hold line)"


def covered_names(src: str) -> set[str]:
    return set(re.findall(r'"(check_[a-z0-9_]+)":', src))


def live_siblings() -> set[str]:
    return {p.stem for p in SCRIPTS.glob("check_*.py")} - {SELF}


def main() -> int:
    out = {"hashes": {"meta_guard": sha(META)}, "checks": {}, "findings": []}

    src = META.read_text()
    covered, live = covered_names(src), live_siblings()
    out["checks"]["coverage_sets"] = {
        "covered": sorted(covered), "live_siblings": sorted(live),
        "live_not_covered": sorted(live - covered),
        "covered_not_live": sorted(covered - live),
    }

    rc, txt = run_meta(SCRIPTS)
    out["checks"]["live"] = {"rc": rc, "hold": hold_line(txt),
                             "clean_and_dirty_mentioned": "OK" in txt}

    p = subprocess.run([sys.executable, str(META), "--self-test"],
                       capture_output=True, text=True, cwd=str(SCRIPTS))
    out["checks"]["self_test"] = {"rc": p.returncode,
                                  "pass": p.returncode == 0}

    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / "scripts"
        shutil.copytree(SCRIPTS, copy)
        rc, txt = run_meta(copy)  # no team/, no repo checkouts needed by driver
        out["checks"]["hermetic_copy"] = {"rc": rc, "hold": hold_line(txt)}

    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / "scripts"
        shutil.copytree(SCRIPTS, copy)
        for g in ("check_required_metrics.py", "check_cross_copy_drift.py"):
            f = copy / g
            f.write_text(f.read_text().replace("raise SystemExit(main())",
                                               "raise SystemExit(0)"))
        rc, txt = run_meta(copy)
        out["checks"]["blinded_two"] = {
            "rc": rc, "hold": hold_line(txt),
            "broken_named": sorted(re.findall(r"^  (\S+): BROKEN", txt, re.M)),
        }

    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / "scripts"
        shutil.copytree(SCRIPTS, copy)
        (copy / "check_zzz_synthetic.py").write_text(
            "#!/usr/bin/env python3\nraise SystemExit(0)\n")
        rc, txt = run_meta(copy)
        out["checks"]["extra_sibling_ignored"] = {
            "rc": rc, "hold": hold_line(txt),
            "mentions_zzz": "zzz" in txt,
        }

    c = out["checks"]
    if c["coverage_sets"]["live_not_covered"] or c["coverage_sets"]["covered_not_live"]:
        out["findings"].append("set mismatch live vs covered")
    if c["blinded_two"]["hold"] != "=== checker exit contracts: 14/16 hold":
        out["findings"].append("blind positive control did not land at 14/16")
    if c["extra_sibling_ignored"]["mentions_zzz"] or \
            c["extra_sibling_ignored"]["hold"] != "=== checker exit contracts: 16/16 hold":
        out["findings"].append("unexpected behaviour with an extra sibling")

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
