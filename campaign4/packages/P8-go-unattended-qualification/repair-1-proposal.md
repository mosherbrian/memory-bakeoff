# P8 single repair: authority mapping + supervisor liveness (proposal, not implemented)

Claude, 2026-09-23, for Tern's OVERNIGHT-EXPOSE-LIVENESS-RULING-20260923.
Pinned candidate `4a00d67` / binary `8cc149bf` is untouched. This file is the
proposed patch and test surface for P8's single repair; nothing below is built.

## Part A: runtime principal -> core authority (finding live-director-findings-1)

### What failed, and why

`live-1/010-command.json`: `agent-loop decide` exited 1 with `E_UNTRUSTED_ACTOR`.
`Loop.Decide` (`internal/loop/loop.go:864`) is the only place where the loop passes
a runtime name into the core as an actor: `seat = Cfg.Director`
(`p6-fixture-p8-director-1`). The frozen core trusts only its fixed cast
(`tern`, `corvid`, `kiln`, `cairn`). Every other path already goes through the
driver's fixed cast. The preserved ledger `live-1/loop.db` shows this for the
steps that passed: publish `kiln/worker`, verify_pass `corvid/verifier`,
authorize `tern/director`. The real principals (`p6-fixture-p8-worker-1`, ...)
survive only in the loop's package record. So the attribution was already a
cast mapping, but an implicit one, and only `decide` broke it.

### Proposal

The core stays frozen. The mapping from runtime principals to the core's cast
becomes explicit, validated and recorded, and every core call goes through it:

| Core role (cast seat) | Runtime principal | Bound when |
|---|---|---|
| worker (`kiln`) | the package's worker seat | dispatch |
| verifier (`corvid`) | the package's verifier seat | dispatch |
| director (`tern`) | config `director` | dispatch |
| duty (`cairn`) | config `duty` (new; the liveness owner) | dispatch |
| reader (`corvid`) | same principal as the verifier (as in the core) | dispatch |

- **At dispatch** the loop resolves each principal to its session id in the
  agent-deck registry (already done by `VerifySeats`) and writes the binding
  into the package record: `principals: {role: {seat, session}}`. Worker,
  verifier and director must be three different sessions (already enforced),
  so no principal can verify its own work or act as director on it.
- **Every core entry path** asks `authority(p, role)`. It re-reads the current
  config binding for that role and refuses with `E_AUTHORITY_CHANGED` when the
  seat or its session differs from the recorded one. Only then does it return
  the core's cast actor. This covers dispatch, the worker handoff, the verdict,
  `decide`, the pre-authorized close (`--on-pass`), the timer callback (duty),
  and reopen, because the record lives in the ledger's kv, not in memory.
- `Loop.Decide` stops passing `Cfg.Director`; it uses `authority(p, "director")`.
- Genuine identity is kept, never erased: the ledger event keeps the cast actor
  the frozen core requires, and the loop's record binds that event to the real
  seat and session. `status --json` shows the real principals. No fixture name
  is added to any allowlist.

Limit, stated plainly: the CLI does not authenticate its caller. Whoever can run
`agent-loop decide` on the host acts as the recorded director, which is the
same trust boundary as the Python adapter. The patch does not change that.

### Patch surface (Part A)

| File | Change | Size |
|---|---|---|
| `internal/loop/authority.go` (new) | principal record; `authority(p, role)` with the re-check; cast lookup | ~70 lines |
| `internal/loop/loop.go` | dispatch records principals; Decide / finishWorker / finishVerify / on-pass call `authority` first; `duty` config field | ~30 lines |

### Tests (Part A)

- The whole P8 positive path with non-cast fixture names for all three roles:
  dispatch, worker claim, verifier PASS, `decide`, closed. This is the exact
  `live-1` failure as a regression test.
- The same path with `--on-pass`, and with a reopen between every step.
- The director is rebound in the config after dispatch: `decide` refused
  `E_AUTHORITY_CHANGED`, ledger unchanged. The same holds for the worker and
  the verifier at their handoffs.
- Worker = verifier session, worker = director session: refused at dispatch
  (existing tests, kept).
- The ledger actors are cast seats, and the package record names the real principals.
- Faults for `mutate_go.py`: Decide uses a config name again; the re-check is
  skipped; the principal record is not persisted across reopen.

## Part B: supervisor liveness

### Semantics

| State | How it arises | Service | Check verdict | Alarm |
|---|---|---|---|---|
| running | `run` completes a pass at least every 30 s | active | `ok` | none |
| legitimate rest | no open packages; passes continue every 30 s | active | `rest` | none |
| intentional stop | `agent-loop stop` writes the stop marker; `run` exits 64 at its next pass | inactive, exit 64 = success, never restarted | `stopped` | none, for as long as the marker exists |
| stop not honoured | marker present, service still active after 120 s | active | `stop-pending` | duty |
| crash | `run` dies (signal, panic, exit != 64) | systemd restarts it after 5 s | `ok` again once a new pass lands; `crashed` if no fresh pass within 120 s | duty if not recovered |
| hung | process alive, no pass completes | systemd watchdog (90 s) kills and restarts it; the outside check sees the pass age | `hung` when the last pass is older than 120 s | duty, then director |
| restart loop | 5 starts in 300 s | systemd start limit puts the unit in `failed` | `restart-loop` (reads `NRestarts`, `Result=start-limit-hit`) | duty, then director |
| unplanned stop | `systemctl stop` or reboot without the marker | inactive, no marker | `down` | duty, then director |
| failing passes | passes complete but `Tick` returns an error 3 times in a row | active | `erroring` | duty, then director |
| unknown | the check cannot read the unit state or the ledger | ? | `unknown`: never green | duty, then director |

