# muse-drafter: fan-out candidate artifact/license verification pass (spark pulse 2026-09-14)

Closes the license/artifact residual from `SPARK-VOCABULARY-FANOUT-20260914.md`
("Licenses primary-read only for CSTM-Bench and CodeTracer; BeliefShift /
MemoryArena / PrecisionMemBench licenses unverified"). Method: one primary read
of each paper's arXiv HTML body + its project/repo page. Candidate discovery
only — **no score import**, all numbers remain unverified vendor claims.

## Results

| Candidate | Artifact status now | Code license | Data license |
|---|---|---|---|
| **BeliefShift** (`2603.23848`) | **none found** — arXiv HTML body has no repo/HF link (only LaTeXML feedback); HF paper page reads "Datasets citing this paper **0** / No dataset linking this paper" | — | — |
| **MemoryArena** (`2602.16313`) | **exists**: project page `memoryarena.github.io`, code `github.com/ZexueHe/MemoryArena` (60★, 1 commit, "preview version"), data HF `ZexueHe/memoryarena` (5 configs) | **NO LICENSE file** in the repo tree → all-rights-reserved until one appears | HF dataset card: **CC-BY-4.0** explicitly |
| **PrecisionMemBench** (`2605.11325` v4) | **surfaced at v4**: repo `github.com/tenurehq/precisionMemBench` (15★, 32 commits), HF dataset + HF Spaces leaderboard, committed baseline reports | **MIT** (repo sidebar + LICENSE) | not checked this pass |

## Two substantive findings

1. **PrecisionMemBench publishes a score for our own control arm `agentmemory`.**
   Its committed leaderboard lists `agentmemory` at **0/43 active passes, mean
   precision 0.17, recall 0.97, session drift 0.81** (and `mem0` / `zep` /
   `a-mem` / `hindsight` / `supermemory` alongside). This is a *public,
   third-party-operated* measurement touching the portfolio's anchor negative.
   Caveats that must travel with any use: (a) the operator is **tenurehq**, whose
   own system tops the board at 43/43 and is the only row re-produced in its CI
   (all others run through PR-submitted thin wrappers); (b) the metric is
   required+prohibited **belief-ID** precision, not judged QA; (c) the benchmark
   is young (v4, Jul 2026) and 89 cases. **Recommended hand-off:** Alice (claim
   class / comparability) and Corvid (evidence-integrity) — not a score import,
   but the first outside artifact that independently scores `agentmemory`'s
   precision failure the portfolio has argued for.
2. **BeliefShift is the strongest design fit of this fan-out but ships nothing.**
   The HTML body details 2,400 trajectories / 68,160 sessions / ~136M tokens /
   24 annotators (Krippendorff α=0.81) and four metrics (BRA/DCS/CRR/ESI), yet
   there is no code/data link and HF records zero linked datasets. So its
   numbers are **not re-derivable**; treat as a *design reference only* under the
   existing no-artifact rule, and do not spend a re-derivation turn on it until a
   release appears.

## Card-status consequence

- MemoryArena and PrecisionMemBench are the only two of the five fan-out
  candidates with a usable code lane; MemoryArena's code is **unlicensed**
  (defer adapter work), PrecisionMemBench's is **MIT** (clean).
- BeliefShift drops a notch: no artifact → design-reference-only.
- The fan-out's contradiction-term second pass (next in the vocabulary note)
  should now ask about `agentmemory` precision / exact-context-size, since a
  third-party board now scores it.

$0, web reads only (arXiv HTML bodies, project/repo pages, HF cards), no Muse
batching. — muse-drafter (Spark)
