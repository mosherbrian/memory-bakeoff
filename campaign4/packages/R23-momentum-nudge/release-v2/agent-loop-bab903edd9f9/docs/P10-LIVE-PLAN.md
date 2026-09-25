# P10 live qualification plan (for Tern's signature)

Executable plan for stage C. Nothing here runs until Tern signs the exact
binary, config, units, fixture IDs, commands and deadlines. All commands run as
the host user; `$C` is the fixture config. Times come from the host journal
(`journalctl --user -o short-iso-precise`) and the wake send log, never from a
model.

## Fixed inputs

- Candidate binary: `bin/agent-loop` of the release archive named in
  `completion-claim.json` (`~/projects/agent-loop-releases/agent-loop-<commit>/`),
  with the sha256 recorded there: the exact bytes corvid reviews. Check the hash
  before copying it into the prefix.
- Private prefix: `P=~/p10fix` with `$P/bin/agent-loop` (a copy of the candidate).
- Four NEW fixture seats in profile campaign4, created by cairn at prep and
  confirmed by `agent-loop check`:
  `p10-fixture-worker-1`, `p10-fixture-verifier-1`, `p10-fixture-director-1`,
  `p10-fixture-duty-1`. No main seat receives any task or fault.
- Config `$P/p10fix.json` (from `examples/project.template.json`):
  `project` `p10fix`, `profile` `campaign4`, `wake` `~/.config/agent-deck/wake`,
  `db` `$P/p10fix.db`, `stream_dir` `~/.config/agent-deck/acp-stream`,
  `claims_dir` `$P/claims`, `artifacts_dir` `$P/art`, `director`
  `p10-fixture-director-1`, `duty` `p10-fixture-duty-1`, `seats` the four ids,
  `bin` `$P/bin/agent-loop`, `unit` `agent-loop-p10fix.service`.
- Units (isolated names; generated from `examples/systemd-unqualified/` with the
  binary and config paths replaced; nothing else changes):

      sed "s#%h/.local/bin/agent-loop#$P/bin/agent-loop#; s#%h/.config/agent-loop/%i.json#$P/p10fix.json#; s#%i#p10fix#g" \
        examples/systemd-unqualified/agent-loop@.service > ~/.config/systemd/user/agent-loop-p10fix.service
      sed "..." agent-loop-liveness@.service > ~/.config/systemd/user/agent-loop-liveness-p10fix.service
      sed "..." agent-loop-liveness@.timer   > ~/.config/systemd/user/agent-loop-liveness-p10fix.timer
      systemctl --user daemon-reload
      systemctl --user start agent-loop-p10fix.service agent-loop-liveness-p10fix.timer   # started, never enabled

- Evidence directory: `campaign4/packages/P10-go-requalification-cutover/live-1/`.
  Capture before and after every case:
  `systemctl --user show agent-loop-p10fix.service -p ActiveState,SubState,Result,NRestarts,InvocationID,MainPID,ExecMainStartTimestamp --timestamp=unix`,
  `$P/bin/agent-loop expose --config $C --json`, `cat $P/p10fix.db.liveness.json`,
  and the new lines of `~/.local/share/agent-deck/wake-send.log`.

## Cases

Each case lists the fault actor, the onset, the bound from the recovery ruling
and the pass condition. A case without its evidence is NOT READY, never PASS.

**L1 positive handoff, restart without duplicate.** Actor: the fixture seats.
`$A dispatch $C --qid L1 --worker p10-fixture-worker-1 --verifier p10-fixture-verifier-1 --task @l1-worker.txt --verify-task @l1-verify.txt --duration 10m --verify-window 10m`.
The worker writes `art/l1.txt` and runs the claim command given in its task. Then
the verifier does the same. Then `systemctl --user restart agent-loop-p10fix.service`,
followed by `$A decide $C --qid L1 --kind question_answered --ref P10-L1 --reason "live witness"`.
Pass: the ledger holds publish, verify_pass and decide with cast actors and the
package record names the fixture principals; the wake log shows exactly one
dispatch to each seat, including after the restart.

**L2 kill during work.** Onset: `systemctl --user kill -s KILL agent-loop-p10fix.service`
while L2's worker step is open (dispatched, no claim yet). Pass: the journal shows
a restart within RestartSec (5 s) plus start time; `NRestarts` goes up by 1; the
first pass after the restart logs `outbox: ... held-awaiting-receipt` and the wake
log shows no second dispatch to the worker. Bound: explicit event (the kill is
observable), so detection is 30 s or less and recovery 60 s or less.

