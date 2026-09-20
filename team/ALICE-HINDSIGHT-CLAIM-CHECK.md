# Hindsight's benchmark claim — a live dashboard that is narrower than the headline

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated from RD-THREADS §Alice
thread 2; Hindsight is the ledger's strongest `third-party` candidate
("independently reproduced") and had no artifact-level check · **Cost:** $0,
eight pinned/live fetches, one turn.

**Receipts:** `team/row-hindsight-check-receipts/` (`MANIFEST.md` with sha256),
at pin `vectorize-io/hindsight@ebad4782` plus the live dashboard repo
`vectorize-io/hindsight-continuous-performance-monitor` (gh-pages, pushed
2026-09-12).

## The claims

- README: *"Hindsight is the most accurate agent memory system ever tested"*;
  *"state-of-the-art performance on the LongMemEval benchmark"*; as of January
  2026.
- Blog (2026-03-23): **LoCoMo 92.0% · LongMemEval 94.6%** · LifeBench 71.5% ·
  PersonaMem 86.6%.
- README: *"The benchmark performance data for Hindsight has been
  independently reproduced by research collaborators at the Virginia Tech
  Sanghani Center … and The Washington Post. Other scores are self-reported by
  software vendors."*

## What the durable artifacts actually show

1. **The harness is shipped** — `benchmarks/locomo/`, `benchmarks/longmemeval/`,
   and run scripts. Good: the claim is re-runnable.
2. **The live dashboard publishes LoCoMo and OBS, but zero LongMemEval.** Its
   `data/` tree has `locomo/` (82 runs), `obs/` (104), `system-evals/` (1) —
   **no `longmemeval/` directory and no longmemeval index**. The headline SOTA
   claim (LongMemEval 94.6) has **no durable published data artifact**.
3. **The published LoCoMo runs are a 3-conversation subset, and never reach
   92.0.** All 82 runs are `total_questions: 411`, `num_items: 3` (3 of 10
   conversations). Nonzero accuracies span **57.66%–90.02%**, not the claimed
   92.0%. (The latest run, 2026-09-12, is 0.0 — a zero/smoke run.)
4. **The publish pipeline strips per-question detail.** `publish-locomo-results.sh`
   deletes `detailed_results` ("kept only in the upload artifact") and keeps only
   per-item `accuracy/correct/total/category_stats`; the published run confirms
   no `detailed_results`. So even the published runs cannot be audited below
   aggregate — the full data is an ephemeral CI workflow artifact.
5. **The "independently reproduced" claim has no cited report.** The README links
   only the VT Sanghani Center *homepage*, the dashboard, and the repo — no
   paper, page, or document by VT or The Washington Post. It is a
   **vendor-asserted third-party claim**, and we do not hold the reference.

## Classification consequence

- The ledger's `third-party` class stays empty. Hindsight moves from
  `vendor-only` to **`vendor-only` + an unreferenced third-party assertion** —
  stronger in intent, still not a reference we can check.
- The published dashboard is a genuine reproducibility effort (continuous,
  commit-stamped, harness shipped) but it is **narrower than the headline**: 3
  conversations, LoCoMo only, stripped detail. It cannot support the LongMemEval
  SOTA claim and does not reproduce the LoCoMo 92.0.
- **To move the row:** (a) locate the Virginia Tech / Washington Post artifact
  (the only path to `third-party`), or (b) run the shipped full harness under a
  pinned reader/judge (a metered product run — the survey notes none exists).
- Third number for the collision register: MemBukkit's competitor table lists
  Hindsight at **91.4** (official prompts, judge swapped to GPT-OSS-120B), after
  Hindsight's own 94.6 and the dashboard's 3-conversation 86–90.

## Method and limits

- Read-only: fetched README, blog, publish script, benchmark README, the
  dashboard tree, the locomo index (82 runs), and one published run. No
  benchmark, engine, or LLM.
- The 92.0 / 94.6 headline numbers are from a mutable blog (no WayBack pin
  recorded); the dashboard and README are pinned by sha. I did not search for a
  VT/WaPo publication beyond the README's own links.
