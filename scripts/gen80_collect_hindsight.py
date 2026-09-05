#!/usr/bin/env python3
"""Fold hindsight's configuration repetitions into the Gen80 engine summary."""
from __future__ import annotations

import json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff import longitudinal as L                    # noqa: E402
from memory_bakeoff.providers import scope_bound as SB          # noqa: E402
from memory_bakeoff.providers import configuration_bound as CB  # noqa: E402
from run_gen80_configuration_isolation import CASE, score       # noqa: E402

OUT = ROOT / "results" / "configuration_isolation_gen80"


def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/gen80hs")
    fixture = L.build_longitudinal_fixture()
    OUT.mkdir(parents=True, exist_ok=True)
    repetitions = []
    for path in sorted(source.glob("rep*.json")):
        payload = json.loads(path.read_text())
        payload["records"] = score(fixture, payload["records"])
        repetitions.append(payload)
    summary = {
        "engine": "hindsight", "generation": 80, "case": CASE,
        "ablation": "Gen79 configuration binding layered on the Gen78 scope binding",
        "ingestion": "prefix of the queried checkpoint only",
        "scope_binding": {k: v for k, v in SB.BINDINGS["hindsight"].items()
                          if k not in ("write", "query")},
        "configuration_binding": {k: v for k, v in CB.BINDINGS["hindsight"].items()
                                  if k not in ("write", "query")},
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repetitions": repetitions,
        "configuration_collapse_total": sum(
            1 for rep in repetitions for r in rep["records"]
            if r["configuration_collapse"]),
        "clean_retrieval_total": sum(1 for rep in repetitions for r in rep["records"]
                                     if r["clean_retrieval"]),
        "case_runs": sum(len(rep["records"]) for rep in repetitions),
    }
    (OUT / "hindsight.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")
    for rep in repetitions:
        for r in rep["records"]:
            print(f"hindsight rep{rep['repetition']}: collapse="
                  f"{r['configuration_collapse']} clean={r['clean_retrieval']} "
                  f"got={r['returned_ids']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
