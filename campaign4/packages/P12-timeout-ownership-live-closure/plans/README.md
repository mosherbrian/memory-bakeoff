# P12 plans and candidate: timeout ownership, prompt shutdown, reload-proof timers

Candidate: agent-loop branch `p12-timeout`, commit `cbfe3d91d02c86942e7640cbd0fe41027bfcbad0` (base
`1341f04`). Release: `/home/bmosher/projects/agent-loop-releases/agent-loop-cbfe3d91d02c/`
(bin sha256 `cf54a94a…`, `MANIFEST.sha256`, `BUILD.json`, source tarball). Main and the installed preview
are unchanged. Python, core, conformance cases and the Python tools are unchanged.
Full source diff: `evidence/source-1341f04-to-cbfe3d9.diff`.

| Part | Change | Evidence (before -> after) |
|---|---|---|
| A timeout settlement | `WakeTransport.Send` classifies a /cancel reply only by its exact receipt for that session: `wake: <seat> -> cancelled` -> cancelled, `-> nothing running` -> idle. Any other reply or a transport error stays failed; outside a /cancel "nothing running" is never accepted. `sendID` accepts cancelled/idle only for a stop. If an effect fails after the core's interrupt, `SettleTimeoutFailure` still settles the step as `timed-out`, records the failure, and tells the director (else duty). A replay (`already-handled`) completes a record that a crash left out. No step is recorded as timed out without the core's interrupt. | `a-cli-timeout.txt`: the frozen binary leaves the step at `worker` with 0 director wakes for all three real reply shapes (even a real "cancelled"). The candidate reaches `timed-out` with 1 director wake for each; a refused transport is settled as `failed: …` and the director is told. Go: `internal/loop/timeout_p12_test.go`, `internal/host/timer_p12_test.go` |
| B acknowledgement | `agent-loop timeout-ack --qid Q --action A --by SEAT --next TEXT --within DUR`. Only the director or duty; the principal recorded at dispatch must still be bound (`authority`) and in the registry (`VerifySeats`). Exact package and timed-out action. Host time; next action required; within must be over 0 and at most 1 h. The same ack is a replay; a different ack while one is in force is refused. Durable in the ledger (`status --json` shows `timeout.ack`). Not a resume or a close. An expired response deadline is escalated to the director once, and a fresh ack is then allowed. Every timeout notice carries the exact command. | Go tests (wrong or unknown actor, wrong action, empty next, zero/past/unbounded deadline, conflict, replay, reopen, expiry, changed principal); CLI in `a-cli-timeout.txt` |
| C normal stop | The wait between passes ends on SIGTERM/SIGINT and sees the stop marker within 1 s. Watchdog behaviour and exit 64 are unchanged. | `c-stop-baseline-1341f04.txt`: 20.1 s, `Result=timeout`, SIGABRT (both wait paths). `c-stop-final-cbfe3d9.txt`: stop, SIGINT and restart all well under 1 s with `Result=success`; `agent-loop stop` about 1.0 s, "exiting 64", no restart |
| D driver | Journal windows are `@EPOCH` (no zoneless `--since`). SETUP accepts `ok` or `rest`. L4a checks that the drop-in is in effect before judging. L4b reports what it saw. L6 requires a recorded acknowledgement (`timeout.ack.at`) within 90 s of the deadline, detection within 30 s; a sent wake is never ownership. `tasks/ack.md` tells the fixture director to run the timeout-ack command. L4a/L4b in P11 were contaminated by C (a failed stop meant `systemctl restart` never started the failing unit); C is the fix. | `f1-helpers-p12.txt` 29/0; `r1-repair-tests-p12.txt` 53/0 (includes the new L6 rule: no ack = FAIL); construction only: `construction-dry/` |
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
