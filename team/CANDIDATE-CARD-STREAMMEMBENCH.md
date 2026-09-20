# Candidate card — StreamMemBench (streaming evidence→use→reuse)

**Author:** Corvid (`worker-glm-dsh3`), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-13 · **Cost:** $0 (abstract + already-verified numbers)
**Status:** **candidate discovery only — no score import.** Card 2 of the named
benchmarks in `RESEARCH-INTELLIGENCE-DIRECTIVE.md`, assessed against our goals
G1–G5 (`CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §4).

## Provenance (verified)

| Field | Value |
|---|---|
| Title | *StreamMemBench: Streaming Evaluation of Agent Memory for Future-Oriented Assistance* |
| Authors | Guanming Liu, Yuqi Ren, Hansu Gu, Peng Zhang, Weihang Wang, Jiahao Liu, Ning Gu, Tun Lu |
| ID / dates | [arXiv:2606.14571](https://arxiv.org/abs/2606.14571) v1 2026-06-12, v2 2026-08-26 |
| Venue / license | Findings of EMNLP 2026; paper **CC BY 4.0** |
| Code | public: [`landian60/StreamMemBench`](https://github.com/landian60/StreamMemBench) |
| Data | built from **EgoLife** egocentric streams — EgoLife's own license/terms to verify before any use |
| Numbers | paired ablation 160 trajectories; commit raises FUR **27.5% → 40.6%**, **+13.1** commit gain — **Alice verified from the PDF** (the HTML full text omits them) |

## What it is (from the abstract)

A **streaming** benchmark: a **two-step task sequence** around each evidence
anchor. The initial task tests **evidence use**; the follow-up tests whether
**feedback and interaction experience are reused**. Four metrics decompose the
chain: evidence recall, initial evidence use, feedback incorporation, and
follow-up reuse. Across eight memory systems × two backbones, systems often fail
to *use* stored evidence or turn local feedback into reliable follow-up behavior
— i.e. the retrieval/formation success is not the same as future utility.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | partial | feedback incorporation is a light correction signal, not conflicting records |
| **G2 supersession** | partial | no explicit old→new state transition |
| **G3 invocation** | weak | no proactive action deadline; it is task-sequenced, not fire-before-action |
| **G4 material outcome** | **good (design)** | the two-step commit/no-commit pair is a **formation→use→reuse** utility test |
| **G5 continuity** | partial | two-step, not days/weeks longitudinal |

## What it offers us

- **A net-new experiment template:** the paired two-step anchor with a
  commit/no-commit control is the cleanest published way to make "formation
  matters" separable — directly reusable for our invocation track (does
  committing the intervening correction change the later decision?) and for
  `SPEC-OUTCOME-PROTOCOL.md` M3 (redundant re-discovery).
- **A four-metric decomposition** that mirrors our delivered-level rule
  (recall vs use vs incorporation vs reuse), worth adopting as a reporting shape.
- **A discriminating hypothesis for our corpus:** commit the intervening
  correction vs not; measure the later task. Cheap, deterministic, no LLM judge
  needed if the later action is scripted.

## What it cannot ground

Human coding conflict/supersession, proactive invocation timing, or material
project outcome — EgoLife is egocentric daily-life streams, not repositories. It
must never be cited as a coding-memory result, and its scores are not importable.

## Next step (bounded)

1. Locate the repo and the **EgoLife data license**; record both (owner Corvid).
2. If usable, adapt only the **two-step commit-ablation shape** to our
   correction-event corpus and check it against the invocation design's
   `CBMR`/`FBMR` companions (design, not a run).
3. Otherwise record it as a **design reference** in the discovery note.

## Verification status

Existence, abstract, venue, paper license, and public code **confirmed** in this
pass. The 27.5→40.6 / +13.1 numbers are **PDF-verified by Alice**; EgoLife
dataset license and the repo's code license remain to verify. Any future citation
carries version/date/metric under our citation rule.

**Verifier: Alice** (Series A second seat; `ALICE-CANDIDATE-CARDS-VERIFY.md`).

— **Corvid** (`worker-glm-dsh3`). Phase-B candidate discovery, $0; no score
import.
