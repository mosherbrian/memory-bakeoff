# Candidate card — ACM (Agentic Context Management for long-horizon tasks)

**Author:** muse-drafter (proposal-drafter seat), watchlist delta #3 follow-up (Sprint-2 goal 5)
**Date:** 2026-09-15 · **Cost:** $0 (abstract/API web reads only)
**Status:** **candidate discovery only — no score import.** Second of two new
reuse-green delta-#3 candidates (`SPARK-WATCHLIST-DELTA-3-20260915.md`). Owner
unassigned; verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *ACM: Agentic Context Management for Long Horizon Tasks* |
| Authors | Xiaochuan Li, Ryan Ming, Meng Chu, Shuai Shao, Rong Jin, Chenyan Xiong |
| ID / date | [arXiv:2607.23809](https://arxiv.org/abs/2607.23809) v1 **2026-07-26**, cs.AI |
| Paper license | **CC BY 4.0** |
| Code | official [`lixiaochuan2020/agentic-context-management`](https://github.com/lixiaochuan2020/agentic-context-management) — **MIT**, 36★ |
| Numbers | vendor-reported only — **NOT verified, do not cite** |

## What it is

**ACM** equips an agent with purpose-built **context-editing tools** so the agent
**autonomously decides when to compress** its context, **offloads discarded
content to an external memory system**, and **queries it on demand** — instead of
fixed heuristic compression triggers. A **post-training pipeline** builds
context-management demonstrations and improves performance on agentic **search and
coding** tasks. Reported analysis: lower peak token pressure, longer
exploration, more consistent solutions across independent runs.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **compaction / context management** | **good** | the trigger question ("when to compress") is the agentic version of our compaction arm |
| **G4 material outcome** | partial | improves coding/agentic-search tasks; no material-outcome metric promised |
| **external memory / E-8** | **good** | offload + on-demand query is the short/long-term-memory split we model |
| **G3 invocation** | partial | the agent decides *when* to act on context, not a proactive deadline |
| G1/G2 conflict/supersession | weak | no lineage/retirement mechanism described |
| provenance | weak | no explicit record→origin gate |

## What it offers us

- **The agentic-trigger framing:** our DIGEST/compaction work uses rules; ACM asks
  the agent to choose *when* — a comparison axis for our compaction arm.
- **Offload-to-external-memory + query-on-demand** as a lossless-ish design
  reference, complementary to Compaction Cliff's typed fidelity lanes.
- **MIT code** — reuse-green if a build is funded.

## What it cannot ground

Memory conflict/supersession or retrieval scoring; no benchmark release described.
Numbers are vendor and stay uncited. It is a method/framework, not a benchmark.

## Released artifact — grounded (2026-09-15, repo + HF)

Affiliations: CMU (Li, Ming, Chu, Xiong) + Meta (Shao, Jin). The official repo
(MIT) ships a full release:

- **Two claimed properties:** *agent-native* — **the agent decides when to
  compress** (not an external trigger); *lossless* — discarded context is
  **written to disk permanently and retrievable on demand**.
- **HF collection**: student rollouts (`pass@4` on BrowseComp-Plus `train-680`,
  both `react/` and `memtool/` modes), teacher top-K logprobs caches, and
  **post-trained checkpoints** (ACM Agent Qwen3.5-9B, OPD iterations 1–3).
- Pipeline: student rollout → grading/filter → teacher logprobs → distillation.

Relevance sharpens: ACM's **lossless offload** is the direct counter-design to
Compaction Cliff's lossy typed compression — two ends of the same axis, both
reuse-green (ACM MIT; Cliff Apache-2.0). Its `memtool/` vs `react/` rollout modes
are a ready-made A/B of context management.

## Next step (bounded)

1. ~~Body/repo pass: context-editing tool interface + post-training shape~~
   **DONE** (grounded above). The tool interface is in-repo (`src/`), the data in
   the HF collection.
2. Otherwise record as a compaction/externalization design reference.

## Verification status

Pin, authors, date, **CC BY 4.0** paper, and **MIT** official repo confirmed via
API. Numbers are **unverified vendor claims — not citable**. No score import.

**Verifier: Alice** (Series C second seat).

— **muse-drafter** (Spark). Candidate discovery, $0; no score import.
