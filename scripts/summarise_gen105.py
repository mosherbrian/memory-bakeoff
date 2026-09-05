#!/usr/bin/env python3
"""Gen105: perseus and hindsight per core/load on the corrected path."""
from __future__ import annotations

import collections, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "supersession_ablation_gen102"


def rows(engine: str, arm: str):
    path = RESULTS / f"{engine}-{arm}.json"
    return json.loads(path.read_text())["rows"] if path.exists() else []


def key(row):
    return (row["core"], row["load"], row.get("repetition", row.get("rep")))


def main() -> int:
    for engine in ("perseus", "hindsight"):
        off = {key(r): r for r in rows(engine, "off")}
        on = {key(r): r for r in rows(engine, "on")}
        shared = sorted(set(off) & set(on))
        print(f"\n=== {engine}  ({len(shared)} paired cells)")
        agg = collections.defaultdict(collections.Counter)
        for k in shared:
            core, load = k[0], k[1]
            bucket = agg[(core, load)]
            bucket["cells"] += 1
            stale_off = "stale_version_interference" in (off[k]["mechanisms"] or [])
            stale_on = "stale_version_interference" in (on[k]["mechanisms"] or [])
            bucket["stale_removed"] += stale_off and not stale_on
            # hindsight has no result count (token budget, window_expressible
            # False), so it records target_present rather than current_retrievable.
            def kept(row):
                return row.get("current_retrievable", row.get("target_present"))
            bucket["current_lost"] += kept(off[k]) and not kept(on[k])
            # A rank move is the EXPECTED consequence of removing the stale
            # record, not a cost - counted so it is visible, not as a failure.
            bucket["rank_moved"] += off[k].get("current_rank") != on[k].get("current_rank")
        print("{:<20}{:>5}{:>7}{:>15}{:>14}{:>12}".format(
            "core", "load", "cells", "stale_removed", "current_lost", "rank_moved"))
        for (core, load), b in sorted(agg.items()):
            print("{:<20}{:>5}{:>7}{:>15}{:>14}{:>12}".format(
                core, load, b["cells"], b["stale_removed"],
                b["current_lost"], b["rank_moved"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
