#!/usr/bin/env python3
"""S10-3 exit-contract driver, extended to the sprint gates
(kiln-flash, 2026-09-18).

The sibling driver (team/tools/check_checker_exit_contracts.py) covers the
guard checkers; this one reaches the S* gate checkers, which were exercised
ad hoc by whichever seat verified. For every gate in covered_gates.json it
requires two things, both from the exit contract:

  --selftest                          exits 0 (the gate can fail AND pass)
  a run on a target that not exists   exits 1, names a [MARKER], and never
                                      shows a traceback

A live sprint gate outside the covered set, or a covered gate that has
vanished from disk, is itself a failure: the sweep would lose control of it
without noticing. Every failure names its gate. Exit 0 only when all hold.

Usage:
  python3 gate_contracts.py --team TEAM --covered FILE
No LLM, no network."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

GATE_GLOBS = ("S*/check.py", "S*-check.py", "D-*/check.py")
MARKER = re.compile(r"^\[[A-Z][A-Z0-9-]*\]", re.M)
TRACEBACK = "Traceback (most recent call last)"
GATE_TIMEOUT = 900  # seconds per gate run; selftests are the slow part


def main() -> int:
    ap = argparse.ArgumentParser(
        description="exit-contract driver for the sprint gates")
    ap.add_argument("--team", required=True,
                    help="team directory the covered paths are relative to")
    ap.add_argument("--covered", required=True,
                    help="covered_gates.json: [paths relative to team/]")
    args = ap.parse_args()

    team = Path(args.team)
    covered = json.loads(Path(args.covered).read_text(encoding="utf-8"))
    live = {str(p.relative_to(team)) for g in GATE_GLOBS for p in team.glob(g)}
    failures: list = []
    for gate in sorted(live - set(covered)):
        failures.append(f"{gate}: live sprint gate outside the covered set "
                        f"(no control over it)")
    for gate in covered:
        path = team / gate
        if not path.is_file():
            failures.append(f"{gate}: covered gate is gone from disk")
            continue
        try:
            st = subprocess.run([sys.executable, str(path), "--selftest"],
                                capture_output=True, text=True,
                                timeout=GATE_TIMEOUT)
            dirty = subprocess.run(
                [sys.executable, str(path),
                 str(team / "__absent__" / "target")],
                capture_output=True, text=True, timeout=GATE_TIMEOUT)
        except subprocess.TimeoutExpired:
            failures.append(f"{gate}: exceeded the {GATE_TIMEOUT}s driver "
                            f"timeout")
            continue
        st_text = st.stdout + st.stderr
        if st.returncode != 0 or TRACEBACK in st_text:
            failures.append(f"{gate}: --selftest exit {st.returncode} "
                            f"(must be 0, no traceback)")
            continue
        d_text = dirty.stdout + dirty.stderr
        if dirty.returncode != 1 or TRACEBACK in d_text \
                or not MARKER.search(d_text):
            failures.append(f"{gate}: dirty run exit {dirty.returncode}, "
                            f"the contract (exit 1, a named [MARKER], no "
                            f"traceback) is not honoured")

    for f in failures:
        print(f"CONTRACT FAIL: {f}")
    held = len(covered) - len({f.split(":", 1)[0] for f in failures})
    print(f"gate contracts: {held} of {len(covered)} hold")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
