# P6-r4-notify-timer-drain — repair candidate recheck

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one ≤15-minute candidate recheck
- **Authority:** `director-repair-decision.md` (`eb8b7fcd…`); contract
  `c5725d291c43…` @ `214e73c`; checklist `966a8cb5…`
- **Bound:** `68741f8e9043…` = `src/host_adapter.py`
  `68741f8e9043da87cfb5f0e0fc4ff5af784eda10d94a26693806874d116b2e62`
- **Preserved:** first `candidate-review.md` (`932f548f…`) untouched; initial
  44-file archive preserved.
- **Mode:** injected OS boundaries + private `/tmp` only; **no live
  seat/service**.

## Verdict

**PASS.** The O settlement defect is corrected on the connected production path.
With a well-formed transport receipt (`wake: <seat> -> started`) plus bound
turn-seen evidence for the exact verifier execution and same-package ledger
advancement, the intent settles atomically and a new-process `rollback` reports
zero unresolved delivered intents. A malformed/ambiguous receipt correctly stays
pending and rollback BLOCKED. T's mapped-unit timer + query/cancel are exercised,
N is retained, and 172 candidate + 59 core tests pass.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/host_adapter.py` | `68741f8e9043da87cfb5f0e0fc4ff5af784eda10d94a26693806874d116b2e62` |
| `src/harness.py` | `6f7008677adf4b06ec0320b9596bfba1d4179cf090fc9d2b46418311857f5db8` |
| `src/turn_handoff.py` | `952572f18df68058b6127a7f309a290d46c897c36d26232cf2ee22e8f29b7f39` |
| `tests/test_repair_o_settle.py` | `962ac6f449f31f9f4d1c72be6d7739c911ed0eade79fdd80f8ce108832cb3130` |
| `tests/test_nto_gates.py` | `260d7bb493f1fa4c24d5c24d47105efa26402f85f9cc2773f32a50f0082fe1c1` |

## Commands and results

```bash
cd campaign4/packages/P6-r4-notify-timer-drain
PYTHONPATH=src python3 -m pytest tests/ -q        # 172 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```
Plus my own **exact shipped** `setup --evidence-cmd` → `run-fixture --live`
(two real-format runtime sources, PATH shims) → **cleanup** (`systemctl
stop`/`reset-failed`/`show` of the mapped unit) → new-process `rollback`.

## O — expected/observed on the exact CLI

| Case | Expected | Observed |
|---|---|---|
| initial (pre-repair) | terminal-rest but intent pending, rollback FAIL | reproduced in `candidate-review.md` (`outbox_settled: []`, `E_ROLLBACK_BLOCKED`) |
| repaired positive | settle on valid receipt + start/outcome proof | `outbox_settled: ["ob-57763d86bcada82d"]`; `terminal-rest` |
| repaired rollback (new process) | zero unresolved delivered intents | rc0; `Intents: none-outstanding-verified`; current executions `exv-…`/`ex-…`; archive written |
| malformed/ambiguous receipt (rc0, no `wake:` line) | stay pending, rollback BLOCKED | refused to settle (`E_ROLLBACK_BLOCKED`) — fail-closed |
| queued/ambiguous or missing turn-seen | stay pending until outcome proof | tests (`test_o_*`) + settlement code requires receipt state in `sent|queued|delivered`, exact action/execution/seat, `turn-seen:<…>:<execution>`, and same-package flight/terminal advancement |

Settlement now rejects wrong/missing seat (via `route_for`), action mismatch,
unrelated/stale execution, missing `turn-seen`, bare/other-package flight and
unrelated terminal disposition; ack + pending-clear are one atomic durable write.

## T — cleanup executed this time

Exact cleanup ran `CALL systemctl` **3** times (`stop`, `reset-failed`, `show
p6-fixture-handoff-1.timer --property=ActiveState`) and the run trace still shows
**1** `systemd-run` on the mapped unit with the executable callback; the archive
rollback report is derived from the identity checks. No false backstop.

## N — retained

The private `/tmp` `DirNotifier` evidence stands: blocking inotify/`select` wait
returns on an appended event without periodic sleep; overflow/closed/timeout
handling present. The exact CLI uses the notification-backed wait.

## Observations (non-blocking)

- Settlement correctly depends on a **well-formed** wake receipt; my first shim
  printed `started` without the `wake:` prefix and the transport classified it
  `ambiguous`, so the intent stayed pending and rollback blocked. That is the
  intended transport-ack vs outcome distinction, not a defect; the real `wake`
  script emits `wake: <seat> -> <status>`.

## Limitations

Simulated/injected evidence only; private `/tmp` notification and shimmed OS
commands were the only host operations. Stage C, live witness 15 and cairn
fixture 15 remain HELD; historical 245/205 unchanged. No live effect, seat
action, service, runtime-wrapper edit, real Signal or clock change occurred.
