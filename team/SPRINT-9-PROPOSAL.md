SELECT: 1, 2, 3, 4
SPRINT-GOAL: Build the missing stale-instruction tests, measure delivery under stronger competition, expose retrieval ordering, and make failed evaluator checks stop subsequent runs.
WHY: These four candidates have no unmet dependencies and require only local, $0 work, so they can proceed on September 18 without metered spend during the free GLM window. Keep their ranked order: build the missing tests, strengthen the delivery measurement, improve reporting, then enforce evaluator checks. Allow approximately 35, 30, 25, and 20 implementer minutes respectively, plus 10 minutes for corrections: a two-hour planning estimate, not a measured duration. Defer rank 5 for capacity, and skip the outcome experiment pending Brian’s campaign decision, SWE-chat acquisition pending a sampling decision or sufficient storage, the research watch until September 20, and the keep-warm rerun until its reset and full-day prerequisites are met.
OUTLINE:

## 1. THEME

Build tests for stale instructions, measure stronger competition for delivered evidence, show retrieval ordering, and enforce checks that protect those measurements.

## 2. GOALS

**Goal 1 - As Brian, I can test whether a worker uses a freshly checked value despite an outdated instruction.**

The completed design has not yet become runnable tests. Build two cases: one requiring the worker to commit the current value returned by a required check, and one where a plausible authorizer asks for the retired path despite the stored current value. Include checks that prevent wording from giving away the answer; this builds the test instrument and does not run a model experiment.

Done when: Both cases and their automatic scoring pass the supplied self-test, including controls that catch use of the superseded value and answer-revealing markers.

**Goal 2 - As Brian, I can see whether more relevant competing text changes what each memory system actually delivers.**

The previous 20,000-byte competing load never entered any system’s highest-ranked retrieved results, so it did not establish what happens under effective competition. Declare stronger competing text using the query’s vocabulary, confirm it contains no helpful evidence, and rerun the same five cases on bm25, pi-lcm tool-level, and claude-mem at the same 600-character delivery budget. Compare against the previous helpful-evidence results of 5/5, 1/5, and 5/5, keeping irrelevant bytes separate; this does not establish improved model outcomes or justify adoption.

Done when: The load is recorded before execution, old and new results appear side by side, and the report states whether competing text reached the retrieved results and whether any delivered text was cut.

**Goal 3 - As Brian, I can see when useful evidence moves down the retrieved list even if it remains present.**

In the previous claude-mem measurement, the first two records changed places for one case while evidence presence and delivered bytes stayed unchanged. Add the existing reciprocal-rank and mean-reciprocal-rank measures to sprint reports, and add normalized discounted cumulative gain to show how useful evidence is ordered across the list. Report these separately for systems that expose ranked results; do not blend them into existing scores or claim the earlier rank measures are new.

Done when: Reports show the separate ordering measures, their automatic checks pass, and an ordering change is visible even when evidence presence stays constant.

**Goal 4 - As Brian, I can trust that failed evaluator checks prevent an experiment from starting.**

The existing protective checks are not required to pass before an expensive experiment, and the automated check of success and failure exit codes does not cover sprint checkers. Make the protective checks a required first step and extend exit-code coverage to the sprint checkers. This repairs the measurement process; it neither runs an expensive experiment nor directly demonstrates better memory behavior.

Done when: A deliberately failing protective check stops execution before the experiment starts, passing checks allow execution to continue, and covered sprint checkers return the expected success and failure codes.

## 3. WHO

Kiln-flash implements the four tasks in order, with only one implementation task active at a time. Corvid-dsh independently confirms each result; no worker confirms their own work.

## 4. NOT DOING

- Three-thread provenance audit, rank 5 — deferred to keep this sprint near two implementer hours.
- Outcome experiment — Brian has not decided campaign 2’s window and scope.
- SWE-chat acquisition — only 14 GB is free against a 39.3 GB full-set projection, and Brian has not approved a smaller sample.
- Standing research watch — the shared-request restriction remains in force until September 20.
- Keep-warm rerun — the OpenCode Go reset and one full steady-pattern day on Muse have not occurred.
- Research batch selection and the roadmap’s Gate F decision — these await GiLMore/Brian.
- Metered experiments that can wait — deferred until after the free GLM window ends on September 20.
- Previously completed Sprint 7 and Sprint 8 work — already verified, with no new reason to repeat it.
