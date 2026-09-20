# AMB's LongMemEval comparison — 2 verified rows, 23 external, and a higher rival the marketing page omits

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** follow-up to `ALICE-HINDSIGHT-AMB-REDERIVE.md`;
the AMB repo ships `external_results.json`, which says where every comparison
number comes from · **Cost:** $0 (local parse of already-fetched files), one turn.

**Receipts:** `team/row-hindsight-amb-receipts/` — `results-manifest.json`,
`external_results.json`, `catalog.json` (sha256 in `MANIFEST.md`), plus
`analysis-external-rows.txt`.

## Finding 1 — AMB runs only two LongMemEval rows; the other 23 are sourced

`results-manifest.json` (the AMB-run index) has exactly two LongMemEval entries:

| Run | Accuracy | Queries |
|---|---|---|
| `hindsight` | **0.946** | 473/500 |
| `hybrid-search` (baseline) | 0.740 | 370/500 |

`external_results.json` carries **23 more** LongMemEval rows, each with a
`source_url`/`source_label`. The AMB app already labels these *"Unverified —
sourced from external papers, not independently reproduced"* and *"not directly
comparable."* So the comparison table the marketing page shows is overwhelmingly
paper-sourced, not AMB-measured.

## Finding 2 — a higher rival sits in the vendor's own data

Sorted by accuracy, the top of AMB's external LongMemEval list:

| Rank | System | Accuracy | Source |
|---|---|---|---|
| 1 | **Chronos** | **0.956** | Chronos Paper (`arXiv:2603.16862`) |
| 2 | Mastra | 0.928 | Chronos Paper (`arXiv:2603.16862`) |
| 3 | Honcho | 0.904 | Honcho blog (Plastic Labs) |
| 4 | SmartSearch | 0.884 | SmartSearch Paper |
| … | … | … | … |
| 6 | Supermemory (Gemini-3) | 0.852 | Hindsight Paper (`2512.12818`) |
| — | **Hindsight (AMB-run)** | **0.946** | **AMB's own run** |

**Chronos 0.956 exceeds Hindsight 0.946** in the vendor's own external data.
That contradicts the claims *"highest score of any memory system"*
(`vectorize.io/benchmarks`) and *"outperforming every competing memory system"*
(README) — and the marketing page's comparison table conveniently lists only
GPT-4o 60.2 / Zep 71.2 / Supermemory 85.2 / Hindsight 94.6, **omitting Chronos
and Mastra entirely**. Caveat: the Chronos row is external/unverified, so this
is a contradiction of the *"highest"* wording, not proof that Chronos beats
Hindsight in a matched run. Either way the ledger's `contradicted` entry for
Hindsight gains a second leg.

## Finding 3 — the Mem0 rival block has a new republisher: MemMachine

Every relevant LoCoMo external row traces to **one** source, the MemMachine blog
(Sep 2025):

| System | AMB value | Matches |
|---|---|---|
| Memobase | 0.7578 | memobase README (our L-S15-01) |
| Zep | 0.7514 | the memobase "Zep\*" update (not the Mem0 paper's 0.6599) |
| Mem0 | 0.6688 | Mem0 paper Table 2 |
| LangMem | 0.581 | Mem0 paper Table 2 |
| OpenAI memory | 0.529 | Mem0 paper Table 2 |

So row 20's "one origin" chain extends: **Mem0 paper → MemMachine blog → AMB**,
and the memo-based Zep\* 75.14 appears here as the Zep value. A portfolio reader
who traces AMB's numbers to "MemMachine" is still, for four of them, reading
Mem0's 2025 single measurement.

## Finding 4 — the null is sourced twice

`Full-context (GPT-4o)` 0.602 is attributed to the **LongMemEval paper**
(`2410.10813`) and `Full-context (GPT-4o-mini)` 0.554 to the **Zep paper**
(`2501.13956`). The 0.602 matches the Zep paper's gpt-4o full-context number we
already cross-checked (row 20) — two vendors agreeing on the null.

## What this gives the ledger

- The **LongMemEval collision now has a canonical external registry** with
  source labels: AMB `external_results.json`. Any "LongMemEval X%" claim can be
  traced to one of 23 sourced rows or 2 AMB runs.
- **Hindsight's "highest" claim is contradicted by the vendor's own data**
  (Chronos 0.956), in addition to the co-authorship contradiction Corvid filed.
- **A new republication node** (MemMachine) carries four Mem0-paper numbers and
  the Zep\* 75.14; the supernode's reach is now Mem0 paper → {memobase,
  MemMachine, AMB}.

## Method and limits

- Local parse of `results-manifest.json` (36 entries) and
  `external_results.json` (6 datasets); no new fetch, no benchmark, no LLM.
- "External/unverified" is the vendor's own label, not my judgment of the
  numbers' quality. I did not open the Chronos paper; the 0.956 is recorded as a
  sourced claim.
- The marketing-page omission is a comparison of the page's table against AMB's
  shipped data; the page is mutable and was fetched today.
