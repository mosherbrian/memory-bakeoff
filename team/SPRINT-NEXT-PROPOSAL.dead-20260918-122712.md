SELECT: 1, 5
SPRINT-GOAL: Make the stale-path tests ready for use and establish whether three known source defects undermine findings Brian relies on.
WHY: Budget roughly two hours: 65 minutes for rank 1, 30 minutes for rank 5, and 25 minutes for independent confirmation; these are planning estimates for substantive work, not a target number of tasks. Follow the ranked order among work that can proceed, reusing rank 1’s existing assignment. Skip ranks 2–4 because the latest update overrides their earlier readiness claims: the duplicate detector refused their assignments, and the file explicitly forbids starting them without those assignments. Rank 5 has no unmet dependency; both selected candidates cost $0, while Brian-dependent, date-dependent, and metered work stays out.
OUTLINE:
## 1. THEME

First build tests of whether workers follow checked, current instructions, then determine whether three source defects affect existing research findings.

## 2. GOALS

**Goal 1 - As Brian, I can test whether a worker uses the current value after checking it, even when a plausible authority points to an obsolete path.**

The design is complete, but the two harder stale-path tests have not been built or run. Implement both cases: one keeps an obsolete value accessible after a required check returns the current value; the other adds a plausible authorizer’s instruction to use the retired path. Include the automatic protection against clues in the test wording revealing the answer; this builds and checks the test equipment without running a model experiment or claiming improved worker behavior.

Done when: `team/S9-STALEPATH-PROBES/check.py --selftest` passes, and corvid-dsh independently confirms that both cases require the checked current value and that the protection against answer-revealing clues works.

**Goal 2 - As Brian, I can see whether three known source defects change the findings used in my research decisions.**

Three questions remain open: inconsistent Habitus class labels, claims referring to different LongMemEval-S benchmark variants, and a Hindsight reference still pointing to a retracted figure. Read the available abstracts and repositories, record which existing findings each defect affects or leaves intact, and update the applicable automatic check, including the LongMemEval qualifier check where needed. This audits the supporting evidence; it does not rerun benchmarks, import outside scores, or turn unresolved claims into established facts.

Done when: `team/S9-PROVENANCE-CHASE/receipt.md` contains a source-supported conclusion or explicit unresolved limitation for each of the three defects, applicable check updates pass, and corvid-dsh independently confirms the conclusions.

## 3. WHO

kiln-flash implements one candidate at a time, completing rank 1 before starting rank 5. corvid-dsh independently checks both; no worker checks their own work, and shared requests remain serial.

## 4. NOT DOING

- Ranks 2–4: stronger retrieval pressure, ranking diagnostics, and evaluator safeguards — their work assignments remain blocked by the duplicate detector’s mistaken use of reused rank numbers.
- Outcome experiment — Brian has not decided campaign 2’s window and scope.
- SWE-chat acquisition — only 14 GB is free against a 39.3 GB full-set projection, pending Brian’s sampling decision or sufficient freed space.
- Standing research watch — the shared-request restriction does not lift until September 20.
- Keep-warm TTL rerun — the required full steady-pattern day on Muse cannot occur before the OpenCode Go reset.
- R-PC experiment-batch choice and R-PF adoption decision — these await GiLMore/Brian.
- MUSE ideation batch 7 — lower priority than the selected work and outside this sprint’s capacity.
- Remaining Engram work — the required capability remains unavailable.
- Metered experiments — deferrable spending stays outside the free GLM window ending September 20.
