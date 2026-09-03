"""Frozen Hindsight v0.9.2 adapter for the longitudinal-v1 ruler (Gen31).

Raw/no-LLM profile. Routing uses only public request coordinates: the case's
target kind, its event time, and its scope. It never sees expected ids,
prohibited ids, truth keys, transition labels, lineage, or rationale.

Unlike Perseus, Hindsight's raw ``retain`` accepts an explicit per-item
timestamp, so the store's timeline is the fixture's own calendar timeline and no
time-base transform is needed.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..longitudinal import LongitudinalCase, LongitudinalObservation, TargetKind

ADAPTER_VERSION = "hindsight-longitudinal-adapter-v1"
CONTEXT_PREFIX = "memory-bakeoff-longitudinal"

# Public intent -> native read. Frozen before any scored query.
CURRENT_STATE_KINDS = (TargetKind.CURRENT, TargetKind.SCOPE, TargetKind.RECOMMENDED_PROCEDURE, TargetKind.NEGATIVE_UNKNOWN)
VANTAGE_POINT_KINDS = (TargetKind.HISTORICAL_BELIEF, TargetKind.AS_OF, TargetKind.CORRECTED_HISTORY, TargetKind.LATE_HISTORY)

FORBIDDEN_FIELDS = ("truth_key", "transition", "corrects_id", "supersedes_id", "retracts_id", "invalidates_id",
                    "historical_only", "procedure_outcome", "expected_ids", "prohibited_ids", "rationale")


def document_id_for(observation_id: str) -> str:
    return f"record-{observation_id}"


def retain_arguments(observation: LongitudinalObservation, bank_id: str) -> dict[str, Any]:
    """One ordinary raw retain call. Public source data only.

    ``timestamp`` becomes Hindsight's ``mentioned_at`` — when the fact was
    stated — so it carries the fixture's public ingestion time. Event and
    effective time travel as ordinary metadata, which the raw profile stores but
    does not interpret; ``occurred_start``/``occurred_end`` are reachable only
    through LLM fact extraction or the curate endpoint, both out of scope here.
    """
    public = observation.public_dict()
    return {
        "bank_id": bank_id,
        "content": public["assertion"],
        "context": f"{CONTEXT_PREFIX}; scope={public['scope']}",
        "timestamp": public["ingestion_time"],
        "document_id": document_id_for(public["canonical_observation_id"]),
        "metadata": {
            "record_id": public["canonical_observation_id"],
            "scope": public["scope"],
            "configuration": public["configuration"],
            "event_time": public["event_time"],
            "effective_time": public["effective_time"],
            "provenance": public["provenance"],
            "source_kind": "benchmark_observation",
        },
    }


def native_operation(case: LongitudinalCase) -> str:
    if case.target_kind in CURRENT_STATE_KINDS:
        return "recall_current"
    if case.target_kind in VANTAGE_POINT_KINDS:
        return "recall_query_timestamp"
    raise ValueError(f"no frozen native operation for target kind {case.target_kind}")


def recall_arguments(case: LongitudinalCase, bank_id: str, limit: int) -> dict[str, Any]:
    arguments: dict[str, Any] = {"bank_id": bank_id, "query": case.query, "max_tokens": 4096}
    if native_operation(case) == "recall_query_timestamp":
        if case.event_time is None:
            raise ValueError(f"{case.id}: vantage-point recall needs a public event time")
        arguments["query_timestamp"] = case.event_time.isoformat()
    return arguments


def assert_public_only(payload: dict[str, Any]) -> None:
    leaked = sorted(set(payload) & set(FORBIDDEN_FIELDS))
    metadata = payload.get("metadata") or {}
    leaked += sorted(set(metadata) & set(FORBIDDEN_FIELDS))
    if leaked:
        raise ValueError(f"hindsight payload leaks benchmark truth: {sorted(set(leaked))}")


def adapter_contract_payload() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "product": "hindsight",
        "product_version": "0.9.2",
        "profile": "raw_product, no-LLM ingestion, ONNX multilingual-e5-small, local CPU cross-encoder reranker",
        "write_path": "hindsight_client.retain (raw, HINDSIGHT_API_LLM_PROVIDER=none)",
        "document_id_rule": "record- + canonical observation id",
        "timestamp_rule": "public ingestion_time -> native mentioned_at",
        "occurred_range": "not set; reachable only via LLM fact extraction or the curate endpoint, both excluded",
        "metadata_fields": ["configuration", "effective_time", "event_time", "provenance", "record_id", "scope", "source_kind"],
        "scope_rule": "one bank per repetition; scope and configuration are ordinary metadata, never a bank boundary",
        "read_paths": {
            "recall_current": "recall(query)",
            "recall_query_timestamp": "recall(query, query_timestamp=public event time)",
        },
        "routing": {
            "current_state": [str(k) for k in CURRENT_STATE_KINDS],
            "vantage_point": [str(k) for k in VANTAGE_POINT_KINDS],
        },
        "routing_inputs": ["target_kind", "event_time", "scope"],
        "forbidden_inputs": list(FORBIDDEN_FIELDS),
        "post_filtering": "none; native order and native limit are preserved",
        "lifecycle_calls": "none; no curate, invalidate, revert, update or delete call is issued",
    }


def adapter_contract_sha256() -> str:
    return hashlib.sha256(json.dumps(adapter_contract_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
