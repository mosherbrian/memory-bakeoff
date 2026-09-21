# Acceptance walkthrough — revision 2

Each example is walked through `transitions.md` (row numbers in brackets).
Labels: **ACTUAL** (recorded history, hashes/dates cited), **SIMULATED**
(constructed branch, concrete path chosen), **PROJECTED** (r2's own unfinished
tail — not a receipt or self-certification). R2 freezes only after corvid
verification and Tern's acceptance. P2 r1 stays EXHAUSTED; nothing here
rewrites it.

## 1. Successful — P1-inspect (ACTUAL, retained)

Contract `04afe817…` DRAFT → corvid admission review accepted with a bounded
pre-release correction [1] → ADMITTED → authorization + version at `33d9a25a`
[3] → REGISTERED → cairn recorded start 14:51Z, deadline 15:36:10Z, dispatched
kiln [4] → RUNNING → `capability-map.md` (`b7279897…`) published 14:53Z [5] →
CHECKING → corvid PASS (`98201be9…`, in bound), Tern accepted [7] →
**COMPLETE / positive finding**. No repair, no block; history intact.

## 2. Valid negative — scored experiment row (SIMULATED, retained)

Registration commit (criteria, numeric bar, pinned inputs) [3] → start with
deadline recorded before dispatch [4] → RUNNING → artifacts published [5] →
CHECKING → evidence satisfies the contract, treatment misses the bar [7] →
**COMPLETE / negative finding**. The negative finishes the job; it is not
exhaustion and spends no repair. Changing the bar afterward would be row 15
(new exploratory row), never a repair.

## 3. Actual P2 r1 exhaustion (ACTUAL)

P2-specify DRAFT → admitted (`30f98fd5…`) [1] → REGISTERED at dispatch
(start 15:08:16Z, absolute deadline 16:08:16Z) [4] → RUNNING → kiln published
four artifacts 15:12:43Z [5] → CHECKING → corvid FAIL (single-value deadline
defect, `3cb6847d…`) → eligible defect, repair budget unspent [8] →
REPAIR_ALLOWED → repair recorded and launched [10] → RUNNING → one-line fix
published 15:57:00Z [5] → CHECKING → corvid post-repair PASS (`49a52df6…`)
— but Tern **withheld acceptance** (`acceptance-withheld.md`): the table's
rows 7/8/9/14 did not explicitly handle failed-verification-with-no-allocation
or blocked-verification resume, so the readiness claim was not established.
Initial attempt + sole repair consumed, no allocation left → [9a] →
**EXHAUSTED / specification not frozen** (`acceptance-withheld`,
`failed-verification-no-allocation` class: post-repair PASS authentic as
bounded-repair evidence, full acceptance condition unmet). Tern recorded the
terminal disposition and opened this warranted successor (r2) with an explicit
new allocation — exactly the row-9a behavior: owned, recorded, no silent
retry, r1 not rewritten.

## 4. Blocked verification resuming within allocation (SIMULATED)

CHECKING → verifier finds a referenced artifact hash mismatched (integrity
impediment) [9] → BLOCKED, record carrying originating phase CHECKING,
attempt identity (attempt 1, launcher-bound actor), remaining verifier
allocation (e.g. 18 of 30 min) → artifact re-published by the worker's
already-completed attempt (no new dispatch — the bytes were missing, not the
work) → recorded resolution [11] → **return to CHECKING under the same
attempt identity**, verifier resumes inside the original 30-min grant →
evidence now satisfies [7] → **COMPLETE**. No worker launch, no new attempt
number, no budget reset — the step r1 row 11 forbade by restricting return to
REGISTERED/RUNNING.

## 5. Expired verification deadline (SIMULATED)

CHECKING → verifier pass exceeds its absolute deadline with no verdict [9]
→ BLOCKED (originating phase CHECKING, remaining verifier allocation zero) →
Tern records no new allocation → [14] → **EXHAUSTED / never completed**
(`why_ended: verification never completed`). The alternative concrete path, if
Tern explicitly grants 10 more verifier minutes with reason recorded, is row
11 → CHECKING → verdict. What cannot happen: the same pass silently acquiring
a fresh deadline and reporting PASS — the table has no such transition, and
row 11's return requires remaining or explicitly allocated time.

## 6. Successful vs exhausted repair (SIMULATED pair, one path each)

(a) **Successful:** CHECKING → eligible implementation defect, repair budget
left [8] → REPAIR_ALLOWED → recorded, launched [10] → RUNNING (attempt 2,
spend carried) → artifacts published [5] → CHECKING → evidence satisfies [7]
→ **COMPLETE**. (P1's admission correction and P2 r1's one-line fix are the
actual historical instances of this shape at their respective stages.)
(b) **Exhausted:** CHECKING → repair consumed (attempt 2 published) →
evidence still fails the contract → no allocation left [9a] → **EXHAUSTED**
(recorded reason `failed-verification-no-allocation`). No third attempt is
automatic; only an explicit new allocation (a successor revision like this
r2) can continue the question.

## 7. Amended — P1 admission correction (ACTUAL, retained)

P1's DRAFT carried a defect corvid bounded (count bound, no wall-clock bound,
no overdue actor). Tern's correction folded in pre-release; reviewed bytes +
correction became the released contract (`04afe817…`); old bytes survive in
git history, revisions linked, no budget consumed — rows [2]/[15]. Had the
question itself changed, the old revision would have gone SUPERSEDED with
evidence preserved and cost history under the stable question id.

## Completion-check verdict (worker-claimed, corvid to confirm)

- Failed verification / withheld acceptance with no allocation has the
  explicit owned recorded terminal path (row 9a, example 3); a valid negative
  still completes (row 7, example 2).
- BLOCKED records phase, attempt identity, remaining allocation (row 9);
  resolved verification blocks return to CHECKING without a worker launch
  (row 11, example 4); expired verification needs termination/exhaustion or
  explicit allocation (examples 5, notes).
- Deadline, integrity, invalid-measurement, repair, and repair-exhaustion
  events have ordered destinations (precedence note); every nonterminal has
  exits; terminals have no execution transition; each dispatch records its
  start before launch (rows 4/10, examples 1/3).
- The actual r1 exhaustion plus blocked-resume, expired-verification, and
  both repair outcomes are walked to concrete terminals on table rows only;
  successful, negative, and amendment cases retained; labels honest.
- Budget/history continuity, independent review, compactness, trust limits,
  and both ownership decisions intact; r1 remains EXHAUSTED.
