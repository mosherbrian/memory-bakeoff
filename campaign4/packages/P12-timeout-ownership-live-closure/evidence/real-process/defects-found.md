# P12-realprocess-1: product defects found (reported to Tern before any production edit; none made)

Frozen source 487cb92 / binary b70665f5. Reproducer for both: `realprocess.sh <binary> drain <outdir>` with
`ARRIVE_FROM=end SLOW_ORDINARY=0` (pre-registered workload `yield-1/workload.json`, commit 02ba59c9).

## D1. A failed SATURATED send is recorded as "duty told"

- Code: `internal/loop/due.go:243-246` stamps `.saturation-reported` when `run(...)` returns `err == nil`.
  The wake runner returns `err == nil` with `RC 1` for a failed wake (transport refused), so a failed send is stamped.
- Seen: in all four runs the only SATURATED send failed (injected refusal); `wake.log` outcome `fail`.
  Then `run1.out` says `due backlog SATURATED ... (duty told within the last minute)` and `.saturation-reported`
  exists (`due-dir-final.txt`). Duty never received a SATURATED notice while the backlog lasted (up to 73 s).
- Smallest successor change: stamp only when `err == nil && (p.RC == 0 || p.RC == 3)` (wake started/queued);
  one line plus a test with a failing wake. Effect: a failed report is retried at the next holder, not a minute later.

## D2. A yield does not hand the lock to waiting writers

- Code: `cmd/agent-loop/loop.go` `if yielded { continue }` locks again at once; `LockLedger` waiters poll
  every 50 ms with `LOCK_NB` (`internal/loop/timeout.go`), and flock has no FIFO.
- Seen (`yield-1/lock.log`): at both yields run released and re-acquired in the same millisecond
  (`1790194421.444 release run` / `1790194421.444 acquire run`; again at `.538` 4 s later). Dispatch pid 2626950,
  waiting since about 1790194418, got the lock only at 1790194427.608, after run's next NON-yielding pass.
- The reverse also happens (`drain-1`, 2x overload by slow dispatches): run got no hold for 114 s
  (`longest gap between run holds`), so its heartbeat stood still that long; due work was drained by the
  dispatch and callback holders instead.
- Smallest successor change: after a yield, sleep a little longer than the waiters' poll (e.g. 150 ms) before
  the next `LockLedger`. That gives waiters a real window but is still not FIFO. A fair ticket queue is the
  full fix and is larger.
