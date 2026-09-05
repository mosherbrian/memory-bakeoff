"""Gen95: freeze the Round-3 interference ruler and prove every class reachable.

No engine runs. Nothing here touches a product; the point is that the ruler is
demonstrated to work before any product sees the fixture.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from dataclasses import asdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import interference as itf


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    fixture = itf.build_fixture()
    controls = itf.controls(fixture)

    payload = {
        "contract": itf.contract(),
        "observations": [asdict(o) for o in fixture.observations],
        "cases": [asdict(c) for c in fixture.cases],
        "visible_per_case": {c.id: list(itf.visible_ids(fixture, c))
                             for c in fixture.cases},
        "controls": controls,
    }
    canonical = json.dumps(payload["contract"], sort_keys=True, separators=(",", ":"))
    payload["contract_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    fixture_blob = json.dumps(
        {"observations": payload["observations"], "cases": payload["cases"]},
        sort_keys=True, separators=(",", ":"), default=str)
    payload["fixture_sha256"] = hashlib.sha256(fixture_blob.encode()).hexdigest()

    fired = {m for entry in controls.values() for m in entry["mechanisms"]}
    payload["reachability"] = {
        "mechanisms": list(itf.MECHANISMS),
        "all_fired": sorted(fired) == sorted(itf.MECHANISMS),
        "clean_control_silent": controls["clean"]["mechanisms"] == (),
    }

    destination = root / "results" / "interference_design_gen95"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "ruler.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))

    print("fixture:", len(fixture.observations), "observations,",
          len(fixture.cases), "cases")
    print("load levels:", [c.load for c in fixture.cases])
    print("fixture sha256:", payload["fixture_sha256"][:16])
    print("all mechanisms reachable:", payload["reachability"]["all_fired"])
    for name, entry in controls.items():
        print(f"  {name:42s} -> {entry['mechanisms']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
