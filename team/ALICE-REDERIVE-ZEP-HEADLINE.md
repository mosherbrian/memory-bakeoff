# Second-driver re-derivation — the Zep paper's headline arithmetic

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated from RD-THREADS §Alice
thread 2 (the Zep paper is the other named origin in the 16-source batch, after
Mem0) · **Cost:** $0, local parse of an already-hashed fetch, one turn.

**Why.** Row 20 traced L-S17-01/02 to arXiv `2501.13956v1` (2025-01-20) and the
Zep blog (2025-01-22, identical text). Same second-driver question as the Mem0
check: do the paper's headline ratios reproduce from its own tables?

**Receipt.** `team/row20-claims-provenance/zep-paper-v1.html`, sha256
`8a16259db129b4109331df4aa17c404115eceb1d7f2df40d06bc34def7c27049`. Tables 1–3
parsed from the arXiv HTML full text. No model, no benchmark.

## Re-derivation table

| # | Paper's claim | Printed table values | Re-derived | Verdict |
|---|---|---|---|---|
| 1 | DMR: Zep beats MemGPT, **94.8% vs 93.4%** | Table 1: Zep 94.8 · MemGPT 93.4 · **full-conversation 94.4** (gpt-4-turbo) | +1.4 pts · **+1.50%** vs MemGPT; **+0.4 pts · +0.42%** vs full-conversation | reproduces as printed, but see F1 |
| 2 | DMR (gpt-4o-mini) 98.2% | Table 1: Zep 98.2 · full-conversation 98.0 | **+0.2 pts · +0.20%** | marginal, correctly described only in the body |
| 3 | LongMemEval-S "**15.2%** accuracy improvement" (gpt-4o-mini) | Table 2: 55.4% → 63.8% | (63.8−55.4)/55.4 = **15.16%** | ✓ (rounds to 15.2) |
| 4 | LongMemEval-S "**18.5%** improvement" (gpt-4o) | Table 2: 60.2% → 71.2% | (71.2−60.2)/60.2 = **18.27%** | ✗ from printed values — see F2 |
| 5 | "reducing response latency by **90%**" | Table 2 latency: full 31.3 s → 3.20 s (mini); 28.9 s → 2.58 s (4o) | mini **89.8%**, 4o **91.1%** | ✓ but the abstract pairs it with the *other* model — see F3 |
| 6 | (not in abstract) context-token reduction | Table 2: 115k → 1.6k | **98.6%** reduction | ✓; unclaimed in the abstract |

Table 3 (question-type breakdown) delta column also arithmetic-checked: every
printed delta reproduces from its two scores — but with an inconsistent
denominator (F4).

## Findings

1. **The abstract is stronger than the paper's own body.** The abstract says
   Zep "outperforms the current state-of-the-art system, MemGPT, in the Deep
   Memory Retrieval (DMR) benchmark" and quotes "94.8% vs 93.4%". Zep's **own
   full-conversation baseline** is **94.4%** (gpt-4-turbo) and **98.0%**
   (gpt-4o-mini), so the real margins over the simplest baseline are **+0.4 and
   +0.2 points**. The body says so plainly — "showing marginal improvements over
   both MemGPT and the respective full-conversation baselines" — and also calls
   DMR less representative (60 messages per conversation). This sharpens
   L-S17-01's interest note: not just a 1.4-point margin, but a **0.4-point
   margin over full-context**, the exact null the portfolio runs (E-1).
2. **The 18.5% does not reproduce from the printed table.** Using the printed
   one-decimal values gives **18.27%** (rounds to 18.3%). 18.5% requires the
   underlying scores to sit at the favorable edge of their rounding intervals
   (e.g. 71.25 vs 60.15 → 18.45%). The analogous 15.2% *does* reproduce
   exactly (15.16%), so the asymmetry is not a general formatting effect.
   Reported as a minor not-reproduced-from-print figure, not proof of error.
3. **The abstract blends two model variants in one sentence.** "accuracy
   improvements of up to 18.5% while simultaneously reducing response latency by
   90%" pairs the **gpt-4o** accuracy (18.5%) with the **gpt-4o-mini** latency
   reduction (89.8%); the gpt-4o latency reduction is **91.1%**. Both round near
   90%, so no number is false, but a reader cannot reconstruct which model each
   belongs to.
4. **Table 3's delta column uses two denominators.** Increases are
   relative-to-full-context (e.g. 30.0→53.3 prints 77.7% = /30.0); decreases are
   relative-to-Zep (e.g. 81.8→75.0 prints 9.06% = /75.0, not 8.31% = /81.8).
   Each row is internally correct, but summing or averaging the column mixes
   bases — worth knowing before anyone quotes a "delta" from it.
5. **What this is not.** Arithmetic consistency is not replication. L-S17-01/02
   remain `vendor-only`; Zep is parked, and the paper is the sole origin of
   both claims. No engine was run.

## Method and limits

- Parsed the arXiv HTML full text (Tables 1–3) with regex; recomputed each
  ratio in Python. No PDF, no model.
- "Not reproduced" is bounded by one-decimal printing; I state the rounding
  interval rather than assert an error. The one value I cannot distinguish
  (18.5% vs 18.27%) is flagged as such.
- The DMR/LongMemEval comparisons are the paper's own baselines; I did not
  re-run either benchmark or check the MemGPT 93.4% attribution (worth a
  separate probe: the MemGPT paper itself reports no DMR score in its abstract).
