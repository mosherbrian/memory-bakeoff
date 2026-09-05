"""`perseus-scored-read-gen92-v1`: is there a scored read that keeps the same semantics?

Gen91 could not say why perseus ranks a superseded record above its replacement,
because the committed results carry `canonical_id`, `native_id`,
`provenance_exact` and `rank` — and no score. That left one prerequisite: does the
pinned build expose a read operation that returns **per-hit relevance scores while
preserving the Round-2 retrieval semantics**?

The constraint is the whole question. Perseus 2.23.2 has several read tools, and
at least one of them is scored. Switching to it because it prints numbers would
answer a different question — what a different retrieval strategy ranks — and
report it as if it explained the strategy actually measured. That substitution is
the failure this generation exists to avoid.

Round 2 used `perseus_vault_recall` with `mode="hybrid"`: fts5 plus dense, fused
by reciprocal rank fusion. A candidate qualifies only if it is that same
operation and that same mode.
"""
from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "perseus-scored-read-gen92-v1"

PINNED_VERSION = "2.23.2"
PINNED_COMMIT = "9c829207a4b44a8e679ba912b4c1c5608c8f1e36"
ROUND2_OPERATION = "perseus_vault_recall"
ROUND2_MODE = "hybrid"

QUALIFIES = "SCORED_READ_AVAILABLE"
OPAQUE = "OPAQUE"
NOT_DEMONSTRABLE = "NOT_DEMONSTRABLE"

# Every field the pinned build returns per hit under mode=hybrid, read from a
# live shape probe on a scratch database rather than from documentation.
HYBRID_ITEM_FIELDS = (
    "agent_id", "always_on", "archive_reason", "archived", "assertion_text",
    "body_json", "canonical_record_id", "category", "certainty",
    "created_at_unix_ms", "decay_score", "efficacy_status", "encoding_strength",
    "epistemic_state", "follow_count", "follow_rate", "hints", "id", "key",
    "last_accessed_unix_ms", "layer", "links", "memory_type", "miss_count",
    "retrieval_count", "source", "status", "tags", "topic_path", "type",
    "untrusted", "verified", "visibility", "why_served", "workspace_hash",
)
HYBRID_TOP_LEVEL_FIELDS = ("items", "retrieval_profile", "total")

# Fields that look score-shaped and are not query relevance.
NOT_RELEVANCE = {
    "decay_score": "a lifecycle importance floor, not query relevance; identical "
                   "(0.5) for both records in the probe",
    "certainty": "a provenance/trust property of the record, not of the match",
    "follow_rate": "a usage statistic accumulated over time",
    "why_served": "a governance projection - memory class, promotion state, "
                  "support count, and a fixed reason string 'matched the recall "
                  "query'; identical for both records in the probe",
    "retrieval_profile": "a single string ('shared'), not a per-hit value",
}

# Read tools considered and why each is or is not a candidate.
CANDIDATES = {
    "perseus_vault_recall (mode=hybrid)": {
        "same_semantics": True,
        "returns_per_hit_scores": False,
        "evidence": "live probe: 35 per-hit fields, none of them a relevance or "
                    "ranking score",
    },
    "perseus_vault_recall (mode=fused)": {
        "same_semantics": False,
        "returns_per_hit_scores": True,
        "evidence": "returns fused_trace with selection_decisions, fusion, rerank, "
                    "strategies and truncation - but 'fused' is TEMPR-style "
                    "multi-strategy (fts5 + dense + graph + temporal, weighted RRF, "
                    "token-budget truncation), a different retrieval strategy",
    },
    "perseus_vault_semantic_search": {
        "same_semantics": False,
        "returns_per_hit_scores": True,
        "evidence": "dense-only, 'ranked purely by embedding similarity (no keyword "
                    "fallback)' - by its own description not the hybrid fusion",
    },
    "perseus_vault_recall_batch": {
        "same_semantics": False,
        "returns_per_hit_scores": None,
        "evidence": "fuses results across a BATCH of queries server-side; the unit "
                    "of retrieval is different",
    },
    "perseus_vault_declared_query": {
        "same_semantics": False,
        "returns_per_hit_scores": False,
        "evidence": "explicitly 'the no-ranking arm' - deterministic exact match",
    },
    "perseus_vault_retrieval_telemetry": {
        "same_semantics": False,
        "returns_per_hit_scores": False,
        "evidence": "aggregate telemetry - concentration, diversity, repeated "
                    "serving - not per-hit scores for one query",
    },
}

