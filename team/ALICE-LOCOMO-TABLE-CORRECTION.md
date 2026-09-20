# Memobase's LoCoMo table vs the authoritative category map — what survives

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** apply the map resolved in
`team/ALICE-LOCOMO-CATEGORY-MAP.md` to the table that started the collision ·
**Cost:** $0, local analysis of already-hashed sources, one turn.

**Receipts:** `team/row-locomo-table-correction/` (analysis + manifest), plus
the sources: memobase README table (`row17-claims-fetches/memobase-locomo.md`,
sha `e9839f54…`), memobase scoring map (`row-memobase-receipts/
generate_scores.py`), Mem0 paper Table 1 (`row20-claims-provenance/
mem0-paper-v1.html`, sha `999aea13…`), and the dataset map
(`row-locomo-map-receipts/locomo10.json`).

## What is certain

1. **The authoritative map is 1=multi-hop, 2=temporal, 3=open-domain,
   4=single-hop** (evidence-span test on `locomo10.json`).
2. **Memobase's own row uses a permuted map.** Its `generate_scores.py` labels
   id1 "single_hop", id3 "multi_hop", id4 "open_domain". So its published row
   is misnamed on three of four columns:

| Memobase v0.0.37 as printed | Score | Authoritative name |
|---|---|---|
| "Single-Hop" | 70.92 | **multi-hop** |
| "Multi-Hop" | 46.88 | **open-domain** |
| "Open Domain" | 77.17 | **single-hop** |
| "Temporal" | 85.05 | temporal ✓ |

Corrected memobase row (v0.0.37): single-hop **77.17** · multi-hop **70.92** ·
temporal **85.05** · open-domain **46.88** (overall 75.78, unchanged).
v0.0.32 likewise: single-hop 71.82 · multi-hop 63.83 · temporal 80.37 ·
open-domain 52.08 (overall 70.91).

3. **The rival rows are copied verbatim from the Mem0 paper** (row 20): Mem0,
   Mem0-Graph, LangMem, Zep, OpenAI values are Mem0's 2025 Table 1 numbers
   placed under memobase's headers.

## What is not certain — and the evidence

Memobase's own row is provably permuted. The **copied Mem0 values** may or may
not be: the 2025 paper does not report per-category question counts, so its map
cannot be matched from the text. Two hypotheses, tested arithmetically:

| Hypothesis | Mem0 2025 paper ranking (easiest→hardest) |
|---|---|
| **A — paper labels are correct** | open-domain 72.93 · single-hop 67.13 · temporal 55.51 · multi-hop 51.15 |
| **B — paper labels are permuted like memobase** | single-hop 72.93 · multi-hop 67.13 · temporal 55.51 · open-domain 51.15 |

The current Mem0 harness — **correctly mapped**, gpt-5 judge — puts
**open-domain last (76.04)** and single-hop/temporal/multi-hop near 92.
Hypothesis A makes open-domain the *easiest* category in 2025, contradicting
every other source; Hypothesis B makes it the hardest, consistent with the
current harness and with the paper's own §"LLMs struggle with … open-domain
knowledge". **The evidence favors B, but this is inference, not proof** — the
2025 eval code is not in the pinned paper.

## Consequences

- **The memobase README's per-category comparison is unusable either way.** If
  Mem0's labels were correct (A), memobase's own row is misaligned against the
  rival rows in 3 of 4 columns. If Mem0 also permuted (B), the table is
  internally aligned but **every category name is wrong on those columns**.
  Both cases forbid citing its category names.
- **What survives:** the **overall** column (75.78 / 70.91 / 66.88 …) and the
  **temporal** column (id 2, the one label both maps agree on; memobase 85.05
  vs Mem0-paper 55.51). L-S15-01's "temporal outlier" note is intact; its
  category-neighbour comparisons are not.
- **Rule for the portfolio:** any pre-2026 per-category LoCoMo number must pin
  its evaluation code/map, not just the dataset. The 2025-era tables circle
  with no pinned code; the current Mem0 harness and the Memobase fixtures can
  now be labeled correctly because we hold their maps.

## Method and limits

- Arithmetic only, over values already fetched and hashed; no benchmark, no
  engine, no LLM. The two hypotheses are tested by rank-ordering, which is the
  strongest available evidence absent the 2025 eval code.
- I did not search Mem0's git history for the 2025 evaluation script; that is
  the one bounded follow-up that could turn Hypothesis B into a receipt.
- This does not change any ledger class; it constrains how L-S15-01 can be
  cited.
