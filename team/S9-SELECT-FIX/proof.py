#!/usr/bin/env python3
"""S10-4 proof: the duplicate detector keys on candidate identity, not rank
number (kiln-flash, 2026-09-18).

Usage:  python3 proof.py [--tool PATH]     (default: the patched copy beside
        this file, team/S9-SELECT-FIX/sprint-next)

Proves BOTH directions the row demands, on a SCRATCH board - a temp directory
wired into the tool through its own SN_TEAM / SN_QUEUE / SN_DIR settings.
Never the live board: nothing here reads or writes team/QUEUE.md.

  refused: the same artifact re-declared under a NEW rank, and under the same
           rank - a true re-admission either way;
  admitted: a fresh artifact over a burned rank number, and at rank 1 while
            the board cites other ranks.

Exit 0 when all directions hold on the tool under test; non-zero when any
fails. Run against sprint-next.before and it exits non-zero - which is the
proof that the bug was there and the fix fixes it. No LLM, no network."""
import argparse
import importlib.machinery
import importlib.util
import json
import os
import tempfile
from pathlib import Path

ROW = ("| S8-1 | alpha work, admitted at rank 2 | kiln-flash | pulse | "
       "`/s/team/S7-ALPHA` (check: python3 /s/team/S7-ALPHA/check.py) | "
       "$0.00 | open (admitted 2026-09-17 by sprint-next from BACKLOG-NEXT "
       "rank 2) — verifier: corvid-dsh |")
CASES = [
    ("the same artifact re-declared under a NEW rank is refused",
     {"rank": 9, "artifact": "`/s/team/S7-ALPHA`"}, "S8-1"),
    ("the same artifact under the SAME rank is refused",
     {"rank": 2, "artifact": "`/s/team/S7-ALPHA`"}, "S8-1"),
    ("a fresh artifact over burned rank 2 is admitted",
     {"rank": 2, "artifact": "`/s/team/S9-FRESH`"}, None),
    ("a fresh artifact at rank 1 while the board cites rank 2 is admitted",
     {"rank": 1, "artifact": "`/s/team/S9-ONE`"}, None),
]


def load(tool_path: str, scratch: Path):
    """Load the tool with its board settings pointed at the scratch board."""
    os.environ.update(SN_TEAM=str(scratch),
                      SN_QUEUE=str(scratch / "QUEUE.md"),
                      SN_DIR=str(scratch))
    loader = importlib.machinery.SourceFileLoader("_s10_4_tool", tool_path)
    mod = importlib.util.module_from_spec(
        importlib.util.spec_from_loader("_s10_4_tool", loader))
    loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(
        description="prove the duplicate detector keys on candidate identity")
    ap.add_argument("--tool",
                    default=str(Path(__file__).resolve().parent / "sprint-next"))
    a = ap.parse_args()
    bad = []
    with tempfile.TemporaryDirectory() as td:
        scratch = Path(td)
        (scratch / "QUEUE.md").write_text(ROW + "\n", encoding="utf-8")
        mod = load(a.tool, scratch)
        for what, cand, want in CASES:
            got = mod.already_admitted(dict(cand))
            ok = got == want
            print(f"  {'ok  ' if ok else 'FAIL'} {what}: already_admitted"
                  f"({json.dumps(cand)}) = {got!r}"
                  + ("" if ok else f", must be {want!r}"))
            if not ok:
                bad.append(what)
    if bad:
        print(f"S10-4 proof: {len(bad)} of {len(CASES)} directions FAIL on "
              f"{a.tool} - the duplicate detector does not key on candidate "
              f"identity")
        return 1
    print(f"S10-4 proof: all {len(CASES)} directions hold on {a.tool} - "
          f"re-admission is refused by artifact identity; a fresh candidate "
          f"over a burned rank number is admitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
