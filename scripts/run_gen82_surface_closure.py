#!/usr/bin/env python3
"""Gen82: close or continue the agentmemory configuration axis. No engine runs."""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.providers import agentmemory_surface as S   # noqa: E402

OUT = ROOT / "results" / "agentmemory_surface_gen82"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = S.verdict()
    (OUT / "surface.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"verdict: {payload['verdict']}")
    print(f"symmetric fields: {payload['symmetric_fields']}")
    for name, entry in payload["candidates"].items():
        mark = "usable" if entry["usable_as_second_identity"] else "no"
        print(f"  {name:22} symmetric={str(entry['symmetric']):5} {mark:6} {entry['why'][:74]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
