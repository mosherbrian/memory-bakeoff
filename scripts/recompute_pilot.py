#!/usr/bin/env python3
"""Recompute every pilot headline from the committed rows, under the committed rule.

Round 7 found the published "cleaned n=30 / 14 vs 0" reproduces under NO
committed rule - it was the pre-rewrite crude turn-scoped cleaning, left standing
through two scorer rewrites, and 34 - 10 does not equal 30 on its face. Sixth
recurrence of the non-reproducible-number class. So the numbers are computed here
and nowhere else, and the documents quote this output.
"""
import glob, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.ordering_scorer import hit  # noqa: E402

SRC = Path("/home/bmosher/.cache/huggingface/hub/datasets--xiaowu0162--longmemeval-cleaned/"
           "snapshots/98d7416c24c778c2fee6e6f3006e7a073259d48f/longmemeval_oracle.json")


def eligible(item):
    """PREREGISTRATION section 2, the committed rule."""
    early, later = (" ".join(t["content"] for t in s) for s in item["haystack_sessions"])
    return hit(item["answer"], later) and not hit(item["answer"], early)


def arms():
    items = {x["question_id"]: x for x in json.loads(SRC.read_text())}
    out = {}
    for pattern, label in (("2*[!s]", "dated"), ("*-nodates", "dates_stripped")):
        dirs = sorted(glob.glob(str(ROOT / "research/pilot_ordering" / pattern)))
        if not dirs:
            continue
        rows = json.loads((Path(dirs[-1]) / "rows.json").read_text())
        by = {}
        for r in rows:
            by.setdefault(r["question_id"], {})[r["order"]] = r["hit"]
        block = {}
        for name, keep in (("as_run", lambda q: True),
                           ("cleaned", lambda q: eligible(items[q]))):
            k = {q: v for q, v in by.items() if keep(q)}
            block[name] = {
                "n": len(k),
                "chronological_hits": sum(v["stale_first"] for v in k.values()),
                "reversed_hits": sum(v["current_first"] for v in k.values()),
                "discordant_chronological_only":
                    sum(1 for v in k.values() if v["stale_first"] and not v["current_first"]),
                "discordant_reversed_only":
                    sum(1 for v in k.values() if v["current_first"] and not v["stale_first"]),
            }
        out[label] = block
    return out


MONTHS = ("january february march april may june july august september october "
          "november december jan feb mar apr jun jul aug sep sept oct nov dec").split()
WEEKDAYS = ("monday tuesday wednesday thursday friday saturday sunday "
            "mon tue tues wed thu thur thurs fri sat sun").split()


def date_words():
    """Round-8 defect 2 / LEDGER 154: the date-word caveats were typed, wrong,
    and load-bearing. Stated rule, computed number.

    Scope: the CONVERSATION TEXT of the pilot-half items only - every turn's
    content, both roles, both sessions. Not the headers, which the stripped arm
    removes anyway. Whole-word, case-folded. Years are 19xx or 20xx.
    """
    import re
    items = {x["question_id"]: x for x in json.loads(SRC.read_text())}
    dirs = sorted(glob.glob(str(ROOT / "research/pilot_ordering" / "*-nodates")))
    rows = json.loads((Path(dirs[-1]) / "rows.json").read_text())
    pilot = sorted({r["question_id"] for r in rows})
    month = re.compile(r"\b(" + "|".join(MONTHS) + r")\b", re.I)
    weekday = re.compile(r"\b(" + "|".join(WEEKDAYS) + r")\b", re.I)
    year = re.compile(r"\b(19|20)\d\d\b")
    counts = {"n_pilot": len(pilot), "month_or_year": 0, "month_and_weekday": 0,
              "month_or_year_or_weekday": 0}
    for q in pilot:
        text = " ".join(t["content"] for s in items[q]["haystack_sessions"] for t in s)
        m, w, y = bool(month.search(text)), bool(weekday.search(text)), bool(year.search(text))
        counts["month_or_year"] += m or y
        counts["month_and_weekday"] += m and w
        counts["month_or_year_or_weekday"] += m or y or w
    counts["_rule"] = ("conversation text only, both roles, both sessions; whole-word "
                       "month names and abbreviations, weekday names and abbreviations, "
                       "years 19xx/20xx")
    return counts


def main():
    res = arms()
    res["date_words"] = date_words()
    res["_rule"] = ("cleaned = PREREGISTRATION section 2 as committed: "
                    "ordering_scorer.hit, whole session, both roles")
    res["_status"] = "PILOT. Exploratory. Held-out items untouched."
    (ROOT / "research/pilot_ordering/PILOT_HEADLINE.json").write_text(
        json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
