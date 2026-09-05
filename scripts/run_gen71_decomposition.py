#!/usr/bin/env python3
"""Gen71: separate temporal capability from adapter routing. No engine is run."""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L                    # noqa: E402
from memory_bakeoff import temporal_capability as C             # noqa: E402
from memory_bakeoff.point_in_time import CLOCK                  # noqa: E402

OUT = ROOT / "results" / "temporal_capability_gen71"
GEN70 = ROOT / "results" / "temporal_blind_spot_gen70"
ENGINES = ("perseus", "mem0", "hindsight", "agentmemory")
TEMPORAL_KINDS = tuple(k for k, clock in CLOCK.items() if clock != "now")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fixture = L.build_longitudinal_fixture()
    kinds = {c.id: str(c.target_kind) for c in fixture.cases}

    engines = {}
    for engine in ENGINES:
        payload = json.loads((GEN70 / f"{engine}.json").read_text())
        records = [r for rep in payload["repetitions"] for r in rep["records"]]
        operations = C.capability(records)
        routes = C.routing(records, kinds)
        by_clock = {"temporal": [0, 0], "current": [0, 0]}
        for record in records:
            clock = CLOCK.get(kinds.get(record["case_id"], ""), "now")
            bucket = by_clock["current" if clock == "now" else "temporal"]
            bucket[1] += 1
            if record["future_leakage"]:
                bucket[0] += 1

        engines[engine] = {
            "operations": operations,
            "leakage_on_temporal_questions": {
                "leaked": by_clock["temporal"][0], "cases": by_clock["temporal"][1]},
            "leakage_on_current_questions": {
                "leaked": by_clock["current"][0], "cases": by_clock["current"][1],
                "note": "asking what is true NOW of a store that has been fed the "
                        "whole timeline should return the later facts; this column "
                        "is largely expected and must not be read as a defect"},
            "routing_by_kind": routes,
            "routing_gaps": C.misrouted(routes, operations, TEMPORAL_KINDS),
            "pooled_leakage": payload["future_leakage_cases"],
            "probe_cases": payload["probe_cases_total"],
            "has_working_temporal_operation": sorted(
                name for name, entry in operations.items()
                if entry["classification"] in (C.EFFECTIVE_TIME, C.KNOWLEDGE_TIME)),
            "has_failed_temporal_surface": sorted(
                name for name, entry in operations.items()
                if entry["classification"] == C.FAILED_SURFACE),
        }

    payload = {
        "contract": C.contract(),
        "temporal_kinds": list(TEMPORAL_KINDS),
        "engines": engines,
        "unknown_hallucination": {
            "status": "CLOSED_NOT_APPLICABLE",
            "layer": "retrieval engine",
            "why": "every frozen adapter returns evidence and never asserts an "
                   "answer, so there is no claim to grade",
            "reserved_for": "a reader or full-product evaluation, where something "
                            "actually produces an answer",
        },
    }
    (OUT / "capability.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")

    for engine, entry in engines.items():
        temporal = entry["leakage_on_temporal_questions"]
        print(f"== {engine}  TEMPORAL-question leakage "
              f"{temporal['leaked']}/{temporal['cases']}  "
              f"(pooled {entry['pooled_leakage']}/{entry['probe_cases']} - NOT a ranking)")
        for name, op in entry["operations"].items():
            print(f"   {name:32s} {op['classification']:28s} "
                  f"{op['leaked']}/{op['cases']} leaked")
        for gap in entry["routing_gaps"]:
            print(f"   ROUTING GAP: {gap['kind']} -> {gap['operation']} "
                  f"({gap['cases']} cases); engine has {gap['engine_has_a_working_temporal_operation'] or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