A new `agent-loop start` removes the marker and starts the unit. `run` refuses
to start (exit 64, no DB write) while the marker exists, so a reboot or a stray
`systemctl start` cannot undo an intentional stop.

## Evidence that the loop is servicing work

The heartbeat is written by the `run` goroutine itself, at the end of each
completed `Tick`, into `driver_kv` key `loop-pass`:
`{"at", "pid", "pass", "advanced", "open_packages", "last_error", "error_streak"}`.
There is no separate heartbeat thread. The systemd watchdog ping
(`WATCHDOG=1`, sd_notify over `NOTIFY_SOCKET`, stdlib only) is sent at the
same point, so a pass that never finishes is killed by systemd and flagged by
the check independently.

## The outside check

`agent-loop liveness --config FILE` runs from its own systemd timer every 60 s.
It is a separate process and unit: it keeps running when `run` exits, hangs or
loops. It reads the ledger read-only, the stop marker, and
`systemctl --user show <unit> -p ActiveState,SubState,Result,NRestarts,ExecMainStatus`.
State that it owns (incidents) lives in `<db>.liveness.json`, not in the
ledger, so a locked or damaged ledger still produces an `unknown` alarm.

Incidents and the acceptance bounds (RECOVERY-ACCEPTANCE-RULING-20260921):

- Detection: stale after 120 s with no pass, checked every 60 s, so the
  worst case is 180 s, within the 180 s suspicion bound.
- On a new incident the check wakes the duty seat (cairn) once, with the
  incident id, the state, the evidence, and the exact command to acknowledge it:
  `agent-loop liveness-ack --config FILE --incident ID --by cairn`.
- If it is neither acknowledged nor cleared by the next check (60 s), the check
  wakes the director (tern) once: the backstop when the receiver is unavailable.
  A queued wake is recorded as sent, never as acknowledged.
- `recovered` (a fresh pass and an active unit) and `escalated` (acknowledged)
  are separate outcomes in the incident record, each with its time.
- An open incident is repeated at most once per 15 min to the director, never
  to the duty seat again.

## Patch surface

| File | Change | Size |
|---|---|---|
| `cmd/agent-loop/loop.go` | `run`: refuse start on marker (exit 64), write `loop-pass` after each Tick, sd_notify READY and WATCHDOG, exit 64 on marker; new `start`, `liveness`, `liveness-ack` | ~150 lines |
| `internal/loop/liveness.go` (new) | pass record; `Assess(unit, pass, marker, now) -> verdict` (pure); incident state machine | ~200 lines |
| `internal/loop/loop.go` | `Tick` returns its counts; config `duty` seat, `unit` name | ~20 lines |
| `deploy/systemd/agent-loop@.service` | `Type=notify`, `ExecStart=agent-loop run --config %h/.config/agent-loop/%i.json`, `Restart=always`, `RestartSec=5`, `RestartPreventExitStatus=64`, `SuccessExitStatus=64`, `WatchdogSec=90`, `StartLimitIntervalSec=300`, `StartLimitBurst=5` | new |
| `deploy/systemd/agent-loop-liveness@.service` + `.timer` | oneshot `agent-loop liveness --config ...`; `OnUnitActiveSec=60s`, `AccuracySec=5s` | new |

Nothing changes in the core, the host blocks, routing, dispatch, claims or
the per-action deadline timers. The shared DB gains one kv key written by
`run`; the check only reads it.

## Tests

In Go (`internal/loop/liveness_test.go`), each verdict row above from a table
of unit properties, pass age, marker and error streak; `unknown` is never
green; incident flow: first alarm wakes duty once, no ack by the next check
wakes the director once, an ack stops the director wake, a clear records
`recovered`, a repeat is rate-limited; `run` exits 64 on the marker without a
DB write. All added to `mutate_go.py`, with at least these faults: a stale pass
treated as fresh; the marker ignored by `run`; exit 64 restarted; a queued wake
counted as an ack; `unknown` reported ok.

Live witness on isolated fixture units (`agent-loop@p8fix`, the P8 fixture
seats as duty and director sinks), each with endpoint times and outcomes:

1. `kill -9` on `run` mid-work: restarted, a fresh pass within the bound, no
   resend (wake receipts unchanged, outbox held-awaiting-receipt).
2. `kill -STOP` on `run`: the watchdog restarts it; with the watchdog disabled
   in a second variant, the check reports `hung` within 180 s and wakes duty.
3. A config that makes `run` exit 1: the start limit is hit, the unit is `failed`,
   duty is woken; no ack, so the director is woken; then an ack is recorded.
4. `agent-loop stop`: exit 64, no restart, the check quiet for 10 min;
   `systemctl --user start` refused while the marker exists; `agent-loop start` resumes.
5. Idle rest for 10 min with no packages: quiet.
6. An armed per-action deadline timer still fires while `run` is down.

No account-wide user or linger change, no main service, no cutover.

## Fit to the single repair (Parts A and B)

Code and Go tests for both parts: about 30 minutes for me. Part A is small
(~100 lines); Part B is most of the work. The live witness runs 1-5 take about
25 minutes of wall time, mostly waiting on the 10-minute quiet windows and the start
limit, so they belong to corvid's 20-minute recheck only if the two quiet windows
shrink to 3 minutes each. If you want 10-minute windows, the witness does not fit
the recheck, and by your rule P8 would end NOT READY on this blocker. That is your call.

The live cases `live-1` never reached (timeout, restart, quiet rest) must run
again on the repaired binary, together with the liveness runs above. If the
recheck cannot hold both, the smallest honest split is: Part A plus its
regression tests plus the positive live case with `decide`, in this repair,
and Part B marked as the named NOT READY blocker.
