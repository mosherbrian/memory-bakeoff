#!/usr/bin/env python3
"""A literal pipe in a row's cells silently moves every column after it.

WHY THIS EXISTS. 2026-09-17, three times in one day:
  - markdown TABLES pasted into QUEUE.md were parsed as rows, and the poller
    paged Brian about rows seeking seats named `1-2m`, `83%` and `100%`;
  - six rows declare a check CONTAINING a pipe, so rowcheck truncated the
    command, it exited 127, and row_gate read that as "no gate declared" - six
    gates were not running and nothing said so;
  - row D-8G, whose whole subject is that pipes break cell parsing, contained a
    literal pipe and so could not be parsed itself. Its seats column read the
    middle of its own task text, and the gate dispatcher never saw it.

The first two were found by an alarm and by a worker. The third was found by
noticing a row had not been picked up. None of them was found by a check, which
is why this exists.

Exit 0 clean, exit 1 with a named finding marker, no traceback - the dialect
`check_checker_exit_contracts.py` enforces.

  check_no_pipes_in_seats.py [QUEUE.md]
  check_no_pipes_in_seats.py --selftest
"""
import re
import sys
from pathlib import Path

QUEUE = Path.home() / "memory-bake-off" / "team" / "QUEUE.md"
ID = re.compile(r"[0-9]+|[A-Za-z]{1,3}[0-9]*-?[0-9]+[A-Za-z]?")
COLS = 9          # leading empty + 7 declared columns + trailing empty


def findings(text):
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        if not line.startswith("|") or "|---" in line:
            continue
        c = line.split("|")
        rid = c[1].strip() if len(c) > 1 else ""
        if not rid or rid == "#" or not ID.fullmatch(rid):
            continue                      # not a row; the isrow guard's job
        if len(c) != COLS:
            out.append(("[EXTRA-PIPE] line %d row %s: %d fields, expected %d - a "
                        "literal pipe in a cell shifts every column after it, so "
                        "the seats and check cells are not what they look like"
                        % (n, rid, len(c), COLS)))
            continue
        seats = c[3].strip()
        if seats and not re.match(r"[A-Za-z]", seats):
            out.append("[SEATS-NOT-A-SEAT] line %d row %s: seats column reads %r"
                       % (n, rid, seats[:40]))
        m = re.search(r"\(check:([^)]*)\)", c[5])
        if m and "|" in m.group(1):
            out.append("[PIPED-CHECK] line %d row %s: the declared check contains "
                       "a pipe, so it truncates and exits 127, which reads as no "
                       "gate at all" % (n, rid))
    return out


def selftest():
    hdr = ("| # | Task | Eligible seats | Trigger | Artifact required | Cost cap "
           "| Status |\n|---|---|---|---|---|---|---|\n")
    clean = hdr + "| D-1 | do a thing | kiln-flash | pulse | `a.md` (check: true) | $0 | open |\n"
    if findings(clean):
        print("selftest: FAIL - a conforming row was rejected: %s" % findings(clean)[0])
        return 1
    dirty = hdr + "| D-2 | a | b | c` ` | d | kiln-flash | pulse | `a.md` | $0 | open |\n"
    if not findings(dirty):
        print("selftest: FAIL - a row with an extra pipe was ACCEPTED")
        return 1
    piped = hdr + "| D-3 | do a thing | kiln-flash | pulse | `a.md` (check: grep -c x a.md \x7c head -1) | $0 | open |\n"
    got = findings(piped)
    if not any("PIPED-CHECK" in g or "EXTRA-PIPE" in g for g in got):
        print("selftest: FAIL - a piped declared check was ACCEPTED")
        return 1
    print("selftest: PASS (conforming row accepted; an extra pipe and a piped "
          "declared check both rejected by name, no traceback)")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    path = Path(argv[1]) if len(argv) > 1 else QUEUE
    try:
        text = path.read_text()
    except OSError as exc:
        print("[UNREADABLE] %s: %s" % (path, exc))
        return 1
    found = findings(text)
    for f in found:
        print(f)
    if found:
        print("%d row(s) have a pipe where a pipe breaks parsing." % len(found))
        return 1
    print("no stray pipes: every row parses into %d fields and every declared "
          "check is pipe-free." % COLS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
