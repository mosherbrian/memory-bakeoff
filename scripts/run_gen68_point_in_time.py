#!/usr/bin/env python3
"""Gen68: read the frozen Round-2 longitudinal runs as point-in-time truth.

No engine is run, nothing is re-scored, no completed system is repeated. This
reads committed artifacts, groups them by the kind of truth each case asks for,
and audits whether the ruler can actually answer the questions it declares.
"""
from __future__ import annotations

import ast, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import point_in_time as P                       # noqa: E402
from memory_bakeoff.longitudinal import (                           # noqa: E402
    FailureClass, build_longitudinal_fixture)

OUT = ROOT / "results" / "round2_point_in_time_gen68"
RUNS = sorted((ROOT / "results").glob("*_longitudinal"))

# Why a declared class cannot fire in this harness, stated once and checked below.
UNREACHABLE = {
    "future_leakage":
        "engines are only ever ingested the visible prefix for a checkpoint, so a "
        "future observation is not in the store to be returned; the harness never "
        "creates the opportunity to leak",
    "unknown_hallucination":
        "scored by score_answer_claim, which no runner calls - the single "
        "negative_unknown case is graded on retrieval alone and the answer claim "
        "is never read",
}


def scorer_calls_answer_claim() -> bool:
    """Verify the dead-code claim rather than asserting it."""
    for path in list((ROOT / "scripts").glob("*.py")) + \
            list((ROOT / "src/memory_bakeoff/providers").glob("*.py")):
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "score_answer_claim":
                return True
            if isinstance(node, ast.Attribute) and node.attr == "score_answer_claim":
                return True
    return False


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fixture = build_longitudinal_fixture()
    kinds = {c.id: str(c.target_kind) for c in fixture.cases}

    engines, observed = {}, set()
    for run in RUNS:
        name = run.name
        reps = sorted(run.glob("repetition-*.json"))
        cases, lifecycle, lifecycle_fails = [], 0, {}
        for path in reps:
            payload = json.loads(path.read_text())
            cases.extend(payload.get("cases", []))
            lifecycle += sum(1 for _ in payload.get("lifecycle", []) or [])
            for failure, count in (payload.get("lifecycle_failure_totals") or {}).items():
                lifecycle_fails[failure] = lifecycle_fails.get(failure, 0) + count
        summary = json.loads((run / "summary.json").read_text())
        for case in cases:
            observed.update(case.get("failure_classes") or [])
        # Lifecycle failures are a second scoring channel; a class observed only
        # there is still observed, and reading cases alone hides it.
        observed.update(k for k, v in lifecycle_fails.items() if v)
        engines[name] = {
            "repetitions": len(reps),
            "cases_scored": len(cases),
            "has_per_case": bool(cases),
            "has_lifecycle": bool(lifecycle) or bool(
                summary.get("lifecycle_failure_totals_all_repetitions")),
            "by_target_kind": P.by_target_kind(cases, kinds) if cases else {},
            "lifecycle_failures": {k: v for k, v in sorted(lifecycle_fails.items()) if v},
        }

    if scorer_calls_answer_claim():
        UNREACHABLE.pop("unknown_hallucination", None)

    payload = {
        "contract": P.contract(),
        "fixture_version": "longitudinal-v1",
        "cases_in_fixture": len(fixture.cases),
        "target_kind_counts": {k: sum(1 for c in fixture.cases
                                      if str(c.target_kind) == k)
                               for k in sorted({str(c.target_kind)
                                                for c in fixture.cases})},
        "engines": engines,
        "ruler_reachability": P.reachability(
            [str(f) for f in FailureClass], observed, UNREACHABLE),
        "provenance": P.provenance_gaps(engines),
    }
    (OUT / "point_in_time.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")

    print("engine                                     reps cases  lifecycle")
    for name, entry in engines.items():
        print(f"{name:42s} {entry['repetitions']:>4} {entry['cases_scored']:>5}  "
              f"{'yes' if entry['has_lifecycle'] else 'NO'}")
    print()
    reach = payload["ruler_reachability"]
    print(f"declared classes: {reach['declared']}   observed: {len(reach['observed'])}")
    print(f"never observed but reachable: {reach['never_observed_but_reachable']}")
    print("UNMEASURABLE BY CONSTRUCTION:")
    for name, why in reach["unmeasurable_by_construction"].items():
        print(f"  {name}: {why[:96]}")
    print()
    print("provenance gaps:", json.dumps(
        {k: v for k, v in payload["provenance"].items() if k != "note"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
