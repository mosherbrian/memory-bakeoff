# P6-r3-cli-recovery — recovery candidate check

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one ≤20-minute recovery check
- **Authority:** `director-repair-decision.md` (`8981747d…`); contract
  `467c3f4d77a5…` @ `a35eace`; pinned `cli-acceptance-cases.md` `b3422cfd…`
- **Bound:** `89c83a13b7cd…` = `src/harness.py`
  `89c83a13b7cd3b89a0a332bf6937f6ef04055c5f022e8509e164b8c845f93e99`
- **Preserved:** `candidate-review.md` (`89f6ac20…`) untouched; initial 41-file
  archive preserved.
- **Mode:** injected OS boundaries only; **no live effect**.

## Verdict

**FAIL** — two bounded defects, both in D2 (observation and timer backstop).
D1 (per-seat setup/stream identity), D3 (honest latency gate) and D4
(identity-reconciling rollback) are substantially improved and independently
exercised, and 156 candidate + 59 core tests pass. But the exact CLI does **not**
invoke the configured host timer, and the primary turn trigger is still periodic
polling rather than a producer notification interface — the two things D2
explicitly required.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/harness.py` | `89c83a13b7cd3b89a0a332bf6937f6ef04055c5f022e8509e164b8c845f93e99` |
| `tests/test_repair_r3.py` | `0fe49e114e45a716c624fc927f3b119109440707609c15115cd63b465a06856a` |
| `tests/test_cli_acceptance.py` | `e7bb897ace97c885e629bc01ca96b2a862e89726c10df12e78c5b0390f9c4358` |
| `fixture-plan.json` | `f3c40527aae65fa431ea606c005d1f92bfc6d91270646f0e6defde7259c6852c` |

## Commands and results

```bash
cd campaign4/packages/P6-r3-cli-recovery
PYTHONPATH=src python3 -m pytest tests/ -q        # 156 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```
Plus my own exact-CLI run: `setup --evidence-cmd …` then `run-fixture --live`
with PATH shims and **two distinct runtime producers** (separate worker/verifier
streams and claim files), then `check-latency` and `rollback`.

## D1/D3/D4 — verified improved

- **D1:** `setup --evidence-cmd <script>` returned `rc0` and produced per-seat
  bindings (`worker_stream_key sk-live-worker`, `verifier_stream_key
  sk-live-verifier`); two distinct streams + claims were consumed and the graph
  reached `terminal-rest` with both `p6-fixture-worker` and `p6-fixture-verifier`
  wakes in the shim trace. Setup fails closed on missing evidence and on a
  reused stream surface (`E_BOUND_IN_USE`).
- **D3:** `check-latency` requires a positive successful sample, validates real
  timestamps and the 30 s/60 s/90 s gates, and keeps failures in the denominator;
  my run returned `{"verdict":"gates-hold","samples":2,"success":2,"failures":0}`.
- **D4:** `rollback` queries units, outstanding intents, current executions and
  receipts, archives via the SQLite backup API, and derives the report; it
  **blocked** on an outstanding intent rather than writing a static success
  (`E_ROLLBACK_BLOCKED`).
- Config faults now return a clean owned JSON with exit 3 via `_run` (the
  earlier traceback observation is fixed).

## Defects (bounded)

### D2a — the configured host timer is never invoked by the CLI
The plan allowlists timer unit `p6-fixture-handoff-1.timer`, but
`_arm_host_timer` calls `create_host("deadline:" + action_id, …)`. That
`timer_id` is not in the allowlist, so `HostTimerService._guard` raises
`E_DISABLED`, `_arm_host_timer` swallows it (`"disabled-held"`), and no
`systemd-run` call is made. Reproduced: the shim trace showed **0**
`systemd-run` calls, while only the in-memory `FakeTimerService.create` ran.
The decision explicitly forbids reporting a live timer backstop from the
in-memory arm. **Required:** arm the allowlisted unit identity (or allowlist the
deadline timer ids), and fail closed rather than silently reporting a held
backstop when the live timer is required.

### D2b — the primary trigger is still periodic polling
`TurnWatcher.notify` has **no caller** anywhere in `src/`, and there is no
`inotify`/`select`/watchdog source; `_wait_end` remains `watcher.poll(...)` plus
`time.sleep(poll_interval_s)`. The decision states that a "notification-first"
docstring does not make the path event-driven and that periodic polling must not
be the primary trigger. **Required:** connect the actual runtime/file
notification interface (with the existing durable cursor/loss fallback), and
exercise that production subscription under injection.

## Additional observation (non-blocking)

- A completed `terminal-rest` run left `outbox-pending:ob-…` for the
  verifier-dispatch intent unacked, so `rollback` blocked. Correct fail-closed
  behaviour for D4, but the closed graph should acknowledge the outbox after
  delivery so a successful fixture can roll back cleanly; worth reconciling.

## Limitations

Simulated/injected evidence only. Stage C remains HELD; live witness 15 and cairn
fixture 15 remain HELD; historical 185/175 unchanged. No live effect, service
installation, seat action, global wrapper edit, host clock change, research or
script retirement occurred.
