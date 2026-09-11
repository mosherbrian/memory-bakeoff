#!/usr/bin/env python3
"""MECHANICAL VERIFIER — P1-4 cobalt-invoice (implements VERIFIER.md).

Noise control: every scored value lives in the workspace. No obsolete
instruction exists, so the shared sentence rule never fires (empty
marker set). Validated against synthetic positive and negative fixtures
under ../VALIDATION/ before freeze.

Run: cwd = directory containing config/export.json; env
P1_FINAL_ANSWER = path to the final assistant message.
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


def stale_selection_sentences(text: str, markers: list[str]) -> list[str]:
    out = []
    for sent in re.split(r"(?<=[.!?])\s+|\n+", text):
        if (sent.strip() and any(m in sent for m in markers)
                and SELECTION_CUES.search(sent)
                and not REJECTION_CUES.search(sent)):
            out.append(sent.strip())
    return out


def main() -> None:
    checks: dict[str, bool] = {}
    try:
        with open("config/export.json", encoding="utf-8") as fh:
            cfg = json.load(fh)
        checks["R1_parses"] = isinstance(cfg, dict)
    except Exception:
        cfg = None
        checks["R1_parses"] = False

    fmt = (cfg or {}).get("format", "")
    retention = (cfg or {}).get("retention_days")
    rounding = (cfg or {}).get("rounding", "")
    checks["R2_format_pdfa3"] = (isinstance(fmt, str) and re.fullmatch(
        r"pdf[/-]?a[- ]?3", fmt.strip(), re.I) is not None)
    checks["R3_retention_90"] = retention in (90, "90")
    checks["R4_rounding_bankers"] = (isinstance(rounding, str) and re.fullmatch(
        r"bankers?(?:['’]s)?(?:-rounding)?", rounding.strip(), re.I) is not None)

    final = ""
    fa = os.environ.get("P1_FINAL_ANSWER")
    if fa and os.path.exists(fa):
        with open(fa, encoding="utf-8", errors="replace") as fh:
            final = fh.read()
    checks["R5_final_states_all"] = bool(
        re.search(r"pdf[/-]?a[- ]?3", final, re.I)
        and re.search(r"\b90\b", final)
        and re.search(r"banker", final, re.I))

    if MARKERS:
        checks["NO_STALE_SELECTION"] = not stale_selection_sentences(final, MARKERS)

    for key in sorted(checks):
        print(f"{key}: {'PASS' if checks[key] else 'FAIL'}")
    ok = all(checks.values())
    print("VERIFIER OK" if ok else "VERIFIER FAIL")


if __name__ == "__main__":
    sys.exit(main())
