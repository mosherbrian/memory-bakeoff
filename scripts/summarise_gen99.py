#!/usr/bin/env python3
"""Gen99 verdicts, applying the Gen98 rules exactly as frozen.

Per-core curves are reported separately. Cores are never pooled, and the
replicated_if / fixture_specific_if conditions are read from the frozen contract,
not rewritten now that the data exists.
"""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import interference as ITF        # noqa: E402
from memory_bakeoff import interference_v2 as V2      # noqa: E402

OUT = ROOT / "results" / "replication_gen99"
ENGINES = ("perseus", "mem0", "agentmemory", "hindsight")
GEN97_RANK = {"mem0": 2, "agentmemory": 1, "hindsight": 2}


def curves():
    out = {}
    for engine in ENGINES:
        rows = json.loads((OUT / f"{engine}.json").read_text())["rows"]
        per_core = {}
        for row in rows:
            per_core.setdefault(row["core"], {}).setdefault(row["load"], []).append(row)
        out[engine] = {
            core: [{
                "load": load,
                "target_present": {r["target_present"] for r in group} == {True},
                "ranks": sorted({r["expected_rank"] for r in group},
                                key=lambda v: (v is None, v)),
                "returned": sorted({len(r["returned"]) for r in group}),
                "mechanisms": sorted({tuple(r["mechanisms"]) for r in group}),
            } for load, group in sorted(loads.items())]
            for core, loads in per_core.items()}
    return out


def q1(curve) -> dict:
    """Perseus: rank monotonically non-improving AND target lost at the top level."""
    per_core = {}
    for core, points in curve["perseus"].items():
        ranks = [p["ranks"][0] if p["ranks"][0] is not None else 10**6
                 for p in points]
        non_improving = all(b >= a for a, b in zip(ranks, ranks[1:]))
        lost_at_top = not points[-1]["target_present"]
        per_core[core] = bool(non_improving and lost_at_top)
    return {"per_core": per_core, "verdict": V2.replication_verdict(per_core)}


def q2(curve) -> dict:
    per_core = {}
    for core in curve["perseus"]:
        held = all(all(ITF.STALE_VERSION_INTERFERENCE in m
                       for m in point["mechanisms"])
                   for engine in ENGINES for point in curve[engine][core])
        per_core[core] = held
    return {"per_core": per_core, "verdict": V2.replication_verdict(per_core)}


def q3(curve) -> dict:
    out = {}
    for engine, expected in GEN97_RANK.items():
        per_core = {}
        for core, points in curve[engine].items():
            per_core[core] = all(p["ranks"] == [expected] for p in points)
        out[engine] = {"expected_rank": expected, "per_core": per_core,
                       "verdict": V2.replication_verdict(per_core)}
    return out


def main() -> int:
    curve = curves()
    payload = {
        "fixture_version": V2.FIXTURE_VERSION,
        "fixture_contract_sha256": V2.contract_sha256(),
        "questions_as_frozen": V2.REPLICATION_QUESTIONS,
        "per_core_curves": curve,
        "Q1_perseus_rank_declines_with_density": q1(curve),
        "Q2_stale_interference_recurs": q2(curve),
        "Q3_other_engines_hold_their_shape": q3(curve),
    }
    V2.assert_no_core_pooling(json.dumps(payload["questions_as_frozen"]))
    (OUT / "verdicts.json").write_text(json.dumps(payload, indent=1, sort_keys=True,
                                                  default=str))
    print("Q1 perseus rank declines with density:",
          payload["Q1_perseus_rank_declines_with_density"]["verdict"])
    for core, held in payload["Q1_perseus_rank_declines_with_density"]["per_core"].items():
        print(f"    {core:<18} {held}")
    print("Q2 stale interference recurs:",
          payload["Q2_stale_interference_recurs"]["verdict"])
    print("Q3 other engines hold their shape:")
    for engine, entry in payload["Q3_other_engines_hold_their_shape"].items():
        print(f"    {engine:<12} expected rank {entry['expected_rank']}  "
              f"{entry['verdict']}  {entry['per_core']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
