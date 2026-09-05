#!/usr/bin/env python3
"""Gen72: why each engine's temporal answers were wrong. No engine is run."""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L                       # noqa: E402
from memory_bakeoff import correction_semantics as S               # noqa: E402

OUT = ROOT / "results" / "correction_semantics_gen72"
RUNS = {
    "perseus": ROOT / "results/perseus_vault_gen29_longitudinal",
    "mem0": ROOT / "results/mem0_gen32_longitudinal",
    "hindsight": ROOT / "results/hindsight_gen31_longitudinal",
    "agentmemory": ROOT / "results/agentmemory_gen33_longitudinal",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fixture = L.build_longitudinal_fixture()
    cases = {c.id: {"target_kind": str(c.target_kind),
                    "expected_ids": c.expected_ids,
                    "prohibited_ids": c.prohibited_ids} for c in fixture.cases}

    engines = {}
    for engine, directory in RUNS.items():
        records = []
        for path in sorted(directory.glob("repetition-*.json")):
            payload = json.loads(path.read_text())
            for case in payload["cases"]:
                records.append({
                    "case_id": case["case_id"],
                    "returned_ids": {item["canonical_id"]
                                     for item in case.get("returned", [])
                                     if item.get("canonical_id")},
                })
        decomposed = S.decompose(records, cases)
        decomposed["storage_reading"] = S.storage_reading(decomposed["by_cluster"])
        engines[engine] = decomposed

    payload = {"contract": S.contract(), "engines": engines}
    (OUT / "semantics.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")

    for engine, entry in engines.items():
        print(f"== {engine}")
        for cluster, counts in entry["by_cluster"].items():
            print(f"   {cluster:14s} {counts}")
        print(f"   reading: {entry['storage_reading']['reading']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
