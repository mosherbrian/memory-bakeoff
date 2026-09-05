"""`temporal-semantics-closure-v1`: three axes, and the claims that do not survive.

Seven generations produced one durable lesson: "temporal accuracy" is not one
property. An engine can keep a perfect record of *what it believed and when* and
have no way to record *when a fact was actually true*, and those two are not
points on a scale - they are different mechanisms with different failures.

So each engine is classified on three axes that vary independently:

**transaction-time history** - can it answer what it believed at a past moment?
Measured by whether a question about a superseded belief is answered with the
superseded version or with its replacement.

**effective-time history** - can it record and retrieve when a fact was actually
true, independently of when it arrived? Measured by whether a backfilled
observation is reachable at its own event time.

**temporal-query surface** - what does the API offer, and does the offer hold?
This is separate from the two above because an engine can expose a filter that
does not work, which is worse than exposing none: a caller cannot tell the
difference without probing.

`NOT_DEMONSTRABLE` is a first-class value here. Gen73 and Gen74 established that
Perseus's effective-time behaviour was never tested and cannot be tested through
this interface, because the store has no caller-settable validity coordinate.
Recording that as a failure would be as wrong as recording it as a pass.
"""
from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "temporal-semantics-closure-v1"

# Axis values. Deliberately not ordered, because they are not a scale.
KEPT = "kept"
NOT_KEPT = "not_kept"
NOT_DEMONSTRABLE = "not_demonstrable"
NO_SURFACE = "no_temporal_surface"
SURFACE_HOLDS = "surface_present_and_holds"
SURFACE_FAILS = "surface_present_and_fails"

# Every Perseus effective-time claim that rested on `valid_at`, and its status.
RETRACTIONS = (
    {
        "generation": 71,
        "claim": "recall_hybrid_valid_at is effective_time_capable",
        "status": "RETRACTED",
        "because": "the adapter fed valid_at a transaction-time instant derived "
                   "from ingestion order, so effective-time capability was never "
                   "exercised (Gen73)",
    },
    {
        "generation": 72,
        "claim": "Perseus makes backfilled event-time facts unreachable",
        "status": "RETRACTED",
        "because": "Perseus was asked what its store held before the backfilled "
                   "fact was written, not for the fact at its event time (Gen73)",
    },
    {
        "generation": 70,
        "claim": "Perseus's temporal operations never leaked (0 of 15)",
        "status": "QUALIFIED",
        "because": "an empty or pre-write snapshot cannot leak, so the figure is "
                   "not evidence of a working effective-time filter (Gen73)",
    },
    {
        "generation": 68,
        "claim": "Perseus fails late-arriving history",
        "status": "REATTRIBUTED",
        "because": "the failure is the harness asking an effective-time question "
                   "through a knowledge-time coordinate, compounded by the store "
                   "having no validity coordinate to set (Gen73, Gen74)",
    },
)

# What survives, with the evidence that carries it.
SURVIVING = (
    {
        "claim": "Perseus preserves what was believed at a past moment",
        "evidence": "Gen68 historical_belief 6/6 clean; those are as_of cases, a "
                    "genuine transaction-time question, correctly mapped",
    },
    {
        "claim": "Hindsight's query_timestamp is accepted and ignored",
        "evidence": "Gen70: 15 of 15 leaked on its own parameter and its own path; "
                    "no Perseus adapter involved",
    },
    {
        "claim": "mem0 and agentmemory expose no temporal surface",
        "evidence": "Gen71: every case routed to current-state search because there "
                    "is nowhere else to send it",
    },
    {
        "claim": "no engine tested keeps both clocks",
        "evidence": "Gen72, asserted in a test; unchanged by the retractions, since "
                    "no engine gained an effective-time capability",
    },
)


def classify(engine: str, *, belief_confusions: int, has_temporal_surface: bool,
             surface_leaks: bool | None,
             effective_time_testable: bool) -> dict[str, Any]:
    """Place one engine on the three axes."""
    transaction = KEPT if belief_confusions == 0 else NOT_KEPT
    if not effective_time_testable:
        effective = NOT_DEMONSTRABLE
    else:
        effective = NOT_KEPT
    if not has_temporal_surface:
        surface = NO_SURFACE
    elif surface_leaks:
        surface = SURFACE_FAILS
    else:
        surface = SURFACE_HOLDS
    return {
        "engine": engine,
        "transaction_time_history": transaction,
        "effective_time_history": effective,
        "temporal_query_surface": surface,
        "belief_confusions": belief_confusions,
    }


def closure() -> dict[str, Any]:
    """The bounded architecture result, as measured across Gen68-74."""
    engines = [
        classify("perseus", belief_confusions=0, has_temporal_surface=True,
                 surface_leaks=False, effective_time_testable=False),
        classify("hindsight", belief_confusions=6, has_temporal_surface=True,
                 surface_leaks=True, effective_time_testable=True),
        classify("mem0", belief_confusions=6, has_temporal_surface=False,
                 surface_leaks=None, effective_time_testable=True),
        classify("agentmemory", belief_confusions=6, has_temporal_surface=False,
                 surface_leaks=None, effective_time_testable=True),
    ]
    # Perseus's surface is present and did not leak, but Gen73 qualified that:
    # it was never exercised as an effective-time filter.
    for entry in engines:
        if entry["engine"] == "perseus":
            entry["temporal_query_surface_note"] = (
                "as_of holds as a transaction-time filter; valid_at was never "
                "exercised as an effective-time filter and cannot be on this build")
    return {
        "contract_version": CONTRACT_VERSION,
        "engines": engines,
        "retractions": list(RETRACTIONS),
        "surviving": list(SURVIVING),
        "no_single_score": "these axes vary independently and must not be collapsed; "
                           "an engine that keeps belief history perfectly and cannot "
                           "record effective time at all has no meaningful average",
        "scope": "perseus-vault 2.23.2, hindsight 0.9.2, mem0 2.0.19, "
                 "agentmemory 0.9.29, in the tested Round-2 configurations, on "
                 "longitudinal-v1 and backfill-v1",
    }
