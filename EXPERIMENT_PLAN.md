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


---

## Architectural synthesis (added 2026-09-04, after Gen38)

*Everything above is preserved as originally written. This section is additive: the
staged plan describes where the project started, and nothing in it has been revised
to look as though the architecture below was known at the outset.*

Thirty-eight generations of measurement changed what the project believes the object
of study is. The plan above treats memory as the thing being evaluated. The evidence
now places memory as **one layer in an agent architecture**, and the bake-off as the
component-level evidence programme inside it.

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for the synthesis: the layer model, the
authority rules, the mapping of every system studied here onto a layer, and the
falsifiable questions that follow.

The short reason for the change, from the measured record: at full external-benchmark
scale two production memory engines land within a point of each other and within three
points of a plain BM25 index on old-truth-versus-new-contradiction questions (Gen38),
and the one engine that actively decides currentness by similarity trades false
persistence for false supersession rather than fixing it (Gen35). Retrieval quality is
not the missing capability.

The phases above remain valid and are unchanged. Phase-level work continues under the
same discipline — frozen evidence classes, calibration before full release, exact
provenance, fail-closed reporting — and now feeds the component layer of the larger
architecture rather than standing alone.
