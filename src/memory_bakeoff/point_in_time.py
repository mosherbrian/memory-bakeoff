"""`point-in-time-truth-v1`: read the frozen longitudinal runs by kind of truth.

The Round-2 longitudinal ruler already separates world time from knowledge time -
`event_time`/`effective_time` say when something was true, `ingestion_time`/
`ingestion_order` say when the system could have known it. What it has never been
read as is a *point-in-time truth* report: how each engine does on current truth
versus as-of truth versus historical belief, rather than one pooled failure count.

This module does that reading. It runs no engine and re-scores nothing: every
failure class here was assigned by `longitudinal-scorer-v1` at run time and is
read back from the committed artifacts.

It also audits the ruler itself, which matters more than the scores. A failure
class that is declared but can never fire is a blind spot, and a class that only
one engine has the evidence to answer cannot be compared across engines. Both are
reported explicitly rather than left to look like zeros.
"""
from __future__ import annotations

import collections
from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "point-in-time-truth-v1"

# Which target kinds ask about which clock. The distinction is the whole point:
# a system can be perfect on "what is true now" and still be unable to say what
# it believed last Tuesday.
CLOCK = {
    "current_truth": "now",
    "scope_truth": "now",
    "recommended_procedure": "now",
    "negative_unknown": "now",
    "as_of_event_truth": "event time",
    "corrected_historical_truth": "event time",
    "historical_belief": "knowledge time",
    "late_arriving_history": "knowledge time",
}


def by_target_kind(cases: Iterable[Mapping[str, Any]],
                   kinds: Mapping[str, str]) -> dict[str, dict[str, Any]]:
    """Failure counts grouped by what kind of truth the case asked for."""
    grouped: dict[str, dict[str, Any]] = {}
    for case in cases:
        kind = kinds.get(case["case_id"], "unknown")
        entry = grouped.setdefault(kind, {
            "clock": CLOCK.get(kind, "unknown"),
            "cases": 0, "clean": 0, "failures": collections.Counter()})
        entry["cases"] += 1
        classes = case.get("failure_classes") or []
        if not classes:
            entry["clean"] += 1
        for name in classes:
            entry["failures"][name] += 1
    for entry in grouped.values():
        entry["failures"] = dict(sorted(entry["failures"].items()))
        entry["clean_rate"] = entry["clean"] / entry["cases"] if entry["cases"] else None
    return grouped


def reachability(declared: Iterable[str], observed: Iterable[str],
                 unreachable: Mapping[str, str]) -> dict[str, Any]:
    """Split declared failure classes into observed, silent, and unmeasurable.

    A class in `unreachable` cannot fire given how the harness feeds engines, so
    its zero is a property of the experiment rather than a result about anyone.
    """
    declared, observed = set(declared), set(observed)
    silent = sorted(declared - observed - set(unreachable))
    return {
        "declared": len(declared),
        "observed": sorted(declared & observed),
        "never_observed_but_reachable": silent,
        "unmeasurable_by_construction": dict(sorted(
            (k, v) for k, v in unreachable.items() if k in declared)),
        "blind_spots": len(unreachable),
    }


def provenance_gaps(engines: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Which engines lack the evidence a class needs, so it cannot be compared."""
    missing_lifecycle = sorted(name for name, payload in engines.items()
                               if not payload.get("has_lifecycle"))
    missing_cases = sorted(name for name, payload in engines.items()
                           if not payload.get("has_per_case"))
    return {
        "engines": sorted(engines),
        "no_per_case_records": missing_cases,
        "no_lifecycle_evidence": missing_lifecycle,
        "lifecycle_classes_not_cross_comparable": bool(missing_lifecycle),
        "note": "a class scored from evidence only some engines emit cannot be "
                "compared across engines; its absence elsewhere is silence, not a "
                "clean result",
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "reads_only": "committed longitudinal artifacts; no engine is run and no "
                      "case is re-scored",
        "groups_by": "target kind, and the clock each kind interrogates",
        "clocks": sorted(set(CLOCK.values())),
        "why": "a pooled failure count hides the distinction the ruler was built "
               "for - current truth, as-of truth and historical belief are "
               "different questions and can fail independently",
        "audits": ["failure classes that can never fire",
                   "failure classes that fired for nobody",
                   "engines lacking the evidence a class needs"],
    }
