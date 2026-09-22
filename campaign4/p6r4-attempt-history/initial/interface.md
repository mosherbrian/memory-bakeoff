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
