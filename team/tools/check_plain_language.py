#!/usr/bin/env python3
"""Reject a status summary that still uses the team's own words.

WHY THIS EXISTS. Brian, 2026-09-17: "Sprint status should probably be run
through an LLM (multiple times maybe) until it is intelligible to me. I can't
understand most of what you all talk about."

"Multiple times until intelligible" needs a stop condition that is not a model's
opinion of its own writing - asked "is this clear?", a model says yes. So the
condition is mechanical: a list of words that are ours rather than Brian's, and
the summary is rejected while any of them survives. The writer rewrites until
this exits 0.

It also enforces two things a fluent rewrite can quietly lose:
  - FRESHNESS. A beautifully clear summary of a sprint that moved on is worse
    than the table, because it reads as current.
  - THE FACTS. The summary must not introduce a number that is absent from the
    computed fact sheet it was written from. Rendering is allowed; inventing is
    not, and a local model asked to be readable will happily round 71 to "about
    70" or add a total nobody computed.

Exit 0 clean, 1 with a named finding marker, no traceback.

  check_plain_language.py [SUMMARY.md] [--facts FACTS.txt] [--max-age-min N]
  check_plain_language.py --selftest
"""
import argparse
import re
import sys
import time
from pathlib import Path

# Absolute on purpose: the declared check must mean the same thing from every
# seat. Path.home() resolved inside sandboxed worker seats, where the check
# exited 1 [MISSING] (or silently disabled the facts cross-check) while the
# same invocation exited 0 canonically (CORVID-D-9-VERIFY, 2026-09-17).
DIR = Path("/home/bmosher/.local/share/agent-deck/conductor/glm")
SUMMARY = DIR / "status-plain.md"
FACTS = DIR / "status-facts.txt"

# Our vocabulary, not his. Every one has appeared in something he was expected
# to act on. Plural and -ed forms are matched by the word-boundary search.
BANNED = [
    "row", "rows", "gate", "gates", "gated", "verdict", "verdicts", "seat",
    "seats", "artifact", "artifacts", "poller", "ledger", "dispatch",
    "dispatched", "claimed", "unclaimed", "mtime", "prefix", "verifier",
    "verified", "unverified", "rowcheck", "fill-work", "standing debt",
    "build rows", "sprint-close", "lane", "lanes", "wake", "woken",
    "upstream", "downstream", "backlog row", "queue row", "in-flight",
]
# Ids like S6-1G or D-8 are our shorthand too: he has never asked about one.
IDLIKE = re.compile(r"\b(?:S\d+-\d+[A-Z]?|D-\d+[A-Z]?)\b")


def numbers(text):
    return set(re.findall(r"\d[\d,]*(?:\.\d+)?", text.replace(",", "")))


def findings(summary, facts=None, max_age_min=None, path=None,
             facts_path=None):
    out = []
    low = summary.lower()
    hit = [w for w in BANNED
           if re.search(r"(?<![a-z-])" + re.escape(w) + r"(?![a-z])", low)]
    if hit:
        out.append("[TEAM-JARGON] the summary still uses our words, not his: "
                   + ", ".join(sorted(set(hit))))
    ids = IDLIKE.findall(summary)
    if ids:
        out.append("[INTERNAL-ID] the summary names work by our id (%s). He has "
                   "never asked about one; say what the work IS."
                   % ", ".join(sorted(set(ids))[:6]))
    if not summary.strip():
        out.append("[EMPTY] the summary is empty")
    elif len(summary.split()) > 220:
        out.append("[TOO-LONG] %d words; the cap is 220, because a status nobody "
                   "finishes reading is not a status" % len(summary.split()))
    # AN INVENTED NUMBER AND A MOVED NUMBER ARE DIFFERENT PROBLEMS. 2026-09-17:
    # cairn wrote a correct, readable summary at 12:39 describing the 12:28
    # facts; six minutes later the fact sheet refreshed and this check called
    # its numbers invented. They were accurate when written. So the test only
    # applies when the summary was written from THIS sheet or a later one - if
    # the sheet is newer, the numbers are allowed to differ and the freshness
    # test below is the one that should speak.
    if facts is not None and path is not None and facts_path is not None:
        try:
            if facts_path.stat().st_mtime > path.stat().st_mtime + 5:
                facts = None
        except OSError:
            pass
    if facts is not None:
        invented = numbers(summary) - numbers(facts)
        invented = {n for n in invented if len(n) > 1}      # ignore 1-digit prose
        if invented:
            out.append("[INVENTED-NUMBER] %s appear in the summary but not in the "
                       "computed facts. Render the facts; do not add to them."
                       % ", ".join(sorted(invented)[:6]))
    if max_age_min and path and path.exists():
        age = (time.time() - path.stat().st_mtime) / 60.0
        if age > max_age_min:
            out.append("[STALE] written %d min ago, over the %d-min limit. A clear "
                       "summary of a sprint that moved on is worse than the table, "
                       "because it reads as current." % (age, max_age_min))
    return out


def selftest():
    facts = "Work finished: 71 of 73\nConfirmed by a second worker: 29\n"
    good = ("Three pieces of work finished this morning and all three passed "
            "their automatic checks. 71 of 73 are done. Nothing needs you.")
    bad_jargon = "Three rows are done but the gate FAILED and no verdict exists."
    bad_id = "S6-1 is finished and D-8 is next."
    bad_num = "Work finished: 71 of 73, and 400 checks ran."
    if findings(good, facts):
        print("selftest: FAIL - a clean summary was rejected: %s"
              % findings(good, facts)[0])
        return 1
    for name, text, marker in (("jargon", bad_jargon, "TEAM-JARGON"),
                               ("internal id", bad_id, "INTERNAL-ID"),
                               ("invented number", bad_num, "INVENTED-NUMBER")):
        got = findings(text, facts)
        if not any(marker in g for g in got):
            print("selftest: FAIL - %s was ACCEPTED" % name)
            return 1
    print("selftest: PASS (a plain summary accepted; team jargon, an internal "
          "id and an invented number each rejected by name, no traceback)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("summary", nargs="?", default=str(SUMMARY))
    ap.add_argument("--facts", default=str(FACTS))
    ap.add_argument("--max-age-min", type=int, default=0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    p = Path(a.summary)
    try:
        summary = p.read_text()
    except OSError as exc:
        print("[MISSING] %s: %s - nothing has written the plain summary yet"
              % (p, exc))
        return 1
    facts = None
    fp = Path(a.facts)
    if fp.exists():
        facts = fp.read_text()
    found = findings(summary, facts, a.max_age_min, p,
                     fp if fp.exists() else None)
    for f in found:
        print(f)
    if found:
        print("%d problem(s). Rewrite and run this again." % len(found))
        return 1
    print("plain enough: no team vocabulary, no internal ids, no invented "
          "numbers, within the length and freshness limits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
