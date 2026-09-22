# P6-r4-notify-timer-drain — three-case expected-call/output checklist

- **Author:** corvid (independent reader; fixes observables, not implementation)
- **Date:** 2026-09-22; pinned before worker dispatch
- **Contract:** `c5725d291c43…` @ `214e73c`; base parent `4b02d0a…`; parent
  verdict `3cc00b9e…`
- **Rule:** all three are **BLOCKING**. Each case lists expected calls/events and
  output, positive and negative. Grading is on the exact shipped CLI plus the
  production notification private-file test — not helpers or fake counters.

## N — notification-backed wait (not periodic polling)

**Positive**
- Instantiate the **production** notification class on a private `/tmp` worker
  stream; start the wait; **after** the wait starts, append an actual-format
  runtime `end` record.
- Expected calls/events: the OS/runtime notification primitive fires; the
  persisted drain reads the record; the end is observed **without** any
  periodic `time.sleep` scan proving the wake; `detected_at` is recorded from the
  trusted receipt clock; the verifier stream is exercised the same way on a
  **distinct** stream; the exact CLI reaches `terminal-rest`.
- Expected output: `transition-committed`/`terminal-rest`; the subscribe/read
  race is closed by attaching the watcher **before** the initial drain
  (a startup-existing event is still observed exactly once).
- Also expected: bounded wait timeout, cancelled-watcher handling and file
  descriptor cleanup are proven; injection does **not** bypass the production
  subscription path.

**Negative**
- No event → bounded owned timeout failure with **nonzero** exit, no invented
  success; partial record held (no advance past it); truncation/rotation,
  overflow/loss and restart reconcile with the durable cursor and do not lose or
  duplicate a handoff.

## T — enforced host timer with a stable action→unit mapping

**Positive**
- The bound plan/manifest declares one stable action→unit mapping used
  consistently by create/query/cancel/callback.
- Exact CLI trace contains a `systemd-run --user --unit=<mapped unit>
  --on-active=<remaining authorized duration> <executable candidate callback>`
  call, followed by the correct query and cancel of the **same** unit.
- Expected output: the timer is created with the remaining authorized duration
  and an executable callback (not `true`); after reopen, the callback fires
  through ledger authority exactly once and duplicate/stale/early/cancelled
  callbacks are rejected.

**Negative**
- Unit not allowlisted → owned failure (`E_DISABLED`, exit 3); no success claim;
  already-delivered work is reconciled.
- Runner failure → owned failure (`E_TIMER_CREATE`, exit 3).
- An in-memory `FakeTimerService.create` alone is **never** accepted as a real
  timer or a supervised backstop.

## O — delivered-outbox drain (settle only on proof)

**Positive**
- Exact CLI → verifier receipt → `terminal-rest` → restart → `rollback`.
- Expected calls/events: transport acknowledgement **and** actual verifier
  start/outcome evidence are correlated to the exact
  action/execution/message; only then is the matching durable intent settled.
- Expected output: rollback reports **zero** unresolved delivered intents, no
  second send, verified unit cleanup and a consistent archived ledger.

**Negative**
- Ambiguous/queued delivery leaves the intent **pending** and rollback
  **BLOCKED** (`E_ROLLBACK_BLOCKED`); terminal phase alone does not forge
  acknowledgement.
- Crash before/after external delivery and before/after local ack reconciles the
  **same** identity (no blind resend, no premature clear, no duplicate effect).

## Retention

Parent C1–C12 and 156+59 semantics are retained; changes are confined to the
connected N/T/O paths and supporting plan/tests/docs. If a gate is not
implemented, the verifier reports FAIL/incomplete rather than a
forward-item/nonblocking note.
