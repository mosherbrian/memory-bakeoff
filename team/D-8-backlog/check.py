#!/usr/bin/env python3
"""Gate for QUEUE row D-8 (backlog refinement: `team/BACKLOG-NEXT.md`).

plumb-fable, row D-8G, 2026-09-17. Written FROM THE ROW TEXT ALONE, before this
seat opened `team/BACKLOG-NEXT.md` or anything kiln produced for D-8. The gate
states the contract; it was not fitted to a document.

The row's point: a backlog that merely EXISTS is not usable. The next sprint is
planned from this file with nobody on the critical path, so each candidate must
be gateable, placed, honest about prior numbers, and ranked without a tie.

The contract (marker in brackets). Candidates live in one or more markdown
tables. A candidate table is any table whose header has an `Artifact` column
and a `Check` column. It must also have these columns (header words, any case):
    Rank                          `rank` / `order` / `priority` / `#`
    Advances                      `goal` / `roadmap` / `advances`
    Prior measurement             `prior` / `previous` / `baseline`
All other columns (the candidate text itself) are free.

  [MISSING-FILE]         the backlog file is absent.
  [PROSE-ONLY]           no candidate table. Paragraphs and bullets are not a
                         backlog a machine can plan from.
  [EMPTY-LIST]           a candidate table with zero rows. The sprint is taken
                         as OPEN unless `--sprint-closed` is given: this gate
                         fails closed, because no sprint-state file was found
                         to read.
  [MISSING-COLUMN]       a candidate table lacks Rank, Advances or Prior.
  [PIPED-CHECK]          a row has MORE cells than its header. Cells are split
                         on EVERY pipe character, escaped or not, in backticks
                         or not, because that is what rowcheck does. A piped
                         check truncates and exits 127; six live rows were
                         silently ungated by exactly that on 2026-09-17. Put
                         the pipeline in a script and call the script.
  [MALFORMED-ROW]        a row has FEWER cells than its header.
  [NO-ARTIFACT]          the artifact cell is not a path (empty, TBD, prose).
  [CHECK-NOT-RUNNABLE]   the check cell is prose, a placeholder, does not parse
                         as shell, or its first word is not a command on this
                         box (that is an exit 127 at the gate).
  [CHECK-CANNOT-FAIL]    the check is only `true` / `echo` / `:` / `printf`.
  [NO-GOAL-LINK]         the Advances cell names no frozen goal (`goal 5`,
                         `G5`), no roadmap item (`roadmap: <item>`), and does
                         not say in words that it advances `neither`.
  [REMEASURE-NO-PRIOR]   the candidate text speaks of measuring (re-measure,
                         benchmark, eval, latency, score, re-run, replicate...)
                         and the Prior cell neither cites a prior measurement
                         (a path or a number) nor states `none exists`.
  [RANK-NOT-TOTAL]       a rank is not a positive whole number (`2=`, `T3`,
                         `1-2`, blank).
  [RANK-TIE]             two candidates share a rank, in one table or across
                         tables. A total order has no ties.

Limits, stated on purpose: the gate does not RUN the declared checks (their
artifacts do not exist yet) and cannot tell if the named goal is the RIGHT goal
or the cited number is the TRUE prior. Those stay with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `D-8 gate findings: N`, never a traceback.

Usage:
  python3 check.py [BACKLOG-NEXT.md] [--sprint-closed]
  python3 check.py --selftest   # prose-only and piped-check REJECTED, minimal
                                # conforming ACCEPTED, each mutant by its marker
"""
from __future__ import annotations

import argparse
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE.parent / "BACKLOG-NEXT.md"

ROLES = (  # order matters: first role to match a header cell takes it
    ("artifact", r"artifact"),
    ("check", r"check"),
    ("rank", r"rank|order|priority|^#$"),
    ("advances", r"goal|roadmap|advances"),
    ("prior", r"prior|previous|baseline"),
)
PLACEHOLDER = re.compile(r"^(tbd|todo|n/?a|none|\?+|-+|—|\.+|)$", re.I)
PATHISH = re.compile(r"^[\w.@+~/-]+$")
GOAL = re.compile(r"\bgoal[\s:#-]*[A-Za-z]?-?\d+|\bG-?\d+\b", re.I)
ROADMAP = re.compile(r"\broadmap\b\W+\w+", re.I)
NEITHER = re.compile(r"\bneither\b", re.I)
MEASURES = re.compile(
    r"measur|bench|\beval|latenc|throughput|accurac|\bscor(e|ing)|tok/s|hit@"
    r"|\brate\b|\btiming|re-?run|re-?test|replicat|reproduc", re.I)
