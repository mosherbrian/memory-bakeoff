#!/usr/bin/env python3
"""Guard the CLAIMS-LEDGER class/origin counts against their tables.

Corvid, R&D pulse 2026-09-13 (rev 2, after Alice's second-seat check). Two
sections state counts that have gone stale when a row moved:

- `## CLASSIFICATION` — the `**Counts:**` line and `**Located … N of M rows**`.
- `## PROVENANCE` — the origin-table row count, repeated in prose as
  "N distinct origin artifacts for M rows", "The N claims come from …", and
  "All N rows remain `vendor-only`".

This re-derives them from the tables and fails on any drift. Definitions:

- a row's class is the first backticked token in its Class cell, canonicalized
  (`vendor-only (narrowed)` inside or outside the backticks → `vendor-only`;
  a hyphenated refinement `third-party-measured` → `third-party`); a cell whose
  token is not a known class is an explicit **unrecognized class cell** finding,
  never silently `unknown`;
- `Located = M − unsourced − no-claim`; `M` = `L-*` rows in `### Summary` only;
- `M` for provenance = `L-*` rows in `### Origin table`.

Usage:
  python3 check_ledger_counts.py [path]     # default team/CLAIMS-LEDGER.md
  python3 check_ledger_counts.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import tempfile
from collections import Counter
from pathlib import Path

KNOWN_CLASSES = ("vendor-only", "verified-by-us", "third-party", "contradicted",
                 "unsourced", "no-claim")
COUNT_RE = re.compile(r"(\d+)\s+`([a-z-]+)`")
LOCATED_RE = re.compile(r"Located and byte-checked:\*\*\s*(\d+)\s+of\s+(\d+)\s+rows", re.I)
ROW_RE = re.compile(r"^\|\s*(L-[A-Z0-9-]+)\s*\|")
CLASS_SPAN_RE = re.compile(r"`([^`]+)`")
WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
            "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
            "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
            "twenty": 20}


def _section(text: str, heading: str) -> str:
    """Text of the `## heading` section, up to the next `## ` heading."""
    out: list[str] = []
    inside = False
    for ln in text.splitlines():
        if ln.startswith("## "):
            inside = ln.startswith(heading)
            continue
        if inside:
            out.append(ln)
    return "\n".join(out)


def _between(text: str, start: str, end: str) -> str | None:
    i = text.find(start)
    if i < 0:
        return None
    j = text.find(end, i + len(start))
    return text[i: j if j >= 0 else len(text)]


def _num(tok: str | None) -> int | None:
    if tok is None:
        return None
    tok = tok.strip().lower()
    if tok.isdigit():
        return int(tok)
    return WORD_NUM.get(tok)


def _class_of(cell: str) -> str | None:
    m = CLASS_SPAN_RE.search(cell)
    if not m:
        return None
    token = m.group(1).strip().lower().split(" ", 1)[0].split("(", 1)[0]
    for k in KNOWN_CLASSES:
        if token == k or token.startswith(k + "-"):
            return k
    return None


def _check_classification(sec: str) -> list[dict]:
    if not sec:
        return [{"finding": "missing prerequisite: ## CLASSIFICATION section",
                 "got": "absent", "want": "present"}]
    summary = _between(sec, "### Summary", "\n### ")
    if summary is None:
        return [{"finding": "missing prerequisite: ### Summary subsection",
                 "got": "absent", "want": "present"}]
    rows = [ln for ln in summary.splitlines() if ROW_RE.match(ln)]
    if not rows:
        return [{"finding": "missing prerequisite: CLASSIFICATION summary rows",
                 "got": "absent", "want": "present"}]

    out: list[dict] = []
    actual: Counter[str] = Counter()
    for ln in rows:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        cell = cells[3] if len(cells) > 3 else ""
        cls = _class_of(cell)
        if cls is None:
            out.append({"finding": f"unrecognized class cell: {cell}",
                        "got": "unrecognized", "want": "a known class"})
        else:
            actual[cls] += 1

    counts_text = _between(sec, "**Counts:**", "**Located")
    if counts_text is None:
        out.append({"finding": "missing prerequisite: **Counts:** line",
                    "got": "absent", "want": "present"})
    else:
        stated = {cls: int(n) for n, cls in COUNT_RE.findall(counts_text)}
        for cls in sorted(set(actual) | set(stated)):
            if stated.get(cls, 0) != actual.get(cls, 0):
                out.append({"finding": f"class count {cls}", "got": actual.get(cls, 0),
                            "want": stated.get(cls, 0)})
        if sum(stated.values()) != len(rows):
            out.append({"finding": "Counts sum vs table rows", "got": sum(stated.values()),
                        "want": len(rows)})

    m = LOCATED_RE.search(sec)
    if not m:
        out.append({"finding": "missing prerequisite: Located line",
                    "got": "absent", "want": "present"})
    else:
        want_located = len(rows) - actual.get("unsourced", 0) - actual.get("no-claim", 0)
        if int(m.group(1)) != want_located or int(m.group(2)) != len(rows):
            out.append({"finding": "located count", "got": f"{m.group(1)} of {m.group(2)}",
                        "want": f"{want_located} of {len(rows)}"})
    return out


def _check_provenance(sec: str) -> list[dict]:
    if not sec:
        return [{"finding": "missing prerequisite: ## PROVENANCE section",
                 "got": "absent", "want": "present"}]
    table = _between(sec, "### Origin table", "\n**")
    if table is None:
        return [{"finding": "missing prerequisite: ### Origin table subsection",
                 "got": "absent", "want": "present"}]
    rows = [ln for ln in table.splitlines() if ROW_RE.match(ln)]
    n_rows = len(rows)
    out: list[dict] = []

    m = re.search(r"([A-Za-z0-9-]+)\s+distinct origin artifacts for\s+([A-Za-z0-9-]+)\s+rows", sec)
    if not m:
        out.append({"finding": "missing prerequisite: 'N distinct origin artifacts for M rows'",
                    "got": "absent", "want": "present"})
    elif _num(m.group(2)) != n_rows:
        out.append({"finding": "origin-table 'for M rows'", "got": _num(m.group(2)),
                    "want": n_rows})

    m = re.search(r"The\s+([A-Za-z0-9-]+)\s+claims come from", sec)
    if m and _num(m.group(1)) != n_rows:
        out.append({"finding": "provenance 'The N claims'", "got": _num(m.group(1)),
                    "want": n_rows})

    m = re.search(r"All\s+([A-Za-z0-9-]+)\s+rows\s+remain", sec)
    if m and _num(m.group(1)) != n_rows:
        out.append({"finding": "provenance 'All N rows remain'", "got": _num(m.group(1)),
                    "want": n_rows})
    return out


def check(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return (_check_classification(_section(text, "## CLASSIFICATION"))
            + _check_provenance(_section(text, "## PROVENANCE")))


def self_test() -> int:
    classification = (
        "## CLASSIFICATION — synthetic\n\n"
        "### Summary\n\n"
        "| Row | Slot | Claim | Class | Receipt |\n"
        "|---|---|---|---|---|\n"
        "| L-S01 | a | c | `vendor-only` | r |\n"
        "| L-S02 | a | c | `vendor-only (narrowed)` | r |\n"
        "| L-S03 | a | c | `third-party-measured` | r |\n"
        "| L-S04 | a | c | `unsourced` | r |\n\n"
        "**Counts:** 2 `vendor-only` · 0 `verified-by-us` ·\n"
        "1 `third-party` · 0 `contradicted` · 1 `unsourced` · 0 `no-claim`.\n"
        "**Located and byte-checked:** 3 of 4 rows.\n\n"
        "### What would move each row\n\n"
        "| Row | Action |\n|---|---|\n| L-S04 | trace it |\n")
    provenance = (
        "## PROVENANCE — synthetic\n\n"
        "### Origin table (earliest located appearance)\n\n"
        "| Row | Claim | First appeared | Origin artifact | Chain |\n"
        "|---|---|---|---|---|\n"
        "| L-S01 | c | 2024-01-01 | art-A | — |\n"
        "| L-S02 | c | 2024-01-02 | art-B | — |\n\n"
        "**Two distinct origin artifacts for two rows:** art-A; art-B.\n\n"
        "The two claims come from two origin artifacts.\n\n"
        "- No benchmark was run; this is provenance, not verification. All two rows\n"
        "  remain `vendor-only`.\n")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "L.md"
        p.write_text(classification + provenance)
        assert check(p) == [], check(p)

        # A class move without a count edit -> drift (both classes + sum).
        p.write_text((classification + provenance).replace(
            "| L-S03 | a | c | `third-party-measured` | r |",
            "| L-S03 | a | c | `vendor-only` | r |"))
        found = {f["finding"] for f in check(p)}
        assert "class count vendor-only" in found and "class count third-party" in found, found

        # An unrecognized class cell is explicit, not silently unknown.
        p.write_text((classification + provenance).replace("`unsourced` | r |",
                                                           "`mystery` | r |"))
        assert any("unrecognized class cell" in f["finding"] for f in check(p)), check(p)

        # Provenance table grows but prose count does not -> drift.
        p.write_text((classification + provenance).replace(
            "| L-S02 | c | 2024-01-02 | art-B | — |",
            "| L-S02 | c | 2024-01-02 | art-B | — |\n| L-S03 | c | 2024-01-03 | art-C | — |"))
        found = {f["finding"] for f in check(p)}
        assert "provenance 'All N rows remain'" in found, found

        # Missing Counts/Located remain structured.
        p.write_text(classification.split("**Counts:**")[0] + provenance)
        assert any("Counts" in f["finding"] for f in check(p)), check(p)
    print("self-test: PASS (counts clean; class move flagged; qualifier-in-backticks "
          "and hyphenated refinement canonicalized; unrecognized class explicit; "
          "provenance count drift flagged; missing Counts reported)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="team/CLAIMS-LEDGER.md")
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
        found = check(path)
    except OSError as exc:
        print(f"unreadable prerequisite: {path}: {exc}")
        return 1
    print(f"=== {path}\n    ledger count findings: {len(found)}")
    for f in found:
        print(f"    {f['finding']}: got={f['got']} want={f['want']}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
