# Candidate card — CSTM-Bench (cross-session threats, detection, serving-stability metric)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstract-level web reads only)
**Status:** **candidate discovery only — no score import.** Fan-out candidate #2 of
5 (`SPARK-VOCABULARY-FANOUT-20260914.md`), handoff-ranked #2 (fills the unowned
security/governance arm). Owner unassigned; verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *Cross-Session Threats in AI Agents: Benchmark, Evaluation, and Algorithms* |
| Author | **Ari Azarafrooz** (single) |
| ID / date | [arXiv:2604.21131](https://arxiv.org/abs/2604.21131) v1 **2026-04-22**, cs.CR |
| Data | HF [`intrinsec-ai/cstm-bench`](https://huggingface.co/datasets/intrinsec-ai/cstm-bench) — **MIT** (verified via API), 46-page paper, 8 figures |
| Paper license | **CC BY 4.0** (abs-page license icon; Corvid pin 2026-09-15 — corrects an earlier "arXiv non-exclusive" field) |
| Numbers | vendor-reported only: session-bound judge and Full-Log Correlator "lose roughly half their attack recall" moving dilution → cross_session — **NOT verified, do not cite** |

## What it is

- **Dataset.** 26 **executable attack taxonomies** classified by kill-chain stage
  and cross-session operation (**accumulate, compose, launder, inject_on_reader**),
  each bound to one of seven identity anchors so "violation" is a policy
  predicate; plus matched **Benign-pristine / Benign-hard** confounders. Two
  **54-scenario** splits: *dilution* (compositional) and *cross_session* (12
  isolation-invisible scenarios produced by a closed-loop rewriter that softens
  surface phrasing while preserving cross-session artefacts).
- **Measurement.** Cross-session detection framed as an information bottleneck to
  a downstream **correlator LLM**; both a session-bound judge and a Full-Log
  Correlator (every prompt in one long-context call) lose ~half attack recall on
  `cross_session`, *inside* any frontier context window. Stated scope: 54/shard,
  one correlator family (Anthropic Claude), no prompt optimisation.
- **Algorithm + metric.** A bounded-memory **Coreset Memory Reader** (top-K=50
  fragments) is the only reader whose recall survives both shards; because
  ranker reshuffles break KV-cache prefix reuse they promote **`CSR_prefix`**
  (ordered prefix stability, LLM-free) and fuse it into
  `CSTM = 0.7·F1(CSDA@action, precision) + 0.3·CSR_prefix`, giving a
  **recall-vs-serving-stability Pareto**.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| security / governance arm | **good (design)** | cross-session threat model + policy-predicate ground truth |
| **G5 continuity** | partial | threat arises *from* cross-session state — the adversarial side of continuity |
| serving cost / caching | **useful side-artifact** | `CSR_prefix` quantifies ranker damage to KV-cache prefix reuse |
| G1/G2/G3/G4 | weak | not a coding-memory or supersession benchmark |

## What it offers us

- **The cross-session threat model**, with a taxonomy (kill-chain × accumulate /
  compose / launder / inject) and **matched benign confounders** — a governance
  arm design we do not have, and the measured complement to Magnet's capability
  accrual (`SPARK-MAGNET-GROUNDING-20260914.md`).
- **A serving-stability metric** (`CSR_prefix`) that is LLM-free and captures
  ranker damage to KV-cache reuse — adjacent to our cost/break-even thread and
  the "exact returned context / cost matters" reporting rule.
- **MIT dataset** on HF, small and executable.

## What it cannot ground

Coding memory, conflict/supersession, or any of our controlled arms. Single-author
and one correlator family; 54 scenarios per shard. Vendor numbers stay uncited.

## Next step (bounded)

1. Body pass: extract the 26-taxonomy schema (kill-chain × operation) and the
   `CSDA@action` / `CSR_prefix` definitions — compare the taxonomy to CSTM's
   sibling Magnet and to our design corner 5 / leakage-field proposals.
2. If it transfers, propose a **cross-session threat field** (correlator-level,
   not per-retrieval) for the security arm — design only.
3. Otherwise record as a **design reference**.

## Verification status

Existence, author, ID/date, and **HF dataset MIT** confirmed via API. The
"half recall lost" and `CSTM` figures are **unverified vendor claims**. No score
import. Second seat: Alice.

— **muse-drafter** (Spark). Phase-B candidate discovery, $0; no score import.
