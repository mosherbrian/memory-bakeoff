"""Perseus Vault adapter for the frozen MemConflict contract (Gen37).

Gen29 identity, unchanged: official v2.23.2, ordinary operator CLI write, native
hybrid recall, limit 5, no rerank and no postfilter. Nothing routes on a
scorer-only field, because the adapter never receives one.

Provenance lives OUTSIDE the indexed text. The write receipt's native id is
recorded in a harness ledger against the released persona/session/turn/message,
and the record key is an ordinal the product would know anyway from write order.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

ADAPTER_VERSION = "perseus-memconflict-adapter-v1"
CATEGORY = "memconflict_message"
PINNED_VERSION = "2.23.2"
PINNED_BUILD = "9c82920"
LIMIT = 5


def workspace_for_persona(persona_id: str) -> str:
    """One workspace per persona vault. Opaque, derived from the released id only."""
    return hashlib.sha256(f"memconflict-persona:{persona_id}".encode()).hexdigest()


def key_for_ordinal(ordinal: int) -> str:
    """Ordinal write key. Carries no released identifier and no label."""
    return f"msg-{ordinal:06d}"


def body_for_message(text: str) -> dict[str, str]:
    """Indexed content is the released message text and nothing else."""
    return {"assertion": text, "source_kind": "memconflict_dialogue_message"}


def write_arguments(text: str, ordinal: int, persona_id: str) -> dict[str, Any]:
    return {
        "category": CATEGORY,
        "key": key_for_ordinal(ordinal),
        "body": body_for_message(text),
        "workspace_hash": workspace_for_persona(persona_id),
    }


def recall_arguments(question_text: str, persona_id: str, limit: int = LIMIT) -> dict[str, Any]:
    """The released question text, the persona workspace, native hybrid, limit 5."""
    return {
        "query": question_text,
        "workspace_hash": workspace_for_persona(persona_id),
        "limit": limit,
        "mode": "hybrid",
    }


def assert_no_identifier_in_body(body: Mapping[str, Any], forbidden: Mapping[str, Any]) -> None:
    """Refuse a write whose indexed text carries a released identifier."""
    blob = json.dumps(body, sort_keys=True)
    leaked = sorted(str(value) for value in forbidden.values()
                    if value is not None and str(value) and str(value) in blob)
    if leaked:
        raise ValueError(f"indexed body carries released identifiers: {leaked}")


def adapter_contract_payload() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "product": "perseus-vault",
        "product_version": PINNED_VERSION,
        "product_build": PINNED_BUILD,
        "source_commit": "9c829207a4b44a8e679ba912b4c1c5608c8f1e36",
        "release_tag": "4f405f53f4c9b6a403df0d42cf0d59bf80c64da4",
        "tarball_sha256": "e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb",
        "profile": "raw_product, Gen29 identity: operator CLI write + native hybrid recall",
        "write_path": "perseus-vault write --category --key --body --workspace-hash",
        "ingestion_unit": "one well-formed released dialogue message = one write",
        "indexed_fields": ["assertion", "source_kind"],
        "indexed_content_rule": "released message text only; no persona/session/turn id, no role, no date, no label",
        "key_rule": "msg- + zero-padded per-persona write ordinal",
        "workspace_rule": "sha256 of memconflict-persona:<released persona id>; one workspace per persona vault",
        "isolation": "fresh encrypted SQLite vault and key per persona",
        "read_path": "perseus_vault_recall(mode=hybrid, limit=5)",
        "read_isolation": "queries run against a byte-for-byte vault snapshot; the write vault only receives writes",
        "temporal_arguments": "none; ordinary writes carry product transaction time, exactly as Gen29",
        "post_filtering": "none; native order, native score and native limit are preserved",
        "query_rule": "released question text, byte for byte, with no prefix or rewrite",
        "provenance_rule": "native write receipt id -> harness ledger -> released persona/session/turn/message",
        "forbidden_inputs": ["answer", "conflict_type", "ability_target", "difficulty", "Session_Type",
                             "Updated_Attributes", "Static_Conflict_Information",
                             "Conditional_Conflict_Information", "gold_support_sessions"],
        "lifecycle_calls": "none; no supersede, update, delete or maintenance is issued",
    }


def adapter_contract_sha256() -> str:
    return hashlib.sha256(json.dumps(adapter_contract_payload(), sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()
