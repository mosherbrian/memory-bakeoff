# MemOS: self-reported vs the only independent academic measurement — a ~16–20 point gap on both benchmarks

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** follow-up to `ALICE-TIMEM-SOURCE-CHECK.md`;
the same TiMem paper also measures MemOS on LoCoMo, completing a
both-benchmarks comparison · **Cost:** $0 (synthesis of already-hashed
receipts), one turn.

**Receipts:** MemOS self-report — `team/row17-claims-fetches/memos-README.md`
(sha `9c2ec97b…`) and `row20-claims-provenance/memos-40f8e832.md` (the
first-appearance commit); independent measurement — `team/row-timem-receipts/`
(`arXiv:2601.02845`).

## The two sides

| Benchmark | MemOS self-report (vendor) | Independent (TiMem, `2601.02845`) | Gap |
|---|---|---|---|
| LoCoMo overall | **88.83** (README, OmniMemEval) | **69.24** (Table 1; GPT-4o-mini, official LoCoMo protocol) | **−19.6** |
| LongMemEval-S | **89.20** (README, OmniMemEval) | **73.07** GPT-4o / **68.68** GPT-4o-mini (Table 2; official template) | **−16.1 / −20.5** |

TiMem's run uses `gpt-4o-mini-2024-07-18` generation, `Qwen3-Embedding-0.6B`,
recall budget `k=20`, and LongMemEval's official QA/LLJ prompts (LoCoMo judged
with "Mem0's evaluation prompt template"). Its MemOS LoCoMo row is 76.07
single-hop / 69.47 temporal / 45.14 open-domain / 56.85 multi-hop / **69.24
overall**.

## Why this is stronger than a single number collision

1. **The self-reported numbers are not in MemOS's own paper.** Row 20 found the
   abstract and body of `2507.03724` v1–v4 contain neither 88.83 nor
   OmniMemEval; they first appear in the **README** on 2026-07-09
   (`40f8e832`). So the claim has no paper receipt.
2. **The self-reported numbers were internally inconsistent at birth.** That
   first-appearance README carried prose **92.34 / 93.40** against its own table
   **88.83 / 89.20** (row 17 §PROVENANCE). The prose was later edited to match
   the table.
3. **The metric/judge is unpinned on the vendor side** (OmniMemEval; judge and
   answer model absent from the fetch), while the independent side follows the
   official template.
4. **The gap is consistent across both benchmarks and both answer models**
   (roughly −16 to −20 points). A single-benchmark miss could be a protocol
   difference; the same direction and magnitude on two benchmarks is a pattern.

## What it does and does not establish

- **Establishes:** on the only third-party academic measurement we hold, MemOS
  scores ~16–20 points below its self-report on LoCoMo and LongMemEval; and its
  self-report has no paper receipt and was self-conflicting at first appearance.
- **Does not establish:** that the vendor number is false. OmniMemEval may use a
  more generous protocol, and TiMem is one run by one group. This is not our own
  receipt, so L-S16-02 does not become `contradicted` — it becomes
  `vendor-only` with a **large `cross-vendor-measured` gap on both benchmarks**.
- **Portfolio consequence:** MemOS (charter S-16) should not be ranked on its
  claimed numbers; if it is run, do it under the frozen harness with the metric,
  judge, and category map pinned — which is also the only way to settle whether
  the gap is protocol or inflation.

## Method and limits

- Arithmetic only, over values already fetched and hashed in this session; no
  benchmark, engine, or LLM run. The TiMem table is quoted from its HTML full
  text; the MemOS self-numbers from the pinned README.
- I did not examine OmniMemEval's code or metric, which is the missing piece
  that would make the comparison strict. That is the bounded next step if the
  portfolio needs MemOS adjudicated rather than flagged.