NO_PRIOR = re.compile(
    r"none exists?|no prior|no previous|never (been )?measured"
    r"|not previously measured|first measurement", re.I)
CITES = re.compile(r"[\w.-]+/[\w./-]+|\w\.(md|json|jsonl|csv|txt|log)\b|\d")
BUILTINS = {"cd", "test", "[", "[[", "source", ".", "export", "set", "exit",
            "command", "exec", "eval", "true", "false", "echo", "printf", ":"}
CANNOT_FAIL = {"true", "echo", "printf", ":"}
SEPARATORS = {"&&", ";", "||", "&"}


def cells(line: str) -> list[str]:
    """Split the way rowcheck does: on every pipe, no escapes honoured."""
    s = line.strip()
    parts = s.split("|")
    if s.startswith("|"):
        parts = parts[1:]
    if s.endswith("|") and parts:
        parts = parts[:-1]
    return [p.strip() for p in parts]


def tables(text: str):
    """Yield (header cells, [(line number, raw line)]) per markdown table."""
    block: list[tuple[int, str]] = []
    fenced = False
    for n, line in enumerate(text.splitlines() + [""], 1):
        if line.strip().startswith(("```", "~~~")):
            fenced = not fenced
        if not fenced and line.strip().startswith("|"):
            block.append((n, line))
            continue
        if len(block) >= 2 and all(
                re.fullmatch(r":?-+:?", c) for c in cells(block[1][1])):
            yield cells(block[0][1]), block[2:]
        block = []


def unquote(cell: str) -> str:
    return cell.strip().strip("`").strip()


def not_runnable(cmd: str) -> tuple[str, str] | None:
    """(marker, reason) when `cmd` is not a runnable command, else None."""
    cmd = unquote(cmd)
    if PLACEHOLDER.match(cmd):
        return "CHECK-NOT-RUNNABLE", f"placeholder {cmd!r}, not a command"
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError as e:
        return "CHECK-NOT-RUNNABLE", f"does not parse as shell ({e})"
    if len(toks) >= 4 and all(t.rstrip(".,").isalpha() for t in toks[1:]):
        return "CHECK-NOT-RUNNABLE", "reads as a sentence, not a command"
    heads, first = [], True
    for t in toks:
        if t in SEPARATORS:
            first = True
        elif first and t not in {"(", "{", "!"} \
                and not re.fullmatch(r"[A-Za-z_]\w*=.*", t):
            heads.append(t)
            first = False
    if not heads:
        return "CHECK-NOT-RUNNABLE", "no command word"
    for h in heads:
        if h not in BUILTINS and "/" not in h and shutil.which(h) is None:
            return ("CHECK-NOT-RUNNABLE",
                    f"first word {h!r} is not a command on this box (exit 127)")
    if all(h in CANNOT_FAIL for h in heads):
        return "CHECK-CANNOT-FAIL", f"{' / '.join(heads)} passes on any input"
    return None


