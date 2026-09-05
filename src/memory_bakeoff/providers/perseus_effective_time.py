"""`perseus-adapter-v2`: give `valid_at` the effective time it was always meant to get.

Gen73 found that the frozen Gen29 adapter derives BOTH temporal arguments from
`TimeBase.store_instant(event_time)`, which bisects ingestion times and returns a
store write instant. `valid_at` - the operation whose whole purpose is to ask
what was true on a date - was therefore being handed a transaction-time
coordinate, and for any backfilled fact it resolved to an instant before that
fact was written.

This revision changes exactly one thing:

- **`valid_at`** now carries the case's own `effective_time`, converted straight
  to unix milliseconds. No ingestion times are consulted.
- **`as_of_unix_ms`** is unchanged. It is a transaction-time question - "what did
  the store hold when we knew this much" - and mapping it through ingestion
  order is correct.

The frozen Gen29 adapter is not touched, imported, or reinterpreted. Its hash
appears in every committed Round-2 result. This is a separate module with its own
version, and the old results stay on record as evidence of the defect rather than
being quietly restated.

**A finding that arrived while building this, measured not assumed.** Writing two
entities to Perseus 2.23.2, one declaring `effective_time` in 2020, shows
`valid_from_unix_ms` set to the write instant in both cases, and
`perseus-vault write --help` exposes no flag for validity. So the store's
validity dimension is populated from write time and cannot be set by the caller.
Repairing the query side is still correct and still necessary - but on this build
it cannot succeed, because there is no effective time stored to match against.
That is a property of the product, and Gen74 measures it rather than asserting it.
"""
from __future__ import annotations

from typing import Any

from memory_bakeoff.longitudinal import LongitudinalCase, TargetKind

ADAPTER_VERSION = "perseus-adapter-v2"
SUPERSEDES = "perseus-adapter-gen29-frozen"

CURRENT_STATE_KINDS = frozenset({
    TargetKind.CURRENT, TargetKind.SCOPE, TargetKind.RECOMMENDED_PROCEDURE,
    TargetKind.NEGATIVE_UNKNOWN})
TRANSACTION_TIME_KINDS = frozenset({
    TargetKind.HISTORICAL_BELIEF, TargetKind.LATE_HISTORY})
VALID_TIME_KINDS = frozenset({TargetKind.AS_OF, TargetKind.CORRECTED_HISTORY})


def native_operation(case: LongitudinalCase) -> str:
    if case.target_kind in CURRENT_STATE_KINDS:
        return "recall_hybrid"
    if case.target_kind in TRANSACTION_TIME_KINDS:
        return "recall_hybrid_as_of"
    if case.target_kind in VALID_TIME_KINDS:
        return "recall_hybrid_valid_at"
    raise ValueError(f"no native operation for target kind {case.target_kind}")


def effective_instant(case: LongitudinalCase) -> int:
    """The repaired mapping: the case's own event time, in unix milliseconds.

    No ingestion time is consulted, which is the entire point - an effective-time
    question must not be answered against a knowledge-time coordinate.
    """
    if case.event_time is None:
        raise ValueError(f"{case.id}: valid_at needs a public event time")
    return int(case.event_time.timestamp() * 1000)


def recall_arguments(case: LongitudinalCase, time_base: Any, limit: int) -> dict[str, Any]:
    """Native arguments for one case. Public coordinates only.

    `time_base` is still accepted, and still used for `as_of`, so this drops into
    the existing runner unchanged.
    """
    arguments: dict[str, Any] = {"query": case.query, "limit": limit, "mode": "hybrid"}
    operation = native_operation(case)
    if operation == "recall_hybrid":
        return arguments
    if operation == "recall_hybrid_as_of":
        # Transaction time: unchanged from the frozen adapter, deliberately.
        arguments["as_of_unix_ms"] = time_base.store_instant(
            case.event_time.isoformat())
        return arguments
    arguments["valid_at"] = effective_instant(case)
    return arguments


def clocks_diverge(case: LongitudinalCase, time_base: Any) -> dict[str, Any]:
    """What the two mappings would produce for the same case. Used by the tests."""
    return {
        "case_id": case.id,
        "valid_at_v2": effective_instant(case),
        "store_instant_v1": time_base.store_instant(case.event_time.isoformat()),
    }


def contract() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "supersedes": SUPERSEDES,
        "single_change": "valid_at now carries the case's effective time in unix ms; "
                         "as_of still maps through ingestion order",
        "frozen_adapter_untouched": "the Gen29 module is not imported, edited or "
                                    "reinterpreted; its hash stays valid for every "
                                    "committed Round-2 result",
        "old_results_status": "retained as invalid-for-effective-time evidence, not "
                              "restated",
        "measured_store_limitation": "perseus-vault 2.23.2 sets valid_from_unix_ms to "
                                     "the write instant regardless of any "
                                     "effective_time in the body, and `write` exposes "
                                     "no validity flag; so a repaired query has "
                                     "nothing stored to match against",
    }
