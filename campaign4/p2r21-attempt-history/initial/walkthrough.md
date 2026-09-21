# Acceptance walkthrough — revision r2.1

Labels: **ACTUAL** (recorded history, cited), **SIMULATED** (constructed,
concrete path), **PROJECTED** (r2.1's own unfinished tail — not a receipt).
R1 stays EXHAUSTED; r2 was SUPERSEDED by the admitted amendment, its outputs
preserved at `164bd06`. No step may require an invented transition; row
numbers refer to `transitions.md`.

## 0. Actual chain r1 → r2 → r2.1 (ACTUAL)

- P2-specify: initial attempt + sole repair consumed, post-repair PASS
  (`49a52df6…`), Tern withheld acceptance (`acceptance-withheld.md`):
  rows 7/8/9/14 left two exits implicit → [9a] → **EXHAUSTED /
  specification not frozen**. Recorded reason
  (`failed-verification-no-allocation` class), owned by Tern.
- Tern opened warranted successor P2-r2 with explicit allocation (contract
  `3d25ab67…`): old revision EXHAUSTED linked, new revision DRAFT → admission
  ACCEPTED → REGISTERED (start 16:25:05Z, deadline 16:55:05Z) → RUNNING →
  kiln published five artifacts 16:31:06Z → timer retired, HOLD for the
  boundary amendment (no verification/repair/freeze per Brian's instruction).
  On the admitted amendment, live r2 → **SUPERSEDED** (`superseded.md`):
  unused repair/verifier allocations cancelled (not spent), 6m01s elapsed
  recorded, cost unknown preserved as unknown. Never an execution transition
  out of a terminal: r1 was already EXHAUSTED, r2 superseded from live-held —
  both dispositions recorded, both histories linked.
- This r2.1: DRAFT → admitted (`9e497dd5…`) → REGISTERED (start 16:42:21Z,
  deadline 17:12:21Z) → RUNNING (this specification). PROJECTED tail:
  publish six artifacts → CHECKING → corvid 20-min pass → COMPLETE or
  REPAIR_ALLOWED or BLOCKED per rows 7/8/9 — then a boundary declaration
  (row 17) commits state + disposition atomically. That close has not
  happened; it is projected, not claimed.

## 1. Successful — P1-inspect (ACTUAL, retained)

Contract `04afe817…` DRAFT → accepted with bounded pre-release correction
[1] → ADMITTED → authorization at `33d9a25a` [3] → REGISTERED (start
14:51Z, deadline 15:36:10Z) [4] → RUNNING → `capability-map.md`
(`b7279897…`) 14:53Z [5] → CHECKING → corvid PASS + Tern acceptance [7] →
**COMPLETE / positive finding**, then boundary `question_answered` (projected
shape — P1 predates the declaration schema; cited as precedent, not as a
schema-conformant record).

## 2. Valid negative (SIMULATED, retained)

Registration commit [3] → start with deadline [4] → RUNNING → artifacts [5]
→ CHECKING → evidence satisfies, bar missed [7] → **COMPLETE / negative
finding** → boundary `question_answered` with evidence_refs. Not exhaustion;
no repair spent.

## 3. Actual r1 director omission — FAILING example (ACTUAL event, schema verdict)

Tern wrote the EXHAUSTED disposition (`acceptance-withheld.md`) but opened no
successor; fresh file activity continued and the silence backstop, watching
activity, stayed quiet. Under this specification the campaign state at that
moment is: `terminal: {P2-r1: {state: EXHAUSTED}}` with **no disposition
key** → validation rule 3 → INVALID `missing-disposition`, wake Tern — fresh
activity explicitly satisfies nothing. **Recovery (ACTUAL):** Brian
intervened; Tern opened the warranted successor with explicit allocation
(r2, then this r2.1 amendment): the corrective chain is EXHAUSTED r1 →
`successor_opened: P2-r2` → SUPERSEDED r2 → `successor_opened: P2-r2.1` →
live work, each link recorded with decision refs — the boundary-schema
`successor-chain-live` shape. No historical BLOCKED verification event is
claimed: r1 never entered lifecycle BLOCKED; its failure was a missing
*boundary* disposition, not a missing *resumption*.

## 4. Blocked verification resuming within allocation (SIMULATED, retained)

CHECKING → hash mismatch on a referenced artifact [9] → BLOCKED record
(phase CHECKING, attempt identity, remaining verifier allocation) →
re-published bytes, recorded resolution [11] → CHECKING, same attempt, no
worker launch → evidence satisfies [7] → **COMPLETE** → boundary declaration
via row 17.

## 5. Expired verification deadline (SIMULATED, retained)

CHECKING → pass exceeds absolute deadline, no verdict [9] → BLOCKED
(remaining allocation zero) → no new allocation → [14] → **EXHAUSTED /
never completed**; or explicit Tern grant → row 11 → verdict. No silent
fresh deadline exists in the table.

## 6. Successful vs exhausted repair (SIMULATED pair, retained)

(a) Eligible defect, budget left [8] → REPAIR_ALLOWED → launched [10] →
attempt 2 → artifacts [5] → satisfies [7] → **COMPLETE**. (Actual historical
instances: P1's admission correction; r1's one-line fix.)
(b) Attempt 2 still fails, no allocation left [9a] → **EXHAUSTED**
(`failed-verification-no-allocation`). No automatic third attempt.

## 7. Amended — P1 admission correction (ACTUAL, retained)

DRAFT defect bounded by corvid; Tern's correction folded pre-release;
released contract `04afe817…`; old bytes in git history, no budget consumed —
rows [2]/[15]. The r1→r2→r2.1 chain (example 0) is the second, larger
amendment instance: question stable, revisions linked, budgets continued
under stable ids, terminals never rewritten.

## Completion-check verdict (worker-claimed, corvid to confirm)

- R2 conditions 1–5 hold as in r2 (row 9a; phase/identity/allocation in
  BLOCKED records; CHECKING return; precedence; continuity; r1 EXHAUSTED).
- Amendment conditions: (1) close requires explicit disposition + attributed
  decision + evidence, else state fault (rows 17–18, schema rules 1–3,
  example 3); (2) `successor_opened` needs an acknowledged bounded successor
  with finite deadline, unrelated seats do not satisfy, chains resolve to
  rest, cycles invalid (schema rules 4–5, examples 0/3); (3) the three rest
  kinds park with reason/evidence/trigger and no automatic successor
  (schema rest leaves, examples 1/2); (4) Tern decides, cairn solely
  writes/publishes/validates, atomic commit, immediate validation, no silent
  rest (transitions boundary section, ownership duties, schema rules 6–7);
  (5) all twelve example classes walked to unambiguous verdicts above and in
  `boundary-schema.md` (missing, dangling, unrelated, three rests,
  malformed/absent, stale activity, expired deadline, two-successor rest,
  cycle, interrupted publication); (6) the actual omission fails and its
  corrective chain recovers (example 3), no invented BLOCKED event, r2
  exhaustion/resume cases preserved (examples 0, 4–6), author contract compact
  (two bullets added across r2+r2.1, no new schema per package).
