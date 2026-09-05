"""`temporal-capability-routing-v1`: what an engine can do, versus what it was asked.

Gen70's totals said perseus leaked 21 of 39 and hindsight 39 of 39. Read as a
ranking that is close to meaningless, because it conflates two independent
things:

- **capability** - when the correct native operation is invoked, does the engine
  actually honour the clock it claims to filter on?
- **routing** - does the frozen adapter send a given question to that operation
  at all?

Perseus leaked only through plain `recall_hybrid`; every call to
`recall_hybrid_valid_at` and `recall_hybrid_as_of` was clean. Hindsight leaked
through `recall_query_timestamp`, which is its temporal surface. Those are
opposite findings that the pooled column renders identical, and the difference
is the whole engineering question: one engine needs better routing, the other
needs a working filter.

So each operation gets a classification of its own:

- `current_only` - no temporal parameter; answers from current state by design
- `effective_time_capable` - filters on when a fact was true, and it holds
- `knowledge_time_capable` - filters on when a fact became known, and it holds
- `temporal_surface_but_failed` - accepts a temporal parameter and leaks anyway

The last is the one worth naming. An engine with no temporal surface is honest
about its limits; an engine that accepts a filter and ignores it is not, and a
caller cannot tell the difference without a probe like Gen70's.

Nothing here runs an engine. It reads committed Gen68 and Gen70 per-case records.
"""
from __future__ import annotations

import collections
from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "temporal-capability-routing-v1"

CURRENT_ONLY = "current_only"
EFFECTIVE_TIME = "effective_time_capable"
KNOWLEDGE_TIME = "knowledge_time_capable"
FAILED_SURFACE = "temporal_surface_but_failed"
UNDETERMINED = "undetermined"

# Which clock an operation's name claims to filter on. An operation absent here
# advertises nothing and is judged current-only.
CLAIMED_CLOCK = {
    "recall_hybrid_valid_at": EFFECTIVE_TIME,
    "recall_hybrid_as_of": KNOWLEDGE_TIME,
    "recall_query_timestamp": KNOWLEDGE_TIME,
}


def classify_operation(operation: str, *, cases: int, leaked: int) -> dict[str, Any]:
    """Judge one operation on the leakage probe alone.

    An operation is only credited with a clock when it was exercised and never
    leaked. Zero observations is `undetermined`, not a pass - the Gen68 lesson
    about unmeasured zeros applies here too.
    """
    claimed = CLAIMED_CLOCK.get(operation)
    if not cases:
        return {"operation": operation, "classification": UNDETERMINED,
                "claims": claimed, "cases": 0, "leaked": 0,
                "why": "never exercised by the probe"}
    if claimed is None:
        return {"operation": operation, "classification": CURRENT_ONLY,
                "claims": None, "cases": cases, "leaked": leaked,
                "why": "no temporal parameter; leakage here is expected and is a "
                       "routing question, not a capability failure"}
    if leaked:
        return {"operation": operation, "classification": FAILED_SURFACE,
                "claims": claimed, "cases": cases, "leaked": leaked,
                "why": "accepts a temporal parameter and returned observations from "
                       "after the queried moment anyway"}
    return {"operation": operation, "classification": claimed,
            "claims": claimed, "cases": cases, "leaked": 0,
            "why": "exercised and never leaked"}


def capability(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Per-operation classification from Gen70 probe records."""
    cases: collections.Counter = collections.Counter()
    leaked: collections.Counter = collections.Counter()
    for record in records:
        operation = record.get("native_temporal_operation") or "none"
        cases[operation] += 1
        if record.get("future_leakage"):
            leaked[operation] += 1
    return {operation: classify_operation(operation, cases=cases[operation],
                                          leaked=leaked[operation])
            for operation in sorted(cases)}


def routing(records: Iterable[Mapping[str, Any]],
            kinds: Mapping[str, str]) -> dict[str, Any]:
    """Which operation the frozen adapter chose, per kind of truth asked for."""
    table: dict[str, collections.Counter] = {}
    for record in records:
        kind = kinds.get(record["case_id"], "unknown")
        operation = record.get("native_temporal_operation") or "none"
        table.setdefault(kind, collections.Counter())[operation] += 1
    return {kind: dict(sorted(counter.items())) for kind, counter in sorted(table.items())}


def misrouted(routes: Mapping[str, Mapping[str, int]],
              operations: Mapping[str, Mapping[str, Any]],
              temporal_kinds: Iterable[str]) -> list[dict[str, Any]]:
    """Temporal questions sent to an operation that has no temporal filter.

    This is the failure that looks like an engine defect and is not one: the
    engine may hold a perfectly good clock that the adapter never asked for.
    """
    findings = []
    working = {name for name, entry in operations.items()
               if entry["classification"] in (EFFECTIVE_TIME, KNOWLEDGE_TIME)}
    for kind in temporal_kinds:
        for operation, count in (routes.get(kind) or {}).items():
            entry = operations.get(operation, {})
            if entry.get("classification") == CURRENT_ONLY:
                findings.append({
                    "kind": kind, "operation": operation, "cases": count,
                    "engine_has_a_working_temporal_operation": sorted(working),
                    "verdict": "routing gap" if working else "no temporal surface",
                })
    return findings


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "separates": ["capability: does the operation honour its clock when invoked",
                      "routing: does the adapter send the question to that operation"],
        "classifications": [CURRENT_ONLY, EFFECTIVE_TIME, KNOWLEDGE_TIME,
                            FAILED_SURFACE, UNDETERMINED],
        "why": "pooled future-leakage totals conflate an engine that lacks a clock, "
               "an engine whose clock is never consulted, and an engine whose clock "
               "is consulted and does not work",
        "not_a_ranking": "pooled totals must not be used to order engines; the "
                         "per-operation classification is the result",
        "zero_observations_is_undetermined": "an operation the probe never exercised "
                                             "is not credited with working",
        "reads_only": "committed Gen68 and Gen70 per-case records; no engine is run",
        "unknown_hallucination": "NOT_APPLICABLE at the retrieval-engine layer - these "
                                 "adapters return evidence and never assert; reserved "
                                 "for a reader or full-product evaluation",
    }
