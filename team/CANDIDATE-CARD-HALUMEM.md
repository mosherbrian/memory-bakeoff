# Candidate card — HaluMem (operation-level memory hallucination)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5, QUEUE row 40)
**Date:** 2026-09-14 · **Cost:** $0 (abstract-level web reads only)
**Status:** **candidate discovery only — no score import.** Card 5 of the named
benchmarks in `RESEARCH-INTELLIGENCE-DIRECTIVE.md`, assessed against our goals
G1–G5 (`CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §4).

## Provenance (verified this pass)

| Field | Value |
|---|---|
| Title | *HaluMem: Evaluating Hallucinations in Memory Systems of Agents* |
| Authors | Ding Chen, Simin Niu, Kehang Li, Peng Liu, Xiangping Zheng, Bo Tang, Xinchi Li, Feiyu Xiong, Zhiyu Li (China Telecom Research Institute / MemTensor / Harbin Engineering University) |
| ID / dates | [arXiv:2511.03506](https://arxiv.org/abs/2511.03506) v1 2025-11-05, v3 2026-01-05 |
| Venue / license | preprint; paper page carries "arXiv.org perpetual non-exclusive license" (no CC grant verified) |
| Code | public: [`MemTensor/HaluMem`](http://github.com/MemTensor/HaluMem) — repo `LICENSE.txt` verified this pass (raw fetch): **CC BY-NC-ND 4.0** |
| Data | HaluMem-Medium (30,073 dialogue rounds, 20 users, ~160k tokens/user, 14,948 memory points, 3,467 QA pairs) + HaluMem-Long (~1M tokens/user, 53,516 rounds); public on HF: `IAAR-Shanghai/HaluMem` |
| Numbers | vendor-reported only this pass: recall <60%, memory accuracy <62% across six systems (Mem0, Mem0-Graph, Memobase, MemOS, Supermemory, Zep); Medium→Long degradation — **NOT verified from the PDF, do not cite** |

## What it is (from the abstract)

The first **operation-level** hallucination benchmark for memory systems.
Instead of end-to-end QA, it decomposes the memory workflow into three
evaluated operations — **memory extraction, memory updating, memory QA** —
each with stage-specific gold standards and metrics (accuracy /
hallucination rate / omission rate). Finding reported: hallucinations are
generated and accumulate at extraction and updating, then propagate to QA.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | partial | extraction/update errors include conflicts, but no adversarial conflict/supersession design |
| **G2 supersession** | partial | memory *updating* is the closest published analogue to our old→new transition; no explicit lineage |
| **G3 invocation** | weak | no proactive action deadline; task-sequenced |
| **G4 material outcome** | weak | QA accuracy, not time/errors/corrections on real tasks |
| **G5 continuity** | partial | 1.5k–2.6k turns/user is long-context, but synthetic-scale dialogue, not days/weeks of real work |

## What it offers us

- **An operation-level reporting shape** (extraction vs updating vs QA
  hallucination/omission rates) that matches our delivered-level instinct:
  separate formation failure from use failure instead of one end-to-end score.
- **The updating task as a design reference** for our supersession work —
  how a benchmark stages old→new memory transitions is directly relevant to
  P1-2/P1-3-style cases, even though HaluMem supplies no lineage mechanism.
- **A caution for our corpus:** extraction-stage omission (recall <60% per
  vendor) is the same class as our F2 binding constraint (query formulation
  misses seed vocabulary).

## What it cannot ground

Coding conflict/supersession, proactive invocation, or material outcome —
and its headline numbers are vendor-harness results on its own datasets,
never to be imported as evidence. Operator-conflict note: the benchmark is
built by a vendor (MemTensor) that also ships a memory product — treat
self-reported system rankings as `vendor-only` per our ledger classes.

## Next step (bounded)

1. Verify the repo license + dataset terms (owner: whoever takes goal-5
   remainder; one web pass).
2. If usable, borrow only the **extraction/updating/QA metric split** as a
   reporting shape for our own runs (design, not a run).
3. Otherwise record it as a **design reference** in the discovery note.

## Verification status

Existence, abstract, authors, version dates, dataset scale figures, and
public code **confirmed** in this pass (abstract-level only). Headline
percentages are **unverified vendor claims — not verified, not citable**.
Paper license is arXiv-nonexclusive (not CC); repo license **verified:
CC BY-NC-ND 4.0** (raw `LICENSE.txt` fetch 2026-09-14). Any future citation
carries version/date/metric under our citation rule.

## Addendum 2026-09-14 (repo-page pass, muse-drafter)

- **Venue:** accepted to **EMNLP 2026 Main** (repo news, 2026-08) — no
  longer preprint-only. Venue does not change the vendor-only status of
  its numbers.
- **License load-bearing:** CC **BY-NC-ND** 4.0 — NonCommercial bars
  commercial use; **NoDerivatives bars SHARING adapted material**
  (§2(a)(1)(b): produce/reproduce but not Share). Reading and measuring
  against it is fine; republishing a re-cut or adapted HaluMem set is
  not. Dataset terms on HF (`IAAR-Shanghai/HaluMem`) not yet checked —
  assume same-or-stricter until read.
- **Data is synthetic, not human:** personas from rule templates seeded
  by Persona Hub → GPT-4o refinement; dialogues LLM-generated with
  adversarial distractor memories inserted; 8 annotators reviewed >50%
  of Medium only (95.70% accuracy, 9.58 relevance, 9.45 consistency —
  vendor-reported). It grounds **no** human-behavior goal.
- **Dataset license closed 2026-09-14:** HF `IAAR-Shanghai/HaluMem` reads
  **cc-by-nc-nd-4.0**, matching the repo — same ND bar on sharing adapted
  sets. Acquisition caveat: the HF dataset viewer is broken for the train
  split (`RowsPostProcessingError`); 140 MB total, 368 downloads last
  month. No viewer, no pre-download inspection.
- **Lineage analogue found:** memory points carry `is_update` +
  `original_memories` (links to the replaced versions) — the closest
  published analogue to our EXPLICIT_LINEAGE yet. Worth one design-read
  of how their update task stages old→new transitions (design reference
  only, no import).
- Second seat: Alice (row 40 verifier).
- Verifier: Corvid (abstract pin ✓ 2026-09-15, `CORVID-HALUMEM-PINCHECK.md`); Alice (row 40 content check, pending).

— **muse-drafter**. Phase-B candidate discovery, $0; no score import.
