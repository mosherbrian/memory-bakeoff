"""Gen96: freeze the Round-3 adapters and audit each engine's retrieval budget.

No engine runs. This records what each surface can express, and refuses to
pretend the four windows are the same quantity.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import interference as itf
from memory_bakeoff import round3_adapters as r3

SCOPE = "server:atlas"
CONFIGURATION = "A1"


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    fixture = itf.build_fixture()

    payload = {
        "preflight": r3.preflight(),
        "bindings": {engine: r3.bindings(engine, SCOPE, CONFIGURATION)
                     for engine in r3.BUDGET_SURFACE},
        "fixture_check": {
            "one_semantic_core": sorted({o.core for o in fixture.observations}),
            "one_query": sorted({c.query for c in fixture.cases}),
            "one_scope": sorted({c.scope for c in fixture.cases}),
            "one_configuration": sorted({c.configuration for c in fixture.cases}),
            "levels": [c.load for c in fixture.cases],
            "visible_per_level": {c.id: len(itf.visible_ids(fixture, c))
                                  for c in fixture.cases},
        },
    }
    # Strategies must be the ones each engine was measured on.
    for engine, surface in r3.BUDGET_SURFACE.items():
        r3.assert_no_mode_substitution(engine, surface["read_path"])
    payload["mode_substitution_checked"] = True

    canonical = json.dumps(payload["preflight"], sort_keys=True, separators=(",", ":"))
    payload["preflight_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()

    destination = root / "results" / "round3_adapters_gen96"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "feasibility.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))

    print("budget surfaces:")
    for engine, surface in r3.BUDGET_SURFACE.items():
        print(f"  {engine:12s} {surface['parameter']:12s} {surface['kind']:20s} "
              f"expressible={surface['window_expressible']}")
    print("\nsaturation meaning:")
    for engine, entry in payload["preflight"]["saturation"].items():
        print(f"  {engine:12s} {entry['saturated_is']}")
    print("\ncomparable windows expressible:",
          payload["preflight"]["comparable_windows_expressible"])
    print("run design:", payload["preflight"]["run_design"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
