# Build manifest

Built in ChatGPT on 2026-08-30 (America/Los_Angeles).

## What was actually executed here

- Python test suite: **45 passed**
- Corpus generation: **50 synthetic coding-memory records / 26 held-out queries**
- Raw deterministic baselines: BM25, TF-IDF cosine, dense LSA, BM25+dense RRF
- Top-k/context-budget sensitivity sweep: BM25, TF-IDF, dense LSA, hybrid RRF at k=1,3,5,8,10; exact returned characters/words recorded
- Verified-feedback learning diagnostic: toy adaptive provider only (harness validation, not a Habitus result)
  - feedback is generated from 5 training-only paraphrases
  - reported learning metrics are measured on 5 distinct held-out procedure queries
- ChatGPT-sidecar protocol smoke test: a blocked benchmark request was answered through the chat/tool loop and resumed successfully
- Real reader-impact trial: **56 queued requests** = 14 deterministic answer cases × 4 offline retrievers
  - GPT-5.6 Sol via ChatGPT sidecar acted only as the reader
  - deterministic harness grading: BM25 **12/14**, TF-IDF **12/14**, dense LSA **14/14**, hybrid RRF **14/14**
  - TF-IDF Q008 repeated a retrieved stale/prohibited deploy command; prohibited-answer rate **1/14 = 0.071**
  - all 56 request/response artifacts are archived under `results/sidecar_reader_trace/` and fingerprint-validated by the offline `replay` backend
- Real vendored/core runs: Habitus, MemBukkit controlled raw architecture, agentmemory controlled retrieval/lifecycle arms, Mem0 controlled search-policy arm, Claude-Mem controlled search-policy arms
- External provider probes: Mem0, agentmemory, MemBukkit, Habitus, Claude-Mem, Hindsight
- External adapter contract/unit tests against current documented API shapes
- Raw Hindsight adapter requires an explicit no-LLM run declaration instead of assuming server configuration
- Hindsight runtime infrastructure proof: preserved pg0 0.15.1 binary successfully started PostgreSQL 18.1 + pgvector 0.8.5 and accepted SQL; official custom OpenAI-compatible embedding seam verified

## What was not executed here

The coding container still has no ordinary outbound GitHub/PyPI network access. Source
for several engines was transferred through the authorized GitHub connector and pinned
by upstream Git blob/commit hashes, allowing real or controlled-core execution for
Habitus, MemBukkit, agentmemory, Mem0, and Claude-Mem. Full service/product deployments for
agentmemory, Mem0, Claude-Mem, and Hindsight have not yet been executed here. Rows that
need unavailable service/model dependencies remain unavailable or explicitly controlled
core arms; **no simulated product result is substituted for a real engine result**.

Claude-Mem is intentionally ineligible for the raw/no-LLM **product** round because its
supported observation ingestion path uses its compression agent; its current rows are
explicit controlled search-policy ablations. Hindsight is eligible for raw mode when
launched with its documented `HINDSIGHT_API_LLM_PROVIDER=none` configuration. Embedded
PostgreSQL has been proven runnable here, but the Hindsight Python service still cannot
be launched because compiled runtime wheels (especially `asyncpg`) cannot currently be
transferred into this container. No Hindsight score is substituted.

## Local baseline snapshot

| Provider | Hit@5 | MRR | All relevant@5 | Prohibited@5 | Useful-before-harmful |
|---|---:|---:|---:|---:|---:|
| BM25 | 0.917 | 0.844 | 0.792 | 0.125 | 0.800 |
| TF-IDF cosine | 0.875 | 0.771 | 0.833 | 0.153 | 0.667 |
| Dense LSA | 0.958 | 0.837 | 0.958 | 0.125 | 0.800 |
| Hybrid RRF | 0.958 | 0.856 | 0.917 | 0.125 | 0.733 |

These numbers validate the harness and establish deliberately strong simple baselines;
they are not the third-party bake-off result.

## Real reader-impact snapshot

| Provider | Reader pass | Required coverage | Prohibited-answer rate |
|---|---:|---:|---:|
| BM25 | 12/14 (0.857) | 0.857 | 0.000 |
| TF-IDF cosine | 12/14 (0.857) | 0.857 | **0.071** |
| Dense LSA | 14/14 (1.000) | 1.000 | 0.000 |
| Hybrid RRF | 14/14 (1.000) | 1.000 | 0.000 |

BM25's two misses were useful diagnostics: Q012 lacked the full three-hop credential
chain and Q016 lacked the verified-success NDJSON procedure. In both cases the reader
abstained with `INSUFFICIENT_MEMORY`. TF-IDF also missed Q016, but Q008 instead surfaced
the obsolete deploy command without its correction and the reader repeated that stale
command; this is why prohibited-answer rate is reported separately from simple pass rate.

## Re-run gates

Before publishing/comparing external-engine results, record exact package commit/version,
embedding model, reranker, LLM/extractor (if any), service configuration, and top-k/token
budget. Product-mode systems that rewrite observations must expose reliable source
provenance back to the benchmark record before their score is considered valid.
