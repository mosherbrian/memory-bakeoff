# Experiment plan

This project is deliberately staged so an impressive chat demo cannot masquerade as a
memory result.

## Phase 0 — harness validation (complete in build sandbox)

Purpose: prove scoring, stale/failed penalties, multi-hop labels, and verified-feedback
measurement work before testing exotic engines.

Providers: BM25, dense LSA, BM25+dense RRF, toy adaptive diagnostic.

Release gate: unit tests green; deterministic results exported; toy feedback provider
must visibly change at least one learning-sensitive metric.

## Phase 1 — raw memory-engine bake-off

Purpose: isolate storage/retrieval behavior from LLM extraction quality.

Eligible field:

- BM25
- dense LSA
- hybrid RRF
- Mem0 with inference disabled
- agentmemory in default no-LLM mode
- MemBukkit via `ingest_facts` + evidence-only `search`
- Habitus via direct `remember`/`recall`
- Hindsight with `HINDSIGHT_API_LLM_PROVIDER=none` (documented chunk-storage/no-extraction mode)

Claude-Mem is not given a fake raw implementation.

Primary metrics:

- Hit@5 / MRR for ordinary recall
- all-relevant@5 for multi-hop questions
- prohibited@5 for stale/failed-memory contamination
- useful-before-harmful for conflict/procedure ordering
- negative-empty-rate (reported separately, not folded into positive recall)
- latency

Do not select a winner from one composite score. Look for Pareto improvements and
category-specific failure modes.

## Phase 1b — verified-experience learning

Purpose: test the Quality-Loop hypothesis: does externally verified success/failure
change what the memory engine surfaces on later related tasks?

The harness issues receipts. Agent/model self-assessment is never accepted as a receipt.

Habitus needs a small retrieval-credit API extension before this is a fair test: stock
`record_outcome()` credits output-decision traversal edges, not the input retrieval paths
that supplied memories. Keep stock and patched Habitus as separate ablations.

Suggested conditions:

1. hybrid retrieval, no feedback
2. Habitus stock, no retrieval credit
3. Habitus + retrieval-path credit from verified receipts
4. any other provider with a documented feedback/update mechanism

Measure a learning curve over held-out paraphrased tasks, not repeated exact queries.

## Phase 2 — product-mode bake-off

Purpose: test each product as intended, including its LLM extractor/compressor.

Adds Claude-Mem and Hindsight and enables product ingestion for the other systems.
Pin every extractor/model/embedder/reranker. Report ingest cost and latency separately
from retrieval latency.

Release gate: source provenance from returned memories must map reliably to benchmark
records. Fuzzy text matching alone is not acceptable for publishable scores.

## Phase 3 — real coding-agent impact

Only Phase-1/2 survivors should be integrated into Pi or another fixed coding-agent
harness.

Hold constant:

- coding model and quantization
- inference server and flags
- Pi/Pi.dev version and extension configuration
- tools and permissions
- repository/task snapshot
- context budget
- compaction configuration
- repeated-run count/seeds where applicable

Measure actual task success, regressions, token/context cost, memory usefulness, stale
memory harm, and post-compaction continuity. This is the phase that answers whether a
strong memory benchmark score actually makes the coding agent better.