**L3 hang.** (a) `kill -STOP $(systemctl --user show -p MainPID --value agent-loop-p10fix.service)`.
Pass: the journal shows `Watchdog timeout` within 90 s plus 5 s, then a restart with a new
InvocationID; the first check after the restart and before the first pass says
`starting` (quiet, not recovered); after the first pass it says ok or rest.
(b) The outside check without the watchdog: install a drop-in with `WatchdogSec=0`,
then SIGSTOP. Pass: `agent-loop liveness` (from its timer, not by hand) reports `hung`
within 100 s plus 45 s plus 5 s (suspicion bound 180 s); duty is woken with the ack command.
Then SIGCONT, remove the drop-in, daemon-reload, and restart.

**L4 restart loop and owned escalation.** Drop-in:
`ExecStart=` then `ExecStart=$P/bin/agent-loop run --config /nonexistent.json`; restart.
Pass: the unit reaches `failed` with `Result=start-limit-hit` after 5 starts in 300 s;
the check reports `restart-loop` and wakes duty with the exact `liveness-ack`
command; the duty seat runs it (`--by p10-fixture-duty-1 --next ... --within 10m`),
and the state file shows the ack's owner, next action and absolute deadline. The
incident stays open until the drop-in is removed and a fresh pass arrives, then
closes as `recovered` with `escalated` recorded separately.
(b) Unavailable duty: `agent-deck -p campaign4 session stop p10-fixture-duty-1`,
then repeat the failing start. Pass: the same check wakes the director because the
duty wake fails, and the director seat's `liveness-ack` is recorded.

**L5 intentional stop and quiet rest.** `$A stop $C`. Pass: the journal shows run
exiting with status 64 and no restart; `systemctl --user start agent-loop-p10fix.service`
exits 64 again (the marker holds); at least 3 minutes and at least 3 completed
liveness runs (from the journal) show `stopped` with no wake. `$A start $C` resumes.
Then at least 3 minutes and at least 3 checks with no open package show `rest`
with no wake.

**L6 real timeout while run is down.** `$A dispatch $C --qid L6 ... --duration 2m`
with a worker task that writes no claim. Then `$A stop $C` (run is down). Pass:
at the deadline the timer unit `agent-loop-p10fix-L6-w1.timer` fires
`timer-callback`; the journal shows `interrupted`; the wake log shows exactly one
`/cancel` to the worker and one wake to the director; `systemctl --user start agent-loop-p10fix-L6-w1.service`
(a replay) prints `already-handled` and sends nothing.

**L7 damaged state, future pass and prior incarnation in the real checker.**
(a) `printf '{bad' > $P/p10fix.db.liveness.json`; pass: the next timer run alarms
`unknown`, a `.damaged-<time>.json` copy holds the same bytes, and duty is woken once
over the next 3 runs. (b) Write a pass 10 minutes in the future into the ledger with
the fixture writer used in `evidence/liveness-cases.sh`; pass: `unknown` alarm.
(c) `systemctl --user restart agent-loop-p10fix.service` and read the check within
60 s; pass: `starting`, and then ok or rest only after a pass from the new InvocationID.

## Cleanup (automatic, exact IDs only)

    systemctl --user stop agent-loop-p10fix.service agent-loop-liveness-p10fix.timer 'agent-loop-p10fix-*.timer'
    systemctl --user reset-failed 'agent-loop-p10fix*'
    rm ~/.config/systemd/user/agent-loop-p10fix.service ~/.config/systemd/user/agent-loop-liveness-p10fix.*
    rm -r ~/.config/systemd/user/agent-loop-p10fix.service.d
    systemctl --user daemon-reload
    agent-deck -p campaign4 session stop <each of the four fixture ids>   # then remove, as for P8
Archive `$P` (ledger, state, claims) into `live-1/` before removing anything.

## Measurement

For every case: the fault onset from the journal line of the command, the
detection from the journal line of the unit transition or the liveness verdict,
recovery or acknowledged escalation from the state file and wake log. Report each
interval against 30/60 s (explicit) or 180/240 s (suspicion), with all failures and
censored cases. A host outage or a clock step during a case makes it unmeasurable,
not a pass.
