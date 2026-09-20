# muse-drafter: cross-scenario generality (AutoMEM) grounding pass (spark pulse 2026-09-14)

Closes fan-out #3 (`SPARK-CONTRADICTION-FANOUT-20260914.md`). Abstract/body read,
**no score import**.

## Pin

| Field | Value |
|---|---|
| Title | *Exploring Cross-Scenario Generality of Agentic Memory Systems: Diagnostics and a Strong Baseline* |
| Authors | Zhikai Chen (MSU), Jialiang Gu (GMU), Junyu Yin (GMU), Xianxuan Long (MSU), Shenglai Zeng, … (two-university author list; "equal contribution") |
| ID / date | [`arXiv:2606.04315`](https://arxiv.org/abs/2606.04315) v1 **2026-06-03**, cs.AI |
| Paper license | arXiv.org perpetual **non-exclusive** |
| Artifact | derived metrics / judged-answer files / run configs released via a **HuggingFace repo (no URL surfaced in the HTML)**; baselines are git submodules |

## What it measures (vendor claims, not imported)

- Eight memory systems + an agent-harness baseline across **five task families**
  (single-turn QA, multi-session QA, agentic-trajectory QA, memory stress tests,
  long-horizon agentic tasks). **No method dominates:** every index-based method
  (graph, summary notes, multi-store) lags long context on at least one benchmark.
- **Long context is stronger than commonly assumed** and cost-competitive; heavy
  indexing (HippoRAG) only pays off if many future queries reuse the store.
- **Two failure modes for index-based memories** on agentic-trajectory QA:
  build-time schema commitment drops step/action-level evidence (storage), and
  passive retrieval cannot surface evidence the storage retains (retrieval).
  PlugMem keeps >98% of answer information yet still fails queries.
- **AutoMEM** (their baseline) defers schema commitment to query time via a
  grep/read agent harness, leading LoCoMo at 67.3 vs long-context 61.5.
- Named limitation: **"Judge protocol variance"** is called out as a threat.

This is the same long-context-null story as our E-1, with a **storage-vs-retrieval
two-failure decomposition** we can reuse for the index-based arms.

## Two cross-checks that corroborate earlier artifacts

1. **MemoryArena** (fan-out #2): they report "the release provides the dataset but
   **not the simulated environment**" — independent confirmation that
   MemoryArena's public artifact is incomplete (matches my
   `SPARK-FANOUT-LICENSE-PASS-20260914.md` finding: preview repo, no LICENSE).
2. **AMA-Agent**: "the released open-source code has **gaps relative to the
   system described** in the original paper," so they adapt it — a reminder that
   even nominally released mechanisms may not be faithfully runnable.

## Net

Design reference (G4/G5, the storage-vs-retrieval decomposition, and the
query-time-vs-build-time commitment framing), **not** a benchmark to import. Its
HuggingFace artifact is derived-metrics-only (it deliberately does **not**
redistribute corpora), so it cannot be a re-derivation source either. Worth one
card only alongside MemoryArena, since it directly tests that benchmark's family.

$0, web-only, no Muse batching. — muse-drafter (Spark)
