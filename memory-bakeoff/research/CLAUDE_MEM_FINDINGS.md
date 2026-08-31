# Claude-Mem controlled-core findings

Pinned source inspected at `thedotmack/claude-mem` commit
`fa6a1e9ec12d23f98326a9b26e243acb0819e105` (package version 10.6.1).

## What is and is not being tested

The published worker bundle is generated at build/publish time; the Git-tracked
`plugin/scripts/worker-service.cjs` is an empty placeholder. The current sandbox
cannot ingest the npm tarball/built worker, so these rows are **controlled search
policy ablations**, not a full Claude-Mem product run and not a test of its LLM
compression quality.

Two current upstream search paths are modeled:

1. `claude_mem_fts5_core` — current `SessionSearch` FTS5 behavior. Raw benchmark
   records are injected only into the observation `text` field. The query is
   escaped exactly as upstream does: the whole natural-language query is wrapped
   in quotes before `MATCH`, producing phrase-search semantics. This is a
   diagnostic of the fallback/search seam, not product ingestion.
2. `claude_mem_chroma_lsa` — current Chroma semantic-search policy with the
   external semantic representation held constant using the benchmark's shared
   32-D LSA vectors. It preserves the current top-100 semantic candidate stage,
   observation relevance order, and implicit 90-day recency filter when the
   caller provides no date range.
3. `claude_mem_chroma_lsa_no_recency` — identical to (2) with only the implicit
   90-day filter removed. This is the causal ablation.

The evaluation clock is pinned at `2026-08-30T12:00:00Z` by default and can be
overridden with `CLAUDE_MEM_EVAL_NOW`.

## Key result

Only 9 of the 50 core memories are inside the current 90-day default window at
the pinned evaluation date. The 450 stress distractors are deliberately older,
so the 500-record stress corpus also has only 9 records inside the window.

| Arm | Core Hit@5 | Stress Hit@5 | Stress all-relevant@5 |
|---|---:|---:|---:|
| Claude-Mem FTS5 phrase core | 0.000 | 0.000 | 0.000 |
| Claude-Mem Chroma policy + shared LSA | 0.208 | 0.208 | 0.208 |
| Same, 90-day filter disabled | 0.958 | 0.583 | 0.542 |
| Dense LSA baseline | 0.958 | 0.583 | 0.542 |

The no-recency arm and dense-LSA baseline have the same retrieval representation
and the same top-5 recall. Therefore, in this controlled experiment the large
loss in the current-policy arm is caused by **recency filtering, not semantic
retrieval quality**.

The FTS5 fallback scores zero because the held-out benchmark queries are natural
paraphrases rather than verbatim substrings. Current upstream `SessionSearch`
wraps the entire query as a quoted FTS phrase. This does not mean FTS5 itself is
incapable of useful lexical retrieval; it means this exact fallback policy is a
poor fit for paraphrased recall.

## Interpretation

This is potentially important for a product advertised as long-term memory.
The result does **not** establish that Claude-Mem users cannot retrieve memories
older than 90 days: callers can supply an explicit date range, other workflows
may reach older data, and product-generated observations differ from our raw
records. It does establish that the current semantic search code applies an
implicit 90-day cutoff when no date range is supplied, and that this policy can
dominate recall on a deliberately long-horizon corpus.

A full product-mode test remains pending until the generated npm worker bundle
can be brought into the sandbox. Once runnable, the existing Anthropic-compatible
ChatGPT sidecar can drive the actual compression pipeline.
