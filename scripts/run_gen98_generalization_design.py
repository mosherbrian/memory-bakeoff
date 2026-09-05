#!/usr/bin/env python3
"""Gen98: freeze `interference-v2` and its predeclared replication questions.

No engine runs. The questions are written and hashed with the fixture, before any
product sees it, so which pattern counts as replicated cannot be decided after
the data arrives.
"""
from __future__ import annotations

import hashlib, json, sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import interference as ITF        # noqa: E402
from memory_bakeoff import interference_v2 as V2      # noqa: E402


def main() -> int:
    fixture = V2.build_fixture()
    controls = {}
    # Every mechanism must still fire, in EVERY core - a class that fires in one
    # neighbourhood and not another would make replication uninterpretable.
    for core in V2.CORES:
        cases = V2.cases_for_core(fixture, core["id"])
        top = max(cases, key=lambda c: c.load)
        tag = top.id.split("-")[0]
        distractors = sorted(fixture.distractors_for(top.core, top.scope,
                                                     top.configuration))[:5]
        controls[core["id"]] = {
            "clean": ITF.score_case(fixture, top, [f"{tag}-CUR"], 5)["mechanisms"],
            ITF.TRUE_FORGETTING: ITF.score_case(
                fixture, top, [distractors[0]], 5)["mechanisms"],
            ITF.DISTRACTOR_DISPLACEMENT: ITF.score_case(
                fixture, top, distractors, 5)["mechanisms"],
            ITF.STALE_VERSION_INTERFERENCE: ITF.score_case(
                fixture, top, [f"{tag}-CUR", f"{tag}-SUP"], 5)["mechanisms"],
            ITF.CROSS_SCOPE_CONTAMINATION: ITF.score_case(
                fixture, top, [f"{tag}-CUR", f"{tag}-FOR"], 5)["mechanisms"],
        }

    payload = {
        "contract": V2.contract(),
        "contract_sha256": V2.contract_sha256(),
        "observations": [asdict(o) for o in fixture.observations],
        "cases": [asdict(c) for c in fixture.cases],
        "visible_per_case": {c.id: len(V2.visible_ids(fixture, c))
                             for c in fixture.cases},
        "controls_per_core": controls,
    }
    blob = json.dumps({"observations": payload["observations"],
                       "cases": payload["cases"]},
                      sort_keys=True, separators=(",", ":"), default=str)
    payload["fixture_sha256"] = hashlib.sha256(blob.encode()).hexdigest()

    fired = {m for core in controls.values() for entry in core.values() for m in entry}
    payload["reachability"] = {
        "all_mechanisms_fire_in_every_core": all(
            {m for entry in core.values() for m in entry} >= set(ITF.MECHANISMS) - {
                ITF.RETRIEVAL_WINDOW_EFFECT}
            for core in controls.values()),
        "mechanisms_seen": sorted(fired),
    }

    V2.assert_no_core_pooling(json.dumps(payload["contract"]["no_core_pooling"]))
    destination = ROOT / "results" / "interference_v2_gen98"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "fixture.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))

    print(f"cores: {len(V2.CORES)}  observations: {len(fixture.observations)}  "
          f"cases: {len(fixture.cases)}")
    print("fixture sha256:", payload["fixture_sha256"][:16])
    print("contract sha256:", payload["contract_sha256"][:16])
    print("all mechanisms fire in every core:",
          payload["reachability"]["all_mechanisms_fire_in_every_core"])
    print("\npredeclared replication questions:")
    for name, entry in V2.REPLICATION_QUESTIONS.items():
        print(f"  {name}\n     {entry['question']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
