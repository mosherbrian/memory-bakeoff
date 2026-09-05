#!/usr/bin/env python3
"""Fold hindsight's per-scope repetitions into the Gen78 engine summary."""
from __future__ import annotations

import json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff import longitudinal as L                 # noqa: E402
from memory_bakeoff.providers import scope_bound as SB       # noqa: E402
from run_gen78_scope_isolation import CROSS_SCOPE_CASES, score   # noqa: E402

OUT = ROOT / "results" / "scope_isolation_gen78"


def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/gen78hs")
    fixture = L.build_longitudinal_fixture()
    OUT.mkdir(parents=True, exist_ok=True)
    repetitions = []
    for path in sorted(source.glob("rep*.json")):
        payload = json.loads(path.read_text())
        payload["records"] = score(fixture, payload["records"])
        repetitions.append(payload)
    summary = {
        "engine": "hindsight", "generation": 78,
        "ablation": "frozen Gen77 scope binding replaces the Round-2 constant "
                    "namespace; one variable moved",
        "cases": list(CROSS_SCOPE_CASES),
        "excluded": {"LQ03": "same scope, different configuration"},
        "ingestion": "prefix of the queried checkpoint only",
        "binding": {k: v for k, v in SB.BINDINGS["hindsight"].items()
                    if k not in ("write", "query")},
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repetitions": repetitions,
        "scope_collapse_total": sum(1 for rep in repetitions
                                    for r in rep["records"] if r["scope_collapse"]),
        "case_runs": sum(len(rep["records"]) for rep in repetitions),
    }
    (OUT / "hindsight.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: summary[k] for k in
                      ("engine", "scope_collapse_total", "case_runs")}, indent=1))
    for rep in repetitions:
        for r in rep["records"]:
            print(" ", rep["repetition"], r["case_id"], r["scope"],
                  "got", r["returned_ids"], r["failure_classes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
