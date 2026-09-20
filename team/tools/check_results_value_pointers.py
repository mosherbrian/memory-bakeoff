#!/usr/bin/env python3
"""Check that RESULTS.md row numbers are backed by a linked result artifact.

Corvid, R&D pulse 2026-09-12. Complements the invalidated-pointer and
dangling-link checks with the third defect class the row-12 audit found: a row
links to an artifact whose summary.csv contains *different* numbers (the
MemBukkit rows 81/82 mislink). Those pointers resolve and are not invalidated,
so neither existing check sees them.

Rule: for each Markdown table row that states a Hit number and links one or
more `results/<dir>` directories, at least one linked directory's summary.csv
must contain that stated hit@5 or all_relevant@5 value (rounded to 3 dp). Rows
whose links carry no machine-readable summary are skipped (nothing to compare).

Usage:
  python3 check_results_value_pointers.py [roots...]   # exit 1 on any finding
  python3 check_results_value_pointers.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import tempfile
from pathlib import Path

LINK_RE = re.compile(r"\]\(results/([A-Za-z0-9._-]+)\)")
NUM_RE = re.compile(r"\b\d+\.\d+\b")
RESULTS_FILES = ("RESULTS.md",)


def parse_summary(directory: Path) -> list[tuple[str, float, float]]:
    path = directory / "summary.csv"
    if not path.is_file():
        return []
    try:
        rows = list(csv.reader(path.read_text(encoding="utf-8", errors="replace").splitlines()))
    except OSError:
        return []
    if len(rows) < 2:
        return []
    header = rows[0]
    try:
        i_p = header.index("provider")
        i_hit = header.index("hit@5")
        i_ar = header.index("all_relevant@5")
    except ValueError:
        return []
    out = []
    for r in rows[1:]:
        if len(r) <= max(i_p, i_hit, i_ar):
            continue
        try:
            out.append((r[i_p], round(float(r[i_hit]), 3), round(float(r[i_ar]), 3)))
        except ValueError:
            continue
    return out


def scan_file(root: Path, md: Path) -> list[dict]:
    findings = []
    try:
        lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        # An unreadable index is a finding, not "no rows" (Assay/Alice 09:31-34).
        return [{"file": str(md.relative_to(root)), "line": 0, "stated": [],
                 "links": "", "text": "unreadable prerequisite", "unreadable": True}]
    for i, line in enumerate(lines):
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        evidence = cells[2]
        if "hit" not in evidence.lower():
            continue
        stated = {round(float(x), 3) for x in NUM_RE.findall(evidence)}
        links = LINK_RE.findall(cells[-1])
        if not links or not stated:
            continue
        unreadable_links = [d for d in links
                            if (root / "results" / d / "summary.csv").is_file()
                            and not os.access(root / "results" / d / "summary.csv", os.R_OK)]
        if unreadable_links:
            findings.append({"file": str(md.relative_to(root)), "line": i + 1,
                             "stated": sorted(stated), "links": ", ".join(unreadable_links),
                             "text": "unreadable prerequisite: linked summary.csv"})
            continue
        link_vals = {d: parse_summary(root / "results" / d) for d in links}
        if not any(v for v in link_vals.values()):
            continue  # no machine-readable linked artifact to compare against
        backed = any(
            round(h, 3) in stated or round(ar, 3) in stated
            for vals in link_vals.values() for _, h, ar in vals
        )
        if not backed:
            described = ", ".join(f"{d}={sorted({(h, ar) for _, h, ar in v})}"
                                  for d, v in link_vals.items() if v)
            findings.append({
                "file": str(md.relative_to(root)), "line": i + 1,
                "stated": sorted(stated), "links": described,
                "text": evidence[:120],
            })
    return findings


def scan(root: Path) -> list[dict]:
    out = []
    for name in RESULTS_FILES:
        p = root / name
        if p.is_file():
            out.extend(scan_file(root, p))
    return out


def missing_prerequisites(root: Path) -> list[dict]:
    # RESULTS.md is this guard's premise; a root without it must not read green.
    return [{"finding": f"missing prerequisite: {name}", "got": "absent", "want": "present"}
            for name in RESULTS_FILES if not (root / name).is_file()]


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for d, hit, ar in (("good_run", 0.5, 0.4), ("bad_run", 0.1, 0.1)):
            (root / "results" / d).mkdir(parents=True)
            (root / "results" / d / "summary.csv").write_text(
                "provider,mode,hit@5,all_relevant@5\n"
                f"engine,raw,{hit},{ar}\n")
        (root / "RESULTS.md").write_text(
            "| Syst | Class | Hit/all-relevant 0.500/0.400 | caveat | research | "
            "[good](results/good_run) |\n"
            "| Syst | Class | Hit/all-relevant 0.900/0.900 | caveat | research | "
            "[bad](results/bad_run) |\n")
        found = scan(root)
        assert len(found) == 1, found
        assert found[0]["line"] == 2 and "bad_run" in found[0]["links"], found
    with tempfile.TemporaryDirectory() as td:
        assert missing_prerequisites(Path(td)), "missing RESULTS.md not reported"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "results" / "d").mkdir(parents=True)
        (root / "results" / "d" / "summary.csv").write_text(
            "provider,mode,hit@5,all_relevant@5\nengine,raw,0.5,0.4\n")
        p = root / "RESULTS.md"
        p.write_text("| a | b | Hit 0.500 | c | research | [d](results/d) |\n")
        os.chmod(p, 0)
        if not os.access(p, os.R_OK):
            unread = [f for f in scan(root) if f.get("unreadable")]
            assert unread and "unreadable" in unread[0]["text"], scan(root)
        os.chmod(p, 0o644)
    print("self-test: PASS (unbacked row flagged; matching row clean; "
          "missing and unreadable RESULTS.md reported, not silently passed)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=["."])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    rc = 0
    for raw in args.roots:
        root = Path(raw).resolve()
        pre = missing_prerequisites(root)
        if pre:
            print(f"=== {root}\n    missing prerequisites: {len(pre)}")
            for f in pre:
                print(f"    {f['finding']}")
            rc = 1
            continue
        found = scan(root)
        print(f"=== {root}\n    RESULTS.md pointer findings: {len(found)}")
        for f in found:
            print(f"    {f['file']}:{f['line']} {f.get('text', '')} "
                  f"stated={f['stated']} links: {f['links']}")
        if found:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
