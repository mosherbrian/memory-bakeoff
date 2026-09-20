# Candidate card — STALE + Supersede (staleness / memory-update gap)

**Author:** Corvid (`worker-glm-dsh3`), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstracts) · **Status:** **candidate
discovery only — no score import.** Card 3 of the named benchmarks in
`RESEARCH-INTELLIGENCE-DIRECTIVE.md`, assessed against our goals G1–G5
(`CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §4).

## Provenance (verified)

| Field | STALE | Supersede |
|---|---|---|
| Title | *STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?* | *Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents* |
| Authors | Hanxiang Chao, Yihan Bai, Rui Sheng, Tianle Li, Yushi Sun | Vedant Patel |
| ID / date | [arXiv:2605.06527](https://arxiv.org/abs/2605.06527), 2026-05-07 | [arXiv:2606.27472](https://arxiv.org/abs/2606.27472), 2026-06-25 |
| License / artifacts | paper **CC BY 4.0** | paper **CC BY 4.0**; open RL env + code/dataset: [`Vrin-cloud/supersede`](https://github.com/Vrin-cloud/supersede) |

## What they are (from the abstracts)

- **STALE** — 400 expert-validated **Implicit Conflict** scenarios (1,200 queries,
  3 dimensions, 100+ topics, contexts to 150K tokens). *Implicit Conflict* = a
  later observation invalidates an earlier memory **without explicit negation**,
  requiring contextual/commonsense inference. Probes: **State Resolution**,
  **Premise Resistance** (reject a query that falsely presupposes a stale state),
  **Implicit Policy Adaptation** (apply the updated state downstream). Best model
  only **55.2%**; models accept outdated assumptions and fail to propagate a
  change in one aspect to related memories. Ships **CUPMem**, a write-time
  revision prototype (structured state consolidation + propagation-aware search).
- **Supersede** — isolates the update gap on LongMemEval's knowledge-update
  subset: replacing full context with bounded self-maintained memory drops
  **92% → 77%** (gpt-5.4; McNemar p<0.005) and does not close with scale; at
  24× conversation length accuracy falls **68% → 28%**, and more memory yields no
  recovery — the failure scales with **conversation length, not compression
  ratio**. Releases an **RL environment** rewarding current-value answers and
  penalizing stale ones; GRPO on Qwen2.5-3B nearly doubles held-out supersession
  (9.0% → 16.7%).

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | **strong** | STALE's implicit conflict is the class behind our Gen38 `dynamic_conflict`; Supersede isolates the update failure |
| **G2 supersession** | **strong** | both are *about* old→new state currency; STALE adds premise resistance + downstream propagation |
| **G3 invocation** | weak | conversational QA, no proactive action deadline |
| **G4 material outcome** | partial | downstream application is probed, but not matched-task utility |
| **G5 continuity** | partial | long contexts (150K) and long conversations, not days/weeks longitudinal |

## What they offer us

- **A new named failure class to add to our taxonomy: *Implicit Conflict*** —
  an observation that invalidates an earlier memory without explicit negation.
  Our ledger/corpus is rich in **explicit** corrections; we should check whether
  implicit conflicts occur in the transcript-miner corpus (a bounded
  re-derivation; if absent, that is itself a finding about our corpus).
- **The three probing dimensions** — State Resolution / Premise Resistance /
  Implicit Policy Adaptation — sharpen our `stale_use` + anachronism reporting and
  suggest a *premise-resistance* companion we do not currently measure.
- **CUPMem** as a **mechanism arm** for E-7 (write-time revision + propagation-
  aware search) — exactly the family our agentmemory/Perseus results live in.
- **Supersede's "length, not compression ratio"** is a discriminating hypothesis
  for our long-context null and memory-vs-context crossover analysis.

## What it cannot ground

Coding-memory conflict/supersession, proactive invocation timing, or material
project outcome — both are conversational/QA. Their numbers are not importable
and must never be cited as coding results.

## Next step (bounded)

1. **Corpus probe:** count explicit vs implicit conflicts in the transcript-miner
   correction events (does an implicit-conflict class exist for us?). One turn,
   local, counts only.
2. Verify the `Vrin-cloud/supersede` repo and STALE's artifact license before any
   code use; record CUPMem only as a design reference.
3. If adopted, add a **PremiseResistance** companion to the invocation/outcome
   reporting (design, not a run).

## Verification status

Existence, abstracts, dates, paper licenses, and the Supersede repo **confirmed**
in this pass. All quantitative findings are **abstract-level, not reproduced**;
the RL-training result is out of our bake-off scope. Repo/dataset licenses
remain to verify; any future citation carries version/date/metric under our
citation rule.

**Verifier: Alice** (`ALICE-CANDIDATE-CARDS-VERIFY.md` — card 3; primary claims
reproduce, discovery-only discipline holds). *Verifier line added by the
card-register librarian (RETRO-2), 2026-09-15 — metadata only.*

— **Corvid** (`worker-glm-dsh3`). Phase-B candidate discovery, $0; no score
import.