def check(text: str, sprint_open: bool) -> tuple[list[str], int]:
    out: list[str] = []
    ranks: dict[int, str] = {}
    found = count = 0
    for header, rows in tables(text):
        col: dict[str, int] = {}
        for i, h in enumerate(header):
            for role, pat in ROLES:
                if role not in col and re.search(pat, h.strip("*` "), re.I):
                    col[role] = i
                    break
        if "artifact" not in col or "check" not in col:
            continue
        found += 1
        lacking = [r for r in ("rank", "advances", "prior") if r not in col]
        if lacking:
            out.append(f"[MISSING-COLUMN] table header {header}: no column for "
                       f"{', '.join(lacking)}")
        free = [i for i in range(len(header)) if i not in col.values()]
        for n, line in rows:
            c = cells(line)
            count += 1
            label = f"line {n}"
            if len(c) > len(header):
                out.append(f"[PIPED-CHECK] {label}: {len(c)} cells under a "
                           f"{len(header)}-cell header. A cell holds a literal "
                           f"pipe; rowcheck splits on it, so the check is "
                           f"truncated and exits 127. Move the pipeline into a "
                           f"script and call the script.")
                continue
            if len(c) < len(header):
                out.append(f"[MALFORMED-ROW] {label}: {len(c)} cells under a "
                           f"{len(header)}-cell header")
                continue
            words = " ".join(c[i] for i in free)
            label = f"line {n} ({words[:40]!r})"

            parts = [p for p in re.split(r"[,\s]+", unquote(c[col["artifact"]]))
                     if p]
            if not parts or not all(
                    PATHISH.match(p) and ("/" in p or "." in p)
                    and not PLACEHOLDER.match(p) for p in parts):
                out.append(f"[NO-ARTIFACT] {label}: artifact cell "
                           f"{c[col['artifact']]!r} is not a path")

            bad = not_runnable(c[col["check"]])
            if bad:
                out.append(f"[{bad[0]}] {label}: check cell "
                           f"{c[col['check']]!r}: {bad[1]}")

            if "advances" in col:
                a = c[col["advances"]]
                if not (GOAL.search(a) or ROADMAP.search(a) or NEITHER.search(a)):
                    out.append(f"[NO-GOAL-LINK] {label}: advances cell {a!r} "
                               f"names no frozen goal (goal N), no roadmap item "
                               f"(roadmap: item), and does not say 'neither'")

            if "prior" in col and MEASURES.search(words):
                p = c[col["prior"]]
                if not NO_PRIOR.search(p) and (
                        PLACEHOLDER.match(unquote(p)) or not CITES.search(p)):
                    out.append(f"[REMEASURE-NO-PRIOR] {label}: the candidate "
                               f"measures something and the prior cell {p!r} "
                               f"cites no prior measurement and does not state "
                               f"'none exists'")

            if "rank" in col:
                r = c[col["rank"]].strip("*` ")
                if not re.fullmatch(r"[1-9]\d*", r):
                    out.append(f"[RANK-NOT-TOTAL] {label}: rank {r!r} is not a "
                               f"positive whole number")
                elif int(r) in ranks:
                    out.append(f"[RANK-TIE] {label}: rank {r} is also held by "
                               f"{ranks[int(r)]}. Resolve the tie.")
                else:
                    ranks[int(r)] = label
    if not found:
        out.append("[PROSE-ONLY] no candidate table. Required: a markdown table "
                   "with the columns Rank, Candidate, Artifact, Check, Advances, "
                   "Prior measurement; one row per candidate.")
    elif not count and sprint_open:
        out.append("[EMPTY-LIST] the candidate table has zero rows while the "
                   "sprint is open (pass --sprint-closed only when it is closed)")
    return out, count


def run(path: Path, sprint_open: bool) -> int:
    if not path.is_file():
        print(f"[MISSING-FILE] {path}")
        print("D-8 gate findings: 1")
        return 1
    findings, count = check(path.read_text(encoding="utf-8", errors="replace"),
                            sprint_open)
    for f in findings:
        print(f)
    if findings:
        print(f"D-8 gate findings: {len(findings)}")
        return 1
    print(f"D-8 gate: clean ({count} candidates, each gateable, placed, and "
          f"ranked without a tie)")
    return 0


# ---- selftest: prove the gate can fail ----

_GOOD = """# Backlog - next sprint

Refined in-sprint. Rank 1 is the first row the next sprint takes.

| Rank | Candidate | Artifact | Check | Advances | Prior measurement |
|---|---|---|---|---|---|
| 1 | B-1 re-measure recall latency at 4.7k writes | team/B-1-latency/report.md | python3 team/B-1-latency/check.py | frozen goal 5 | results/gen38/summary.csv, 212 ms |
| 2 | B-2 tidy the seat roster | team/B-2-roster/report.md | test -s team/B-2-roster/report.md | advances neither a frozen goal nor a roadmap item | n/a |
"""
_PROSE = """# Backlog - next sprint

Next we should re-measure recall latency. The artifact will be a report and the
check is that somebody reads it. After that, tidy the roster.

- latency first, it matters most
- roster second, or maybe tied with latency
"""
_B1_CHECK = "python3 team/B-1-latency/check.py |"
_B2_CHECK = "| test -s team/B-2-roster/report.md |"
_HEAD, _ROWS = _GOOD.split("|---|---|---|---|---|---|\n")

