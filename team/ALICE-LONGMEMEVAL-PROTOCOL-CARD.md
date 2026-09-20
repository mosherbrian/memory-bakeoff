# LongMemEval comparability card — group by harness, not by benchmark name

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated capstone from the day's
re-derivations; operationalizes the "de facto protocol" and "14 pp framework
swing" findings · **Cost:** $0 (synthesis of already-hashed receipts), one turn.

**How to use it.** A "LongMemEval score" is only comparable to another with the
**same harness** (data version + prompts + answer model + judge + split). The
model pair alone is *not* sufficient — see Finding 1. Cite the group, or don't
compare.

## The groups

| Harness (answer / judge, split) | Numbers in that harness | Source |
|---|---|---|
| **gpt-4.1-mini / gpt-4o-mini, LongMemEval-S** — OmniMemEval | MemOS **89.20** · Zep 79.80 · Hindsight 72.20 · Supermemory 66.07 · Mem0 56.00 · EverOS 80.40 · Letta 77.67 · mem9 78.00 | OmniMemEval `results.md` (vendor-operated; generic generous judge) |
| **gpt-4.1-mini / gpt-4o-mini, LongMemEval-S** — SmartSearch | SmartSearch **88.4** · Memora 87.4 · EverMemOS 83.0 · MemOS **77.8** · Nemori 74.6 · Mem0 66.4 · full-context 65.6 | SmartSearch paper `arXiv:2603.15599` Table 7 |
| **gpt-4o-mini / official LLJ, LongMemEval-S** — TiMem | TiMem 76.88 · MemOS 68.68 · Mem0 64.96 · MemoryOS 58.04 · A-MEM 55.44 | TiMem paper `arXiv:2601.02845` Table 2 |
| **GPT-4o / official LLJ, LongMemEval-S** — TiMem | TiMem 78.96 · MemOS 73.07 · Mem0 67.56 · A-MEM 63.40 | same, stronger answerer |
| **Gemini 3.1 Pro / Gemini 2.5 Flash Lite** — AMB | Hindsight **94.6** · hybrid-search 74.0 | AMB raw per-question rows |
| **gpt-5 / gpt-5** — current Mem0 harness | Mem0 91.56 (top_200) · 82.66 (top_50) | `mem0ai/memory-benchmarks` |
| **official gpt-4o judge, mixed readers** — MemBukkit's table | MemBukkit 92.6 (gpt-5.4 reader) · Zep 71.2 · Supermemory 85.2 · full-context 60.2 | competitor-published |
| **strong-model configs** | Chronos 95.6 (Claude Opus 4.6) · Mastra 92.8 · Hindsight 91.4 (OSS-120B judge) | Chronos paper Table 2 |
| **no judge — retrieval recall** | agentmemory R@5 95.2 / R@10 98.6 (`recall_any@K`) | agentmemory raw rows |
| **vendor self, harness opaque** | MemOS 89.20 · Mem0 94.4 · Supermemory 95.0 · Zep 90.2/94.7 | vendor pages |

## Finding 1 — the model pair is necessary but not sufficient

**MemOS appears at 89.20 (OmniMemEval) and 77.8 (SmartSearch) under the *same*
`gpt-4.1-mini` answer + `gpt-4o-mini` judge pair** — an 11.4-point gap. So even a
matched model pair does not make two numbers comparable: the **judge prompt and
harness** still move it (OmniMemEval's generic "same topic = CORRECT" rubric vs
SmartSearch's own protocol). `ALICE-OMNIMEMEVAL-JUDGE-CHECK.md`.

## Finding 2 — only within-harness comparisons are safe

- **Within OmniMemEval** (same data/prompts/answerer/judge, one operator): the
  cross-system ordering is meaningful; the operator is MemOS (COI).
- **Within AMB**: Hindsight 94.6 vs its own hybrid-search baseline 74.0.
- **Within a paper's table**: SmartSearch 88.4 vs Memora 87.4 vs EverMemOS 83.0
  (the paper's own matched run).
- **Across groups:** not comparable. The paper that documents the swing says so:
  *"The full-context baseline alone shifts from 77.1% to 91.2% across frameworks
  — a 14 pp swing with no retrieval change"* and reports under two protocols
  separately, *"never compar[ing] numbers across them."*

## Finding 3 — the best available reference protocol

`gpt-4.1-mini` answer + `gpt-4o-mini` judge on LongMemEval-S is now used by
both OmniMemEval and SmartSearch (independent groups). It is the closest thing to
a shared reference — but Finding 1 means the **judge prompt must be pinned too**,
and OmniMemEval's is demonstrably looser than the official LongMemEval rubric.

## Finding 4 — the null is framework-dependent

Full-context LongMemEval numbers in play: 60.2 (LongMemEval paper, official
judge) · 65.6 (SmartSearch) · 55.4 (Zep paper mini) · 60.2 (Zep paper 4o) ·
77.1–91.2 (across frameworks). Any portfolio E-1 claim must name its harness.

## What to cite

1. A number **with** its group (harness) — never "LongMemEval 94.6" alone.
2. For cross-system claims, prefer a single matched table (OmniMemEval or a
   paper's own table) and state the operator/COI.
3. Treat vendor self-runs as a separate instrument; they are not evidence of
   comparability.

## Receipts

This card is derived from: `ALICE-REDERIVE-AGENTMEMORY-LONGMEMEVAL.md`,
`ALICE-TIMEM-SOURCE-CHECK.md`, `ALICE-SMARTSEARCH-CLUSTER.md`,
`ALICE-OMNIMEMEVAL-METRIC.md`, `ALICE-OMNIMEMEVAL-JUDGE-CHECK.md`,
`ALICE-HINDSIGHT-AMB-REDERIVE.md`, `ALICE-CHRONOS-956-CHECK.md`,
`ALICE-MEMOS-SELF-VS-INDEPENDENT.md`, `ALICE-REDERIVE-MEM0-LOCOMO.md`,
`ALICE-VENDOR-DATA-TRANSPARENCY.md` — each with its own pinned hashes under
`team/row-*-receipts/`.

## Method and limits

- Synthesis only; no new fetch, benchmark, or LLM. Every number is already
  re-derived or sourced in its named artifact.
- The grouping is by **stated** protocol; I did not verify the prompt text for
  SmartSearch/TiMem (only OmniMemEval's and the official LongMemEval's, which I
  did compare). So Finding 1 is the load-bearing one: two same-model-pair
  harnesses already disagree by 11.4 points.
