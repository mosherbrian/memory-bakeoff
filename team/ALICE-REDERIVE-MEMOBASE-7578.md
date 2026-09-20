# Second-driver re-derivation — memobase 75.78 / 70.91 from the raw judge fixtures

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated from RD-THREADS §Alice
thread 2; row 17 called memobase's temporal 85.05 "the single highest-value
reproduction target in this batch" · **Cost:** $0 (three pinned fetches + a
local recompute), one turn.

**Why this one is different.** The Mem0 and Zep checks recomputed ratios from
a paper's *summary table*. Memobase ships the thing itself: the per-question
LLM-judge results (`memobase_eval_0710_3000.json`) and the vendor's scoring
script. So this re-derives the headline **from the raw rows**, not from a
summary — the strongest offline check available in the batch.

**Receipts:** `team/row-memobase-receipts/` (`MANIFEST.md` with sha256):
`memobase_eval_0710_3000.json`, `memobase_eval_0503_3000.json`, the vendor's
`generate_scores.py`, and my `recompute-output.txt`. All at pinned commit
`358c16bbc6d687937d79bc2f984a11c3be8da901`.

## Result: exact reproduction (to 4 decimals), both versions

I flattened the 10 conversation lists → 1,540 per-question items, grouped by
`category` (1=single_hop, 2=temporal, 3=multi_hop, 4=open_domain), and took the
mean `llm_score`. Pure Python; no pandas, no reuse of the vendor script.

| Version | single-hop | temporal | multi-hop | open-domain | overall | README/table says |
|---|---|---|---|---|---|---|
| **v0.0.37** (0710 fixture) | **70.92** | **85.05** | **46.88** | **77.17** | **75.78** | 70.92 / 85.05 / 46.88 / 77.17 / **75.78** — ✓ exact |
| **v0.0.32** (0503 fixture) | **63.83** | **80.37** | **52.08** | **71.82** | **70.91** | 63.83 / 80.37 / 52.08 / 71.82 / **70.91** — ✓ exact |

Counts also match the README (282 / 321 / 96 / 841; 1,540 total). Every
per-category and overall number in the vendor table is the mean of the shipped
per-question judge results. L-S15-01's Memobase own-run figures are internally
consistent and exactly reproducible from the raw fixture.

## Findings

1. **Aggregation trap — "overall" is question-weighted, not category-averaged.**
   The overall is the flat mean over all 1,540 questions, and open_domain is
   54.6% of them. The unweighted mean of the four category means is **70.00%**
   (v0.0.37) and **67.03%** (v0.0.32) — versus the advertised **75.78%** /
   **70.91%**. The README's phrase "Calculates overall mean scores across all
   categories" suggests the former; the code does the latter. Anyone who
   averages the four published percentages will be ~5.8 points below the
   vendor's overall and think the table contradicts itself.
2. **This verifies the arithmetic, not the measurement.** The `llm_score` is
   the judge's 0/1 output; the fixture also carries `question`, `answer`, and
   `response`, so re-running the `gpt-4o` judge on a sample is possible — but it
   is LLM spend and was not done. The predicted answers' provenance (that they
   came from the pinned v0.0.37 method) is likewise taken as shipped.
   **Class stays `vendor-only`, upgraded to `vendor-only (arithmetic
   recomputed from shipped raw rows)`** — not `verified-by-us`, because nothing
   was re-measured.
3. **Load-bearing bonus: the same README shows the Mem0-paper Zep copy was
   wrong.** A later block in the pinned README updates the rival table after
   the Zep team disputed it (issue #101): **Zep\* 75.14** overall
   (74.11 / 66.04 / 67.71 / 79.79). The original table lists Zep as
   **65.99 / 49.31**, pasted from Mem0's paper (row 20). So one vendor document
   now carries two Zep numbers differing by ~9 points, and it is the
   Mem0-paper copy that moved. This is a concrete, in-document instance of the
   register's "Zep, not comparable / duplicate" row — and it is evidence that
   the Mem0 paper's rival block is stale, not just borrowed.
4. **Why this matters for the supernode.** Row 20's finding was that Mem0's
   paper is the single origin of five rival numbers. Memobase's own update is
   the first independent signal that one of them (Zep) is wrong by a wide
   margin. The other four — langmem 58.10, openai 52.90, mem0 66.88/68.44 —
   still have exactly one measurement behind them.

## What would move L-S15-01

- Already done here: the aggregation is independently reproduced. The remaining
  gap is the judge and the predicted answers.
- To reach substantive `verified-by-us`: either (a) re-run the pinned v0.0.37
  method end-to-end under our reader/judge, or (b) re-judge a random sample of
  the shipped `response`/`answer` pairs with the same `gpt-4o` judge and check
  the sample mean against the fixture's — a bounded, metered check.

## Method and limits

- Fetched the three files at the ledger's pin; flattened and averaged with a
  ~15-line Python script; did not execute the vendor's `generate_scores.py`
  (it needs pandas) or reuse its output. My recompute and the README's printed
  output agree to 4 decimals, which cross-validates both.
- `_3000` in the filenames is not the question count (there are 1,540); I did
  not investigate what the 3000 refers to.
- No benchmark, engine, or LLM was run; no new measurement exists. This is
  arithmetic reproduction from the vendor's own raw artifact.
