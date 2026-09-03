"""Frozen agentmemory 0.9.29 adapter for the longitudinal-v1 ruler (Gen33).

Raw-product profile with the product's OWN write-time supersession left enabled.
The harness never chooses what to retire; it only records what the product did.

agentmemory exposes no temporal read, so every case runs the same native
smart-search. Its lifecycle rule is strict lexical Jaccard > 0.7 over
whitespace tokens longer than two characters, case- and punctuation-sensitive.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..longitudinal import LongitudinalCase, LongitudinalObservation

ADAPTER_VERSION = "agentmemory-longitudinal-adapter-v1"
PROJECT = "memory-bakeoff-longitudinal"
JACCARD_THRESHOLD = 0.7

FORBIDDEN_FIELDS = ("truth_key", "transition", "corrects_id", "supersedes_id", "retracts_id", "invalidates_id",
                    "historical_only", "procedure_outcome", "expected_ids", "prohibited_ids", "rationale",
                    "configuration", "scope", "event_time", "effective_time")


def remember_arguments(observation: LongitudinalObservation, agent_id: str) -> dict[str, Any]:
    """One ordinary native write. Gen13 carried the canonical id as sourceObservationIds.

    Scope and configuration are deliberately NOT sent: Gen13 established that a
    single agentId and one ordinary project namespace are the evaluated identity,
    and smart-search does not isolate by project anyway. The scope and
    configuration wording already present in the assertion stays in the text.
    """
    public = observation.public_dict()
    return {
        "agentId": agent_id,
        "project": PROJECT,
        "content": public["assertion"],
        "sourceObservationIds": [public["canonical_observation_id"]],
    }


def native_operation(case: LongitudinalCase) -> str:
    """agentmemory offers no as-of, date-range or history read in this profile."""
    return "smart_search_current_state"


def search_arguments(case: LongitudinalCase, agent_id: str, limit: int) -> dict[str, Any]:
    return {"agentId": agent_id, "project": PROJECT, "query": case.query, "limit": limit}


def assert_public_only(payload: dict[str, Any]) -> None:
    leaked = sorted(set(payload) & set(FORBIDDEN_FIELDS))
    if leaked:
        raise ValueError(f"agentmemory payload leaks benchmark truth or a non-Gen13 field: {leaked}")


def classify_supersession(predecessor_id: str | None, successor_id: str | None,
                          truth: dict[str, dict[str, Any]]) -> str:
    """Judge a retirement the PRODUCT already made, against frozen canonical truth.

    Legitimate when the successor genuinely corrects or supersedes the
    predecessor. False when the ruler holds them as concurrent or unrelated.
    """
    if predecessor_id is None or successor_id is None:
        return "unmapped"
    successor = truth.get(successor_id) or {}
    if successor.get("corrects_id") == predecessor_id or successor.get("supersedes_id") == predecessor_id:
        return "legitimate_supersession"
    return "false_supersession"


def adapter_contract_payload() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "product": "agentmemory", "product_version": "0.9.29",
        "upstream_commit": "e04ba88819c365c9acf9d6661ea802143e728bd6",
        "profile": "raw_product, native /agentmemory/remember + /agentmemory/smart-search, local q8 all-MiniLM-L6-v2",
        "write_path": "native /agentmemory/remember with the product's own write-time supersession ENABLED",
        "provenance_rule": "sourceObservationIds -> mem_* -> obsId, exact",
        "isolation": "fresh iii data directory and a distinct agentId per repetition; one project namespace; never a project or agent per scope",
        "read_path": "native /agentmemory/smart-search",
        "temporal_surface": "none; no as-of, date-range or history read exists in this profile",
        "routing": "single native operation for every target kind",
        "native_lifecycle_rule": {
            "mechanism": "write-time supersession during remember",
            "similarity": "strict lexical Jaccard over whitespace tokens of length > 2, case- and punctuation-sensitive",
            "threshold": JACCARD_THRESHOLD,
            "predecessors_per_write": 1,
            "cross_project": "never supersedes across an explicit project boundary",
            "retired_state": "isLatest=false; the record stays in KV and leaves the search index; absence from search is not deletion",
        },
        "harness_lifecycle_calls": "none; the harness never selects what to retire and never calls an update, delete or supersede API",
        "forbidden_inputs": list(FORBIDDEN_FIELDS),
        "post_filtering": "none; native order and native limit are preserved",
        "disabled": ["LLM provider/extractor", "CONSOLIDATION_ENABLED", "GRAPH_EXTRACTION_ENABLED",
                     "AGENTMEMORY_AUTO_COMPRESS", "learned reranking"],
    }


def adapter_contract_sha256() -> str:
    return hashlib.sha256(json.dumps(adapter_contract_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
