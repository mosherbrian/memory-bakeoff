# Candidate adapter/reader interface (P6-r4 Stage A)

Inherits the P6-r3 trusted boundary unchanged; connected corrections:

## Notification (`src/notify.py`, `DirNotifier`)

- `DirNotifier(path)` attaches an inotify watch (close_write, moved_to,
  create, delete, overflow); `wait(timeout_s)` blocks on the fd (True =
  event, False = timeout); `close()` releases the fd. Overflow counts
  and forces rescan notes. Unavailable inotify fails closed
  (`E_NO_NOTIFY`).
- `_wait_end` (harness): attach → drain → block → redrain until an end
  or the trusted bound; no `time.sleep` anywhere on the path; labels
  notified vs replay-fallback come from the watcher.

## Timers (stable mapping + enforced creation)

- Plan allowlist carries `timer_units: {action: unit}` plus
  `systemd_run`/`systemctl` executable paths; the manifest binds them.
- `HostTimerService.create_host` runs the exact argv through the
  injected-or-real runner; `cancel_host`/`query_host` use the same unit
  identity. Fixture flow fails owned (`E_NO_TIMER`/`E_DISABLED`/
  `E_TIMER_CREATE`) without a runnable backstop — never a silent
  in-memory claim.

## Outbox drain (`drain_outbox_settled`)

- Settles a pending intent iff transport state is delivered AND ledger
  evidence exists (flight for the target action, or terminal
  disposition). Returns settled ids; everything else stays pending for
  the rollback guard. Terminal phase alone settles nothing.

## Reader

Unchanged ledger-authoritative supervision (REST/INVALID/ACTION_DUE) plus
SIMULATED-labeled status. Latency fields per action ID for the
30 s / 180 s / 60 s gates (totals 90 s / 240 s).

## O-settlement repair (strict proof rule)

- Settle requires, for the exact outbox identity: a well-formed kv
  message receipt in `sent/queued/delivered` (ambiguous/failed/unknown
  never settle), receipt action/execution matching the pending intent,
  execution current (or superseded-to-current), a bound turn-seen record
  for that execution, ledger advancement in the SAME package (live
  flight for the target action, or its terminal disposition), and the
  receipt seat equal to the contract-bound route. Anything else stays
  pending with rollback BLOCKED.
- Message IDs come from a durable kv counter (fresh instances never
  restart at 1); colliding writes raise `E_MSG_COLLISION` instead of
  overwriting receipt history. Ack + clear is one atomic durable write;
  crash before/after ack reconciles the same identity with no resend.

## O-settlement repair (strict proof rule)

- `drain_outbox_settled` settles only on: well-formed receipt in
  sent/queued/delivered; receipt action/execution == pending intent;
  execution current or superseded-to-current; bound turn-seen for that
  execution; same-package flight or terminal disposition; receipt seat
  == contract-bound route. Malformed/unroutable intents are skipped,
  never cleared. Ack + clear is atomic (`_kv_put_many`).
- `HostWakeTransport._record` uses a durable kv counter and refuses
  overwrites (`E_MSG_COLLISION`). `outbox_send` binds execution into
  the pending record and the transport receipt.
