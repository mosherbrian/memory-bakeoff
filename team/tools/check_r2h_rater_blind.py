#!/usr/bin/env python3
"""Is the R2H blind rater still blind? Measured, not promised.

WHY. Brian, 2026-09-17: "Has corvid seen anything? If not, that's the natural
rater to assign." It has not - measured the same day - so it is the rater. This
keeps checking, because eligibility is not a property you establish once: the
arm map is a plain-text table in team/R2H-FREEZE.md, and `r2h_deploy.py status`
prints the whole schedule in one line. Either could enter the rater's context
between now and day 10, and a rater who saw the map and rates anyway is worse
than no rater, because the numbers then LOOK valid.

Exit 0 = still blind. Exit 1 = exposed, and it names what leaked.

  check_r2h_rater_blind.py [--seat corvid-dsh]
  check_r2h_rater_blind.py --selftest
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
HIST = HOME / ".config/agent-deck/acp-history"
FREEZE = HOME / "memory-bake-off/team/R2H-FREEZE.md"

# Every string that carries the arm assignment. Derived from the freeze file
# rather than retyped, where possible.
TELLS = {
    "the arm table": r"ON \| ON \| OFF",
    "the schedule heading": r"Derived schedule",
    "the derivation rule": r"first five in the permutation",
    "a status dump": r"d1:(ON|OFF) +d2:",
    "the seed": r"9e2aac78cbc3243967a557cd10fddf7a2382046516e90e9e6ce196f0c38371e7",
}


def seat_id(title):
    try:
        rows = json.loads(subprocess.run(
            [str(HOME / ".local/bin/agent-deck"), "list", "--json"],
            capture_output=True, text=True, timeout=90).stdout)
    except Exception:                                   # noqa: BLE001
        return None
    for r in rows:
        if (r.get("title") or "").lower() == title.lower():
            return (r.get("id") or "")
    return None


def scan(files):
    found = {}
    for f in files:
        try:
            text = open(f, errors="ignore").read()
        except OSError:
            continue
        for name, rx in TELLS.items():
            if re.search(rx, text):
                found.setdefault(name, []).append(os.path.basename(f))
    return found


def findings(seat="corvid-dsh", files=None):
    out = []
    if files is None:
        sid = seat_id(seat)
        if not sid:
            return [f"[NO-SEAT] {seat} is not in the registry, so its exposure "
                    f"cannot be measured - do not let it rate until it can be"]
        files = glob.glob(str(HIST / f"{sid[:8]}*.jsonl"))
        if not files:
            return [f"[NO-HISTORY] no transcript found for {seat}; absence of a "
                    f"file is not evidence of blindness"]
    for name, where in scan(files).items():
        out.append(f"[EXPOSED] {name} appears in {', '.join(sorted(set(where)))} "
                   f"- the rater has seen the arm assignment and is no longer "
                   f"blind. Say so out loud; do not rate.")
    return out


def selftest():
    import tempfile
    d = Path(tempfile.mkdtemp())
    clean = d / "clean.jsonl"
    clean.write_text('{"text":"R2H REV-3 signed off; r2h_deploy.py verified"}\n')
    if findings(files=[str(clean)]):
        print("selftest: FAIL - a clean transcript was called exposed")
        return 1
    for name, sample in (("arm table", "| Arm | ON | ON | OFF | ON |"),
                         ("status dump", "days flipped: 0/10 d1:ON  d2:ON"),
                         ("derivation", "first five in the permutation are ON"),
                         ("seed", "seed 9e2aac78cbc3243967a557cd10fddf7a2382"
                                  "046516e90e9e6ce196f0c38371e7")):
        f = d / f"{name.replace(' ','_')}.jsonl"
        f.write_text(json.dumps({"text": sample}) + "\n")
        if not findings(files=[str(f)]):
            print(f"selftest: FAIL - {name} leaked through undetected")
            return 1
    print("selftest: PASS (a transcript about the deploy script stays clean; the "
          "arm table, a status dump, the derivation rule and the seed are each "
          "caught)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seat", default="corvid-dsh")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    f = findings(a.seat)
    for x in f:
        print(x)
    if f:
        return 1
    print(f"{a.seat} is still blind: the arm table, the schedule heading, the "
          f"derivation rule, a status dump and the seed all appear zero times "
          f"in its transcript.")
    print("  Keep it that way: never open team/R2H-FREEZE.md, never run "
          "r2h_deploy.py status, never read the flip log.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
