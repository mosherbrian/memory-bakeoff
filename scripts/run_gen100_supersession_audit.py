#!/usr/bin/env python3
"""Gen100: is the 192/192 stale co-return a defect, or a question nobody asked?

No engine runs. Surfaces read from the pinned builds and the frozen adapter
contracts; the agentmemory rule is reimplemented and applied to the fixture text.
"""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import interference as ITF                    # noqa: E402
from memory_bakeoff import interference_v2 as V2        # noqa: E402
from memory_bakeoff import supersession_surface as SS    # noqa: E402


def main() -> int:
    fixture = V2.build_fixture()
    per_core = {}
    for core in V2.CORES:
        case = next(c for c in fixture.cases
                    if c.core == core["id"] and c.load == 0)
        order = [o.id for o in ITF.ordered_observations(
            fixture, case, V2.visible_ids)]
        per_core[core["id"]] = SS.explains_gen99_kestrel(fixture, core["id"], order)

    fired = sorted(c for c, e in per_core.items() if e["rule_can_fire"])
    payload = {
        "contract_version": SS.CONTRACT_VERSION,
        "surfaces": SS.SURFACES,
        "verdict": SS.verdict(),
        "agentmemory_rule_per_core": per_core,
        "cores_where_the_rule_can_fire": fired,
        "gen99_kestrel_explained": all(per_core[c]["explains_absence"] for c in fired),
    }
    destination = ROOT / "results" / "supersession_gen100"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "audit.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))

    for engine, entry in SS.SURFACES.items():
        print(f"{engine:12s} {entry['status']:32s} {entry['mechanism'][:44]}")
    print("\nagentmemory rule, per core:")
    for core, entry in per_core.items():
        print(f"  {core:<18} jaccard={entry['jaccard']:.3f} "
              f"can_fire={entry['rule_can_fire']} "
              f"explains_absence={entry['explains_absence']}")
    print("\ncores where it can fire:", fired)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
