# P2 r2.1 — declare terminal boundaries and legitimate rest

**Status:** DRAFT; independent admission required.
**Question:** P2-specification; revision r2.1, amendment of live r2.
**Author/allocation authority:** Tern under CHARTER and Brian's new requirement.
**Reader/verifier:** corvid. **Worker:** kiln. **Controller/duty owner:** cairn.
**Type:** judgment; specification only, no controller implementation.

## Task and decision

Complete the r2 transition-gap work and specify a machine-readable terminal
boundary declaration that distinguishes a missed director handoff from a
legitimately resting campaign. Decide whether the complete specification can
be frozen and a separately admitted implementation package can start.

Observed evidence: Tern exhausted P2 r1, wrote a disposition and failed to open
the warranted successor. Fresh file activity hid the missing handoff from the
silence backstop. Brian intervened. A requirement that a successor always be
running before closure is rejected: legitimate completion must remain possible
without inventing work. This requirement arrived after r2 admission and launch
(16:25:05Z), so it is an explicit amendment, not a hidden change to that run.

## Inputs and preservation

- Prior r2 contract at `557083bd34300ddb6c924eae43d78e15f24578d0`,
  `campaign4/packages/P2-r2-complete-transitions/package.md`, SHA256
  `3d25ab67376866ff09e97c22497cce751aca2060ac945c02b0497da264f14de1`.
  Its five completion conditions remain required here.
- All architecture, r1 and director-decision pins named in that contract remain
  binding. Brian's boundary instruction is in CHARTER at the same commit.
- r2's current five outputs and dispatch record: cairn must first collect and
  pin their exact bytes, full commit and hashes, without calling them accepted.
  If r2 does not finish within its existing 16:55:05Z bound, stop and preserve
  its partial artifacts and failure evidence instead. No new r2 repair or
  verification is authorized after this amendment instruction.
- `boundary-design.md` here is Tern's proposed design, independently reviewed
  with this contract; pin its commit and hash before amended execution.

r1 remains EXHAUSTED. Live r2 becomes SUPERSEDED only after its running attempt
has ended or been stopped and evidence has been captured. If it became terminal
before reconciliation, preserve that terminal status and link the successor;
never add an execution transition out of a terminal. Record actual r2 effort
and close unused allocations without claiming they were spent.

## Outputs

Here write `contract.md`, `transitions.md`, `ownership.md`, `walkthrough.md`,
`changes.md`, and `boundary-schema.md`. The last specifies exact JSON structure,
enums, validation rules and concrete valid/invalid examples; it is a controller
state interface, not bespoke gate-writing for individual packages.

Extend the r2 candidate minimally. Keep immutable old outputs outside this
directory. No watcher or controller code under this contract.

## Independent completion check

Corvid checks the full result against all five r2 completion conditions and:

1. A package cannot validly close without an explicit enumerable disposition,
   attributable director decision and evidence. A missing declaration is a
   state fault regardless of fresh file activity or an active seat.
2. `successor_opened` identifies the specific successor and observable in-flight
   work with an acknowledged dispatch and finite deadline. An unrelated busy
   seat/package does not satisfy it. A missing, never-dispatched or broken
   successor reference is invalid. Completed successor chains may reach valid
   rest without leaving permanent historical alarms; cycles are invalid.
3. `question_answered`, `budget_spent`, and owned `blocked` can mean legitimate
   rest with no work in flight. They carry the required reason/evidence and,
   for blocked, a resolvable blocker and explicit resumption trigger. Before a
   valid trigger/revisit deadline, rest must not enter the generic silence
   ladder. No automatic successor is required or authorized.
4. Specify exactly who decides, who writes, when terminal state and disposition
   become committed, one authoritative location, atomic publication/recovery,
   and immediate boundary validation. Missing/unreadable/malformed/incomplete
   state never silently passes as rest. Verify completeness against the ledger;
   an empty declaration cannot hide known terminal packages.
5. Cover concrete examples of missing disposition; claimed-but-absent successor;
   unrelated in-flight work; each legitimate rest kind; malformed/absent state;
   stale file activity; expired in-flight deadline; two completed successors
   ending at rest; cycle; and an interrupted atomic publication. Expected
   verdict/action must be unambiguous without prose interpretation.
6. Show actual r1 director omission as a failing example and its corrective
   successor chain as recovery. Do not invent a historical BLOCKED verification
   event. Preserve the r2 exhaustion/resume cases and compact author contract.

Tern's acceptance, after independent hash-bound PASS, freezes the documents.
An admitted contract or worker-written “frozen” heading does not.

## Explicit incremental allocation and handoff

- Corvid admission: 15 minutes, plus one 10-minute confirmation if Tern repairs
  the contract. No execution before independent acceptance of exact bytes.
- Kiln: one 30-minute initial attempt plus one eligible 15-minute repair.
  Corvid execution verification: 20 minutes per pass, including post-repair.
- Historical r1+r2 grants: at most 135 worker and 100 execution-verifier
  minutes. This adds 45 worker and 40 verifier minutes: historical cumulative
  grants 180/140. Report cancelled unused r2 allocations separately; actual
  cost/time remain separate from ceilings and unknown cost remains unknown.
  No question/history reset. r1's repair remains spent; r2's executed attempt
  remains counted. No extra external spend or service is authorized.
- Cairn pins inputs, writes start/deadline before dispatch, arms absolute
  one-shot wakes, verifies acknowledged delivery and binds all outputs before
  verification. Redelivery retains the same attempt/deadline. Never poll.
- Timeout: stop overdue activity, BLOCKED with evidence, wake Tern. No automatic
  repair on timeout. One eligible defective-output repair is allocated above;
  after it is spent no further execution is automatic.
- At the terminal boundary Tern opens a warranted successor with explicit
  authorization or records why none is warranted. She does not wait for Brian.
  Today's machinery allocation and the two hard stops remain binding.

## Permissions

Read repository sources and read-only host configuration for comparison;
worker writes only the six outputs here. Cairn/corvid write their manifests,
dispatch/review evidence here. No modification of previous revisions, live
watcher, state.json, system services, controller code, upgrades or research.
