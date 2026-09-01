# Matched Hindsight learned-reranker raw-product summary

Configuration: Hindsight 0.9.2, raw/no-LLM, pinned E5-small ONNX, local CPU `cross-encoder/ms-marco-MiniLM-L-6-v2`, Homebrew PostgreSQL 17.11 + pgvector 0.8.6, top-k 5. Three fresh repetitions per corpus were identical.

| Metric | Core (50) | Stress (500) |
|---|---:|---:|
| Hit@5 / all-relevant@5 / MRR | 1.000 / 1.000 / 0.931 | 0.833 / 0.708 / 0.812 |
| Prohibited@5 / harmful presence / mean count | 0.142 / 0.667 / 0.708 | 0.083 / 0.417 / 0.417 |
| Useful-before-harmful / negative-empty | 0.812 / 0.000 | 0.917 / 0.000 |
| Context chars / latency ms | 437.6 / 387.7 | 534.5 / 1082.5 |

The RRF-only external stress diagnostic remains separate (mean Hit@5 0.208). Native trace mapped all 29 relevant targets into retrieval arms, fused candidates, and final ranked results. Hindsight’s trace `final_rrf_rank` is the position after its candidate/fusion pipeline, not a guarantee that two arm-local rank-1 chunks aggregate to document rank 1: chunk/node-level candidates, cross-source graph candidates, deduplication/hydration, candidate capping, and the subsequent combined-score/final-order stage intervene. Thus the rank-1/rank-1 anomaly does not show absent candidates; it is consistent with downstream node/document aggregation and final ordering. The learned cross-encoder restores useful rank but increases harmful exposure versus RRF.
