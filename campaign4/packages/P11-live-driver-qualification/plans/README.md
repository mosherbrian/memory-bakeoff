# P11 plans: the P10 plans with F1, F2, F3 and repair-1 corrected

Source 1341f04 and binary c1c49a29 are unchanged. The historical P10 files are unchanged.
The initial candidate is archived in `attempt-history/initial`.

Diffs:
- `evidence/live-driver.diff`: P10 driver -> this driver.
- `evidence/repair-1-driver.diff`: the initial P11 driver -> this driver.
- `evidence/readme.diff`: this README, a new file with no P10 counterpart (diff against /dev/null).
- `evidence/rename.diff`: the other plan files. They differ from P10 only by the rename P10 -> P11 (`evidence/rename-only-check.txt`).

| Item | Correction in `live-driver.sh` | Executable evidence (offline) |
|---|---|---|
| F1 captured stdout | `out()` logs to driver.log only, and only `show()` and `state()` use it (read-only). `verdict()` prints `PARSE-ERROR` with rc 1 for unusable state. A timed-out wait writes `wait:<label> INCOMPLETE`. The run exits 1 on any FAIL or INCOMPLETE row. DRY runs write only DRY rows. | `f1-helpers.txt`: P10 10 PASS / 19 FAIL, P11 29 / 0 |
| F2 wall-stop | The driver runs inside the owned scope `p11live-driver-$RUN`. If `systemd-run` cannot create the scope, the result is SETUP FAIL, never a silent end. The driver checks by cgroup that it is in the scope. The wall timer has `AccuracySec=1s` and gets `PATH` and `AGENTDECK_PROFILE`, and it is checked active before any effect. The wall stops the scope, writes `WALLSTOP INCOMPLETE`, then runs cleanup once, under a lock. | `f2-wallstop-p10.txt` (P10: 10 late effects, driver alive), `f2-wallstop-p11.txt`, `f2-arm-failure.txt` |
| F3 L2 open work | L2 runs 3 min. It settles to `timed-out` through its own deadline timer. `L2-settle` checks one /cancel and one director wake, then rest. There is no decide: the core refuses it. | `f3-go-settlement.txt`: 15 / 0 on the frozen CLI |
| R1 profile | After the inputs are read: `export AGENTDECK_PROFILE=$PROFILE`, and the IDs and names must be four distinct pairs. Before any unit or seat effect, `registry_check` reads the profile's registry: each ID appears once, with its declared title, in `$PROFILE`, and not archived. Otherwise the result is SETUP FAIL. The wall gets the profile. | `r1-repair-tests.txt`: registry valid, wrong title, missing, duplicate, archived, wrong profile. Whole-driver runs for wrong profile, title mismatch, duplicate ID, bad deadline, past deadline and no scope stop before any effect. The wall's agent-deck calls carry the profile (`f2-wallstop-p11.txt`) |
| R2 L4b and cleanup | `stop_seat` succeeds only if the stop command succeeds and the registry then says `stopped`. If the duty stop is not confirmed, L4b is INCOMPLETE and no fault is injected. Cleanup checks that every fixture is gone from the registry and that no unit of the run is active. Otherwise it writes `CLEANUP FAIL` and does not log "cleanup done". | `r1-repair-tests.txt`: stop ok, stop fails, stop ok but still idle; cleanup with a failing remove |
| R3 L5 window | `quiet_window L5-stopped stopped 245`: collection time only, with the same acceptance (at least 3 checks, all stopped, no liveness wake). | construction run |
| R4 L6 timing | Before the fault: the authorized deadline from `status --json`, and the send-log position. After the window: the ledger interrupt time, the /cancel and director send times, the callback start and the duty wakes, all in `l6-timing.json`. The class is explicit, declared in advance: detection is 30 s or less from the deadline, and owned (/cancel and director wake sent) is 90 s or less. A late timer counts against detection, and a missing timestamp gives INCOMPLETE. | `r1-repair-tests.txt`: on time, 45 s late, exactly 30 s, 31 s, owned 95 s, before the deadline, no director wake, no deadline |
| Deadline guard | `guard()` runs in `run()`, `task()` and the config write, which are all the paths that start work. At or past `LIVE_DEADLINE` it refuses, writes `DEADLINE INCOMPLETE` and exits. Teardown sets `TEARDOWN=1` and is not refused. Reads may continue. A missing or unparseable deadline fails before any effect. The guard refuses new work when it sees expiry. Work admitted just before the deadline can still end after it, and the scope wall stops that. | `r1-repair-tests.txt`: 1 s before (runs), at the deadline (refused), 5 s after (refused), `task()` refused, expired cleanup succeeds |

Mutating paths (audit): every unit, seat, file and fault command goes through `run()`, except these, which are guarded or read-only:
- `task()`: guarded.
- The config write: guarded.
- `snap`, `log`, `result` and `l6_timing`: they write evidence only.
- `out()`, `step()`, `wakes()`, `verdict()`, `registry_check()`, `seat_status()` and the journal reads: read-only.
- The MODE=cleanup scope stop and `cleanup()`: teardown.

`evidence/construction-dry/` shows command construction only (DRY): 15 DRY rows. It is not behavioural evidence.
