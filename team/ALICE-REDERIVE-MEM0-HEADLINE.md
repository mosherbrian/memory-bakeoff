# Second-driver re-derivation — the Mem0 paper's headline arithmetic

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** RD-THREADS §Alice thread 2 (re-derive one
load-bearing number per session) · **Cost:** $0 (local parse of an already-hashed
fetch), one turn.

**Why this number.** QUEUE row 20 found that arXiv `2504.19413v1` (the Mem0
paper, 2025-04-28, Table 2) is the **single origin** of five numbers the
ecosystem cites as independent (langmem 58.10 · zep 65.99 · openai 52.90 ·
mem0 66.88 · mem0-graph 68.44). A supernode that load-bearing deserves the
second-driver check: do its own headline ratios reproduce from its own tables?

**Receipt.** `team/row20-claims-provenance/mem0-paper-v1.html`, 244,706 bytes,
sha256 `999aea13b219b6fc761cbb517df11dda2c8d9ae0ebf7cdd9b7c0482777005436`.
Tables 1 and 2 parsed from the arXiv HTML full text (no model in the loop).

## Re-derivation table

| # | Paper's claim | Arithmetic from the paper's tables | Re-derived | Verdict |
|---|---|---|---|---|
| 1 | Mem0 **26%** relative improvement over OpenAI (J) | (66.88 − 52.90) / 52.90 | **26.43%** | ✓ (truncated to 26) |
| 2 | Mem0ᵍ **~2%** higher overall than base Mem0 | (68.44 − 66.88) / 66.88 | **2.33%** | ✓ |
| 3 | Mem0 **~10%** over strongest RAG | best RAG J = 60.97 (chunk 256); (66.88 − 60.97) / 60.97 | **9.69%** | ✓ |
| 4 | Mem0ᵍ **~12%** over strongest RAG | (68.44 − 60.97) / 60.97 | **12.25%** | ✓ |
| 5 | **5%** single-hop over best other | Mem0 67.13 vs OpenAI 63.79; (67.13 − 63.79) / 63.79 | **5.24%** | ✓ |
| 6 | **11%** temporal over best other | Mem0 55.51 vs A-Mem\* 49.91; (55.51 − 49.91) / 49.91 | **11.22%** | ✓ |
| 7 | **7%** multi-hop over best other | Mem0 51.15 vs LangMem 47.92; (51.15 − 47.92) / 47.92 | **6.74%** | ✓ |
| 8 | **91%** lower p95 latency vs full-context | (17.117 − 1.440) / 17.117 = **91.59%**; Mem0ᵍ (17.117 − 2.590)/17.117 = **84.87%** | 91.59% / 84.87% | ✓, but see note A |
| 9 | saves **more than 90%** token cost | Table 2 Tok: (26031 − 1764)/26031 = **93.22%**; §4.5 store size: 7k vs 26k ≈ **73%** | 93.22% or ~73% | ✓ only on the Table-2 column; see note B |

Values used (parsed verbatim): Table 2 — Full-context `26031 · p95 17.117 ·
J 72.90`; Mem0 `1764 · 1.440 · 66.88`; Mem0ᵍ `3616 · 2.590 · 68.44`; RAG best
`60.97`. Table 1 (J per category) — Mem0 `67.13 / 51.15 / 72.93 / 55.51`;
best other single-hop OpenAI `63.79`; best other temporal A-Mem\* `49.91`;
best other multi-hop LangMem `47.92`.

## Findings

1. **All seven accuracy ratios reproduce.** Every percentage in the abstract
   and conclusion is the paper's own tables, correctly computed. Nothing in the
   headline set is fabricated or copied from elsewhere — for the numbers it
   originates, the Mem0 paper is internally consistent.
2. **Note A — the same latency figure is 91% and 92% in one paper.** The
   abstract says "91% lower p95 latency"; §4.2 says "around 1.44 seconds (a 92%
   reduction)". The arithmetic is 91.59%, so the abstract truncates and the body
   rounds. Harmless, but a downstream citer can quote either, and "91%" vs
   "92%" will look like two different measurements. Pick the body's 92% or cite
   the raw ratio.
3. **Note B — "more than 90% token cost" depends on which token column you
   mean.** Table 2's Tok column is per-query retrieval cost (1,764 vs 26,031 →
   93.2%). §4.5's token analysis is *store size* (Mem0 "only 7k tokens per
   conversation" vs full-context "roughly 26k" → ~73%). Both are real and
   different quantities; the abstract's ">90%" holds only for the per-query
   column. Any portfolio comparison against Mem0's token claim must name the
   column.
4. **The temporal comparator is A-Mem\*, not Zep.** The 11% only reproduces
   against A-Mem\*'s 49.91 (the best non-Mem0 temporal J in Table 1), not
   against Zep's 49.31 (12.57%) or the graph variant (17.89%). The paper never
   names the comparator, so a re-deriver must test all candidates — the first
   plausible pick (Zep, the better-known rival) gives the wrong number.
5. **What this is not.** Arithmetic consistency is not replication. This says
   the paper's percentages match its tables; it says nothing about whether the
   tables are correct. Rows L-S13-02 and L-S15-01 remain `vendor-only`; the
   supernode still has exactly one upstream measurement (row 20).

## Method and limits

- Parsed the arXiv HTML full text with regex; no PDF, no model. Table 1's
  Mem0ᵍ open-domain/temporal cells were read from the surrounding text (75.71 /
  58.13); the trailing table was truncated in the HTML render and those two
  values were confirmed from a second context window of the same file.
- "Best performing method" per category is *inferred* from Table 1 (the highest
  non-Mem0 J), not stated by the paper. That inference is what makes finding 4
  a flag rather than a defect.
- No benchmark was run; no external source consulted. One artifact, one turn.
