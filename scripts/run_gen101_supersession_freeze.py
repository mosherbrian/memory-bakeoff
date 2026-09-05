#!/usr/bin/env python3
"""Gen101: freeze the repaired fixture and the four minimal bindings.

No engine runs. The deterministic controls prove two things before anything is
run: the corrected order is visible to agentmemory's write-time rule, and no
binding manufactures success by deleting a record.
"""
from __future__ import annotations

import hashlib, json, sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV  # noqa: E402
from memory_bakeoff import interference_v2 as V2          # noqa: E402
from memory_bakeoff import interference_v3 as V3          # noqa: E402
from memory_bakeoff import supersession_binding as SB     # noqa: E402
from memory_bakeoff import supersession_surface as SS     # noqa: E402


def main() -> int:
    fixture = V3.build_fixture()

    # Control 1: the corrected order is visible to agentmemory's own rule.
    order_control = {}
    for core in V2.CORES:
        case = next(c for c in fixture.cases if c.core == core["id"] and c.load == 0)
        v3_order = list(V3.visible_ids(fixture, case))
        v2_order = list(V2.visible_ids(fixture, case))
        current = next(o for o in fixture.observations
                       if o.core == core["id"] and o.role == "current")
        superseded = next(o for o in fixture.observations
                          if o.core == core["id"] and o.role == "superseded")
        rule = SS.can_agentmemory_supersede(current.text, superseded.text)
        # v2 retired the CURRENT record; v3 must retire the SUPERSEDED one.
        v2_retires = "current" if v3_order and v2_order[0] == current.id else "superseded"
        v3_retires = "superseded" if v3_order[0] == superseded.id else "current"
        order_control[core["id"]] = {
            **V3.order_changed(fixture, case, v2_order),
            **rule,
            "v2_would_retire": v2_retires if rule["rule_can_fire"] else "nothing",
            "v3_would_retire": v3_retires if rule["rule_can_fire"] else "nothing",
            "repair_visible_to_the_rule": bool(
                rule["rule_can_fire"] and v3_retires == "superseded"),
        }

    # Control 2: no binding deletes, and none is allowed to.
    deletion_control = {}
    for engine, binding in SB.BINDINGS.items():
        SB.assert_no_deletion(engine, binding)
        deletion_control[engine] = {"call": binding["call"],
                                    "old_record_retained": binding["old_record_retained"],
                                    "kind": binding["kind"]}
    try:
        SB.assert_no_deletion("control", {"call": "Memory.delete(memory_id)",
                                          "old_record_retained": True})
        raised = False
    except ValueError:
        raised = True
    deletion_control["_guard_rejects_a_delete_binding"] = raised

    payload = {
        "fixture_contract": V3.contract(),
        "fixture_contract_sha256": V3.contract_sha256(),
        "binding_contract": SB.contract(),
        "observations": [asdict(o) for o in fixture.observations],
        "cases": [asdict(c) for c in fixture.cases],
        "ingest_order_per_case": {c.id: list(V3.visible_ids(fixture, c))[:3]
                                  for c in fixture.cases},
        "control_order_visible_to_the_rule": order_control,
        "control_nothing_deletes": deletion_control,
    }
    blob = json.dumps({"observations": payload["observations"],
                       "cases": payload["cases"],
                       "order": payload["ingest_order_per_case"]},
                      sort_keys=True, separators=(",", ":"), default=str)
    payload["fixture_sha256"] = hashlib.sha256(blob.encode()).hexdigest()

    destination = EV.next_attempt(ROOT, 101)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "freeze.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))

    print("fixture:", V3.FIXTURE_VERSION, "supersedes", V3.SUPERSEDES)
    print("fixture sha256:", payload["fixture_sha256"][:16])
    print("\ningest order repair, per core:")
    for core, entry in order_control.items():
        print(f"  {core:<18} v2={entry['v2_order']} -> v3={entry['v3_order']}")
        print(f"  {'':<18} rule_can_fire={entry['rule_can_fire']} "
              f"v2_would_retire={entry['v2_would_retire']} "
              f"v3_would_retire={entry['v3_would_retire']}")
    print("\nbindings:")
    for engine, entry in SB.BINDINGS.items():
        print(f"  {engine:<12} {entry['kind']:<18} {entry['call'][:50]}")
    print("\nguard rejects a delete binding:", raised)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
