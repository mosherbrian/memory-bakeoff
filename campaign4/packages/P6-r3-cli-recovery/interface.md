# Candidate adapter/reader interface (P6-r3 Stage A)

Inherits the r2.1 trusted boundary unchanged; the composition fix:

## CLI (`src/harness.py`)

- `setup --plan P --manifest M --session S --stream-key K`: manifest IDs
  bound from explicit evidence + durations/authorized dispositions from
  the plan; refuses without evidence args.
- `run-fixture [--live --plan P --plan-hash H --allowlist-seat S...]
  [--db D --manifest M --claims C --qid Q]`: full graph (dispatch →
  worker send → bounded subscribed wait → claim+artifacts → publish →
  verifier send → verifier end → authorized close/recovery → latency →
  outbox reconcile). Exits: 0 observed/recovered, 2 usage, 3 owned
  failure/no-end.
- Live mode: HostClock, production transports/timers, plan-hash-verified
  plan binding seats/units/wake path; fakes refused; missing pieces fail
  closed. `timer-callback --timer T` fires through ledger authority.

## Watcher/transports/timers/observer

- Same production branches under injected runners/files; exit 0 sent /
  3 queued / other failed / timeout-malformed ambiguous; kv-stable
  message identity; queued≠completion.
- Timer argv with executable candidate callback; shared unit identity
  for create/cancel/query; durable handled checks.
- Real ACP turn schema; cursor/binding/artifact verification;
  completion→`drive_next` through code; escalation ack evidence required.

## Reader

Unchanged ledger-authoritative supervision (REST/INVALID/ACTION_DUE) plus
SIMULATED-labeled status. Latency fields per action ID for the
30 s / 180 s / 60 s gates (totals 90 s / 240 s).

## Recovery additions (D1–D4 completion)

- D1: setup resolves launcher evidence (explicit args or exact evidence
  command) by creating per-seat stream surfaces; reuse rejected
  (E_BOUND_IN_USE); per-seat streams separate worker/verifier ends; wake
  texts carry plan-pinned task instructions.
- D2: `create_host` runs the configured runner with the candidate
  callback from the fixture path (unit identity shared).
- D3: `check-latency` subcommand enforces positive-sample +
  real-timestamp + denominator + gate rules with failing exits.
- D4: `rollback` subcommand reconciles units/IDs/receipts/intents,
  archives via SQLite backup, derives its report; any failure blocks it.
