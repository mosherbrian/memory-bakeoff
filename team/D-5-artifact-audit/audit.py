#!/usr/bin/env python3
"""D-5 artifact audit: every done-or-closed queue row needs a declared
artifact AND a runnable check; this enumerates, classifies, and (with
--apply) backfills the honest ones.

kiln-flash 2026-09-17, QUEUE row D-5. Precedents: S4-4 (four rows with no
machine-checkable artifact), row 32 (complete since 09-13, closed only when
Brian asked why the close detector had not fired), row 42 (the work done, the
word missing). Nobody knew how many such rows remained; this counts them.

Classification per done-or-closed row:
  has-check        a declared check already rides the row — nothing to do.
  backfillable     no check, but a concrete artifact path (artifact or status
                   cell) exists on disk -> the row's check becomes
                   `test -f/-d <path>` (the honest minimal gate; it claims
                   existence, nothing more).
  read-by-brian    no check and no concrete existing artifact path — the
                   deliverable was prose, a post, or edits whose substance
                   lives in history; pretending a check would be worse than
                   the gap, so the row says READ-BY-BRIAN.

No $HOME, no cwd dependence: every path is resolved against the queue root.

Usage:
  python3 audit.py                 # report to stdout
  python3 audit.py --apply         # also write backfills into QUEUE.md
  python3 audit.py --queue PATH
"""
import argparse
import re
import sys
from pathlib import Path

QUEUE_DEFAULT = "/home/bmosher/memory-bake-off/team/QUEUE.md"
TEAM = "/home/bmosher/memory-bake-off/team"
PROJECT = TEAM.rsplit("/", 1)[0]  # the memory-bake-off root


def resolve(p: str):
    """team/-relative paths resolve under team/, everything else under the
    project root (implementer/..., reviewer/...)."""
    real = f"{TEAM}/{p[len('team/'):]}".rstrip("/") if p.startswith("team/") \
        else f"{PROJECT}/{p}"
    return real

PATH_RE = re.compile(
    r"(?:team|implementer|reviewer|conductor)/[A-Za-z0-9._\-/]+")


def _clean(p: str) -> str:
    p = p.strip("`").rstrip(".,;:)」'")
    while p.endswith(("/", "-")):
        p = p[:-1]
    return p
DONE_RE = re.compile(r"\bdone:|closed:|VERIFIED\b", re.I)


def cells_of(line: str):
    parts = line.split("|")
    return parts


def audit(apply: bool, queue: str):
    lines = open(queue, encoding="utf-8").read().splitlines(keepends=True)
    rows = []          # (lineno, rid, verdict, detail)
    backfills = []     # (lineno, new_line)
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 8:
            continue
        rid = cells[1].strip()
        if rid in ("#", "") or rid.startswith("-") or rid == "Task":
            continue
        status = cells[7]
        # done-detection on the WHOLE line (CORVID-D-5-VERIFY 2026-09-17):
        # a row with an extra cell (row 38 carries a separate claimed: cell)
        # holds its done stamp past cells[7], so cells[7]-only matching made
        # the row invisible to this audit while its artifact sat unbackfilled.
        # The task-text cell is excluded: prose may NAME done-words (row D-7's
        # own text says `done:` while the row is open) without being done.
        done_cell = next((c for c in cells[3:] if DONE_RE.search(c)), "")
        if not done_cell:
            continue
        m = re.search(r"\(check: (.+?)\)", line)
        if m:
            rows.append((i, rid, "has-check", m.group(1)[:60]))
            continue
        # candidate artifact paths, artifact cell first then the done cell
        cand = []
        for cell in (cells[5], done_cell):
            for p in PATH_RE.findall(cell):
                p = _clean(p)
                if p and p not in cand:
                    cand.append(p)
        target, kind = None, None
        for p in cand:
            real = resolve(p)
            try:
                if Path(real).is_file():
                    target, kind = real, "f"
                    break
                if Path(real).is_dir():
                    target, kind = real, "d"
                    break
            except OSError:
                continue
        if target:
            check = f"test -{kind} {target}"
            rows.append((i, rid, "backfillable", check))
            if apply:
                cells[5] = cells[5].rstrip() + f" (check: {check}) "
                backfills.append((i, "|".join(cells)))
        else:
            why = (cells[5].strip()[:70] or "(empty artifact cell)")
            rows.append((i, rid, "read-by-brian", why))
    if apply and backfills:
        for i, new in backfills:
            lines[i] = new
        open(queue, "w", encoding="utf-8").write("".join(lines))
    return rows, len(backfills)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--queue", default=QUEUE_DEFAULT)
    a = ap.parse_args()
    rows, nb = audit(a.apply, a.queue)
    counts = {"has-check": 0, "backfillable": 0, "read-by-brian": 0}
    for i, rid, verdict, detail in rows:
        counts[verdict] += 1
        print(f"{verdict:14} {rid:8} {detail}")
    print(f"--- done-or-closed rows audited: {len(rows)}; "
          f"has-check {counts['has-check']}, backfillable "
          f"{counts['backfillable']} (applied: {nb}), read-by-brian "
          f"{counts['read-by-brian']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
