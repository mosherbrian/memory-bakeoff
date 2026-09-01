# Hindsight v0.9.2 local raw-mode smoke (generation 3)

This is a **non-scored service and provenance smoke**, not a benchmark result. It
used four existing synthetic harness records only (`M023`--`M026`), did not run a
benchmark query set or reader evaluation, and does not amend any archived result
directory.

## Environment and configuration

- Host: macOS on Apple Silicon (`arm64`); Python 3.13 virtual environment.
- Hindsight packages: `hindsight-api-slim==0.9.2`,
  `hindsight-client==0.9.2`, and `hindsight-embed==0.9.2`.
- Embedded database: `pg0-embedded==0.15.1`, `asyncpg==0.31.0`, using the named
  local instance `pg0://memory-bakeoff-gen3-smoke`.
- Raw ingestion: `HINDSIGHT_API_LLM_PROVIDER=none` and the harness-side explicit
  declaration `HINDSIGHT_RAW_LLM_PROVIDER=none`. No external or paid LLM was
  configured.
- Embeddings: Hindsight's supported `onnx` provider, not the package default
  local sentence-transformer provider. Model: `intfloat/multilingual-e5-small`,
  snapshot revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`; 384 dimensions,
  mean pooling, normalized vectors, 512-token limit, and `query: `/`passage: `
  prefixes. Runtime: `onnxruntime==1.29.0`, `transformers==5.15.1`,
  `tokenizers==0.22.2`.
- Reranker: `rrf` passthrough, rather than the package-default learned local
  cross-encoder. Hindsight v0.9.2 accepts `rrf`; despite an upstream config hint,
  `HINDSIGHT_API_RERANKER_PROVIDER=none` raises `ValueError: Unknown reranker
  provider: none`.

These deviations are intentional and must be retained in any comparison: the
smoke validates a real upstream Hindsight service in a no-LLM configuration, not
the normal learned-reranker product configuration.

## Service and retrieval observations

The API started at `127.0.0.1:8891`, passed `/health/ready`, then shut down cleanly.
It was restarted against the same named embedded database without re-ingestion;
the recall result still contained `M023`, `M024`, `M026`, and `M025`.

For the intentionally non-scored query, “Which workflow prevents stale generated
Go code from failing regeneration checks?”, the first native `RecallResult` was
`M023`. The object included `document_id='M023'`,
`metadata.record_id='M023'`, and a native chunk identifier. The same response
contained `M024`, the semantic negative/procedural distractor, so this smoke does
not imply safety or benchmark performance.

The generation-2 Hindsight adapter was exercised against this real object-shaped
client response. It returned `['M023', 'M024', 'M026', 'M025']`; its provenance
report was `status=verified`, `publishable=true`, and `methods={'native': 4}`.
Thus it used native source identifiers rather than fuzzy or subtext matching.

## Active arms in this configuration

Runtime startup identified `pgvector (vector)` and `native (text)` extensions.
The returned scores showed non-null `semantic` and `keyword` components, while
`reranker` was null, consistent with the configured RRF passthrough. Source
configuration declares the recall strategies `semantic`, `bm25`, `graph`, and
`temporal`, with graph retriever `link_expansion`; the raw/no-LLM retain path did
not produce source facts in this smoke, so graph and temporal behavior was not
validated here. No learned cross-encoder or LLM extraction arm was active.

## Scope boundary

No authoritative result, leaderboard entry, product score, or reader score was
produced. The long-term Claude Code transcript corpus was not inspected or
ingested. Local pg0 state, model cache, logs, and transient session artifacts are
outside the repository and untracked.
