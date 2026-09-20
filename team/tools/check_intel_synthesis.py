#!/usr/bin/env python3
"""Every intel report must be answered, or the channel starves silently.

WHY. Brian, 2026-09-17, adding a free daily research feed: "We should
incorporate the intake and synthesis of these into our research portfolio and
repo as part of our overall loop."

Intake is the easy half and it is already automatic. SYNTHESIS is the half that
rots: a report lands, nobody reads it, and the folder fills with unread
intelligence while the board looks healthy. That is the same shape as the R2H
day-0 receipt, which sat three days because the obligation lived in a document
instead of on the board with a check.

So: each fetched report needs a synthesis note that accounts for every section
of it - naming either a candidate card it produced, or a plain reason no card
was warranted. "Nothing actionable today" is a PASSING answer; silence is not.

  check_intel_synthesis.py [--max-age-h 30]
  check_intel_synthesis.py --selftest

Exit 0 = every report is answered. Exit 1 = one is not, and it names which.
"""
import argparse
import re
import sys
import time
from pathlib import Path

# Absolute on purpose: the declared check must mean the same thing from every
# seat. Path.home() resolved inside sandboxed worker seats, where the check
# gives a false [NO-REPORTS] on an answered feed (same class as the
# check_r2h_smoke_receipt DEFAULT fix, D-10, and check_plain_language DIR,
# D-9). Fixed by corvid 2026-09-17 before first producer use.
TEAM = Path("/home/bmosher/memory-bake-off/team")
INTEL = TEAM / "INTEL"
# The sections the report carries. A synthesis must speak to each one that is
# actually present, so a partial read cannot pass as a complete one.
SECTIONS = ("PRIORITY CHANGES", "SYSTEMS TO INVESTIGATE",
            "BENCHMARKS TO INVESTIGATE", "EXPERIMENTS TO CONSIDER",
            "RESEARCH LEADS")


def reports(intel=INTEL):
    return sorted(intel.glob("AGENT_MEMORY_INTEL_*.md"))


def findings(max_age_h=30, intel=INTEL, team=TEAM):
    out = []
    rs = reports(intel)
    if not rs:
        out.append("[NO-REPORTS] nothing in team/INTEL/ - either the feed has "
                   "not started or intel-intake is failing. An empty folder is "
                   "not the same as a quiet day; check the intake log.")
        return out
    for r in rs:
        date = re.search(r"(20\d\d-\d\d-\d\d)", r.name)
        date = date.group(1) if date else r.stem
        syn = intel / f"SYNTHESIS-{date}.md"
        age_h = (time.time() - r.stat().st_mtime) / 3600.0
        if not syn.exists():
            if age_h > max_age_h:
                out.append(f"[UNREAD] {r.name} arrived {age_h:.0f}h ago and has "
                           f"no SYNTHESIS-{date}.md. The feed is being collected "
                           f"and not read, which is worse than not collecting it.")
            continue
        text = syn.read_text()
        body = r.read_text()
        present = [s for s in SECTIONS if s in body]
        for s in present:
            if s.lower() not in text.lower():
                out.append(f"[SECTION-SKIPPED] SYNTHESIS-{date}.md does not "
                           f"mention {s!r}, which the report carries. Say what "
                           f"you did with it, even if the answer is nothing.")
        # Every claimed card must exist. A synthesis naming a file that was
        # never written is the most flattering possible failure.
        for m in re.finditer(r"(?:team/)?(EXTERNAL-[A-Za-z0-9._-]+\.md)", text):
            if not (team / m.group(1)).exists():
                out.append(f"[CARD-MISSING] SYNTHESIS-{date}.md cites "
                           f"{m.group(1)} but that file does not exist")
        has_card = "EXTERNAL-" in text
        declines = re.search(r"no card|nothing actionable|not worth a card|"
                             r"no candidate", text, re.I)
        if not has_card and not declines:
            out.append(f"[NO-VERDICT] SYNTHESIS-{date}.md neither produced a "
                       f"card nor said plainly that none was warranted")
    return out


def selftest():
    import tempfile
    d = Path(tempfile.mkdtemp()); i = d / "INTEL"; i.mkdir()
    body = "\n".join(["report_date: 2026-01-01"] + list(SECTIONS))
    (i / "AGENT_MEMORY_INTEL_2026-01-01.md").write_text(body)
    if not any("UNREAD" in f for f in findings(0, i, d)):
        print("selftest: FAIL - an unread report was accepted"); return 1
    ok = "Reviewed all of: " + ", ".join(SECTIONS) + ". No card warranted."
    (i / "SYNTHESIS-2026-01-01.md").write_text(ok)
    if findings(0, i, d):
        print("selftest: FAIL - an honest 'no card' synthesis was rejected: %s"
              % findings(0, i, d)[0]); return 1
    (i / "SYNTHESIS-2026-01-01.md").write_text(
        "Reviewed " + ", ".join(SECTIONS) + ". See team/EXTERNAL-ghost-1.md")
    if not any("CARD-MISSING" in f for f in findings(0, i, d)):
        print("selftest: FAIL - a cited card that does not exist was accepted")
        return 1
    (i / "SYNTHESIS-2026-01-01.md").write_text("Looked at PRIORITY CHANGES. No card.")
    if not any("SECTION-SKIPPED" in f for f in findings(0, i, d)):
        print("selftest: FAIL - a synthesis skipping four sections was accepted")
        return 1
    (i / "SYNTHESIS-2026-01-01.md").write_text("Reviewed " + ", ".join(SECTIONS))
    if not any("NO-VERDICT" in f for f in findings(0, i, d)):
        print("selftest: FAIL - a synthesis with no verdict was accepted"); return 1
    print("selftest: PASS (an honest 'no card' answer accepted; an unread "
          "report, a cited-but-missing card, a skipped section and a missing "
          "verdict each rejected by name)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age-h", type=float, default=30.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    f = findings(a.max_age_h)
    for x in f:
        print(x)
    if f:
        print(f"\n{len(f)} problem(s). The feed is only worth having if it is "
              f"read.")
        return 1
    print(f"every intel report in team/INTEL/ is answered "
          f"({len(reports())} report(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