# name -> (text, extra argv, expected marker or None for clean)
_CASES = {
    "conforming": (_GOOD, [], None),
    "prose-only": (_PROSE, [], "PROSE-ONLY"),
    "piped check": (_GOOD.replace(
        _B1_CHECK, "python3 team/B-1-latency/check.py | grep -q PASS |"),
        [], "PIPED-CHECK"),
    "escaped pipe in backticks": (_GOOD.replace(
        _B1_CHECK, "`python3 team/B-1-latency/check.py \\| grep -q PASS` |"),
        [], "PIPED-CHECK"),
    "empty, sprint open": (_HEAD + "|---|---|---|---|---|---|\n", [],
                           "EMPTY-LIST"),
    "empty, sprint closed": (_HEAD + "|---|---|---|---|---|---|\n",
                             ["--sprint-closed"], None),
    "check is prose": (_GOOD.replace(
        _B2_CHECK, "| Verify by hand that the roster looks right |"),
        [], "CHECK-NOT-RUNNABLE"),
    "check is a sentence led by a real command": (_GOOD.replace(
        _B2_CHECK, "| test that the roster is tidy |"), [], "CHECK-NOT-RUNNABLE"),
    "check command not on this box": (_GOOD.replace(
        _B2_CHECK, "| frobnicate-d8 --verify |"), [], "CHECK-NOT-RUNNABLE"),
    "check is TBD": (_GOOD.replace(_B2_CHECK, "| TBD |"), [],
                     "CHECK-NOT-RUNNABLE"),
    "check cannot fail": (_GOOD.replace(_B2_CHECK, "| echo ok |"), [],
                          "CHECK-CANNOT-FAIL"),
    "no artifact": (_GOOD.replace("| team/B-2-roster/report.md | test",
                                  "| a short report | test"), [], "NO-ARTIFACT"),
    "no goal link": (_GOOD.replace("| frozen goal 5 |", "| helps the goal |"),
                     [], "NO-GOAL-LINK"),
    "re-measure without prior": (_GOOD.replace(
        "| results/gen38/summary.csv, 212 ms |", "| n/a |"),
        [], "REMEASURE-NO-PRIOR"),
    "rank tie": (_GOOD.replace("| 2 | B-2", "| 1 | B-2"), [], "RANK-TIE"),
    "rank tie across two tables": (
        _GOOD + "\n" + _HEAD.split("\n\n")[-1] + "|---|---|---|---|---|---|\n"
        + _ROWS.splitlines()[1] + "\n", [], "RANK-TIE"),
    "rank left as a tie mark": (_GOOD.replace("| 2 | B-2", "| 1= | B-2"), [],
                                "RANK-NOT-TOTAL"),
    "no prior column": (_GOOD.replace("Prior measurement", "Notes"), [],
                        "MISSING-COLUMN"),
    "short row": (_GOOD.replace(" | n/a |", " |"), [], "MALFORMED-ROW"),
    "binary junk": ("\x00\xff|\x00|\n|--|\n" * 3, [], "PROSE-ONLY"),
}
_MARKER = re.compile(r"^\[([A-Z][A-Z-]+)\]", re.M)


def selftest() -> int:
    bad: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        jobs = [(name, Path(td) / f"{i}.md", text, argv, want)
                for i, (name, (text, argv, want)) in enumerate(_CASES.items())]
        jobs.append(("missing file", Path(td) / "absent.md", None, [],
                     "MISSING-FILE"))
        for name, path, text, argv, want in jobs:
            if text is not None:
                path.write_text(text, encoding="utf-8")
            p = subprocess.run([sys.executable, __file__, str(path), *argv],
                               capture_output=True, text=True, timeout=60)
            text_out = p.stdout + p.stderr
            got = set(_MARKER.findall(text_out))
            if "Traceback (most recent call last)" in text_out:
                bad.append(f"{name}: traceback")
            elif want is None and (p.returncode != 0 or got):
                bad.append(f"{name}: should be ACCEPTED, got exit "
                           f"{p.returncode} {sorted(got)}")
            elif want is not None and (p.returncode != 1 or got != {want}
                                       or "D-8 gate findings: " not in text_out):
                bad.append(f"{name}: should be REJECTED by exactly {want}, got "
                           f"exit {p.returncode} {sorted(got)}")
    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS ({len(_CASES) + 1} fixtures: conforming and "
          f"closed-sprint-empty accepted; prose-only, piped check, and every "
          f"other mutant rejected by exactly its own marker, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row D-8")
    ap.add_argument("backlog", nargs="?", default=str(DEFAULT))
    ap.add_argument("--sprint-closed", action="store_true",
                    help="an empty list is allowed only with this flag")
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(Path(a.backlog), not a.sprint_closed)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("D-8 gate findings: 1")
        raise SystemExit(1)
