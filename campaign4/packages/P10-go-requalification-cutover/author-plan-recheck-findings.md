# P10 plan recheck: author findings (Claude, 2026-09-23)

Scope: findings only. No plan, script, task, source or binary file was changed.
Plans as hashed in plan-repair-claim.json (commit d1b9f7c).

## F1 BLOCKER (confirms Tern's reproducer): out() puts its log line into captured stdout

`live-driver.sh:40` `out()` calls `log()`, and `log()` (`:38`) uses `tee`, so the line goes to stdout.
Every `$(out ...)` capture starts with a log line. `verdict()` (`:45`) feeds `state` to `json.load`,
which fails; the error is hidden by `2>/dev/null`, so `verdict` prints nothing and `state_is` (`:74`)
is always false. The state file field names are correct (`last_verdict`, `last_check_at`, `open`:
`internal/loop/liveness.go:304-308`), so this is the only cause.

Not affected: `prop()` (its sed keeps only `Name=` lines), `snap()`, file reads by python in L4a/L7a,
journal and wake-log checks.

Effect on a live run:
- Cannot PASS: L2 (`:142`), L7c (`:164-166`), L3b (`:173`), L4a (`:182`), L7b (`:205`), L4b (`:234`).
- Silent timeouts with no result row: SETUP first pass (`:120`, 120 s), L1 settled (`:134`), L3a pass (`:154`), L3b recovered (`:177`), L4a settled (`:190`), L7b recovered (`:206`).

My error: the offline rehearsal's own `rehearsal/live-dry-evidence/results.tsv` shows 9 FAIL rows
(L1, L2, L3a, L7c, L3b, L7b, L5-stray, plus empty verdicts). I reported only the exit code (rc 0) and
filed COMPLETE without reading those rows. Most DRY FAILs come from empty stub values, but the L7c
row `window FAIL(), after ` is this bug, visible before filing.

Minimal fix (not applied): in `out()`, write the line to the log file only, for example
`echo "$(ts) + $* (captured)" >>"$EV/driver.log"`.

## F2 wall-stop cleanup does not stop the original driver

`:99` arms `systemd-run ... live-driver.sh INPUTS cleanup`, a separate process. `cleanup()` (`:76-90`)
stops the units, removes the unit files and seats, and stops the wall timer. It does not signal the
driver that is still running. That driver continues its case sequence after the wall: it can dispatch
to removed seats through `$A`, write the ledger in `$ROOT`, recreate `$SD/$U.d` drop-ins (`:170`, `:180`, `:232`)
after cleanup deleted them, and send `run` commands against unit files that no longer exist. At its
own exit the trap runs cleanup a second time. No result row records that the wall fired.

Minimal fix (not applied): the driver records its PID in `$EV/driver.pid` at start; cleanup in
MODE=cleanup writes `WALLSTOP INCOMPLETE` to results.tsv and sends TERM to that PID before it
stops units, and the driver's trap does not rerun cleanup after a TERM from the wall.

## F3 L2 leaves open work for the rest of the run

`:138` dispatches L2 with a no-claim worker, `--duration 15m --verify-window 5m`. Nothing closes or
cancels it. So from L2 to the end there is an open package:
- The `state_is rest` waits at `:190` (L4a settled) and `:206` (L7b recovered) expect rest, but with an
  open package the verdict is ok. They time out, silently (90 s and 150 s lost; after F1 is fixed these
  still fail).
- L2's 15-minute deadline fires its timer callback during a later case (by the case durations,
  about L4a or L7a). That sends a /cancel to the worker seat and a wake to the director. If the run is
  slow enough for it to land after `:211`, L6's exact counts (`c1+1`, `dd1+1`) fail for a reason not
  under test.
- Only one quiet `rest` window exists (`:135`, before L2), so this does not break that window.

Minimal fix (not applied): after the L2 assertion, close L2 by a Tern-approved command (for
example `decide` with a recorded reason) and wait for `is_step L2 closed`, or give L2 a deadline that
expires, and is asserted, before L3a. Then the later rest waits become valid.

## Status

plan-repair-claim.json says COMPLETE. With F1, that is not correct: the live driver as hashed cannot
qualify L2, L3b, L4a, L4b, L7b or L7c. I do not edit the claim or the plans without a release.