# Measured, not inferred: the scored trace is refused on the Round-2 mode.
SELECTION_DECISIONS_ON_HYBRID = {
    "arguments": {"mode": "hybrid", "include_selection_decisions": True},
    "is_error": True,
    "message": "include_selection_decisions requires mode='fused' and a searchable "
               "query",
    "why_it_matters": "the product itself refuses to attach the scored trace to the "
                      "Round-2 mode, so this is a product constraint rather than an "
                      "adapter omission",
}


def qualifying_candidates() -> list[str]:
    return sorted(name for name, entry in CANDIDATES.items()
                  if entry["same_semantics"] and entry["returns_per_hit_scores"])


def verdict() -> dict[str, Any]:
    qualifying = qualifying_candidates()
    if qualifying:
        return {"contract_version": CONTRACT_VERSION, "verdict": QUALIFIES,
                "path": qualifying}
    return {
        "contract_version": CONTRACT_VERSION,
        "pinned_build": f"perseus-vault {PINNED_VERSION} ({PINNED_COMMIT[:7]})",
        "round2_path": f"{ROUND2_OPERATION} mode={ROUND2_MODE}",
        "verdict": OPAQUE,
        "lq11_perseus_cause": NOT_DEMONSTRABLE,
        "why": "no read operation on this build returns per-hit relevance scores "
               "while preserving the Round-2 retrieval semantics. Scored traces "
               "exist, and every one of them is a different retrieval strategy.",
        "substitution_declined": "mode='fused' and semantic_search both expose "
                                 "scores and both rank differently; using either "
                                 "would answer what a different strategy ranks and "
                                 "report it as an explanation of the one measured",
        "product_constraint_not_adapter_omission": SELECTION_DECISIONS_ON_HYBRID,
        "gen93_targeted_rerun": "NOT UNBLOCKED - there is no path to freeze",
        "closes": "the perseus share of the LQ11 ranking failures closes as OPAQUE",
        "no_benchmark_rerun": True,
    }


def closed_mechanisms() -> dict[str, Any]:
    """The other two Gen91 causes, closed as established. No further experiment."""
    return {
        "mem0": {"mechanism": "NEAR_TIE", "status": "CLOSED",
                 "finding": "no meaningful preference; the pair is separated by 1.2% "
                            "of the distance to the next record in its own list",
                 "further_experiment": "none unless a later question specifically "
                                       "targets tie-breaking"},
        "hindsight": {"mechanism": "MEANINGFUL_PREFERENCE", "status": "CLOSED",
                      "finding": "a real stale preference, localised to the reranker: "
                                 "keyword identical, semantic gap 0.001655, reranker "
                                 "gap 0.078265",
                      "further_experiment": "none unless a later question "
                                            "specifically targets reranker quality"},
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "question": "does the pinned build expose a read that returns per-hit "
                    "relevance scores AND preserves the Round-2 retrieval semantics?",
        "hard_constraint": "a different search mode does not qualify merely because "
                           "it exposes scores",
        "round2_semantics": "perseus_vault_recall mode=hybrid - fts5 plus dense, "
                            "fused by reciprocal rank fusion",
        "method": "MCP tools/list on the pinned binary, plus a live shape probe on a "
                  "scratch database - the item fields are read from a real response, "
                  "not from documentation",
        "candidates_considered": sorted(CANDIDATES),
        "no_benchmark_rerun": True,
    }
