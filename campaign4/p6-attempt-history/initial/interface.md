# Candidate adapter/reader interface (P6 Stage A)

Inherits the P5-r2 trusted boundary (recorded_at, bound actors,
derived/checked deadlines, epochs, atomic authority) unchanged; the only
new module is `src/host_adapter.py` (fake transports/timers/subscription).

## Host adapter (`HostAdapter(driver)`)

- `capture(package, attempt, action, event, execution, outcome, at_utc,
  observed_skew_s)` / `receipt(...)`: durable source receipts in
  `driver_kv`; persisted `host-cursor` survives restart.
- Identity: `register_execution`, `current_execution`,
  `apply_execution_result` (stale retained-not-applied),
  `resume_execution` (same IDs + resume relationship),
  `replace_action` (atomic supersedes note + new registration).
- Timers: `arm_from_ledger(timer_id, ledger_deadline, now)` (remaining
  duration; expired → owned `E_EXPIRED`); `FakeTimerService.fire`
  rejects stale/early/cancelled against the ledger deadline.
- Reconciliation: `reconcile_send` (delivered/queued-failed/ambiguous
  mapped to settled/hold/owned-failure — never blind retry);
  `escalate_unavailable` (bounded owned escalation, fake target).
- Observation: `FakeEventSubscription.tick(max_events=16)` — explicit,
  drained, model-free; absence is no-evidence, never completion.
- Effect allowlist (Stage A): fixture-owned seats/files/units/ledger ONLY,
  all fake. Real `wake`/`campaign4-pause` referenced by inventory hash,
  never executed here. Destructive/all-seat/Signal effects exist only as
  fake targets in tests.

## Latency instrumentation (for Stage C measurement)

Trusted `recorded_at` at ingress is the receipt clock; per-action
source→detection, detection→recovery/escalation, end-to-end keyed by
action ID. Gates (recovery ruling): explicit detection ≤30 s,
never-started suspicion ≤180 s, detection→recovery-or-acknowledged-
escalation ≤60 s (totals ≤90 s/≤240 s). Queued wake alone is neither
recovery nor escalation; outages/clock ambiguity never count as passing
samples.

## Reader

Unchanged ledger-authoritative supervision (REST/INVALID/ACTION_DUE) plus
SIMULATED-labeled status. Independent controller-health supervision does
not depend on the supervised process (separate module, separate state).
