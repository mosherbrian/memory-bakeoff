#!/usr/bin/env python3
"""Gen75: the temporal closure. No engine is run and nothing is re-scored."""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import temporal_closure as C   # noqa: E402

OUT = ROOT / "results" / "temporal_closure_gen75"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = C.closure()
    payload["engines_run"] = 0
    (OUT / "closure.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")

    width = max(len(e["engine"]) for e in payload["engines"])
    print(f"{'engine':{width}}  {'transaction-time':18} {'effective-time':18} surface")
    for entry in payload["engines"]:
        print(f"{entry['engine']:{width}}  "
              f"{entry['transaction_time_history']:18} "
              f"{entry['effective_time_history']:18} "
              f"{entry['temporal_query_surface']}")
    print()
    for item in payload["retractions"]:
        print(f"Gen{item['generation']} {item['status']}: {item['claim']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
