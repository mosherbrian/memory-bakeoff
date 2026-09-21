# P4-r2-durable-events — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P4-r2-durable-events/package.md`,
  sha256 `ad6df34a599a41c622688cbc27e792b590122432091e1f0cd2f5e602b3196b8d`,
  commit `cdd0ee2fb21e61f3addf22bd29a4a3bcbd79c9d6` (re-derived; working tree
  matches)
- **Receipt:** `admission-receipt.json` (`bdb8db2a…`), start
  2026-09-21T22:06:56Z, deadline 2026-09-21T22:21:56Z

## Disposition

**ACCEPTED**, bound to the exact bytes above. The three claimed failures are
real and independently reproduced on the pinned parent; the required
correction is complete, bounded to event/durability handling, and does not
redesign the accepted core; inputs resolve; and the allocation arithmetic is
correct. This is admission, not execution verification.

## The three claimed failures are real (reproduced on pinned parent)

Against `campaign4/packages/P4-integration-rehearsal` at
`945e3384011962ac665905bd0b0d9278cbac0fd1` (working tree matches; `src/driver.py
4726a583…`, `tests/test_rehearsal.py 3838b03a…`):

1. **Stale worker deadline blocks CHECKING** — publish with a verifier action
   deadline, advance past the worker deadline but before the verifier deadline,
   then `on_deadline("w")`: observed `BLOCKED`, `stops=1 wakes=1`
   (`interrupted`). The stale worker deadline must not interrupt current
   verification.
2. **Early current deadline blocks before due time** — call `on_deadline` for an
   armed deadline at `now < deadline`: observed `BLOCKED`, `stops=1 wakes=1`.
   The callback must check current UTC time before acting.
3. **Reopen duplicates stop/wake** — handle a deadline, close the store, reopen
   a fresh `Driver`, re-arm, and call `on_deadline` again: observed a second
   `interrupted`, `stops=1 wakes=1`. Handled effects must be durable across
   reopen, not held in an in-memory set.

These match `director-event-probes.json` (pinned in the parent tree).

## Pinned inputs resolve

- Parent `945e338…` contains the P4 source/tests/fixtures/docs,
  `verification-v2.md` and `director-event-probes.json`; verified that the
  parent's `src/driver.py`/`tests/test_rehearsal.py` equal the present
  working-tree bytes.
- Original P4 contract `53c901bb…`/`c0f31dd0…`; P3-r3 accepted core
  `d27d5be…`; frozen P2 `5bfbb071…` — all resolve.
- Deployment addendum `campaign4/CONTROLLER-DEPLOYMENT-20260921.md` at
  `d087e87` resolves; the contract correctly states it governs real seat
  metadata without changing frozen behavior/pins.
- Prior-P4 `EXHAUSTED` disposition with successor `P4-r2-durable-events` is
  recorded (`P4-integration-rehearsal/acceptance-withheld.json`), satisfying the
  dispatch's release precondition.

## Contract validity

- **Task/evidence** (lines 6–11): repair event handling before live use; the
  prior stale-timer test called only the validator and the prior restart test
  never handled the same event across reopen — accurate and independently
  confirmed.
- **Completion requirements** (lines 22–48) are complete and testable:
  1. The deadline callback must check authoritative package/current
     action/phase/deadline and current UTC time before interrupting; removed,
     never-armed, old-generation/action, wrong-package and early callbacks
     cannot interrupt; worker completion rotates/cancels its timer and arms the
     current verifier or handoff deadline; restart reconstructs from ledger
     facts, not caller-supplied stale identities/deadlines.
  2. Action intents and handled/acknowledged external effects (stop/wake and
     `ACTION_DUE` reconciliation) must be durable; reopening fresh Driver and
     adapters cannot repeat acknowledged effects; external state must be
     simulated independently of the Driver; crash between intent/delivery/ack
     requires bounded owned reconciliation, never an unsafe exactly-once claim
     or blind replay; an in-memory set is explicitly not durable state; ledger
     facts stay authoritative; no automatic new attempt or budget reset.
  3. Reproduce all three probes on the pinned parent and correct them; test
     actual event delivery through reopened drivers and fresh fake adapters, not
     validator output or an in-memory set; include genuine due
     verifier/handoff/worker, cancelled/stale/early/wrong-package, repeat
     stop/wake/trigger across reopen, and interrupted effect acknowledgement;
     retain all 16 rehearsal and 59 core tests, the removed-timer regression,
     REST/INVALID semantics and no live effects; correct misleading tests
     without relaxing requirements; report to Tern before changing accepted core
     semantics (local driver persistence is in scope).
  4. Corvid independently tests the three parent/current cases and unshared
     cross-phase and crash-boundary cases with fresh temporary stores, verifies
     output hashes, durable recovery and no duplicate effects, and reports only
     executed evidence; simulated evidence never certifies live behavior.
- **Outputs/permissions** (lines 50–55): `src/`, `tests/`, `fixtures/`,
  `README.md`, `interface.md`, `rehearsal-report.md` here plus `/tmp`; stdlib
  only; fake time/adapters; no live subprocess/network/wake/stop/Signal,
  `state.json`, watcher/service edits, research, upgrade, prior-package edits or
  live rollout; no extra telemetry platform; explicit upstream-failure-event
  integration remains a future live requirement, not silently added.
- **Independence** holds: author/director Tern, reader/verifier corvid, worker
  kiln, controller/duty cairn; the reader did not author or repair this contract.

## Allocation

Prior P4 grants 83m56s worker (including the 1136 s infrastructure extension) /
40m verifier; this adds worker 30m + 15m = 45m and verifier 20m × 2 = 40m,
giving the stated cumulative **128m56s worker / 80m verifier** — arithmetic
correct, prior failures, late archive recovery, timing corrections and missing
timer-evidence deviations preserved, no reset. Admission ≤15m + one ≤10m
confirmation. Timeout stops overdue work, records BLOCKED and wakes Tern with no
automatic extension; controller-recovery verification ≤10m inside remaining
allocations.

## Non-blocking observations

- The parent's pre-repair archive is an after-the-fact reconstruction and no
  explicit repair-deadline timer evidence was located; both are already recorded
  as deviations in the parent's `version-reconciliation.json` and are preserved
  by this contract rather than re-litigated.
- The receipt records an acknowledged delivery (`wake: corvid -> started`),
  which is consistent with the admission actually running.

## Effect

Bound to contract bytes
`ad6df34a599a41c622688cbc27e792b590122432091e1f0cd2f5e602b3196b8d` at commit
`cdd0ee2fb21e61f3addf22bd29a4a3bcbd79c9d6`. Cairn may dispatch this exact
contract under the recorded conditional release once admission is recorded and
the pinned parent terminal disposition is present; changed bytes require
independent confirmation. No live effects.
