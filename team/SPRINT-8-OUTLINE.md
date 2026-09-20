# SPRINT 8 OUTLINE - the agreed work, 2026-09-17

Written to be decided from one read. Selected by the planner from the
candidates in `BACKLOG-NEXT.md`; the machine-readable decision is in
`SPRINT-8-PROPOSAL.md`. Tracker ids in parentheses are bookkeeping for the
fleet - every sentence stands without them.

## 1. THEME

Sprint 8 tests whether combining memory retrieval systems and adding a small state layer improve memory behavior, checks performance on independently created fixed test worlds, and closes the agreed design and operations follow-ups.

## 2. GOALS

**Goal 1 - As Brian, I can know whether filtering common words fixes bm25’s unnecessary memory retrieval.**

Previously, bm25 retrieved useful memory in all 5 cases that needed it but also retrieved memory in all 5 cases that required no retrieval. This work declares the common-word filter before repeating the same tests, then supplies the result to Goal 2. It does not adjust the filter after seeing the results (S8-1).

Done when: The declared filter and repeatable before-and-after results show whether bm25 avoids unnecessary retrieval while preserving useful retrieval.

**Goal 2 - As Brian, I can know whether pi-lcm and bm25 work better together than separately.**

Previously, pi-lcm correctly declined retrieval in all 5 no-retrieval cases but found useful memory in only 1 of 5 retrieval cases; bm25 found useful memory in all 5 but retrieved unnecessarily in the other 5. This work uses pi-lcm to decide whether to retrieve and bm25 to find the memory, applying Goal 1’s findings and comparing all three arrangements on the same fixed test collection. It is a local experiment without language-model calls, not a production integration (S8-2).

Done when: Repeatable results show how the combination compares with each system alone on both useful retrieval and correctly declining retrieval.

**Goal 3 - As Brian, I can know whether a small state layer reduces mistakes about which memories are still valid.**

Under distracting information, agentmemory incorrectly treated still-valid memories as replaced in 418 of 450 cases, or 92.9%; pi-lcm has no equivalent measurement yet. This work compares pi-lcm’s own storage with a small layer that marks older information as replaced when newer information is written, using the existing stress-test method. It measures this specific behavior without building a full state-management system (S8-3).

Done when: Repeatable results report how often each pi-lcm arrangement incorrectly replaces valid memories, alongside the existing agentmemory comparison.

**Goal 4 - As Brian, I can know how our memory systems perform on independently created test worlds.**

Our systems have not yet run on KnowledgeDrift’s fixed `worlds/v2` test worlds, so our conclusions still lack this independent comparison. This work runs those tests locally and calculates results separately for each test family, carrying forward the documented limitations of using KnowledgeDrift. It does not import leaderboard scores or treat these results as interchangeable with our existing tests (S8-4).

Done when: Results identify the fixed worlds and seeds used, show newly calculated scores for each test family, and explain the limits on what those scores establish.

**Goal 5 - As Brian, I can understand how two documented instruction failures should inform our tests.**

Our test design has not yet incorporated HANDBOOK’s two failure classes concerning standing rules versus requests encountered during work, and outdated instructions. This work reads the paper and repository, extracts the scoring rules, and explains whether and how each failure class applies to our tests. It produces a design only and does not run an experiment (S8-5).

Done when: A written design describes both failure classes, their scoring rules, and the reason for including or excluding each from our tests.

**Goal 6 - As Brian, I can know what restarts the workers and whether their status summary can be trusted to be current.**

The source of the controlling process’s clean restarts remains unattributed, and an outdated status summary remains an unresolved issue. This work examines system logs and polling configuration, including the recorded restarts at 16:39:59 and 16:52:31, and records whether the stale summary is fixed or accepted with a specific mitigation. It addresses these two operations issues without expanding into a broader infrastructure redesign (S8-6).

Done when: Log evidence identifies who or what initiated the restarts, and the status-summary issue has a documented fix or an explicit mitigation.

## 3. WHO

kiln-flash builds the six items sequentially, one at a time, in the order above. The implementation budgets are approximately 15, 25, 25, 35, 10, and 10 minutes: two hours total, with $0 spending.

corvid-dsh independently checks each result. Automatic checks must be written from the agreed requirements before examining the implementation, test the substance of the work, and demonstrate that they accept a valid example and reject an invalid one (S8-1G, S8-2G, S8-3G, S8-4G, S8-5G, S8-6G). No one checks their own work.

## 4. NOT DOING

- Real-work outcome experiment: Brian’s campaign scope and timing decision and the budget rule after September 20 remain unresolved.
- SWE-chat acquisition and labeling design: download and storage budgets and the required three joint approval conditions are not established.
- Ongoing external research watch: it cannot start until after September 20.
- Keep-warm timing remeasurement: the OpenCode Go reset and a full day of steady Muse activity have not occurred.
- Measuring the exact context delivered to the model: the undeveloped measurement work exceeds the capacity remaining after the selected work.
