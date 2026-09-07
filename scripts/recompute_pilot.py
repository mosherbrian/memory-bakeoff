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


def main():
    res = arms()
    res["_rule"] = ("cleaned = PREREGISTRATION section 2 as committed: "
                    "ordering_scorer.hit, whole session, both roles")
    res["_status"] = "PILOT. Exploratory. Held-out items untouched."
    (ROOT / "research/pilot_ordering/PILOT_HEADLINE.json").write_text(
        json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
