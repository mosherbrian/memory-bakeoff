"""Frozen Perseus Vault adapter for the longitudinal-v1 ruler (Gen29).

Routing uses ONLY public request coordinates: the case's target kind, its event
time, and its scope. It never sees expected ids, prohibited ids, truth keys,
transition labels, correction/supersession lineage, or rationale.

The store's transaction timeline is real wall-clock time, while the fixture's
timeline is fictional calendar time. `TimeBase` maps one onto the other using
public fixture ingestion times and the observed write instants only.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import hashlib
from typing import Any, Mapping

from ..longitudinal import LongitudinalCase, LongitudinalObservation, TargetKind

ADAPTER_VERSION = "perseus-longitudinal-adapter-v1"
CATEGORY = "benchmark_record"

# Public intent -> native read operation. Frozen before any scored query.
CURRENT_STATE_KINDS = (TargetKind.CURRENT, TargetKind.SCOPE, TargetKind.RECOMMENDED_PROCEDURE, TargetKind.NEGATIVE_UNKNOWN)
TRANSACTION_TIME_KINDS = (TargetKind.HISTORICAL_BELIEF,)
VALID_TIME_KINDS = (TargetKind.AS_OF, TargetKind.CORRECTED_HISTORY, TargetKind.LATE_HISTORY)


def workspace_for_scope(scope: str) -> str:
    return hashlib.sha256(scope.encode()).hexdigest()


def key_for_observation(observation_id: str) -> str:
    return f"record-{observation_id}"


def body_for_observation(observation: LongitudinalObservation) -> dict[str, str]:
    """Publication-safe source data only: no transition, lineage or truth key."""
    public = observation.public_dict()
    return {
        "canonical_observation_id": public["canonical_observation_id"],
        "assertion": public["assertion"],
        "event_time": public["event_time"],
        "effective_time": public["effective_time"],
        "ingestion_time": public["ingestion_time"],
        "scope": public["scope"],
        "configuration": public["configuration"],
        "provenance": public["provenance"],
        "source_kind": "benchmark_observation",
    }


@dataclass(frozen=True)
class TimeBase:
    """Maps fixture calendar instants onto observed store transaction instants."""

    fixture_iso: tuple[str, ...]
    write_instants: tuple[int, ...]

    def store_instant(self, fixture_instant_iso: str) -> int:
        """Latest store instant at which the fixture prefix known at this time exists."""
        index = bisect_right(self.fixture_iso, fixture_instant_iso)
        if index == 0:
            return self.write_instants[0] - 1
        if index >= len(self.write_instants):
            return self.write_instants[-1] + 1
        return (self.write_instants[index - 1] + self.write_instants[index]) // 2

    def payload(self) -> dict[str, Any]:
        return {"fixture_ingestion_times": list(self.fixture_iso), "store_write_instants": list(self.write_instants)}


def native_operation(case: LongitudinalCase) -> str:
    if case.target_kind in CURRENT_STATE_KINDS:
        return "recall_hybrid"
    if case.target_kind in TRANSACTION_TIME_KINDS:
        return "recall_hybrid_as_of"
    if case.target_kind in VALID_TIME_KINDS:
        return "recall_hybrid_valid_at"
    raise ValueError(f"no frozen native operation for target kind {case.target_kind}")


def recall_arguments(case: LongitudinalCase, time_base: TimeBase, limit: int) -> dict[str, Any]:
    """Native arguments for one case. Public coordinates only."""
    arguments: dict[str, Any] = {
        "query": case.query,
        "workspace_hash": workspace_for_scope(case.scope) if case.scope else None,
        "limit": limit,
        "mode": "hybrid",
    }
    if arguments["workspace_hash"] is None:
        del arguments["workspace_hash"]
    operation = native_operation(case)
    if operation != "recall_hybrid":
        if case.event_time is None:
            raise ValueError(f"{case.id}: {operation} needs a public event time")
        instant = time_base.store_instant(case.event_time.isoformat())
        arguments["as_of_unix_ms" if operation == "recall_hybrid_as_of" else "valid_at"] = instant
    return arguments


def adapter_contract_payload() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "category": CATEGORY,
        "key_rule": "record- + canonical observation id",
        "workspace_rule": "sha256 hex of public scope",
        "body_fields": ["assertion", "canonical_observation_id", "configuration", "effective_time",
                        "event_time", "ingestion_time", "provenance", "scope", "source_kind"],
        "write_path": "documented operator CLI write (no supersede/update/delete/maintenance)",
        "read_paths": {
            "recall_hybrid": "perseus_vault_recall(mode=hybrid)",
            "recall_hybrid_as_of": "perseus_vault_recall(mode=hybrid, as_of_unix_ms=...)",
            "recall_hybrid_valid_at": "perseus_vault_recall(mode=hybrid, valid_at=...)",
        },
        "routing": {
            "current_state": [str(k) for k in CURRENT_STATE_KINDS],
            "transaction_time": [str(k) for k in TRANSACTION_TIME_KINDS],
            "valid_time": [str(k) for k in VALID_TIME_KINDS],
        },
        "routing_inputs": ["target_kind", "event_time", "scope"],
        "forbidden_inputs": ["expected_ids", "prohibited_ids", "truth_key", "transition", "corrects_id",
                             "supersedes_id", "retracts_id", "invalidates_id", "historical_only", "rationale"],
        "time_base_rule": "fixture ingestion instants mapped to observed store write instants; queried instant is the midpoint between the bracketing writes",
        "post_filtering": "none; native order and native limit are preserved",
    }


def adapter_contract_sha256() -> str:
    import json

    return hashlib.sha256(json.dumps(adapter_contract_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def assert_public_only(body: Mapping[str, Any]) -> None:
    """Fail closed if a write envelope ever carries hidden benchmark truth."""
    forbidden = {"truth_key", "transition", "corrects_id", "supersedes_id", "retracts_id", "invalidates_id",
                 "historical_only", "expected_ids", "prohibited_ids", "rationale", "procedure_outcome"}
    leaked = sorted(set(body) & forbidden)
    if leaked:
        raise ValueError(f"write envelope leaks benchmark truth: {leaked}")
