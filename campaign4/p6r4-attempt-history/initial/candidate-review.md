# P6-r4-notify-timer-drain — Stage B candidate check

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one 15-minute candidate pass
- **Authority:** contract `c5725d291c43…` @ `214e73c`; admission-review
  `5c9fa73a…`; pinned `three-case-checklist.md` `966a8cb5…`
- **Bound:** `35805761083e…` = `src/notify.py`
  `35805761083ec5ee100041654983d9539954131c49333f7b12e2e0c44bdbae4c`
- **Mode:** injected OS boundaries + private `/tmp` notification only; **no live
  seat/service**.

## Verdict

**FAIL** — one bounded defect in **O**. N is implemented and independently
demonstrated; T is implemented and its `systemd-run` mapped-unit timer with an
executable callback is present; but the **delivered-outbox drain never settles on
the connected production path**, so a successfully completed `terminal-rest`
fixture still blocks rollback. 165 candidate + 59 core tests pass, but the O
positive test relies on a transport state the production transport never emits.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/notify.py` | `35805761083ec5ee100041654983d9539954131c49333f7b12e2e0c44bdbae4c` |
| `src/harness.py` | `8575bbb04e408a4f871254c0aad92dbf48e673dfd82a3611d868f921b37cb170` |
| `src/host_adapter.py` | `5deb352117ff2dcb2f925fc875029599bcf9ad1c1f1f4ebd974af805e268ee5a` |
| `tests/test_nto_gates.py` | `fbe484bc884ccb87e89373c7a4203471faa2de754ac21aeedefd9a124402c9f0` |

## Commands and results

```bash
cd campaign4/packages/P6-r4-notify-timer-drain
PYTHONPATH=src python3 -m pytest tests/ -q        # 165 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```
Plus my own exact-CLI run: `setup --evidence-cmd` → `run-fixture --live` with
PATH shims, two distinct producers, then `check-latency` and `rollback` across a
new process; and a private-file `DirNotifier` test.

## N — PASS
- Private `/tmp` file test: `DirNotifier` on a temp dir; a `wait(3)` in a thread
  returned **True in 0.30 s** after an event was appended (blocking inotify via
  `select`, not periodic sleep), and `close()` released the fd.
- Exact CLI used the notification-backed wait (`notify.DirNotifier`), attached
  before the drain; the run reached `terminal-rest` with 2 latency samples.
- `notify.py` handles `IN_Q_OVERFLOW`, timeout returns `False`, closed watcher
  raises `E_WATCHER_CLOSED`; missing dir fails closed (`E_NO_NOTIFY`).

## T — PASS (with a note)
- Exact CLI trace: **1** `systemd-run` call containing the mapped unit
  `p6-fixture-handoff-1.timer` and the executable `harness.py timer-callback`
  callback; a missing bound unit returns `owned-failure no-bound-timer-unit`, and
  a failed runner/allowlist raises `E_TIMER_CREATE`/`E_DISABLED` (tests).
- Note: `systemctl` query/cancel is not called inside `run-fixture`; it is in the
  plan's cleanup step (`stop`/`reset-failed`/`show …ActiveState | grep -q
  inactive`), which I did not execute in this candidate pass.

## O — FAIL (bounded)

`HostWakeTransport.send` records only `sent` (rc0), `queued` (rc3),
`ambiguous`, or `failed` — **never `delivered`**. `HostAdapter.drain_outbox_settled`
settles an intent only when `self.transport.state(mid) == "delivered"`, so on the
connected production path the verifier-dispatch intent is never settled.
Reproduced with the exact CLI:

```
CLI run rc=0  decision=terminal-rest  outbox_settled: []
check-latency: gates-hold (2 samples)
rollback rc=3  E_ROLLBACK_BLOCKED
  detail: outstanding intents remain: ['outbox-pending:ob-57763d86bcada82d']
```

The worker's `test_o_crash_boundaries_same_identity` makes the case pass by
calling `ha.transport.mark(mid, "delivered")` — a state the production transport
does not produce — so the positive O path is only proven against a fake state,
which the checklist explicitly excludes ("exact shipped CLI … not disconnected
helpers").

**Required correction:** correlate the acknowledgement the production transport
actually emits (the confirmed wake receipt, `sent`/`queued` with its receipt) and
the ledger verifier evidence to settle the matching durable intent, or have the
transport record `delivered` on a confirmed receipt; then a positive
`terminal-rest` run must show zero unresolved delivered intents and `rollback`
must succeed across restart. Keep the rollback guard, queued/ambiguous handling
and no-blind-resend/no-premature-clear behaviour, and the negative ambiguous case
must still leave the intent pending and rollback BLOCKED.

## Limitations

Simulated/injected evidence only; private `/tmp` notification was the only host
operation and touched no agent-deck effect. Stage C, live witness 15 and cairn
fixture 15 remain HELD; historical 245/205 unchanged. Per the contract, O is
reported FAIL rather than a non-blocking forward item.
