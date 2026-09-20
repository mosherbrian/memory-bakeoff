# Assay second-driver — baseline real reader trace

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~22:0x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations
**Target:** the protected baseline finding (AGENTS.md §"Existing findings to
protect"; `results/READER_FINDINGS.md`): BM25 12/14, TF-IDF 12/14 with one
prohibited stale answer, dense LSA 14/14, hybrid RRF 14/14.

## Method

Recomputed per-provider pass / prohibited / insufficient counts from the **56
per-case records** in `results/reader.json` (14 cases × 4 providers), compared
them to `results/reader_summary.csv`, and checked the sidecar request/response
trace ids.

## Result — AGREE

| Provider | passed | prohibited | insufficient | summary |
|---|---|---|---|---|
| bm25 | **12/14** | 0 | Q012, Q016, Q025, Q026 (4) | matches |
| tfidf_cosine | **12/14** | **Q008 (1)** | Q016, Q025, Q026 (3) | matches |
| dense_lsa | **14/14** | 0 | Q025, Q026 (2) | matches |
| hybrid_rrf | **14/14** | 0 | Q025, Q026 (2) | matches |

- Total prohibited = **1**, and it is TF-IDF's **Q008** — the obsolete deploy
  command, exactly the stale-answer shape `READER_FINDINGS.md` describes.
- Sidecar trace: **56 requests / 56 responses**, and the trace request-id set
  equals the per-case `request_id` set exactly.
- All four recomputed rates agree with `reader_summary.csv` to 1e-9.

## Limit

- This confirms the stored trace's counts and its linkage to the archived sidecar
  envelopes. It does not re-run the `replay` LLM backend through the providers
  (the sidecar trace README's "full replay reproduces exactly" is Stratum's/its
  author's claim, not re-executed here).

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/reader_trace_rederive.py`
  sha256 `eaf642c4fbbf1bbca1d2069cf653076c76fc53ad378b50bc128dda0f83ba8336`
- Result: `.../sealed-reader-trace-rederive-20260912/result.json`
  sha256 `0fbcb6004df0e69ced4b19efe78ddabe5a8ad9d93fc42b3dfce25c7c85013603`
- Re-run: `python3 scripts/verify-20260912-assay-row1/reader_trace_rederive.py`

— **Assay** (worker-glm-dsh2).
