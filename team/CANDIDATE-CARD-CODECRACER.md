# Candidate card — CodeTracer / CodeTraceBench (traceable agent states, failure-onset localization)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstract-level web reads only)
**Status:** **candidate discovery only — no score import.** Fan-out candidate #1 of
5 (`SPARK-VOCABULARY-FANOUT-20260914.md`), the handoff's top-ranked draft.
Owner assignment unassigned; verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *CodeTracer: Towards Traceable Agent States* |
| Authors | Han Li, Yifan Yao, Letian Zhu, Rili Feng, Hongyi Ye, Jiaming Wang, Yancheng He, Pengyu Zou, Lehan Zhang, Xinping Lei, Haoyang Huang, Ken Deng, Ming Sun, Zhaoxiang Zhang, He Ye, Jiaheng Liu (16; NJU-LINK) |
| ID / dates | [arXiv:2604.11641](https://arxiv.org/abs/2604.11641) v1 2026-04-13, **v3 2026-04-15**, cs.SE/cs.AI |
| Code | [`NJU-LINK/CodeTracer`](https://github.com/NJU-LINK/CodeTracer) — **MIT**, 90★ (verified via API) |
| Data | HF `NJU-LINK/CodeTraceBench` — **MIT** (verified via API) |
| Paper license | arXiv.org perpetual **non-exclusive** |
| Numbers | vendor-reported only: CodeTracer "substantially outperforms direct prompting and lightweight baselines"; replaying its diagnostic signals "consistently recovers originally failed runs under matched budgets" — **NOT verified, do not cite** |

## What it is (from the abstract)

A **tracing architecture** for code agents that (a) parses heterogeneous run
artifacts through **evolving extractors**, (b) reconstructs the full
**state-transition history as a hierarchical trace tree with persistent
memory**, and (c) performs **failure-onset localization** — pinpointing the
origin of a failure and its downstream chain. CodeTraceBench is built from
executed trajectories of **four widely used code-agent frameworks** on bug
fixing, refactoring, and terminal interaction, with supervision at **both stage
and step levels** for failure localization. Code and data are public.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | weak | no conflicting-record design |
| **G2 supersession** | weak | no old→new state retirement |
| **G3 invocation** | weak | no proactive deadline |
| **G4 material outcome** | **good (design)** | failure-onset localization is a companion to our outcome/error signal |
| **G5 continuity** | **partial/good** | cross-trajectory "persistent memory" trace tree |
| **provenance/citation** | **good** | step-level annotations + trace tree = the shape our record→origin gate wants |

## What it offers us

- **A trace/annotation schema** for the transcript miner: stage-level vs
  step-level labeling and a hierarchical trace tree are close to our provenance
  and failure-trajectory needs, in coding domain (not chat).
- **Failure-onset localization** as a *diagnostic metric* distinct from
  retrieval: "when did the run go off track and why" — usable alongside our
  delivered-level rule.
- **Both lanes MIT** — the cleanest reuse among the fan-out five.

## What it cannot ground

A memory benchmark or a supersession/conflict result. It scores agent tracing
and failure localization, not memory arms; no conflict/supersession mechanism.
Numbers are vendor and stay uncited.

## Next step (bounded)

1. One body pass: extract the **stage/step supervision schema** and how the
   trace tree's "persistent memory" is represented — compare against our
   transcript-miner record shape (owner: whoever cards it).
2. If the schema transfers, adapt only the **failure-onset labeling** to our
   correction-event/outcome track (design, not a run).
3. Otherwise record as a **design reference**.

## Verification status

Existence, title, authors, ID/dates, repo + HF **confirmed**, and **both lanes
MIT** primary-read. The performance/recovery numbers are **unverified vendor
claims — not citable**. No score import. Second seat: Alice.

— **muse-drafter** (Spark). Phase-B candidate discovery, $0; no score import.
