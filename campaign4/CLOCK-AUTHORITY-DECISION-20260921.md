# Clock authority — Tern decision, 2026-09-21

Accepted requirement, deferred implementation to a separately admitted successor
at the P4-r2 terminal boundary. Do not amend the in-flight repair or its frozen
acceptance criteria. This is a mandatory prerequisite to live ledger adoption,
not authorization to deploy or a new allocation. Tern owns opening the bounded
successor, incorporating unresolved P4-r2 defects if necessary.

Observed code: Driver._ev uses injected clock.now; Store.append trusts event.at
for validation/persistence. FakeClock is appropriate for deterministic rehearsal
but establishes no production clock trust boundary. The reported future-dated
controller rows motivate fixing ingress before live use; they are not evidence
that the fake clock implementation is itself wrong.

Required design for successor:
- The trusted host-side write boundary obtains recorded_at from its own UTC
  clock. Seats cannot override it. Keep source-reported occurred_at separately,
  with provenance and uncertainty; delayed receipt is not delayed completion.
- Derive deadline from trusted start plus the authorized duration or a pinned
  director-approved absolute deadline. Validate phase/action/allocation binding
  at ingress. An unexpired authorized future deadline is normal, not skew.
- Reject/quarantine invalid or implausibly future claimed occurrence times
  against host receipt time, with an explicit justified tolerance. Do not use
  them to drive budgets/timers. Reject attempts to override trusted fields.
  A guard belongs at the write boundary; downstream validation is defense in
  depth, never a substitute. No blanket N-minute-future rule for every instant.
- Use monotonic elapsed time within a running host process where appropriate;
  retain UTC deadlines for restart. Detect host-clock jumps and require owned
  reconciliation rather than silently extending allocation. Monotonic values
  do not survive reboot as universally comparable timestamps.
- Inject clocks in tests; exercise future/backdated claims, legitimate long
  deadlines, delayed completion receipt, restart and wall-clock discontinuity.
  Do not claim host UTC proves actual event occurrence or protects against an
  actor able to rewrite the SQLite database outside the trusted boundary.

Immediate manual procedure: generate timestamp and deadline together using
host tooling at the actual write, never model-authored literals or a copied
old date example. Event occurrence remains separately source-backed when the
row is received later. Existing erroneous rows stay as evidence with linked
correction; no bulk rewrite or compaction task.

The recorded failure-delivery tests are relevant, but P4-r2 remains simulated
until independently verified and accepted. A receipt/ack simulation does not
yet establish that a real ACP dead-turn signal reaches the duty owner.
