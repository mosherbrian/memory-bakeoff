#!/usr/bin/env python3
"""The research answer must rest on verdict files, never on yesterday's answer.

WHY. Brian, 2026-09-18: "No sense of whether anything we are doing is
meaningfully progressing the bake-off ... and no one else seems to be in charge
that could tell." The planner now writes `team/ANSWER.md` at each close - one
page saying what the evidence currently supports. That page is the only thing
in the project whose main content is PROSE, which makes it the easiest place
for a claim to survive after its evidence stops supporting it.

The named failure it guards is the telephone game (ASTRA-HUMAN-INTERFACE-DESIGN
-20260917.md, section E): "A daily briefing queries claims and primary
evidence, not yesterday's briefing." Without that rule an answer drifts by
recopying: each version keeps the conclusion and drops the conditions, and
nothing on disk ever contradicts it.

WHAT THIS GUARANTEES, NARROWLY. It checks PROVENANCE SHAPE, not truth:

  - an EVIDENCE line exists and names at least one verdict file;
  - every path it names exists on disk;
  - no cited evidence is a previous ANSWER (the telephone-game rule);
  - CHANGED SINCE LAST TIME and DECISION-READY are both present, so "nothing
    changed" must be stated rather than omitted;
  - the question table has at least one row.

It CANNOT establish that the evidence entails the answer. That judgement
belongs to the reviewing seat, per the same design: "No LLM should be the sole
judge of whether another LLM's explanation is faithful." Do not read a pass
here as a verified answer.

  check_answer_provenance.py [--answer PATH]
  check_answer_provenance.py --selftest

Exit 0 = the answer's provenance holds. Exit 1 = it does not, and it names why.
"""
import argparse
import re
import sys
import tempfile
from pathlib import Path

TEAM = Path("/home/bmosher/memory-bake-off/team")
ANSWER = TEAM / "ANSWER.md"
REQUIRED = ("CHANGED SINCE LAST TIME:", "DECISION-READY:", "EVIDENCE:")
# A path that looks like a superseded answer page. Citing one is the exact
# defect: the claim would then rest on an interpretation, not a measurement.
PRIOR_ANSWER = re.compile(r"ANSWER(\.\d{8}-\d{6})?\.md$")


def findings(text: str, root: Path) -> list[str]:
    out = []
    for key in REQUIRED:
        if not re.search(rf"^{re.escape(key)}", text, re.M):
            out.append(f"[MISSING-SECTION] the answer has no {key!r} line")
    rows = [ln for ln in text.splitlines()
            if ln.startswith("|") and ln.count("|") >= 5
            and not re.match(r"^\|[\s:-]+\|", ln)]
    # header + at least one question
    if len(rows) < 2:
        out.append("[NO-QUESTIONS] the answer carries no question table rows")

    m = re.search(r"^EVIDENCE: *(.+(?:\n(?!\w+[- ]).*)*)", text, re.M)
    cited = re.findall(r"[\w./-]+\.(?:json|jsonl|md)", m.group(1)) if m else []
    if not cited:
        out.append("[NO-EVIDENCE] the EVIDENCE line names no file")
    verdicts = 0
    for c in cited:
        p = Path(c)
        if not p.is_absolute():
            p = (root / c) if (root / c).exists() else (root.parent / c)
        if PRIOR_ANSWER.search(c):
            out.append(f"[CITES-PRIOR-ANSWER] {c} is a previous answer, not "
                       f"evidence - a claim may not rest on an earlier claim")
            continue
        if not p.exists():
            out.append(f"[MISSING-EVIDENCE] cited file does not exist: {c}")
            continue
        if p.name == "verdict.json":
            verdicts += 1
    if cited and not verdicts and not any(
            f.startswith("[CITES-PRIOR-ANSWER]") for f in out):
        out.append("[NO-VERDICT] no cited file is a verdict.json - the answer "
                   "rests on nothing the fleet measured")
    return out


CLEAN = """| Q | A | Limit | Next |
|---|---|---|---|
| Does X help? | No. | one case | try Y |

CHANGED SINCE LAST TIME: nothing new since the last answer.
DECISION-READY: none
EVIDENCE: S7-COMPOSE/verdict.json
"""


def selftest() -> int:
    bad = 0
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "S7-COMPOSE").mkdir()
        (root / "S7-COMPOSE" / "verdict.json").write_text("{}")
        (root / "ANSWER.20260918-120000.md").write_text("old")
        if findings(CLEAN, root):
            print("SELFTEST FAIL: a conforming answer was rejected:",
                  findings(CLEAN, root)); bad += 1
        mutants = {
            "no CHANGED line": CLEAN.replace("CHANGED SINCE LAST TIME: nothing "
                                             "new since the last answer.\n", ""),
            "no DECISION-READY": CLEAN.replace("DECISION-READY: none\n", ""),
            "no EVIDENCE line": CLEAN.replace("EVIDENCE: S7-COMPOSE/verdict.json",
                                              "EVIDENCE:"),
            "no question rows": re.sub(r"^\|.*$", "", CLEAN, flags=re.M),
            "cites a prior answer": CLEAN.replace(
                "S7-COMPOSE/verdict.json", "ANSWER.20260918-120000.md"),
            "cites a missing file": CLEAN.replace(
                "S7-COMPOSE/verdict.json", "S7-GHOST/verdict.json"),
            "cites no verdict": CLEAN.replace(
                "S7-COMPOSE/verdict.json", "BACKLOG-NEXT.md"),
        }
        for name, txt in mutants.items():
            if not findings(txt, root):
                print(f"SELFTEST FAIL: mutant accepted: {name}"); bad += 1
    if bad:
        return 1
    print(f"selftest clean: 1 conforming answer accepted, "
          f"7 non-conforming rejected")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--answer", default=str(ANSWER))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    p = Path(a.answer)
    if not p.exists():
        print(f"[NO-ANSWER] {p} does not exist - the planner has not filed one")
        return 1
    f = findings(p.read_text(), p.parent)
    for line in f:
        print(line)
    if f:
        return 1
    print(f"answer provenance holds: every cited file exists, at least one is a "
          f"verdict, and no claim rests on an earlier answer ({p})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
