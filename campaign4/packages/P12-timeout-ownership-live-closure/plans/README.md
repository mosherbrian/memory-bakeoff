# P12 plans and candidate: timeout ownership, prompt shutdown, reload-proof timers

Candidate: agent-loop branch `p12-timeout`, commit `cbfe3d91d02c86942e7640cbd0fe41027bfcbad0` (base
`1341f04`). Release: `/home/bmosher/projects/agent-loop-releases/agent-loop-cbfe3d91d02c/`
(bin sha256 `cf54a94a…`, `MANIFEST.sha256`, `BUILD.json`, source tarball). Main and the installed preview
are unchanged. Python, core, conformance cases and the Python tools are unchanged.
Full source diff: `evidence/source-1341f04-to-cbfe3d9.diff`. Conformance on the exact release binary, stdout/stderr/rc
captured separately: `evidence/conformance-release-binary/` (rc 0, stderr "conformance: 125/125 cases ok, 1751 steps"; the
summary goes to stderr, which is why the initial stdout-only capture was empty).

| Part | Change | Evidence (before -> after) |
|---|---|---|
| A timeout settlement | `WakeTransport.Send` classifies a /cancel reply only by its exact receipt for that session: `wake: <seat> -> cancelled` -> cancelled, `-> nothing running` -> idle. Any other reply or a transport error stays failed; outside a /cancel "nothing running" is never accepted. `sendID` accepts cancelled/idle only for a stop. If an effect fails after the core's interrupt, `SettleTimeoutFailure` still settles the step as `timed-out`, records the failure, and tells the director (else duty). A replay (`already-handled`) completes a record that a crash left out. No step is recorded as timed out without the core's interrupt. | `a-cli-timeout.txt`: the frozen binary leaves the step at `worker` with 0 director wakes for all three real reply shapes (even a real "cancelled"). The candidate reaches `timed-out` with 1 director wake for each; a refused transport is settled as `failed: …` and the director is told. Go: `internal/loop/timeout_p12_test.go`, `internal/host/timer_p12_test.go` |
| B acknowledgement | `agent-loop timeout-ack --qid Q --action A --by SEAT --next TEXT --within DUR`. Only the director or duty; the principal recorded at dispatch must still be bound (`authority`) and in the registry (`VerifySeats`). Exact package and timed-out action. Host time; next action required; within must be over 0 and at most 1 h. The same ack is a replay; a different ack while one is in force is refused. Durable in the ledger (`status --json` shows `timeout.ack`). Not a resume or a close. An expired response deadline is escalated to the director once, and a fresh ack is then allowed. Every timeout notice carries the exact command. | Go tests (wrong or unknown actor, wrong action, empty next, zero/past/unbounded deadline, conflict, replay, reopen, expiry, changed principal); CLI in `a-cli-timeout.txt` |
| C normal stop | The wait between passes ends on SIGTERM/SIGINT and sees the stop marker within 1 s. Watchdog behaviour and exit 64 are unchanged. | `c-stop-baseline-1341f04.txt`: 20.1 s, `Result=timeout`, SIGABRT (both wait paths). `c-stop-final-cbfe3d9.txt`: stop, SIGINT and restart all well under 1 s with `Result=success`; `agent-loop stop` about 1.0 s, "exiting 64", no restart |
| D driver | Journal windows are `@EPOCH` (no zoneless `--since`). SETUP accepts `ok` or `rest`. L4a checks that the drop-in is in effect before judging. L4b reports what it saw. L6 (repair-1) requires, in order deadline <= detection <= ack: detection within 30 s, the recorded acknowledgement (`timeout.ack.at`) within 60 s of detection AND within 90 s of the deadline; a sent wake is never ownership. `tasks/ack.md` tells the fixture director to run the timeout-ack command. L4a/L4b in P11 were contaminated by C (a failed stop meant `systemctl restart` never started the failing unit); C is the fix. | `f1-helpers-p12.txt` 29/0; `r1-repair-tests-p12.txt` 58/0 (L6 boundaries: gap 60 s PASS, 61 s FAIL, detection 25 + ack 88 FAIL, detection 10 + ack 90 FAIL, no ack FAIL); the initial driver fails those 3 interval cases (`r1-repair-tests-initial-driver.txt`); construction only: `construction-dry/` |
| E wall and timers | The wall is `--on-calendar="<deadline> UTC"` with AccuracySec=1s. The driver checks its `TimersCalendar next_elapse=@N` equals the deadline when armed and after every daemon-reload, and stops with `WALL FAIL` otherwise. Go deadline timers with a known instant use the same explicit-UTC calendar form (`CommandAt`); `--on-active` is kept only for a deadline without an instant. | `e-reload-timers-run1.txt`: each real daemon-reload restarted the `--on-active` countdown (next_elapse +5.2 s per reload; not fired by target+15 s); the calendar timer was unchanged and fired 0.386 s after target. `e-wall-reload-p11-baseline.txt`: the P11 wall drifted about 10 s per reload and the driver was still alive after the deadline. `e-wall-reload-p12.txt`: 3 real reloads, schedule unchanged `@deadline`, WALLSTOP at deadline+0.4 s, driver and children gone, 0 driver effects from the deadline, 1 cleanup |

