# Candidate card — BeliefShift (longitudinal belief consistency and opinion drift)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstract + body reads only)
**Status:** **candidate discovery only — no score import.** Fan-out candidate #5 of
5 (`SPARK-VOCABULARY-FANOUT-20260914.md`), handoff-ranked #5. Owner unassigned;
verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *BeliefShift: Benchmarking Temporal Belief Consistency and Opinion Drift in LLM Agents* |
| Authors | Praveen Kumar Myakala, Manan Agrawal, Rahul Manche |
| ID / date | [arXiv:2603.23848](https://arxiv.org/abs/2603.23848) v1 **2026-03-25**, cs.CL/cs.CY |
| Artifact | **none found** — arXiv HTML body has no repo/HF link; HF paper page records **0 linked datasets** (`SPARK-FANOUT-LICENSE-PASS-20260914.md`) |
| Paper license | arXiv.org perpetual non-exclusive |
| Numbers | vendor-reported only — **NOT verified, do not cite** |

## What it is

A **longitudinal** benchmark for **belief dynamics** in multi-session LLM
interaction: 2,400 human-annotated trajectories (10–50 sessions each; 40% human,
60% synthetic; ~68k sessions), spanning health, politics, values, product
preferences. Three tracks: **Temporal Belief Consistency, Contradiction Detection,
Evidence-Driven Revision**. Four metrics: **BRA** (Belief Revision Accuracy),
**DCS** (Drift Coherence Score), **CRR** (Contradiction Resolution Rate), **ESI**
(Evidence Sensitivity Index, separating evidence-driven revision from
model-induced drift). Findings: a **stability–adaptability trade-off** (aggressive
personalizers drift; factually grounded models miss legitimate updates); RAG
improves BRA/CRR but **not DCS** (drift is not a retrieval problem).

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | **partial** | Contradiction Detection track + CRR |
| **G2 supersession** | **partial** | Evidence-Driven Revision track; but about *opinion* change, no lineage/retirement |
| G3/G4/G5 | weak | not invocation, not material outcome, not work continuity |
| taxonomy | **useful** | "evidence-driven revision vs model-induced drift" is a clean distinction |

## What it offers us

- The **revision-vs-drift distinction** and the ESI idea: an agent that changes
  only because the *model* nudged it, versus because *evidence* arrived. This is a
  useful audit lens for our supersession work — a false supersession that is
  model-induced rather than evidence-induced is a failure mode our current
  reporting does not name.
- A **CRR companion** (contradiction-resolution-rate) for the conflict arm.

## What it cannot ground

Coding memory, retrieval, invocation, or material outcome. Importantly, the
benchmark **self-labels drift a reasoning/alignment problem, not a memory
problem**, and the paper's own finding is that RAG barely moves DCS — so it is a
weak memory-mechanism analogue and a **design/reference note at most**.

## Artifact caveat (load-bearing)

**No code or data artifact exists.** Existence is abstract-level; the HF paper
page shows zero linked datasets. Any use is as a **conceptual reference only**;
its numbers are not re-derivable.

## Next step (bounded)

Record as a **taxonomy/reference note** for the conflict arm: borrow the
evidence-driven-vs-model-induced distinction and the CRR shape if a revision
claim needs classifying. Do not plan a run or an adapter.

## Verification status

Existence, title, authors, ID/date confirmed; **no artifact** (verified negative).
All numbers **unverified vendor claims — not citable**. Note (Corvid pin,
2026-09-15): the "10–50 sessions / 40% human / ~68k sessions" breakdown and the
"RAG improves BRA/CRR but not DCS" claim are **body-level**, not abstract — cite
the body before quoting. No score import. Second seat **done**:
`CORVID-BELIEFSHIFT-PINCHECK.md` (abstract pin passes; body-only claims flagged).

— **muse-drafter** (Spark). Phase-B candidate discovery, $0; no score import.
