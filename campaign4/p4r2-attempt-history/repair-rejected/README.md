# P4-r2 durable events (SIMULATED)

Repairs the P4 integration rehearsal's event handling (parent
`campaign4/packages/P4-integration-rehearsal` at `945e3384`, bytes kept;
accepted source never modified). Baseline core/store/validator/supervisor/
status copied verbatim into `src/`; only `src/driver.py` is new repair scope
plus tests.

What was wrong (director probes, reproduced on parent): a stale worker
deadline interrupted CHECKING; an early current-deadline callback interrupted
before due time; reopening plus replaying a handled deadline issued another
stop/wake (handled state was an in-memory set).

What changed: `on_deadline` checks authoritative ledger facts (package,
current action, phase, deadline) and current UTC time before any interrupt or
external action; worker completion rotates/cancels its timer and arms the
current verifier/handoff deadline from ledger facts; restart reconstructs
timers from ledger facts only. Intents and handled/acked stop/wake/trigger
effects persist in a `driver_kv` table in the same SQLite database; fresh
Drivers with fresh adapters cannot repeat acknowledged effects. External
delivery is simulated by `FakeExternalWorld`, held independently of any
Driver (optionally file-backed under /tmp). Crash ambiguity holds for owned
reconciliation — no exactly-once claim, no blind replay, no new attempt.

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (28 tests, fake time only).
Accepted core suite: 59 passed. No Brian notification; duty cairn /
escalation tern appear as fake output only. Simulated evidence never
certifies live behavior.

## Sole repair (D1 + D2)

- D1: `on_deadline`/`on_handoff_deadline` durably intend each effect before
  its external call and separately ack each world receipt after it. Replay
  reconciles per effect: delivered-but-unacked effects are acked, never
  resent; pending effects complete. `Driver.crash_points` (+ SimulatedCrash)
  is a rehearsal-only hook to crash after each call; production paths leave
  it empty.
- D2: supported cancellation is `cancel_deadline(action, qid, owner,
  reason)` — durable, survives reopen, distinct from accidental timer loss
  (which reconstructs the still-valid ledger deadline). Bare
  `timer.remove()` is process-local only. Cancellation never clears the
  ledger flight/deadline, so supervision still flags overdue work.
