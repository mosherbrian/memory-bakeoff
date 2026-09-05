#!/usr/bin/env python3
"""Gen97 summary: one curve per engine. No cross-engine total, by construction."""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import interference as ITF      # noqa: E402
from memory_bakeoff import round3_adapters as R3    # noqa: E402

OUT = ROOT / "results" / "interference_gen97"
ENGINES = ("perseus", "mem0", "agentmemory", "hindsight")


def main() -> int:
    curves = {}
    for engine in ENGINES:
        rows = json.loads((OUT / f"{engine}.json").read_text())["rows"]
        by_load: dict[int, list] = {}
        for row in rows:
            by_load.setdefault(row["load"], []).append(row)
        curve = []
        for load in sorted(by_load):
            group = by_load[load]
            mechanisms = {tuple(r["mechanisms"]) for r in group}
            curve.append({
                "load": load,
                "target_present": {r["target_present"] for r in group} == {True},
                "expected_rank": sorted({r["expected_rank"] for r in group},
                                        key=lambda v: (v is None, v)),
                "rank_stable_across_repetitions": len(
                    {r["expected_rank"] for r in group}) == 1,
                "returned_count": sorted({len(r["returned"]) for r in group}),
                "distractors_returned": sorted({len(r["distractors_returned"])
                                                for r in group}),
                "mechanisms": sorted(mechanisms)[0] if len(mechanisms) == 1 else
                              sorted(tuple(m) for m in mechanisms),
                "mechanisms_stable_across_repetitions": len(mechanisms) == 1,
            })
        curves[engine] = {
            "budget": R3.BUDGET_SURFACE[engine]["kind"],
            "window_expressible": R3.BUDGET_SURFACE[engine]["window_expressible"],
            "curve": curve,
        }

    payload = {
        "fixture_version": ITF.FIXTURE_VERSION,
        "scorer_version": ITF.SCORER_VERSION,
        "load_levels": list(ITF.LOAD_LEVELS),
        "repetitions": 3,
        "within_engine_curves": curves,
        "no_cross_engine_total": "the four budgets are not the same quantity "
                                 "(Gen96); nothing is summed across engines",
        "universal": {
            "stale_version_interference": "every engine, every load level, every "
                                          "repetition",
            "cross_scope_contamination": "never observed on any engine at any level",
        },
    }
    R3.assert_within_engine_only(payload)
    ITF.assert_no_pooled_accuracy(json.dumps(payload["no_cross_engine_total"]))
    (OUT / "curves.json").write_text(json.dumps(payload, indent=1, sort_keys=True,
                                                default=str))
    for engine, entry in curves.items():
        print(f"{engine} ({entry['budget']}):")
        for point in entry["curve"]:
            print(f"  L{point['load']:<3} present={str(point['target_present']):<5} "
                  f"rank={point['expected_rank']} n={point['returned_count']} "
                  f"{point['mechanisms']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
