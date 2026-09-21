# Candidate adapter/reader interface (P5 clock ingress)

## Clocks

- `HostClock.utc_now() -> "YYYY-MM-DDTHH:MM:SSZ"` (host UTC, read-only) and
  `monotonic() -> float`. Only code permitted to read host time; never sets it.
- `FakeTestClock` (ingress tests) and `FakeClock` (driver, coherent wall +
  monotonic; direct `now` assignment tracks mono so ordinary test time travel
  never mimics a discontinuity; `advance_wall_only` / `advance_mono_only`
  inject genuine jumps). All test time is injected; no sleeps.

## Trusted ingress (`src/ingress.py`)

- `TrustedIngress(store, clock, kv_put, kv_get, epoch=None).append(event,
  budget, atomic, grants)` / `.record_terminal(v, d, budget, grants)`:
  stamps `receipt {recorded_at, occurred_at, provenance, skew_s, epoch}`,
  overwrites legacy `at` (caller value kept as `caller_at_ignored`),
  derives start deadlines (`duration_s` default per action, or absolute
  pinned `grant_ref`), persists receipt in the event body (replay-unchanged).
- Error/owned dispositions: `E_FORGED_RECEIPT` (owner tern), `E_DEADLINE_FORGE`
  (tern), `E_BAD_DURATION` / `E_ALLOC_EXCEEDED` / `E_GRANT_UNKNOWN` /
  `E_GRANT_MALFORMED` / `E_GRANT_EXPIRED` / `E_GRANT_MISMATCH` /
  `E_BAD_DEADLINE` (cairn), quarantines `E_BAD_OCCURRED` / `E_SKEW_EXCEEDED` /
  `E_DISCONTINUITY` (cairn, with evidence; lifecycle untouched).
- `reconcile_clock(note, owner)`: bounded post-anomaly reconcile; new epoch,
  deadlines unchanged. `Driver.pin_grant` persists grants across restart.

## Tolerances (finite, justified)

- `FUTURE_SKEW_TOLERANCE_S = 120`: honest NTP (<1 s) + provisioning/delivery
  latency (seconds) pass; the observed +32 min future-dating exceeds it 16x.
  No blanket N-minute rule for every instant — this tolerance applies only to
  source-reported occurrence vs trusted receipt, never to deadlines.
- `DISCONTINUITY_THRESHOLD_S = 60`: catches manual steps / large NTP
  corrections; tolerates drift and scheduling jitter.

## Reader

Unchanged ledger-authoritative supervision (`E_OVERDUE_ACTION` still fires on
stale snapshots regardless of ingress) plus SIMULATED-labeled status reports.
No alternate public write path: `src/driver.py`, `status.py`, `supervisor.py`
contain no `store.append(`/`store.record_terminal(` (enforced by test).