Named adjudication (host parity): `conformance/host/adjudicated.json` `final_corrected` for
"host timers: create, reuse, conflict, refuse, query, cancel" / `runner_calls`. Go arms explicit-UTC
calendar timers where Python arms `--on-active`; all other ops are unchanged (316/321 identical, 5
held to the existing corrections).

Independent fallback: cairn's prep cleanup timer must also be an explicit-UTC calendar timer, for example
`systemd-run --user --unit=<name> --timer-property=AccuracySec=1s --on-calendar="YYYY-MM-DD HH:MM:SS UTC" <cleanup command>`.
Check its `TimersCalendar next_elapse=@N` after arming. The P11 prep cleanup timer was `--on-active`, so reloads could postpone it.

Clock discontinuity: calendar timers follow the realtime clock. A forward step makes the wall and
deadlines fire early (the wall fails safe). A backward step postpones them by the size of the step.
The driver's deadline guard reads the same clock. No real clock step was made (that would be a global host
change); this is a declared residual.

## P12-closure-1 (candidate 669648c, bin `3916950a…`; templates now pin this release)

Source diff from cbfe3d9: `evidence/closure-1/source-cbfe3d9-to-669648c.diff`. The core, py and cases are unchanged.

- **Never-acked timeout escalation**:
  - `unacked()` runs on every `run` pass. A `timed-out` step with no ack for `NoAckAfter` (60 s) after settlement is escalated to duty. The director follows at 120 s, or at once if duty cannot be reached.
  - Each send is checked against the principals recorded at dispatch.
  - The record is `timeout.no_ack_duty` / `no_ack_director`: `sent <t>` or `failed <t>: <why>`. A failed send is retried on the next pass and is never recorded as delivered.
  - Achievable bound: duty gets it at most 60 s + the pass interval (`--every`, 30 s) + the pass time after settlement, so about 90–95 s; the director gets it about 30 s + one pass later still. While `run` is stopped, nothing escalates; the liveness check owns that state.
  - An escalation is not an acknowledgement and not a recovery. L6 still needs an ack within 60 s of detection.
- **Clock discontinuity**:
  - A deadline callback that runs before the ledger deadline (`no-op-early`) re-arms the **same** unit at the **original** ledger instant. The spent unit is stopped and reset first. A replay while the re-armed unit waits reuses it, so one timer is due.
  - Anything other than the running step's current action (stale, settled, other action) is refused before any timer call.
  - A failed re-arm, and every re-arm, is told to duty as a clock discontinuity (an owned state, not green).
  - `timeout.callback_lateness` records settlement time minus the ledger deadline. A late callback beyond 30 s fails L6 detection.
  - Evidence comes from injected-clock tests (core.FakeClock). They do NOT show how systemd delivers a calendar timer after a real host clock rollback. Qualification assumes a continuous host UTC clock, and a real discontinuity invalidates the timing sample.
- **Duplicate notice (the only allowed one)**: a failed-cancel settlement tells the director, then the timer's replay delivers the cancel and the core's own wake tells the director again. It is the same `T-<action>` incident with the same settlement time, so there is no per-pass flood and no second cancel or dispatch. Tested in `TestTheOnlyDuplicateNoticeIsBounded`.
- Tests: `evidence/closure-1/closure-tests.txt`. Mutation 110/110 (`evidence/closure-1/mutate-go.txt`). Conformance on the release binary: `evidence/closure-1/conformance-release-binary/` (rc 0, 125/125).

