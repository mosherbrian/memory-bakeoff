#!/usr/bin/env python3
"""Flag unqualified LongMemEval score references (Corvid, R&D pulse 2026-09-12).

Three distinct benchmarks now circulate under the name "LongMemEval":
- our oracle split (`longmemeval_oracle.json`, knowledge-update, reader-attribution);
- the S variant (500-Q retrieval haystack; agentmemory's recall_any@K);
- the judged QA pipeline (MemBukkit; official gpt-4o judge).

A score line that says only "LongMemEval" cannot be compared or reproduced. This
check flags lines that pair "LongMemEval" with a numeric score while naming no
qualifier (oracle | LongMemEval-S | -s | v2 | version 2 | knowledge-update |
cleaned | split). Raw vendor-fetch dirs are skipped: they are verbatim sources,
not our prose.

Adjacency is **within the same sentence**: a number after a sentence end
(`. ! ?` + space) belongs to another subject and is not a LongMemEval score
(the named FP class that flagged `use LongMemEval (Gen124) … Cost: ~26%`).

Usage:
  python3 check_longmemeval_qualifiers.py [roots...]   # exit 1 on any finding
  python3 check_longmemeval_qualifiers.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import tempfile
from pathlib import Path

NAME_RE = re.compile(r"longmemeval", re.I)
# a percentage, or a decimal score like 89.20, within 60 chars and the SAME
# sentence as the name (a sentence end means the number belongs to another subject)
SCORE_TOK_RE = re.compile(r"\d+(?:\.\d+)?\s*%|\b\d{1,3}\.\d+\b")
SENTENCE_END_RE = re.compile(r"[.!?]\s")
QUAL_RE = re.compile(
    r"longmemeval[-_ ]?s\b|longmemeval[-_ ]?v2\b|longmemeval[-_ ]?oracle|"
    r"longmemeval[-_ ]?cleaned|oracle[-_ ]?(split|json|subset)|"
    r"\bs[-_ ]?variant\b|longmemeval[^.\n]{0,25}knowledge[- ]update", re.I)
DISCLAIM_RE = re.compile(
    r"split (?:un)?specified|split not specified|unspecified split", re.I)
SKIP_DIRS = ("row17-claims-fetches", "row20-claims-provenance",
             "rd-threads-fetches", "results")


def score_after_name(line: str) -> bool:
    m = NAME_RE.search(line)
    if not m:
        return False
    window = line[m.end(): m.end() + 60]
    cut = SENTENCE_END_RE.search(window)
    if cut:
        window = window[:cut.start()]
    return SCORE_TOK_RE.search(window) is not None


def findings_for(root: Path, md: Path, lines: list[str]) -> list[dict]:
    out = []
    for i, line in enumerate(lines):
        if not score_after_name(line):
            continue
        if QUAL_RE.search(line) or DISCLAIM_RE.search(line):
            continue
        out.append({"file": str(md.relative_to(root)), "line": i + 1,
                    "text": line.strip()[:160]})
    return out


def scan(root: Path) -> list[dict]:
    out = []
    for md in sorted(root.rglob("*.md")):
        parts = md.relative_to(root).parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        if not md.is_file():
            continue
        try:
            lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            # An unreadable prose file is a finding, not "no hits" (Assay/Alice 09:31-34).
            out.append({"file": str(md.relative_to(root)), "line": 0,
                        "text": "unreadable prerequisite", "unreadable": True})
            continue
        out.extend(findings_for(root, md, lines))
    return out


def missing_prerequisites(root: Path) -> list[dict]:
    # No scannable prose is a mis-root, not a clean tree.
    for md in root.rglob("*.md"):
        if any(p in SKIP_DIRS for p in md.relative_to(root).parts):
            continue
        if not md.is_file():
            continue
        return []
    return [{"finding": "missing prerequisite: *.md prose files "
                        "(no scannable sources)", "got": "absent", "want": "present"}]


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "BAD.md").write_text("MemOS achieves LongMemEval 89.20 overall.\n")
        (root / "GOOD.md").write_text("agentmemory LongMemEval-S R@5 95.2%.\n")
        (root / "GENERIC.md").write_text("the 14-item LongMemEval holdout stays untouched.\n")
        (root / "SENTENCE.md").write_text(
            "stop hand-writing cores, use LongMemEval (Gen124) — took seventeen "
            "generations. Cost: ~26% of all commits.\n")
        found = {f["file"] for f in scan(root)}
        assert found == {"BAD.md"}, found
    with tempfile.TemporaryDirectory() as td:
        assert missing_prerequisites(Path(td)), "empty root not reported"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = root / "LOCKED.md"
        p.write_text("MemOS LongMemEval 89.20\n")
        os.chmod(p, 0)
        if not os.access(p, os.R_OK):
            assert any(f.get("unreadable") for f in scan(root)), scan(root)
        os.chmod(p, 0o644)
    print("self-test: PASS (unqualified score flagged; LongMemEval-S clean; "
          "non-score mention clean; sentence-boundary number clean; source-less "
          "and unreadable prose reported)")
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
        print(f"=== {root}\n    unqualified LongMemEval score lines: {len(found)}")
        for f in found:
            print(f"    {f['file']}:{f['line']}  {f['text']}")
        if found:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
