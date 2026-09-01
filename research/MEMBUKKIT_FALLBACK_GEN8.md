# MemBukkit documented-fallback raw-product result

Generation 7 established that the pinned upstream's intended Hugging Face
repositories are unavailable.  This separate, explicitly labeled run uses the
fallback pair defined by that same pinned resolver; it does **not** replace or
invalidate the intended-model availability blocker.

## Identity and execution

- Upstream: `MemseekAI/membukkit` commit
  `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807`, installed editable from a
  separate checkout and selected with `MEMBUKKIT_UPSTREAM_PATH`.
- Experiment class/mode: `raw_product` / `raw`.  Ingestion used upstream
  `MemorySystem.ingest_facts`, one canonical record per atomic fact, with no
  distiller or LLM.
- Encoder: `sentence-transformers/all-mpnet-base-v2` at cached revision
  `e8c3b32edf5434bc2275fc9bab85f82640a19130`.
- Reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2` at cached revision
  `233902d25c440f23af6f7d6e94d2946bac0bee0a`.
- Runtime: macOS 26.5.1 arm64, CPython 3.13.15, `membukkit` 0.1.0,
  `sentence-transformers` 6.0.1, `transformers` 5.15.1, and `torch` 2.13.0
  on CPU.
- Retrieval: in-memory backend; `bucket_mode=topic`, `num_buckets=24`,
  `scan_budget=0.3`, atomic lane only, `select=hybrid` (RRF over cosine and
  cross-encoder ranks), `rerank_cap=50`, `top_k=10`, `k_rrf=60`, and
  `lexical_lane=false`.  Scoring requested the top 5 results.

The clean six-record sentinel loaded both fallback models and returned native
canonical `source_ref` values.  The six scored runs subsequently recorded
native provenance for every returned item (122 returned items per run), so no
fuzzy or text-derived record-ID recovery was used.

## Results

All three repetitions in each condition were identical on relevance and
harmfulness metrics.  The result directories are
`results/membukkit_fallback_gen8_core-r{1,2,3}` and
`results/membukkit_fallback_gen8_stress-r{1,2,3}`.

| Condition | Repetitions | Hit@5 | MRR | All relevant@5 | Prohibited@5 | Useful before harmful | Mean context chars |
|---|---:|---:|---:|---:|---:|---:|---:|
| Core (0 distractors) | 3 | 1.000 | 0.585 | 1.000 | 0.125 | 0.688 | 378.0 |
| Stress (450 distractors) | 3 | 0.875 | 0.553 | 0.750 | 0.067 | 0.692 | 500.9 |

The mean end-to-end retrieval latency was 82.6 ms across the core repetitions
and 397.7 ms across the stress repetitions.  These are documented-fallback
raw-product results only: they must remain distinct from both the controlled
LSA arm and any future run with MemBukkit's unavailable intended pretrained
weights.
