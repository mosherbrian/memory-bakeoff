# Assay second-driver — Claude-Mem controlled 90-day window ablation

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~22:1x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations
**Target:** the protected finding (AGENTS.md §"Existing findings to protect";
`research/CLAUDE_MEM_FINDINGS.md`): the implicit 90-day recency filter drops
Claude-Mem controlled Hit@5 to **0.208**; disabling it restores the dense-LSA
result (core **0.958**, stress **0.583** Hit@5 / **0.542** all-relevant@5).

## Method

Recomputed every arm from the 26 per-case rows in
`results/claude_mem_compare_{core,stress450}/detail.csv`, using the harness's own
aggregation convention (`metrics.aggregate` excludes `category == "negative"`,
so 24 scored positives), and compared to `summary.csv` and the doc table.

## Result — AGREE

| Arm | core Hit@5 | stress Hit@5 | stress all-relevant@5 |
|---|---|---|---|
| `claude_mem_chroma_lsa` (default window) | **0.2083** | **0.2083** | 0.2083 |
| `claude_mem_chroma_lsa_no_recency` | **0.9583** | **0.5833** | **0.5417** |
| `dense_lsa` | **0.9583** | **0.5833** | **0.5417** |

All six arm values match `summary.csv` and the doc to 1e-9. The window arm loses
~0.75 Hit@5 on both corpora; removing the window recovers it exactly at the
metric level.

## Nuance worth recording (causal-claim precision)

"No-recency has the same retrieval representation and top-5 recall as dense-LSA"
is true **at the metric level**, not per case: the two arms' scored positives are
identical on `hit_at_k`/`all_relevant_at_k`, but their **retrieved id sets differ
on 1 core case (Q026, a negative case excluded from scoring) and 18 of 26 stress
cases**. The shared representation does not imply byte-identical top-5 lists;
k=5 metrics happen to agree. Stated so a future reader does not expect identical
ids.

## Limit

- Controlled-core policy ablation, not a Claude-Mem product run (the doc says so).
  The FTS5 phrase arm (0.000) was not independently re-derived here.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/claude_mem_window_rederive.py`
  sha256 `5af2e6ba79eed7d7db5c0bfd61b84d12fcb162e500d984304793c709eb8952fc`
- Result: `.../sealed-claude-mem-window-rederive-20260912/result.json`
  sha256 `6b9ee37ece97a29ac5710ae529cdf75a569c28275f00bf2a31a88a77d24c3da4`
- Re-run: `python3 scripts/verify-20260912-assay-row1/claude_mem_window_rederive.py`

— **Assay** (worker-glm-dsh2).
