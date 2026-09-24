# OPERATOR HANDOFF — deployed agent-loop (campaign4)

Generated 2026-09-24 (UTC) from live host commands. Every value below was
read from this host; nothing copied from plans. SUPERVISED PREVIEW / NOT
QUALIFIED FOR UNATTENDED USE (unit files say so verbatim).

## Pins

- Binary: `sha256sum /home/bmosher/.local/bin/agent-loop`
  `97a57db11aa8a4a87d89fd912804d42ce899bb35b3790742d790d424184a948f`
  (matches release pin).
- Source commit: `vcs.revision=8ad12b86fa825ae3f47e97a2642695bf63eb05a9`
  (from binary strings; `go` not installed on host), `vcs.time=2026-09-23T23:33:18Z`.
  NOTE: `agent-loop version` prints the campaign repository state
  (`memory-bake-off ... @ c4ef8b9...`), NOT the binary's version. The binary
  is identified by the sha256 + vcs.revision above.
- Config: `sha256sum /home/bmosher/.config/agent-loop/campaign4.json`
  `84e1c9cff48f157f038c787862709580aa777a99de8cb40b241a88e4c969cee6`.
- Units (`systemctl --user cat`, template files under
  `/home/bmosher/.config/systemd/user/`):
  - `agent-loop@.service`: `ExecStart=%h/.local/bin/agent-loop run --config
    %h/.config/agent-loop/%i.json`; `Restart=always`, `RestartSec=5`,
    `RestartPreventExitStatus=64`, `SuccessExitStatus=64` (exit 64 =
    intentional `stop`, neither restarted nor failed); `WatchdogSec=90`,
    `TimeoutStartSec=60`, `TimeoutStopSec=20`; start-limit burst 5/300s.
  - `agent-loop-liveness@.service`: oneshot outside check
    (`agent-loop liveness`); `TimeoutStartSec=35`;
    `OnFailure=agent-loop-liveness-failed@%i.service`.
  - `agent-loop-liveness@.timer`: `OnCalendar=*-*-* *:*:00,30 UTC`
    (every 30 s wall-clock), `AccuracySec=1s`, `Persistent=false`.
  - `agent-loop-liveness-failed@.service`: oneshot
    (`agent-loop checker-failed --unit agent-loop-liveness@%i.service`);
    no OnFailure of its own (no recursion).

## Commands

- Install (qualified binary + release units, then reload):
  `install -m 755 <qualified-release-binary> /home/bmosher/.local/bin/agent-loop`
  `cp <release>/examples/systemd-unqualified/agent-loop@{,,-liveness@.service,-liveness@.timer,-liveness-failed@.service} /home/bmosher/.config/systemd/user/`
  `systemctl --user daemon-reload`
- Run (the units):
  `systemctl --user enable --now agent-loop@campaign4.service agent-loop-liveness@campaign4.timer`
- Status: `agent-loop expose --config /home/bmosher/.config/agent-loop/campaign4.json`
  (append `--json` for machine-readable).
- Stop: `agent-loop stop` (exit 64: stays stopped until start; deadline
  timers still fire).
- Start: `agent-loop start` (clears the stop, starts the configured unit).
- Restore/rollback (cutover script, drains agent-loop effects, restores
  old owners from captured state, hands open items to cairn):
  `/home/bmosher/memory-bake-off/campaign4/packages/P12-timeout-ownership-live-closure/plans/cutover.sh <INPUTS.env> rollback`
  (see `rollback()` there: archive expose/DB/claims → disable units, drain
  callbacks and the OnFailure handler → open items to cairn, no resend →
  previous binary + unit files back → daemon-reload → exact captured
  enabled/active state → verify).

## Effect ownership (live now)

- `systemctl --user list-timers --all`: `agent-loop-liveness@campaign4.timer`
  active, next elapse on the :00/:30 cadence; also present is the worker's
  own callback timer `agent-loop-campaign4-P12-production-handoff-1-w1.timer`.
- Enabled now: `openwork.timer: disabled`, `coax-dry.timer: disabled`,
  `shadow-watch.timer: disabled`, `agent-loop@campaign4.service: enabled`,
  `agent-loop-liveness@campaign4.timer: enabled`.
- Active now: `agent-loop@campaign4.service: active`,
  `agent-loop-liveness@campaign4.timer: active`,
  `agent-loop-liveness-failed@campaign4.service: inactive` (normal: the
  handler starts only when a check fails; it is not enabled).
- Cairn is duty only (receives owned alarms; owns no loop effects).
- Failure owner of the check:
  `systemctl --user show agent-loop-liveness@campaign4.service -p OnFailure`
  → `OnFailure=agent-loop-liveness-failed@campaign4.service`.

## Known limits

From `agent-loop expose --json` (known_limits), verbatim:
- Not qualified for unattended use: P8 ended NOT READY; P10 requalification is in progress.
- The three P8 liveness blockers (damaged incident state, future pass time, process incarnation) are fixed in the P10 candidate and tested with stubs; not yet observed live.
- Real systemd behaviour (restart, watchdog, exit 64, start limit, timer accuracy) was never observed live; the unit files are unqualified examples.
- The CLI does not authenticate its caller: any host user who can run it acts for the recorded roles.
- Packages registered before principals were recorded cannot be continued (E_AUTHORITY_MISSING, by design).

Plus live acceptance (P12 live-2, 17/17), not in that list:
- (a) On this host's systemd (258) a restart loop keeps `Result=exit-code`,
  so the loop reports it as `crashed` — still an owned alarm to duty, then
  director.
- (b) Contention: another writer can wait up to 143 s worst case (above the
  100 s freshness limit, which then alarms honestly).
- (c) The timeout acknowledgement bound assumes local commit under 1 s
  (measured, not guaranteed).
- (d) The director's checker-failure escalation arrives up to 137 s after
  duty was told (60 s threshold plus check cadence).
- (e) Not covered: the systemd timer not firing, or the user manager being down.
