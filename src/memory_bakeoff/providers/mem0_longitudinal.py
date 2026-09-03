"""Frozen Mem0 2.0.19 adapter for the longitudinal-v1 ruler (Gen32).

Raw `infer=False` profile, preserving the Gen10 scored identity exactly.

Mem0 has no temporal retrieval surface in this profile: its only time-shaped
APIs are mutation (`update`, `_update_memory`) and audit (`history`). Every case
therefore runs the same native search, and the ruler's vantage-point intents are
answered by whatever the store holds at that checkpoint.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..longitudinal import LongitudinalCase, LongitudinalObservation

ADAPTER_VERSION = "mem0-longitudinal-adapter-v1"
USER_ID = "memory-bakeoff"
THRESHOLD = 0.1
EMBEDDING_DIMS = 1024

FORBIDDEN_FIELDS = ("truth_key", "transition", "corrects_id", "supersedes_id", "retracts_id", "invalidates_id",
                    "historical_only", "procedure_outcome", "expected_ids", "prohibited_ids", "rationale",
                    "configuration", "event_time", "effective_time")


def source_ref_for(observation_id: str) -> str:
    return f"record-{observation_id}"


def add_arguments(observation: LongitudinalObservation) -> dict[str, Any]:
    """One ordinary raw add. Gen10 carried exactly these four metadata fields.

    `configuration` is deliberately absent: Gen10 did not carry it, and adding it
    would hand Mem0 a routing key the scored Round-1 identity never had. The
    configuration wording already present in the assertion text stays there.
    """
    public = observation.public_dict()
    return {
        "text": public["assertion"],
        "user_id": USER_ID,
        "infer": False,
        "metadata": {
            "record_id": public["canonical_observation_id"],
            "source_ref": source_ref_for(public["canonical_observation_id"]),
            "scope": public["scope"],
            "timestamp": public["ingestion_time"],
        },
    }


def native_operation(case: LongitudinalCase) -> str:
    """Mem0 exposes no as-of/date/history read in this profile."""
    return "search_current_state"


def search_arguments(case: LongitudinalCase, limit: int) -> dict[str, Any]:
    """Gen10 semantics: the frozen query, the constant user_id filter, nothing else."""
    return {"query": case.query, "filters": {"user_id": USER_ID}, "limit": limit, "threshold": THRESHOLD}


def assert_public_only(payload: dict[str, Any]) -> None:
    metadata = payload.get("metadata") or {}
    leaked = sorted((set(payload) | set(metadata)) & set(FORBIDDEN_FIELDS))
    if leaked:
        raise ValueError(f"mem0 payload leaks benchmark truth or a non-Gen10 routing key: {leaked}")


def adapter_contract_payload() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "product": "mem0ai", "product_version": "2.0.19",
        "upstream_commit": "19cb89aff472325c707f64b2f34ae6afdbf7faf7",
        "profile": "raw_product, Memory.add(infer=False), embedded on-disk Qdrant, FastEmbed dense + BM25 sparse",
        "write_path": "upstream Memory.add(text, user_id, metadata, infer=False)",
        "metadata_fields": ["record_id", "scope", "source_ref", "timestamp"],
        "timestamp_rule": "public ingestion_time as opaque ISO metadata; Mem0 does not rank on it",
        "read_path": "Memory.search(query, filters={user_id}, limit, threshold)",
        "scored_filter": "constant user_id only, exactly as Gen10",
        "unscored_capability": "Mem0 can also filter on metadata such as scope; deliberately NOT used in the scored identity",
        "temporal_surface": "none; update/_update_memory/history are mutation and audit, not retrieval",
        "routing": "single native operation for every target kind; no vantage-point read exists",
        "forbidden_inputs": list(FORBIDDEN_FIELDS),
        "post_filtering": "none; native order and native limit are preserved",
        "lifecycle_calls": "none; no update, delete, reset or history rewrite is issued",
        "threshold": THRESHOLD, "embedding_dims": EMBEDDING_DIMS,
    }


def adapter_contract_sha256() -> str:
    return hashlib.sha256(json.dumps(adapter_contract_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
