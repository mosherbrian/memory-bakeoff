#!/usr/bin/env python3
"""Gen104: the corrected agentmemory arm, per core, against what Gen102 reported."""
from __future__ import annotations

import collections, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "supersession_ablation_gen102" / "agentmemory-on.json"


def main() -> int:
    data = json.loads(RESULTS.read_text())
    rows = data["rows"]
    print(f"fixture: {data['fixture_version']}  rows: {len(rows)}  "
          f"kind: {data['mechanism_kind']}")
    agg = collections.defaultdict(collections.Counter)
    for row in rows:
        bucket = agg[row["core"]]
        bucket["cells"] += 1
        bucket["current_kept"] += bool(row["current_retrievable"])
        bucket["stale"] += "stale_version_interference" in (row["mechanisms"] or [])
        bucket["clean"] += bool(row["clean"])
    head = ("core", "cells", "current_kept", "stale_co_return", "clean")
    print("{:<20}{:>6}{:>14}{:>17}{:>7}".format(*head))
    total = collections.Counter()
    for core, bucket in sorted(agg.items()):
        print("{:<20}{:>6}{:>14}{:>17}{:>7}".format(
            core, bucket["cells"], bucket["current_kept"],
            bucket["stale"], bucket["clean"]))
        total.update(bucket)
    print("{:<20}{:>6}{:>14}{:>17}{:>7}".format(
        "TOTAL", total["cells"], total["current_kept"],
        total["stale"], total["clean"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
