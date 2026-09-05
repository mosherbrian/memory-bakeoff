#!/usr/bin/env python3
"""Gen76: audit the scope ruler. No engine runs and nothing is re-scored."""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L        # noqa: E402
from memory_bakeoff import scope_audit as S         # noqa: E402

OUT = ROOT / "results" / "scope_audit_gen76"


def prove_scope_collapse(fixture) -> dict:
    """Drive the frozen scorer with a synthetic cross-scope answer, plus a control."""
    byid = {o.id: o for o in fixture.observations}
    target = None
    for case in fixture.cases:
        for prohibited in case.prohibited_ids:
            other = byid.get(prohibited)
            if other is not None and case.scope and other.scope != case.scope:
                target = (case, prohibited)
                break
        if target:
            break
    if target is None:
        return {"fires": False, "why": "no cross-scope prohibited id in the fixture"}
    case, prohibited = target
    dirty = L.score_longitudinal_case(fixture, case,
                                      tuple(case.expected_ids) + (prohibited,))
    clean = L.score_longitudinal_case(fixture, case, tuple(case.expected_ids))
    name = str(L.FailureClass.SCOPE_COLLAPSE)
    return {
        "case": case.id, "cross_scope_observation": prohibited,
        "fires": name in dirty.failure_classes,
        "classes_when_violated": list(dirty.failure_classes),
        "control_clean": name not in clean.failure_classes,
        "control_classes": list(clean.failure_classes),
    }


def prove_configuration_collapse(fixture) -> dict:
    byid = {o.id: o for o in fixture.observations}
    for case in fixture.cases:
        for prohibited in case.prohibited_ids:
            other = byid.get(prohibited)
            if (other is not None and case.scope and other.scope == case.scope
                    and case.configuration
                    and other.configuration != case.configuration):
                dirty = L.score_longitudinal_case(
                    fixture, case, tuple(case.expected_ids) + (prohibited,))
                clean = L.score_longitudinal_case(fixture, case,
                                                  tuple(case.expected_ids))
                name = str(L.FailureClass.CONFIGURATION_COLLAPSE)
                return {
                    "case": case.id, "same_scope_other_configuration": prohibited,
                    "fires": name in dirty.failure_classes,
                    "classes_when_violated": list(dirty.failure_classes),
                    "control_clean": name not in clean.failure_classes,
                }
    return {"fires": False, "why": "no same-scope other-configuration prohibited id"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fixture = L.build_longitudinal_fixture()
    observations = {o.id: {"scope": o.scope, "configuration": o.configuration}
                    for o in fixture.observations}
    cases = [{"id": c.id, "scope": c.scope, "configuration": c.configuration,
              "prohibited_ids": c.prohibited_ids} for c in fixture.cases]

    adapters = {name: {**entry, **S.capability_verdict(entry)}
                for name, entry in S.ADAPTER_SCOPE.items()}
    payload = {
        "contract": S.contract(),
        "reachability_in_fixture": S.reachable_classes(cases, observations),
        "scope_collapse_proof": prove_scope_collapse(fixture),
        "configuration_collapse_proof": prove_configuration_collapse(fixture),
        "adapters": adapters,
        "engines_run": 0,
    }
    (OUT / "scope_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")

    sc = payload["scope_collapse_proof"]
    cc = payload["configuration_collapse_proof"]
    print(f"scope_collapse fires={sc['fires']} control_clean={sc.get('control_clean')}")
    print(f"configuration_collapse fires={cc['fires']} control_clean={cc.get('control_clean')}")
    print()
    for name, entry in adapters.items():
        print(f"{name:12} {entry['scope_exercised']:20} "
              f"capability={entry['engine_scope_capability']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
