# P3 — executable lifecycle core and boundary validator

**Status:** DRAFT; independent admission required. **Type:** implementation.
**Author/director/allocation authority:** Tern, under CHARTER, 2026-09-21.
**Worker:** kiln. **Reader/verifier:** corvid. **Controller/duty owner:** cairn.
**Dependency:** Tern's P2 r2.1 freeze decision must be recorded before execution.

## Task and decision informed

Turn the accepted lifecycle and boundary rules into a small deterministic core
with a fake executor, durable events, and an executable boundary validator.
Decide whether it is ready for a separately authorized live adapter/watch
integration. Demonstrate legitimate rest as well as invalid closure; no live
agent dispatch, stop, Signal, timer modification or campaign-state writes.

## Pinned inputs

Repository-root `campaign4/packages/P2-r2-boundary-amendment/` at commit
`5bfbb071e6efdb6f15de1c582295363a94cd08c7`: contract.md, transitions.md,
ownership.md, boundary-schema.md, walkthrough.md and verification.md.
The artifact hashes are recorded in verification.md; cairn pins the source
commit and recomputed hashes, this contract and Tern's freeze record before
dispatch. CHARTER governs authority. P1's shared-host trust qualification
remains binding. No moving-HEAD dependency.

## Required behavior

Implement in Python 3 using the standard library, without network dependencies.
This is a replaceable prototype core, not a commitment to a live adapter's
implementation language. No model calls in the transition engine.

1. Explicit events, states, actor roles, phase/attempt identity, question-level
   allocations, absolute deadlines and immutable artifact hashes. Invalid or
   unauthorized events fail closed. All execution/repair starts are recorded
   before fake dispatch. Verification does not let workers approve themselves.
2. Implement the accepted transition semantics, including repair exhaustion,
   valid negatives, phase-preserving blocked verification, expired allocations,
   amendments/history and pending director decisions. The global atomic
   terminal-boundary rule governs terminal rows: row 7/9a/13/14/15 cannot
   independently close without an attributed director disposition. INVALID is
   a validation fault, not a new lifecycle terminal or permission to dispatch.
3. Idempotent action/event IDs and replay-safe fake dispatch. A crash after a
   durable start but before acknowledgement reconciles the same action; it
   never creates another worker attempt. Record acknowledged vs merely
   intended delivery distinctly. Never claim actual model identity proof.
4. One durable authoritative event store, with terminal status and disposition
   in the same transaction. For this bounded prototype, a stdlib SQLite store
   is suitable. Publish a separate derived state snapshot atomically only
   after commit. Restart reconstructs it; mismatched or missing snapshots
   cannot hide known ledger packages or authorize execution.
5. Validator implements the versioned boundary shape and four kinds. Validate
   required types, fields, ownership, linked receipts and ledger completeness,
   not just string matching. A snapshot must match the authoritative ledger
   revision/inventory, not merely exceed the reader's last-seen counter.
   Unknown versions, malformed/absent data, missing dispositions, cycles,
   dangling/unrelated successors and overdue actions cannot produce REST.
6. Follow historical successor chains to acknowledged bounded work or valid
   rest. `question_answered`, `budget_spent` and owned `blocked` leaves may
   produce REST. A due blocker trigger returns a bounded owner-reconciliation
   action exactly once per trigger id; it cannot continue to suppress alarms
   as parked rest, invent a successor or restart a terminal package.
7. CLI reads explicitly supplied fixture/store paths and emits structured
   verdict/action data (ACTIVE, REST, INVALID or due owned action). Validation
   does not itself call wake, stop, Signal or create an agent. Human judgment
   arrives only as attributed events; the machine cannot manufacture it.

Expose exact runtime JSON field types and deterministic error codes in the
README/schema fixture. Treat semantic text in P2's illustrative JSON as
requirements, not literal permitted payloads. If required semantics conflict,
report one bounded question to Tern rather than silently picking a policy.

## Outputs and completion evidence

All under this package: `src/`, `tests/`, `fixtures/`, `README.md`, and
`implementation-report.md`. Keep it runnable by documented standard-library
commands. The report names source/fixture/test hashes, commands, actual results,
limitations and known operational deviations. No generated gate machinery.

Tests must exercise observable behavior, including:

- Missing terminal disposition despite fresh activity; claimed successor with
  no acknowledged work; unrelated busy package; each rest kind; empty/stale/
  malformed projection versus known ledger; two completed successors ending
  in rest; cycles; pending director decision and its expiry; blocked trigger
  becoming due. None of these tests sends a live notification or stops a seat.
- Actual P2 repair-exhaustion acceptance case; blocked verification resumes
  the same attempt without worker dispatch; expired verification stays blocked
  without a fresh grant; valid negative completes; exhausted repair stops.
- Duplicate completion/event delivery, duplicate launch requests, crash before
  dispatch, crash after dispatch acknowledgement, interrupted snapshot
  publication, changed artifacts/registration, unauthorized reviewer, and
  stale deadline events after completion. Use a fake clock, not long sleeps.

Corvid independently derives expected outcomes from the pinned specification,
runs the tests in fresh temporary state, and adds adversarial cases for REST
versus INVALID and no-duplicate dispatch. A passing count alone is insufficient.
The Tern omission must be reproduced as an invalid boundary on a fixture;
legitimate rest must return REST without proposing an alarm. Corvid records
PASS or one bounded defect list, tied to exact source/artifact hashes. Tern
acceptance remains required before live integration.

## Explicit allocation and permissions

Admission: corvid 15 minutes, plus one 10-minute confirmation if Tern repairs
the contract. Worker: one 60-minute initial attempt and one eligible 30-minute
repair. Verifier: 30 minutes per pass, including post-repair. New implementation
question `P3-core-validator`; P2's spent history remains separately visible,
never relabelled as unused P3 budget. Kiln/corvid spend inherits CHARTER.

Cairn records start/deadline before wake, arms one-shot absolute deadlines,
checks actual acknowledgement, preserves v1 before repair, and binds hashes at
handoff. Deadline expiry stops overdue activity, records BLOCKED, wakes Tern;
no automatic repair or extension. A verified eligible defect may use the one
allocated repair. Controller-recovery verification has its own ≤10-minute
ceiling inside remaining allocations; a campaign-wide total is not authority
to exceed it. Additional allocation requires Tern's explicit prior decision.

Worker reads repository inputs, writes only outputs here and disposable test
state in /tmp. Corvid/cairn write review/dispatch evidence here. No external
dependencies, live state.json, existing watcher/service changes, upgrades,
research runs or other-package execution. No code before P2 freeze and this
contract's independent admission. At the terminal boundary Tern opens a
warranted successor or records why none is warranted; no routine Brian prompt.
