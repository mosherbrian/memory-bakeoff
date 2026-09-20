#!/usr/bin/env python3
"""Guard RD-THREADS time labels against the file's own mtime.

Corvid, R&D pulse 2026-09-13 (instantiates Alice's time-label audit,
`team/ALICE-TIME-LABEL-AUDIT.md`). A clock label cannot be later than the last
write of the file that contains it: every entry is in the file by the time of
its last write, so any dated label after the file mtime is an estimate, not a
clock read.

The check is clock-independent on purpose: it compares labels to the **file
mtime**, never to `now`, so it cannot be confounded by an NTP step. It is a
pulse-end / pre-append check — once the file is appended past a bad label, the
window to see it closes.

Coverage, so nothing escapes silently. A label may be at column 0, indented, or
a list item (`^\\s*(?:[-*]\\s+)?\\*\\*`); a `**YYYY-MM-DD ...**` quoted mid-line
in prose is not treated as an entry label.

- `**YYYY-MM-DD HH:MM[:SS] UTC` — checked against mtime; an after-mtime label is
  `[AFTER-MTIME]`, an impossible timestamp is `[MALFORMED]`.
- `**YYYY-MM-DD —` — date-only is the policy-compliant form; the calendar date
  is validated (`[MALFORMED]` if impossible) **and** compared to the mtime date
  (`[AFTER-MTIME]` if it post-dates the file).
- `**YYYY-MM-DD HH:MM` in any other form (e.g. no `UTC` suffix) — **not**
  checked because the zone is unknown; counted and listed as `[UNCHECKED-TIME]`.
  Default exits 0 for these (historical local-time labels exist); `--strict`
  fails closed instead, for policy-compliant seats.

Usage:
  python3 check_rd_thread_labels.py [path]      # default team/RD-THREADS.md
  python3 check_rd_thread_labels.py --strict [path]
  python3 check_rd_thread_labels.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_PREFIX = r"^\s*(?:[-*]\s+)?\*\*"
LABEL_RE = re.compile(_PREFIX + r"((\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2})(?::(\d{2}))? UTC)", re.M)
DATE_ONLY_RE = re.compile(_PREFIX + r"((\d{4}-\d{2}-\d{2}) —)", re.M)
LOOSE_TIME_RE = re.compile(_PREFIX + r"((\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2}))", re.M)
_UTC_SUFFIX_RE = re.compile(r"(?::\d{2})? UTC")


def _date_ok(y: int, mo: int, d: int) -> bool:
    try:
        datetime(y, mo, d)
        return True
    except ValueError:
        return False


def labels_after_mtime(path: Path) -> tuple[int, int, list[str], list[str]]:
    """Return (dated, date_only, flagged, unchecked_time).

    `flagged` entries are `[AFTER-MTIME] <label>` or `[MALFORMED] <label>`.
    `unchecked_time` are time-bearing labels whose zone is not the canonical
    `UTC` suffix, so mtime comparison is undefined. Caller supplies a readable
    path.
    """
    mtime = os.path.getmtime(path)
    mtime_date = datetime.fromtimestamp(mtime, tz=timezone.utc).date()
    text = path.read_text(encoding="utf-8", errors="replace")
    dated = 0
    bad: list[str] = []
    for m in LABEL_RE.finditer(text):
        dated += 1
        label = m.group(1)
        try:
            dt = datetime(int(m.group(2)[0:4]), int(m.group(2)[5:7]),
                          int(m.group(2)[8:10]), int(m.group(3)), int(m.group(4)),
                          int(m.group(5)) if m.group(5) else 0, tzinfo=timezone.utc)
        except ValueError:
            bad.append(f"[MALFORMED] {label}")
            continue
        if dt.timestamp() > mtime:  # cannot have been written yet
            bad.append(f"[AFTER-MTIME] {label}")

    # Date-only: validate the calendar date and the mtime date (G1).
    date_only = 0
    for m in DATE_ONLY_RE.finditer(text):
        label = m.group(1)
        y, mo, d = int(m.group(2)[0:4]), int(m.group(2)[5:7]), int(m.group(2)[8:10])
        if not _date_ok(y, mo, d):
            bad.append(f"[MALFORMED] {label}")
        elif datetime(y, mo, d, tzinfo=timezone.utc).date() > mtime_date:
            bad.append(f"[AFTER-MTIME] {label}")
        else:
            date_only += 1

    # Time-bearing labels in a non-canonical form are not mtime-checkable.
    unchecked: list[str] = []
    for m in LOOSE_TIME_RE.finditer(text):
        if _UTC_SUFFIX_RE.match(text[m.end():]):
            continue  # canonical UTC label, already handled by LABEL_RE
        label = m.group(1)
        if not _date_ok(int(m.group(2)[0:4]), int(m.group(2)[5:7]), int(m.group(2)[8:10])):
            bad.append(f"[MALFORMED] {label}")
        else:
            unchecked.append(label)
    return dated, date_only, bad, unchecked


def self_test() -> int:
    epoch = datetime(2026, 1, 2, tzinfo=timezone.utc).timestamp()
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "RD-THREADS.md"
        p.write_text(
            "**2026-01-01 00:00 UTC — early entry.** ok\n"
            "**2099-01-01 00:00 UTC — future entry.** impossible\n"
            "**2026-01-01 — date-only policy entry.** no time to check\n")
        os.utime(p, (epoch,) * 2)
        dated, date_only, bad, unchecked = labels_after_mtime(p)
        assert dated == 2 and date_only == 1, (dated, date_only)
        assert len(bad) == 1 and "2099" in bad[0], bad
        assert unchecked == [], unchecked

        # All labels in the past -> clean; date-only still ignored.
        p.write_text("**2026-01-01 00:00 UTC — a.** ok\n**2026-01-01 — b.** ok\n")
        os.utime(p, (epoch,) * 2)
        dated, date_only, bad, unchecked = labels_after_mtime(p)
        assert bad == [] and unchecked == [], (bad, unchecked)

        # Impossible regex-shaped timestamps are malformed findings, not crashes.
        p.write_text("**2026-13-01 00:00 UTC — bad month.**\n"
                     "**2026-09-31 00:00 UTC — bad day.**\n"
                     "**2026-01-01 24:00 UTC — bad hour.**\n")
        os.utime(p, (datetime(2027, 1, 1, tzinfo=timezone.utc).timestamp(),) * 2)
        dated, _, bad, _ = labels_after_mtime(p)
        assert dated == 3 and len(bad) == 3 and all("[MALFORMED]" in b for b in bad), bad

        # F1: an impossible date-only label is malformed, not counted clean.
        p.write_text("**2026-13-01 — bad date-only.**\n")
        os.utime(p, (datetime(2027, 1, 1, tzinfo=timezone.utc).timestamp(),) * 2)
        _, date_only, bad, _ = labels_after_mtime(p)
        assert date_only == 0 and len(bad) == 1 and "[MALFORMED]" in bad[0], (date_only, bad)

        # F2: a time-bearing label without a UTC suffix is surfaced as unchecked.
        p.write_text("**2026-01-01 00:00 — no zone.**\n"
                     "**2026-01-01 00:00:30 UTC — canonical.**\n")
        os.utime(p, (epoch,) * 2)
        dated, _, bad, unchecked = labels_after_mtime(p)
        assert dated == 1 and bad == [] and unchecked == ["2026-01-01 00:00"], \
            (dated, bad, unchecked)

        # G1: a future date-only label post-dates the file -> flagged.
        p.write_text("**2099-01-01 — future date-only.**\n")
        os.utime(p, (epoch,) * 2)
        _, date_only, bad, _ = labels_after_mtime(p)
        assert date_only == 0 and any("[AFTER-MTIME]" in b for b in bad), (date_only, bad)

        # G2/G3: indented and list-item entry labels are recognised (and checked).
        p.write_text("  **2026-01-01 00:00 UTC — indented.**\n"
                     "- **2099-01-01 00:00 UTC — list-item future.**\n")
        os.utime(p, (epoch,) * 2)
        dated, _, bad, _ = labels_after_mtime(p)
        assert dated == 2 and any("2099" in b and "[AFTER-MTIME]" in b for b in bad), (dated, bad)

    # Default CLI: unchecked-time is advisory (rc 0); --strict fails closed.
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "RD-THREADS.md"
        p.write_text("**2026-01-01 00:00 — no zone.**\n")
        os.utime(p, (epoch,) * 2)
        script = str(Path(__file__).resolve())
        r = subprocess.run([sys.executable, script, str(p)], capture_output=True, text=True)
        assert r.returncode == 0, (r.returncode, r.stdout[-200:])
        r = subprocess.run([sys.executable, script, "--strict", str(p)],
                           capture_output=True, text=True)
        assert r.returncode == 1 and "[UNCHECKED-TIME]" in r.stdout, r.stdout[-200:]

    # An unreadable log is a structured verdict on the real CLI, not a traceback.
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "RD-THREADS.md"
        p.write_text("**2026-01-01 00:00 UTC — x.**\n")
        os.chmod(p, 0)
        if not os.access(p, os.R_OK):
            r = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(p)],
                               capture_output=True, text=True, timeout=60)
            blob = r.stdout + r.stderr
            assert r.returncode == 1 and "unreadable prerequisite" in blob, \
                (r.returncode, blob[-200:])
            assert "Traceback (most recent call last)" not in blob, blob[-200:]
        os.chmod(p, 0o644)
    print("self-test: PASS (after-mtime time/date flagged; in-past/date-only clean; "
          "malformed flagged; non-UTC surfaced and --strict fails; indented/list-item "
          "labels seen; unreadable log is a verdict, not a crash)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="team/RD-THREADS.md")
    ap.add_argument("--strict", action="store_true",
                    help="fail if any time-bearing label is not canonical UTC")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    path = Path(args.path).resolve()
    if not path.is_file():
        print(f"missing prerequisite: {path}")
        return 1
    if not os.access(path, os.R_OK):
        print(f"unreadable prerequisite: {path}")
        return 1
    try:
        dated, date_only, bad, unchecked = labels_after_mtime(path)
    except OSError as exc:
        print(f"unreadable prerequisite: {path}: {exc}")
        return 1
    print(f"=== {path}\n    dated_labels={dated}  date_only={date_only}  "
          f"unchecked_time_labels={len(unchecked)}  flagged_labels={len(bad)}")
    for label in bad:
        print(f"    {label}")
    for label in unchecked:
        print(f"    [UNCHECKED-TIME] {label}  (no canonical UTC suffix)")
    return 1 if bad or (args.strict and unchecked) else 0


if __name__ == "__main__":
    raise SystemExit(main())
