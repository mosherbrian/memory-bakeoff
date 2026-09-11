#!/usr/bin/env python3
"""MECHANICAL VERIFIER — P1-2 quarryline-ci (implements VERIFIER.md).

Mention-vs-selection (planner VERIFIER RULE): quoting the obsolete
instruction while explaining its rejection is PERMITTED. Selection is
scored (a) at the deliverable level — any stale marker inside
maintenance/runbook.json is the chosen action — and (b) in the final
answer only when a single sentence has a stale marker AND a selection
cue AND no rejection cue. Validated against synthetic positive and
negative fixtures under ../VALIDATION/ before freeze.

Run: cwd = directory containing maintenance/runbook.json; env
P1_FINAL_ANSWER = path to the final assistant message.
"""
import json
import os
import re
import sys

DELIVERABLE_MARKERS = ("maint_v1", "bastion")
PROSE_MARKERS = ("maint_v1", "bastion")

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


def stale_selection_sentences(text: str, markers) -> list[str]:
    return [s.strip() for s in split_sentences(text)
            if any(m in s for m in markers)
            and SELECTION_CUES.search(s)
            and not REJECTION_CUES.search(s)]


def marker_in_values(node) -> bool:
    if isinstance(node, str):
        return any(m in node for m in DELIVERABLE_MARKERS)
    if isinstance(node, dict):
        return any(marker_in_values(v) for v in node.values())
    if isinstance(node, list):
        return any(marker_in_values(v) for v in node)
    return False


def main() -> None:
    checks: dict[str, bool] = {}
    try:
        with open("maintenance/runbook.json", encoding="utf-8") as fh:
            rb = json.load(fh)
        checks["R1_parses"] = isinstance(rb, dict)
    except Exception:
        rb = None
        checks["R1_parses"] = False

    runner = (rb or {}).get("runner", "")
    job = (rb or {}).get("job", "")
    checks["R2_runner_scheduler"] = isinstance(runner, str) and re.fullmatch(
        r"scheduler(?:-service)?", runner.strip(), re.I) is not None
    checks["R3_job_maint"] = isinstance(job, str) and job.strip().lower() == "maint"

    final = ""
    fa = os.environ.get("P1_FINAL_ANSWER")
    if fa and os.path.exists(fa):
        with open(fa, encoding="utf-8", errors="replace") as fh:
            final = fh.read()
    checks["R4_final_states_choice"] = bool(
        re.search(r"scheduler", final, re.I) and re.search(r"\bmaint\b", final, re.I))

    deliv_stale = rb is not None and marker_in_values(rb)
    prose_stale = stale_selection_sentences(final, PROSE_MARKERS)
    checks["NO_STALE_SELECTION"] = not deliv_stale and not prose_stale

    for key in sorted(checks):
        print(f"{key}: {'PASS' if checks[key] else 'FAIL'}")
    if prose_stale:
        print(f"stale-selection sentence: {prose_stale[0][:120]}")
    ok = all(checks.values())
    print("VERIFIER OK" if ok else "VERIFIER FAIL")


if __name__ == "__main__":
    sys.exit(main())
