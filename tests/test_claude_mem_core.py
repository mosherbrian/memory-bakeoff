from datetime import timedelta

from memory_bakeoff.corpus import build_corpus
from memory_bakeoff.providers.claude_mem_core import (
    CHROMA_BATCH_SIZE,
    DEFAULT_EVAL_NOW,
    RECENCY_WINDOW_DAYS,
    ClaudeMemChromaLSAProvider,
    ClaudeMemChromaLSANoRecencyProvider,
    ClaudeMemFTS5CoreProvider,
)
from memory_bakeoff.runner import run_provider


def test_claude_mem_fts5_core_executes_real_fts5():
    p = ClaudeMemFTS5CoreProvider()
    records, _ = build_corpus()
    p.ingest(records)
    # Exact phrase exists in M001; SessionSearch wraps the whole query in quotes.
    from memory_bakeoff.models import QueryCase
    q = QueryCase("T", "exact", "cosign OIDC token", ("M001",))
    r = p.retrieve(q, 5)
    assert r.ids and r.ids[0] == "M001"
    assert r.raw["quoted_phrase"] is True


def test_claude_mem_default_recency_policy_is_pinned_and_small_on_corpus():
    records, cases = build_corpus()
    cutoff = DEFAULT_EVAL_NOW - timedelta(days=RECENCY_WINDOW_DAYS)
    assert sum(r.timestamp >= cutoff for r in records) == 9
    p = ClaudeMemChromaLSAProvider(); p.ingest(records)
    # A normal, non-as-of case gets the implicit 90-day policy.
    case = next(c for c in cases if c.as_of is None)
    result = p.retrieve(case, 5)
    assert result.raw["recency_policy"] == "default_90d"
    assert result.raw["semantic_batch_size"] == min(CHROMA_BATCH_SIZE, len(records))
    assert all(p._records[rid].timestamp >= cutoff for rid in result.ids)


def test_claude_mem_as_of_suppresses_implicit_recency_window():
    records, cases = build_corpus()
    case = next(c for c in cases if c.as_of is not None)
    p = ClaudeMemChromaLSAProvider(); p.ingest(records)
    r = p.retrieve(case, 5)
    assert r.raw["recency_policy"] == "explicit_date_end"
    assert all(p._records[rid].timestamp <= case.as_of for rid in r.ids)


def test_no_recency_ablation_matches_dense_shape_nontrivially():
    p = ClaudeMemChromaLSANoRecencyProvider()
    records, cases = build_corpus(); p.ingest(records)
    r = p.retrieve(cases[0], 5)
    assert r.items
    assert r.raw["recency_policy"] == "recency_disabled_ablation"


def test_claude_mem_core_providers_run_in_harness():
    for name in ("claude_mem_fts5_core", "claude_mem_chroma_lsa", "claude_mem_chroma_lsa_no_recency"):
        r = run_provider(name, distractors=0, top_k=5)
        assert r["status"] == "ok"