## P12-stopped-ownership-1 (candidate 53c9719, bin `ec184be9…`; templates now pin this release)

- **What changed**: the outside liveness check (its own timer, 45 s, AccuracySec=1s) now also runs the never-acked and ack-expiry escalation, so a timeout is escalated while `run` is stopped. The escalation is reported apart from the liveness verdict and opens no incident, so an intentional stop stays quiet.
- **Concurrency**: `run` (after every pass), the liveness check and `timeout-ack` each write timeout records from a freshly opened ledger under one file lock (`<db>.timeouts.lock`). This prevents a double escalation from a stale view and prevents an ack being overwritten.
- **Bounds from settlement**:
  - While stopped: duty at most 60 + 45 s + check time; the director at most 120 + 45 s + check time.
  - While running: the same, or 30 s (the pass interval) in place of 45 s.
- **New live case L6b** (after L5/L6, before L4b): stop `run`, let a 1 min deadline pass, and nobody acknowledges (`tasks/ack.md` tells the fixtures to leave L6b alone).
  - PASS needs duty 60..110 s and the director 120..170 s after settlement, no ack, and the liveness verdict still `stopped`.
  - `l6b_eval` is a helper with boundary tests (`evidence/stopped-ownership/l6b-eval-tests.txt`).
- **Evidence**: `evidence/stopped-ownership/`:
  - `cli-stopped-noack.txt`, a real CLI run in real time with the stop marker in force: verdict `stopped`, no alarm, no incident; duty at +60 s, director at +120 s;
  - `tests.txt`;
  - mutation 112/112;
  - conformance on the release binary (rc 0, 125/125);
  - parity 316/321 + 5;
  - `f1-helpers.txt` 29/0 and `r1-repair-tests.txt` 58/0 on the new driver;
  - `e-wall-reload.txt` (WALLSTOP, LATE 0);
  - construction dry run.

## P12-writer-safety-1 (candidate 844d156, bin `ab3cfc22…`; templates now pin this release)

- **One ledger lock for every writer**:
  - `run` passes, deadline callbacks, the outside check's timeout escalation, `timeout-ack`, `decide`, `dispatch` and `claim` all take `<db>.lock` (flock) before they open the ledger.
  - They hold it through the core transition, the package record and the effects. So no writer acts on a stale view, and the core state and the package record cannot diverge.
  - There is no nesting: a run pass escalates on its own locked view.
  - Waits are bounded: 60 s for run and the CLI commands, 120 s for a callback, 30 s for the outside check. A timeout is `E_LEDGER_BUSY`. A callback that cannot get the lock tells duty the exact command to rerun.
  - The lock is held while wake sends are made (each send times out at 30 s), so a stalled transport slows other writers but cannot block them forever.
- **Timeout record**: a timeout is recorded only for the core's current action. A step the loop marked `blocked` is still timed out by its deadline.
- **Real process race** (`evidence/writer-safety/race-callback-vs-run.sh`): a run pass is frozen after it has read the ledger, the callback runs in a second process, then the pass is released. The frozen pass reads a declared input that is a named pipe, before its hand-off. Results:
  - old build 53c9719, input changed: the callback finishes while the pass is frozen, the pass then writes `blocked` from its old view, and the final state is `timeout=null`: **the timeout is lost**;
  - new build: the callback waits for the lock, and the final state is `timed-out` with the timeout recorded, one cancel and no duplicate;
  - same-content mode: both builds keep the timeout; the new build still serializes.
- **Measured timer cadence** (`cadence-unitfile-*.txt`, a real unit-file timer with OnActiveSec/OnUnitActiveSec=45s and AccuracySec=1s):
  - no reloads: checks at 45.8 s and 91.8 s;
  - a reload every 60 s: checks every 46 s;
  - a reload every 20 s: **no check at all in 300 s**, because each reload restarts the first OnActiveSec countdown until the timer has fired once.
  - Declared limit: a reload storm less than 45 s apart just after the liveness timer starts delays the outside check. Once it has fired, reloads did not move it.
