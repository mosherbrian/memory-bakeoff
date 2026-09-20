# AMB's TiMem-sourced cluster, verified — and an independent MemOS measurement 16 points below its self-report

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** follow-up to `ALICE-AMB-EXTERNAL-ROWS.md`;
AMB sources five rows to the TiMem paper, including our ledger's MemOS ·
**Cost:** $0 (two arXiv fetches), one turn.

**Receipts:** `team/row-timem-receipts/` (`MANIFEST.md` with sha256):
`arXiv:2601.02845` ("TiMem: Temporal-Hierarchical Memory Consolidation for
Long-Horizon Conversational Agents") abs + HTML + text.

## Finding 1 — the cluster is faithfully sourced

TiMem's Table 2 reports LongMemEval-S under two answer models; AMB's external
rows match its **GPT-4o** column exactly:

| System | TiMem (GPT-4o) | AMB external |
|---|---|---|
| MemoryBank | 22.88 | 0.2288 |
| A-MEM | 63.40 | 0.6340 |
| MemoryOS | 61.20 | 0.6120 |
| Mem0 | 67.56 | 0.6756 |
| **MemOS** | **73.07** | **0.7307** |
| TiMem | 78.96 | 0.7896 |

AMB picks the stronger GPT-4o column (the paper also reports GPT-4o-mini:
MemOS 68.68 · Mem0 64.96 · TiMem 76.88). No sourcing error.

## Finding 2 (load-bearing) — MemOS's self-report vs an independent measurement

Our ledger's **L-S16-02 has MemOS at LongMemEval 89.20** (self-reported via the
vendor's OmniMemEval framework; the metric/judge were recorded as unknown).
TiMem measures the **same benchmark** at **73.07 (GPT-4o) / 68.68 (GPT-4o-mini)**
using the official LongMemEval-S template and Mem0's LLJ prompt.

- Gap: **−16.1 points** (GPT-4o) against MemOS's self-report.
- Caveat: MemOS's 89.20 metric is unpinned, so this is "not comparable until the
  metric is fixed" in the strict sense. But it is the **first third-party,
  academic measurement** of any ledger system, and a gap that large is exactly
  the kind that "pin the metric" should either explain or fail to.
- This is a cross-vendor measurement, not our own receipt, so it does not by
  itself make the row `contradicted` — it makes it `vendor-only` with a strong
  `cross-vendor-measured` flag.

## Finding 3 — Mem0's LongMemEval has yet another value

TiMem puts Mem0 at **67.56** (GPT-4o) / **64.96** (mini). The Hindsight paper's
table lists Mem0 Cloud **94.4** / OSS **91.0**; Mem0's own current harness
reports **94.4**. So Mem0's LongMemEval now spans ~64.96–94.4 depending on who
runs it — the same pattern as its LoCoMo four-configuration drift.

## Finding 4 — a fourth source confirms the authoritative LoCoMo map

TiMem's LoCoMo Table 1 uses category counts **single-hop 841Q · temporal 321Q ·
open-domain 96Q · multi-hop 282Q** — exactly the dataset's id counts under the
authoritative map (1=multi-hop, 2=temporal, 3=open-domain, 4=single-hop). That
is independent external corroboration of `ALICE-LOCOMO-CATEGORY-MAP.md` (and
another vendor, alongside Mem0's current harness, using the correct labels).

## Finding 5 — the judge prompt also traces to Mem0

TiMem states it computes LLJ "using Mem0's evaluation prompt template." So the
supernode's reach extends past the numbers to the **judge prompt** itself — the
same artifact Mem0 originated is now grading several systems' LongMemEval runs.
That strengthens the "name the grader (and its lineage)" rule.

## Consequence for the ledger

- AMB's external registry is **faithful** for the TiMem cluster (spot-checked
  against source).
- **MemOS L-S16-02** gains `cross-vendor-measured: 73.07/68.68 (TiMem, official
  LongMemEval template) vs 89.20 self` — the largest self-vs-other gap found so
  far.
- The LoCoMo authoritative category map now has a fourth independent user.

## Method and limits

- Read the paper's HTML full text and extracted Table 2 and the setup verbatim;
  no benchmark, engine, or LLM run.
- I did not verify TiMem's own 78.96 beyond its report, nor open its code; the
  MemOS 73.07 is recorded as TiMem's measurement, with MemOS's metric still
  unpinned on its side.
