# Acceptance walkthrough — Tern's evidence

Each example is walked step-by-step through `transitions.md` (row numbers in
brackets). Real history is labeled **ACTUAL**; constructed branches are
labeled **SIMULATED**; P2's unfinished tail is labeled **PROJECTED** — a
walkthrough is not an execution receipt or self-certification, and P2 freezes
only after corvid verification and Tern's acceptance.

## 1. Successful — P1-inspect (ACTUAL)

P1 ran the full table with no repair. Contract `04afe817…` DRAFT → corvid
admission review accepted with a bounded pre-release correction folded in
[1] → ADMITTED → authorization + version recorded at `33d9a25a` [3] →
REGISTERED → cairn recorded start 14:51Z with deadline 15:36:10Z and
dispatched kiln [4] → RUNNING → kiln published `capability-map.md`
(`b7279897…`) at 14:53Z, cairn bound contract+output hashes and handed to
corvid [5] → CHECKING → corvid PASS (`98201be9…`, within the 20-min bound),
Tern accepted (`acceptance.md`) [7] → **COMPLETE / positive finding**.
No row 8, no row 6, history intact. Binds at: start-before-dispatch [4],
publish-before-transition [5], hash-bound handoff, independent receipt [7].

## 2. Negative — scored experiment row (SIMULATED)

A memory-on/off pair registers criteria, numeric bar, pinned inputs as its
own commit [3] → REGISTERED → start recorded with deadline [4] → RUNNING →
artifacts published [5] → CHECKING → evidence satisfies the contract but the
treatment misses the bar: eligible, valid, negative [7] →
**COMPLETE / negative finding**. The negative finishes the job (contract.md:
completion ≠ success); it is a finding, not an EXHAUSTED row, and no repair
is spent chasing a better number — changing the bar now would be row 15, a
new exploratory row, never a repair.

## 3. Blocked — hung attempt (SIMULATED, with P1's real deadline machinery)

Worker dispatched with a 45-min one-shot deadline [4] → RUNNING → no
artifacts by the deadline; cairn's timer fires, the seat is stopped, BLOCKED
recorded with reason and evidence [6] → BLOCKED. Two exits walked:
(a) recorded resolution (host recovered, attempt still within budget) →
return to RUNNING as a new attempt number, spend carried [11] → artifacts →
CHECKING → defect ineligible (environment, not implementation) → BLOCKED [9]
→ budget exhausted with `why_ended: never_completed` [14] →
**EXHAUSTED / inconclusive**. Expiry never spent the repair; no step reset
the count; the seat being alive at expiry discharged nothing (transitions.md:
liveness section). Cairn's own recovery, if any, runs inside the ≤15+≤15
per-incident ceiling and, if unverifiable, stays BLOCKED → Tern.

## 4. Amended — P1's admission correction (ACTUAL) + P2's tail (PROJECTED)

P1's contract reached DRAFT with a defect corvid bounded: attempt count with
no wall-clock bound and no overdue disposition (`admission-review.md`). Tern's
correction (deadlines, cairn as overdue actor, BLOCKED disposition,
`admission-20260921.md:15-20`) was folded into the contract text pre-release;
the reviewed bytes plus the correction became the released contract
(`04afe817…`, dispatch record). Old bytes preserved in git history, revisions
linked, no budget consumed — a DRAFT-stage revision under rows [2]/[15]:
had the question, population, or acceptance criteria changed instead, the old
revision would have gone SUPERSEDED with evidence preserved and cost history
surviving under the stable question id, and the new revision would re-enter
at DRAFT. **P2 PROJECTED tail:** this specification is at RUNNING (start
15:08:16Z, deadline 16:09:31Z); on publication cairn binds all four hashes →
CHECKING → corvid 30-min pass → COMPLETE or REPAIR_ALLOWED or BLOCKED per
rows [7]/[8]/[9]. That terminal step has not happened; it is projected, not
claimed.

## Completion-check verdict (worker-claimed, corvid to confirm)

- Every nonterminal state above has an exit; terminal states (COMPLETE,
  EXHAUSTED, TERMINATED, SUPERSEDED) have no outgoing execution transition —
  rows 12–14 originate from BLOCKED, row 15 from a live revision, never from
  a terminal.
- The amendment path exists (row 15, example 4) and budgets continue under
  the stable question id — no reset.
- Every role's "may not" is stated (`ownership.md` table, column 4).
- All four examples reach a terminal state using only table rows.
