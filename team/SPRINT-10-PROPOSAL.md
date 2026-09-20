SELECT: 6, 8, 9, 12
SPRINT-GOAL: Establish whether stronger competing text changes evidence delivery, make retrieval order visible, and repair the checks and duplicate detection that keep research runs reliable.
WHY: These four substantial candidates are explicitly startable today, require no paid model calls, and preserve the strict ranking. A planning estimate is 30, 25, 30 and 20 minutes respectively for implementation and local checks, plus about 15 minutes for independent confirmation: roughly two hours, with uncertain durations. Ranks 13 and 14 remain unblocked but are deferred for capacity; this is explicitly the provenance audit’s second deferral. The outcome experiment still needs Brian’s campaign decision, SWE-chat needs a sampling decision or more disk space, and the research watch and keep-warm rerun have unmet time prerequisites. The existing budget tool clears none of those dependencies, and no metered experiment is admitted during the free window ending September 20.
OUTLINE:
## 1. THEME
Measure evidence delivery under stronger competition, expose retrieval order, then repair the safeguards for running experiments and admitting future work.

## 2. GOALS
**Goal 1 - As Brian, I can see whether more relevant-looking distractions change what evidence reaches a model.**

The previous 20,000-byte competing load never entered any adapter’s highest-ranked results, so it did not establish that stronger competition is harmless. Declare distracting text that shares the queries’ vocabulary but contains no helpful evidence, then repeat the same five fixed items with bm25, pi_lcm_toollevel and claude_mem. Report the previous and new evidence-delivery results side by side; this does not test whether a model completes a real task successfully.

Done when: The declared load, automatic-check results and five-item comparisons are available, including whether the distracting text actually reached the selected results.

**Goal 2 - As Brian, I can see when helpful evidence moves down the search results even if it remains present.**

Current sprint reports can hide changes in retrieval order: claude_mem’s first two results swapped on one item without changing evidence presence or delivered bytes. Add the existing reciprocal-rank measures, which show how early relevant evidence appears, and nDCG, which measures the quality of the ranked list. Keep these measures separate from existing scores and apply them only to systems that expose ranked results; this does not create a combined leaderboard score.

Done when: Reports show the separate ranking measures alongside evidence presence, and automatic examples demonstrate that changing result order can change those measures while presence stays unchanged.

**Goal 3 - As Brian, I can trust that failed evaluator checks stop an experiment before it starts.**

Nothing currently requires the evaluator’s protective checks to pass before an expensive experiment begins, and the existing failure-behavior test does not cover the sprint’s automatic checkers. Make those protective checks a mandatory first step that stops execution on failure, and extend the failure-behavior test to the sprint checkers. Prove this locally without launching a paid experiment; this repairs the measurement process rather than claiming better model performance.

Done when: A deliberately failing protective check prevents the experiment from starting, passing checks allow it to proceed, and the covered sprint checkers return the expected success or failure status.

**Goal 4 - As Brian, I can reuse a backlog rank without the planner rejecting genuinely new work.**

The planner mistakes an old rank citation for proof that a new candidate has already been admitted, and this has stopped two planning attempts. Make duplicate detection depend on the candidate’s artifact path, with rank citations counting only when they refer to that same artifact. Demonstrate the repair using scratch copies of the planner and work board; this does not edit the live board or reopen completed work.

Done when: A fresh artifact using a previously used rank is accepted, while the same artifact presented under a different rank is still rejected.

## 3. WHO
kiln-flash implements one candidate at a time, and corvid-dsh independently confirms each result before the next candidate starts. Confirm corvid-dsh is available at the start; nobody confirms their own work.

## 4. NOT DOING
- Provenance audit, rank 13 — deferred a second time because the selected implementation and confirmation work fills the two-hour allowance.
- Single-run labels, rank 14 — deferred for capacity behind the higher-ranked work.
- Outcome experiment — Brian has not decided the campaign-2 window and scope.
- SWE-chat acquisition — only 14 GB is free against a 39.3 GB full-set projection, requiring Brian’s sampling decision or more space.
- Standing research watch and the Heimdall code review — the shared-request restriction remains in force until September 20.
- Keep-warm rerun — a full day of steady Muse activity after the OpenCode Go reset has not occurred.
- Batch selection, Gate F adoption and the next experiment build — the required Brian/GiLMore decisions remain outstanding.
- First model-scored run of the stale-instruction test — no startable candidate with an authorized run window is supplied.
