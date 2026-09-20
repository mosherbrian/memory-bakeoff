# Second-driver re-derivation — agentmemory LongMemEval (R@5 95.2 / R@10 98.6 / MRR 88.2)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated from RD-THREADS §Alice
thread 2; L-LME-01 (Corvid's audit) is `vendor-only` and the repo ships its raw
per-question results · **Cost:** $0, five pinned fetches + a local recompute,
one turn.

**Why.** agentmemory advertises LongMemEval-S **R@5 95.2 / R@10 98.6 / R@20 99.4
/ NDCG@10 87.9 / MRR 88.2** (`benchmark/LONGMEMEVAL.md`), and Corvid's audit
classified it `vendor-only` with metric `recall_any@K`, no LLM. The repo ships
`benchmark/data/longmemeval_results_{hybrid,bm25}.json` containing ranked
retrieved session ids and gold ids per question — so the metrics can be
re-derived rather than trusted.

**Receipts:** `team/row-agentmem-receipts/` (`MANIFEST.md` with sha256), at pin
`e04ba88819c365c9acf9d6661ea802143e728bd6`: both raw result files, the claim
doc, the bench script, and `eval/runner/score.ts` (the metric definitions), plus
my `recompute-output.txt`.

## Result — three metrics reproduce, two are not re-derivable

I recomputed each metric directly from `retrieved_session_ids` /
`gold_session_ids` (binary relevance; `recall_any@K` = any gold in top-K; MRR =
mean reciprocal rank of first gold; NDCG@10 with binary gains), independent of
the stored summary fields.

| Metric | stated (hybrid) | recomputed | Verdict |
|---|---|---|---|
| R@5 | 0.952 | **0.952000** | ✓ exact |
| R@10 | 0.986 | **0.986000** | ✓ exact |
| NDCG@10 | 0.878588 | **0.878588** | ✓ exact |
| R@20 | 0.994 | 0.986000 | ✗ **not re-derivable — see below** |
| MRR | 0.882143 | 0.881564 (Δ +0.000579) | ✗ **not re-derivable** |

BM25-only is the same shape: R@5 0.862 ✓, R@10 0.946 ✓, NDCG@10 0.730237 ✓;
R@20 0.986 → recomputes to 0.946 ✗; MRR 0.715380 → 0.712525 (Δ +0.002855) ✗.

## Diagnosis: the shipped ranked list is truncated at 10

- `retrieved_session_ids` has **exactly 10 entries for all 500 questions** in
  both files (min = max = 10). The run computed R@20 and MRR against the full
  top-20 list, but only the top 10 were serialized.
- The per-question `recall_any_at_20` and `mrr` fields **do** carry the
  run-time values (their means equal the aggregates exactly: 0.994 / 0.882143),
  so the headline numbers are internally consistent — but the ranks 11–20 that
  produced them are **not in the artifact**, so a third party cannot reproduce
  them.
- The MRR gap is exactly the reciprocal-rank mass of golds first appearing
  beyond rank 10: **7 hybrid questions and 27 bm25 questions have no gold in the
  stored top-10**. R@20 recomputed from the truncated list necessarily equals
  R@10.

## Consequence for L-LME-01

- **R@5, R@10, and NDCG@10 move to `vendor-only (independently recomputed from
  shipped raw rows)`** — the same upgrade the memobase figures got. The
  advertised 95.2 / 98.6 are real and exactly reproducible.
- **R@20 (99.4) and MRR (88.2) remain `vendor-only` (self-attested only)** —
  internally consistent with the per-question fields, but not independently
  re-derivable from the published data. If the portfolio wants them verified,
  the ask is the **untruncated top-20 lists**; otherwise cite only R@5/R@10.
- This also confirms Corvid's metric call: it is `recall_any@K` (retrieval
  recall), and the vendor doc itself says it is "not end-to-end QA accuracy" —
  so it is **not comparable** to MemBukkit's 92.6% judged-QA figure (L-LME-02).
- A naive recompute from the shipped list would have reported R@20 = 98.6 (not
  99.4) and MRR 88.16 (not 88.21) and wrongly called the vendor inflated. The
  truth is **data truncation, not overstatement** — which is why the diagnosis
  matters.

## Method and limits

- Recompute is ~20 lines of Python over the 500 per-question records; the
  vendor's own `eval/runner/score.ts` defines `recall_any@K` as "any gold in
  top-K" through its `hit` flag, and MRR from `topGoldRank` — my formulas match
  that reading.
- No LLM, no judge, no engine run: this reproduces the **retrieval** metric, not
  LongMemEval QA accuracy, which agentmemory explicitly disclaims.
- I did not check how the 500 questions were selected or whether the embeddings
  run used the pinned model; that is a separate provenance question.
