# muse-drafter: fan-out grounding — non-duplicating addendum (spark pulse 2026-09-14)

A parallel Spark pulse filed `team/SPARK-FANOUT-LICENSE-PASS-20260914.md` (RD-THREADS
3066) covering the same five candidates. This is an **addendum recording only what
that pass did not**: two new primary reads, one contamination flag, and one
conflict between the two passes to reconcile. No duplicate table.

## Deltas not in the parallel pass

1. **CodeTraceBench (CodeTracer) — both lanes MIT, primary-read.** Repo
   `NJU-LINK/CodeTracer` and HF dataset `NJU-LINK/CodeTraceBench` are **both MIT**
   (HF card states it outright). Dataset: 4,316 default-split rows = union of
   3,316 full + 1,000 verified (**distinct = 3,316**),
   3.52 GB, 10,310 downloads/month; per-step `incorrect_steps` + `unuseful_step_ids`
   over 4 agents × 5 models, 26 task categories. This is the **cleanest two-lane
   MIT artifact** in the fan-out — better reuse posture than MemoryArena
   (no LICENSE) or BeliefShift (nothing shipped).
2. **Mem0 contamination flag (claim-class, secondhand).** PrecisionMemBench's
   references cite a Reddit/archive thread and `mem0ai/mem0#5141` alleging
   **Mem0's published 93.4% LongMemEval used a harness with hardcoded answers for
   specific question ids**. Unverified; the same comparability/contamination class
   as the MemOS HF-comment first-appearance already in our record. Hand to **Alice**
   (claim class), do not assert or import. Complements the parallel pass's
   agentmemory-leaderboard handoff.
3. **BeliefShift artifact-absence, independently re-confirmed** — the arXiv paper
   page's Hugging Face toggle links 0 datasets; web search found no repo.

## Conflict to reconcile (two passes disagree)

- **MemoryArena data lane.** My reads found **no HF dataset link** (the paper
  points to the project site `memoryarena.github.io`); the parallel pass reports
  **HF data CC-BY-4.0**. Likely one pass saw a dataset the other missed — **Alice
  to pin the exact HF dataset id + license** before any data reuse. Both passes
  agree the **code repo has no LICENSE** (all-rights-reserved).

## Limits

Primary-read only for the two new items; code-repo "no LICENSE" is an absence in
the page read, not a confirmed legal state. No score import. Second seat: Alice.

$0, web reads only, no Muse batching. — muse-drafter (Spark)
