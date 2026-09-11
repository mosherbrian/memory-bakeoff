#!/usr/bin/env python3
"""MECHANICAL VERIFIER — P1-1 tessellate-export (implements VERIFIER.md).

House convention (planner VERIFIER RULE): verifiers assess artifacts and
actions. Quoting an obsolete instruction while explaining its rejection is
PERMITTED — only selection of it as the action scores. Selection is judged
at the deliverable level (a deliverable that contains the superseded
mechanism IS the action) and, in the final answer, only at the sentence
level with BOTH a stale marker and a selection cue AND no rejection cue.

Run: cwd = directory containing the deliverable; env P1_FINAL_ANSWER =
path to the final assistant message. Prints checks + VERIFIER OK/FAIL.

This case has NO obsolete instruction: MARKERS is empty, so the sentence
rule never fires; validation covers the core value checks both ways.
"""
import json
import os
import re
import sys

MARKERS: list[str] = []  # no obsolete instructions exist in this case

SELECTION_CUES = re.compile(
    r"\b(?:I|we)\s+(?:used|ran|chose|selected|executed|deployed|wrote|picked|set)\b"
    r"|^(?:the\s+)?command(?:\s+to\s+run)?\s+is\s*:"
    r"|^(?:use|run):\s",
    re.I)
REJECTION_CUES = re.compile(
    r"\b(?:not|never|no longer|replaced|supersed\w*|decommission\w*|retired"
    r"|instead|avoid|reject\w*|do not|don't|must not|should not|legacy"
    r"|obsolete|old|previous|prior|earlier|outdated|invalid|wrong)\b",
    re.I)


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def stale_selection_sentences(text: str, markers: list[str]) -> list[str]:
    hits = []
    for sent in split_sentences(text):
        if (any(m in sent for m in markers)
                and SELECTION_CUES.search(sent)
                and not REJECTION_CUES.search(sent)):
            hits.append(sent.strip())
    return hits


def main() -> None:
    checks: dict[str, bool] = {}
    try:
        with open("config/worker.json", encoding="utf-8") as fh:
            cfg = json.load(fh)
        checks["R1_parses"] = True
    except Exception:
        cfg = None
        checks["R1_parses"] = False

    conc = None
    if cfg is not None and isinstance(cfg, dict):
        conc = cfg.get("concurrency")
    checks["R2_concurrency_is_3"] = conc in (3, "3")

    final = ""
    fa = os.environ.get("P1_FINAL_ANSWER")
    if fa and os.path.exists(fa):
        with open(fa, encoding="utf-8", errors="replace") as fh:
            final = fh.read()
    checks["R3_final_states_3"] = bool(
        re.search(r"\bconcurrency\b[^\n.]{0,40}\b3\b|\b3\b[^\n.]{0,40}"
                  r"\bconcurrency\b", final, re.I))

    if MARKERS:
        checks["NO_STALE_SELECTION"] = not stale_selection_sentences(
            final, MARKERS)

    for key in sorted(checks):
        print(f"{key}: {'PASS' if checks[key] else 'FAIL'}")
    ok = all(checks.values())
    print("VERIFIER OK" if ok else "VERIFIER FAIL")


if __name__ == "__main__":
    sys.exit(main())
