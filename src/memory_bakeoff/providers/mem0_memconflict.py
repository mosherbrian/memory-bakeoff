"""Mem0 adapter for the frozen MemConflict contract (Gen37).

Gen32 identity, unchanged: package 2.0.19 from the pinned checkout,
`Memory.add(infer=False)`, embedded on-disk Qdrant, FastEmbed dense + BM25
sparse, native search at threshold 0.1 and limit 5, no rerank and no postfilter.

No metadata is written. Gen32's metadata fields described the longitudinal
fixture and have no counterpart here; provenance is recovered from the native id
the add call returns, so nothing needs to be embedded in or beside the text.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

ADAPTER_VERSION = "mem0-memconflict-adapter-v1"
THRESHOLD = 0.1
EMBEDDING_DIMS = 1024
LIMIT = 5


def user_id_for_persona(persona_id: str) -> str:
    """Opaque per-persona namespace. Never enters indexed text."""
    return "mc-" + hashlib.sha256(f"memconflict-persona:{persona_id}".encode()).hexdigest()[:32]


def add_arguments(text: str, persona_id: str) -> dict[str, Any]:
    return {"text": text, "user_id": user_id_for_persona(persona_id), "infer": False}


def search_arguments(question_text: str, persona_id: str, limit: int = LIMIT) -> dict[str, Any]:
    return {"query": question_text, "filters": {"user_id": user_id_for_persona(persona_id)},
            "limit": limit, "threshold": THRESHOLD}


def config_for(path: str, collection: str, history_db: str) -> dict[str, Any]:
    """Gen32's configuration. The OpenAI client is built at init and never called."""
    return {
        "llm": {"provider": "openai", "config": {"api_key": "not-used-in-raw-mode"}},
        "embedder": {"provider": "fastembed",
                     "config": {"model": "thenlper/gte-large", "embedding_dims": EMBEDDING_DIMS}},
        "vector_store": {"provider": "qdrant",
                         "config": {"path": path, "collection_name": collection,
                                    "embedding_model_dims": EMBEDDING_DIMS, "on_disk": True}},
        "history_db_path": history_db,
    }


def adapter_contract_payload() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "product": "mem0ai",
        "product_version": "2.0.19",
        "upstream_commit": "19cb89aff472325c707f64b2f34ae6afdbf7faf7",
        "profile": "raw_product, Gen32 identity: Memory.add(infer=False), embedded on-disk Qdrant, "
                   "FastEmbed dense + BM25 sparse",
        "write_path": "upstream Memory.add(text, user_id, infer=False)",
        "ingestion_unit": "one well-formed released dialogue message = one add",
        "indexed_content_rule": "released message text only; no metadata, no identifiers, no labels",
        "metadata_fields": [],
        "isolation": "fresh on-disk Qdrant path and collection per persona, plus an opaque per-persona user_id",
        "read_path": "Memory.search(query, filters={user_id}, limit=5, threshold=0.1)",
        "query_rule": "released question text, byte for byte, with no prefix or rewrite",
        "temporal_surface": "none; no date filter, no as-of read, no ranking on time",
        "post_filtering": "none; native order, native score and native limit are preserved",
        "provenance_rule": "native id returned by add -> harness ledger -> released persona/session/turn/message",
        "forbidden_inputs": ["answer", "conflict_type", "ability_target", "difficulty", "Session_Type",
                             "Updated_Attributes", "Static_Conflict_Information",
                             "Conditional_Conflict_Information", "gold_support_sessions"],
        "lifecycle_calls": "none; no update, delete, reset or history rewrite is issued",
        "threshold": THRESHOLD,
        "embedding_dims": EMBEDDING_DIMS,
        "embedding_snapshot": "qdrant/gte-large-onnx 770e825c74a004f165b78793f7c8fc4a95280878",
        "sparse_snapshot": "Qdrant/bm25 22b8d2af71a76161e18dd432d2cee0eefa66e412",
    }


def adapter_contract_sha256() -> str:
    return hashlib.sha256(json.dumps(adapter_contract_payload(), sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()
