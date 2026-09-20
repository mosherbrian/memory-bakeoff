# Verification — Phase-B candidate cards 1–3 (MemOps / StreamMemBench / STALE+Supersede)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-14 00:5x UTC · **Cost:** $0, primary-source reads, one turn.
**Trigger:** three candidate cards filed against the directive's named
benchmarks; standing second-check of new R&D artifacts. No tree modified.

## Verdict

**All three cards' primary claims reproduce; no number is wrong.** The cards keep
their "candidate discovery only, no score import" discipline.

## Card 1 — MemOps (`CANDIDATE-CARD-MEMOPS.md`)

arXiv [`2607.12893`](https://arxiv.org/abs/2607.12893) abstract confirms every
descriptor the card uses: lifecycle of explicit operations (**remembering,
forgetting, updating, reflecting** and compositions); a structured trace
specifying **trigger, target, scope, state transition, supporting evidence**; a
controllable generation pipeline producing **gold operation traces** and **six
categories of operation-level probes**, under **adjacent-evidence** and
**long-context** settings; and the findings that **session-level retrieval
outperforms turn-level** and long-context models are weak at **ordered
memory-state reconstruction**. First-author/submission match (`Xixuan Hao`).
The card's honesty holds: **code/data not located** and the license is stated as
non-exclusive — consistent with the abs page showing **no CC link**.

## Card 2 — StreamMemBench (`CANDIDATE-CARD-STREAMMEMBENCH.md`)

Its numbers (**paired 160 trajectories; FUR 27.5% → 40.6%, +13.1 commit gain**)
are the ones I verified from the paper **PDF** earlier (the HTML full text omits
them — the card records that method note). Code repo
[`landian60/StreamMemBench`](https://github.com/landian60/StreamMemBench)
resolves (HTTP 200). **Not independently verified:** the "Findings of EMNLP 2026"
venue and the EgoLife data license (the card already lists the latter as an open
bounded step).

## Card 3 — STALE + Supersede (`CANDIDATE-CARD-STALE-SUPERSEDE.md`)

| claim | source | verdict |
|---|---|---|
| STALE: **400** expert-validated scenarios, **1,200** queries, **100+** topics, contexts **≤150K** tokens, best model **55.2%** | [`2605.06527`](https://arxiv.org/abs/2605.06527) abstract | **CONFIRMED** |
| STALE dimensions: State Resolution / Premise Resistance / Implicit Policy Adaptation; **CUPMem** = write-time revision via structured state consolidation + propagation-aware search | same | **CONFIRMED** |
| Supersede: LongMemEval knowledge-update **92% → 77%** with bounded memory (gpt-5.4; McNemar p<0.005) | [`2606.27472`](https://arxiv.org/abs/2606.27472) abstract | **CONFIRMED** |
| **24×** conversation length: **68% → 28%**; failure scales with **length, not compression ratio** | same | **CONFIRMED** |
| both **CC BY 4.0**; repo [`Vrin-cloud/supersede`](https://github.com/Vrin-cloud/supersede) | abs pages / repo | **CONFIRMED** (200) |

One wording note (not a defect): the 92→77 and 68→28 results are two different
settings (bounded-memory vs growth) in the abstract; the card's single bullet
reads cleanly if the reader keeps that split in mind.

## Net

Number/provenance risk in cards 1–3 is low. The remaining unverified surface is
**venues and dataset/code licenses** (MemOps code/data, StreamMemBench EgoLife
data + venue), which the cards already flag as bounded next steps. Recommend the
cards proceed to the goal-fit work; no correction needed.

## Limits

- Abstract-level reads plus one repo HEAD per source; "confirmed" = the source
  states the figure, not that the experiment was reproduced. No data downloaded.
