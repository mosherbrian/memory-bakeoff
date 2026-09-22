# Candidate adapter/reader interface (P6-r2 Stage A)

Inherits the P5-r2 trusted boundary unchanged; new/rewritten surface:

## Entrypoint (`src/harness.py`)

- `build_adapter(db_path, clock, live, plan_hash, allowlist_seats,
  wake_path, transport, timers, observer)`: live mode requires a bound
  plan hash + non-empty allowlist + non-fake collaborators (fail-closed
  otherwise); Stage A injects fakes/runners.
- `run_step(adapter, spec)`: dispatch → send → capture → arm-timer →
  observe → reconcile → outcome record with latency fields.
- `timer_callback(db_path, timer_id, qid, action_id)`: executable unit
  callback firing through ledger authority. CLI: `harness.py [--live
  --plan-hash H --allowlist-seat S...] [--db PATH] timer-callback
  --timer T`.

## Transport (`HostWakeTransport`)

- Injectable `runner` (subprocess-compatible); real kwargs incl.
  `AGENTDECK_PROFILE=campaign4`; `command_for(seat, text)` exact argv.
- `send(..., action, execution)` persists `msg:<id>` receipts;
  `state(mid)` stable across instances. Queued/sent hold; delivered
  settles; failed is an owned dead-turn; ambiguous never redispatches.

## Timers (`HostTimerService`)

- `create_host(timer, deadline, delay_s, callback_argv)` (exact
  systemd-run argv, armed record persisted); `cancel_host` (stop +
  reset-failed by the same unit identity, durable cancel);
  `query_host` (ActiveState/SubState parse). Durable handled/stale/
  early/cancelled checks inherited; restart-safe.

## Observer (`ACPOutcomeObserver`)

- Real schema: turn rows `kind/id/status/at`; message rows skipped as
  partial. `observe(cursor_bytes)` → `(outcomes, new_cursor, note)` with
  truncation-reset and rotation-unavailable notes.
- Adapter: `bind_session`, `observe_bound` (binding match or stale
  retention), `verify_artifacts` (hash-equality or structural-presence),
  `drive_next` (verified worker completion → verifier flight in-ledger),
  `confirm_escalation_ack` (transport-delivered evidence required).

## Reader

Unchanged ledger-authoritative supervision (REST/INVALID/ACTION_DUE) plus
SIMULATED-labeled status. Latency instrumentation per action ID for the
30 s / 180 s / 60 s Stage-C gates.
