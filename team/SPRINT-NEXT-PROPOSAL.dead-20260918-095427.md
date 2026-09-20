SELECT: 7, 10, 11
SPRINT-GOAL: Give Brian independently checked evidence about missing instruction tests, fleet restart control, and whether useful retrieved information actually reaches the model.
WHY: These are the remaining unblocked candidates, in their existing rank order; ranks 2–5 were completed and independently confirmed in Sprint 7. Allow roughly 25 minutes for rank 7, 20 for rank 10, and 75 for rank 11: two hours of implementation, with the new measurement work making this more substantial than three small documentation tasks. Rank 1 still needs Brian’s campaign scope/window decision and the post-September-20 budget rule; rank 6 needs a storage or sampling resolution and the required co-signs. Rank 8 cannot start until after September 20, and rank 9 requires the OpenCode Go reset followed by a full steady-pattern Muse day. All selected work costs $0 and requires no metered model calls.
OUTLINE:

## 1. THEME
First identify missing instruction tests, then establish who restarts the fleet, then measure what retrieved information actually reaches the model.

## 2. GOALS

**Goal 1 - As Brian, I can decide whether HANDBOOK’s two documented failure classes belong in our instruction tests.**

Our existing tests may miss documented failures involving conflicting instructions and outdated instructions. Read HANDBOOK’s paper and Apache-2.0 repository, extract how the two failure classes are scored, and explain whether each applies to our tests. This produces a test design, not a new experiment run.

Done when: Brian can read how each failure is recognized and scored, whether it belongs in our tests, and the reason for that recommendation.

**Goal 2 - As Brian, I can know what restarts the fleet and whether its displayed status can become misleadingly old.**

The previous review left the 16:39:59 and 16:52:31 restarts unattributed and a remaining concern about outdated displayed status. Use system journals and polling configuration to identify who or what caused the restarts, and document whether the status problem is fixed or accepted with a concrete mitigation. This does not redesign the fleet’s restart system.

Done when: Journal evidence supports the restart attribution, and the status problem has a documented resolution or an explicit mitigation for its continued presence.

**Goal 3 - As Brian, I can see whether useful evidence reaches the model and how much irrelevant text accompanies it.**

Retrieval scores tell us what was found, but do not establish what the model actually received. Measure the exact text delivered by each existing adapter at a declared context budget, recording useful-evidence presence and irrelevant bytes both normally and under competing tool-output pressure. This adds a second measurement alongside Sprint 7’s external-corpus results; it does not import another benchmark’s scoring weights or claim that real task outcomes improved.

Done when: Reproducible results show both measurements for each adapter under both conditions, and the supplied automatic check passes.

## 3. WHO
kiln-flash implements one candidate at a time, with roughly two hours allocated across the three candidates. corvid-dsh independently checks each result; no worker checks their own work, and confirmation is required before calling it complete.

## 4. NOT DOING

- Rank 1, real-work outcome experiment — Brian’s campaign window/scope decision and the post-September-20 budget rule remain unresolved.
- Ranks 2–5, retrieval, composition, supersession, and KnowledgeDrift experiments — already completed and independently confirmed in Sprint 7.
- Rank 6, SWE-chat acquisition — the projected 39.3 GB corpus exceeds 15 GB free space, requiring a sampling decision or more storage plus the required co-signs.
- Rank 8, standing research watch — its start date is after September 20.
- Rank 9, keep-warm remeasurement — the OpenCode Go reset and subsequent full steady-pattern Muse day have not been established.
