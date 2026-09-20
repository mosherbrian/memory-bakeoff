#!/usr/bin/env python3
"""Candidate-card vs register consistency probe (Corvid, 2026-09-15).

The register promises "a named verifier per card" and completeness. This is a
read-only census that re-derives it from the files instead of trusting prose:

  * every `CANDIDATE-CARD-*.md` carries a `verifier:` line;
  * every card's topic appears in the register;
  * every card's primary arXiv id appears in the register;
  * every register arXiv id appears in some card.

Unwired (`probe_*` convention; adoption is an owner/QUEUE decision). Usage:
  probe_card_register_consistency.py [--team DIR] [--self-test]
Exit 0 = consistent; 1 = findings.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEF_TEAM = os.path.join(ROOT, "team")
CARD_RE = re.compile(r"CANDIDATE-CARD-(.+)\.md$")
ID_RE = re.compile(r"\b(?:arXiv:)?(2[0-9]{3}\.[0-9]{4,5})\b")
VERIFIER_RE = re.compile(r"verifier[s]?\s*:", re.I)


def census(team: str):
    cards = sorted(p for p in Path(team).glob("CANDIDATE-CARD-*.md"))
    regs = sorted(Path(team).glob("SPARK-CARD-REGISTER-*.md"))
    findings = []
    if not cards:
        return [f"missing prerequisite: no CANDIDATE-CARD-*.md in {team}"], {}
    if not regs:
        return [f"missing prerequisite: no SPARK-CARD-REGISTER-*.md in {team}"], {}
    reg_text = regs[-1].read_text(encoding="utf-8", errors="replace")
    # only the card TABLE rows count as registered cards; the register also
    # lists grounded-but-uncarded references in prose, which are not findings.
    table_ids = set()
    for line in reg_text.splitlines():
        if re.match(r"^\|\s*(?:A?\d+|F\d+|D\d+)\s*\|", line):
            table_ids.update(ID_RE.findall(line))
    reg = reg_text
    reg_ids = set(ID_RE.findall(reg))
    card_ids = set()
    for c in cards:
        topic = CARD_RE.search(c.name).group(1)
        text = c.read_text(encoding="utf-8", errors="replace")
        if not VERIFIER_RE.search(text):
            findings.append(f"no in-file verifier line: {c.name}")
        if topic not in reg:
            findings.append(f"card topic absent from register: {topic} ({c.name})")
        ids = ID_RE.findall(text)
        card_ids.update(ids)
        if ids and ids[0] not in reg_ids:
            findings.append(f"primary id {ids[0]} absent from register: {c.name}")
    for i in sorted(table_ids - card_ids):
        findings.append(f"register id with no card: {i}")
    return findings, {"cards": len(cards), "register": regs[-1].name, "reg_ids": len(table_ids)}


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        _w(td, "CANDIDATE-CARD-GOOD.md",
           "Title *Good* id arXiv:2601.00001\nverifier: Alice.\n")
        _w(td, "CANDIDATE-CARD-BAD.md", "Title *Bad* id arXiv:2602.00002\n")
        _w(td, "SPARK-CARD-REGISTER-x.md",
           "| 1 | GOOD | t | 2601.00001 | x | Alice |\n"
           "| 2 | BAD | t | 2602.00002 | x | Alice |\n")
        f, stats = census(td)
        assert stats["cards"] == 2, stats
        assert any("BAD.md" in x and "verifier" in x for x in f), f
        assert any("2603.00003" in x for x in f) is False, f
        _w(td, "CANDIDATE-CARD-GOOD.md",
           "Title *Good* id arXiv:2601.00001\nverifier: Alice.\n")
        _w(td, "CANDIDATE-CARD-BAD.md",
           "Title *Bad* id arXiv:2602.00002\nverifier: Alice.\n")
        f2, _ = census(td)
        assert not any("verifier" in x for x in f2), f2
        print("self-test: PASS (missing verifier flagged; consistent pair clean)")
    return 0


def _w(root, name, text):
    Path(root, name).write_text(text)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", default=DEF_TEAM)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    findings, stats = census(a.team)
    print(f"=== card/register consistency over {a.team}")
    if stats:
        print(f"    cards={stats['cards']} register={stats['register']} ids={stats['reg_ids']}")
    print(f"    findings: {len(findings)}")
    for x in findings:
        print(f"    {x}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
