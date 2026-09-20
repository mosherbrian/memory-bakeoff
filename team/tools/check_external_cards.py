#!/usr/bin/env python3
"""Guard: every team/EXTERNAL-*.md card carries a goal mapping and a
do-not-trust section.

kiln-flash, QUEUE D-6 2026-09-17 (the row's declared check pointed here; the
file did not exist). The R&D intake route lands external findings as
EXTERNAL-*.md cards, and the council brief reads every card IN FULL; the card
contract (row D-6) makes two sections mandatory — how the finding maps onto
the frozen goals G1-G5 or a roadmap phase, and what about it should NOT be
trusted. A card without the second is a press release, which is exactly what
the KnowledgeDrift card's caveat section exists to prevent.

Checks, per card (deterministic text rules, no LLM):
  [NO-GOAL-MAPPING]   no frozen-goal id (G1..G5) and no roadmap mention
  [NO-DO-NOT-TRUST]   no do-not-trust / caveat / vendor-adjacent marker
Zero cards is not a violation (the route has nothing to check yet); the
summary says so rather than reading as a silent pass.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named finding marker and the line `external-cards check: N`, never a
traceback.

Usage:
  python3 check_external_cards.py [teamdir]   # default /home/bmosher/memory-bake-off/team
  python3 check_external_cards.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

DEFAULT_TEAM = "/home/bmosher/memory-bake-off/team"
GLOB = "EXTERNAL-*.md"
GOAL_RE = re.compile(r"\bG[1-5]\b|\broadmap\b|\bphase [a-h]\b", re.I)
# BROADENED 2026-09-17. The pattern required the literal "do not trust", and
# two authors independently wrote "What NOT to trust" instead - the fleet's own
# EXTERNAL-ENGRAM-ALPHA card and the atlas/heimdall cards written the same day.
# When the practice and the convention diverge, and the practice is the same in
# both places, the practice is the convention. The checker's job is to catch a
# card with NO caveat section, not to enforce one wording.
TRUST_RE = re.compile(
    r"do[ -]?not[ -]?trust|not[ -]to[ -]trust|not be trusted|vendor-adjacent|"
    r"\bcaveats?\b|disclaim|what not to trust", re.I)


def check(teamdir: Path) -> list[str]:
    findings: list[str] = []
    cards = sorted(teamdir.glob(GLOB))
    if not cards:
        print(f"no {GLOB} files under {teamdir}: nothing to check yet")
        return findings
    for card in cards:
        text = card.read_text(encoding="utf-8", errors="replace")
        if not GOAL_RE.search(text):
            findings.append(f"[NO-GOAL-MAPPING] {card.name}: no frozen-goal id "
                            "(G1-G5) or roadmap phase reference")
        if not TRUST_RE.search(text):
            findings.append(f"[NO-DO-NOT-TRUST] {card.name}: no do-not-trust / "
                            "caveat section — a card without one is a press release")
    return findings


_GOOD_CARD = """# External benchmark: Example Bench v1

## What it is
A benchmark for evolving agent state.

## Goal mapping
Abstention grounds **G3** invocation; the currency family maps onto **G2**
supersession and the Phase-E external lane of the roadmap.

## What it would let us stop building
Nothing new — it overlaps our abstention control.

## What about it should NOT be trusted
The author's own system tops its leaderboard: a vendor-adjacent claim. Its
post and repo report different scales; cite neither until reconciled.
"""


def _fixture(root: Path, break_goal: bool = False, break_trust: bool = False):
    card = _GOOD_CARD
    if break_goal:
        card = card.replace("Abstention grounds **G3** invocation; the currency "
                            "family maps onto **G2**\nsupersession and the Phase-E "
                            "external lane of the roadmap.", "It is relevant.")
    if break_trust:
        card = card.replace("## What about it should NOT be trusted\n"
                            "The author's own system tops its leaderboard: a "
                            "vendor-adjacent claim. Its\npost and repo report "
                            "different scales; cite neither until reconciled.\n",
                            "")
    (root / "EXTERNAL-EXAMPLE-20260917.md").write_text(card, encoding="utf-8")


def _selftest() -> int:
    fails: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _fixture(root)
        if check(root):
            fails.append(f"clean card REJECTED: {check(root)}")
        for label, kw in (("no-goal", dict(break_goal=True)),
                          ("no-trust", dict(break_trust=True)),
                          ("neither", dict(break_goal=True, break_trust=True))):
            d = root / label
            d.mkdir()
            _fixture(d, **kw)
            got = check(d)
            want = "[NO-GOAL-MAPPING]" if kw.get("break_goal") else None
            want2 = "[NO-DO-NOT-TRUST]" if kw.get("break_trust") else None
            if not got:
                fails.append(f"[{label}] dirty card ACCEPTED")
            if want and not any(want in f for f in got):
                fails.append(f"[{label}] missing {want}: {got}")
            if want2 and not any(want2 in f for f in got):
                fails.append(f"[{label}] missing {want2}: {got}")
        empty = root / "empty"
        empty.mkdir()
        if check(empty):
            fails.append(f"zero-cards dir reported findings: {check(empty)}")
    for f in fails:
        print(f"[SELFTEST-FAIL] {f}")
    if fails:
        print(f"external-cards selftest findings: {len(fails)}")
        return 1
    print("selftest: PASS (clean card accepted; no-goal / no-trust / neither "
          "rejected by name; zero-cards dir reads as nothing-to-check)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="EXTERNAL-*.md card contract guard")
    ap.add_argument("teamdir", nargs="?", default=DEFAULT_TEAM)
    ap.add_argument("--team", dest="teamdir_kw", default=None)
    ap.add_argument("--self-test", "--selftest", dest="selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    findings = check(Path(a.teamdir_kw or a.teamdir))
    for f in findings:
        print(f)
    print(f"external-cards check: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as e:  # a crash must still read as a finding
        print(f"[GUARD-ERROR] {type(e).__name__}: {e}")
        print("external-cards check: 1")
        raise SystemExit(1)
