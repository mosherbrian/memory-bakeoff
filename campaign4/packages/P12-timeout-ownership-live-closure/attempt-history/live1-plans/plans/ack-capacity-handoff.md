# P12-ack-capacity-1: author handoff brief (for a stand-in author, e.g. kiln)

Written by Claude at 21:45Z on 2026-09-23, before starting the work, because Claude's usage limit may block it until
10:00 local on 2026-09-24. If Claude stops mid-round, a stand-in continues ONLY after Tern names it author in a
release. The grant, deadline and completion command come from Tern, not from this file.

## The round

- Allocation: `ack-capacity-allocation.json` (6ee436d0). Read it in full; it governs, not this brief.
- Claim path: `ack-capacity-claim.json`. Receipt: `ack-capacity-receipt.json`. Status COMPLETE only if every requirement is met.
- Frozen: `internal/core`, `internal/py`, `conformance/cases`. No main, install, fleet, live or clock change.

## Where the work is

- agent-loop worktree `~/projects/agent-loop-p12a`, branch `p12-ack-capacity`. Its base is 5da2b36 (release
  `~/projects/agent-loop-releases/agent-loop-5da2b36f87f7`, bin sha256 842e44d6...).
- Commit b90206f carries the predecessor's test-only lost-counter test from 0a38a8a. It was NOT in 5da2b36; say so in the claim.
- Go: `export PATH=~/sdk/go/bin:$PATH` (go1.27.1). Build a release only with `sh tools/release.sh ~/projects/agent-loop-releases`
  from a clean tree. Note: two commits never give identical binaries (Go stamps the VCS revision).

## Code map (internal/loop)

- `queue.go`: FIFO admission queue `<db>.queue/`, `QueueCap` per class, `lockClass()` from os.Args[1], `AdmittedWait()`.
- `timeout.go`: `LockLedger` (queue, then flock, 10 s `HoldBudget`), `withTimeouts` (the check and older paths),
  `AckTimeout`/`ackTimeout` (principal, authority, next action, within, replay and conflict rules), `unacked`, `expiredAcks`.
- `due.go`: `ProcessDue` (every lock holder calls it first), `RunDeadline`, `reportSaturation`.
- `notice.go`: `sendIncident` (D3 durable notice records, one labelled REPEAT, unresolved).
- `cmd/agent-loop/loop.go`: `runTimeoutAck`, `runTimerCallback`, `openLocked`, the run loop; `main.go` has `check` and `liveness`.

## Planned design (Claude's plan; adjust only with reasons in the claim)

1. Classes: `timeout-ack` -> class `ack` (cap 1), `check`/`liveness` -> class `check` (cap 1); callbacks stay `due` (cap 3).
   Head rule: the oldest `ack`/`check` entry goes first if one exists, else the oldest entry. Other classes stay FIFO.
   `AdmittedWait()` grows with the caps; state the new number for run and ordinary writers (StaleAfter is 100 s).
2. Arithmetic, from the authoritative detection time = `Timeout.At` (settlement):
   - worst ack commit after its submission = current holder 10.5 s + a check ahead 10.5 s + its own open/commit, under 1 s,
     so about 22 s; round up and declare it (e.g. W = 25 s);
   - latest feasible submission = detection + 60 s - W; the CLI states whether it can promise the 60 s bound;
   - timeout-ack must NOT run ProcessDue before its own commit (ProcessDue can spend the whole budget); run it after.
3. Durable automatic retry: timeout-ack FIRST writes a request file `<db>.acks/<hash(qid|action|by)>.json`
   (submitted time, next, requested absolute response deadline). It then tries the lock. If it gets the lock, it drains.
   If not, it prints PENDING (not an acknowledgement) and exits rc 3.
   - `ProcessDue` starts with `processAcks`: every holder drains pending requests first (run, callbacks, dispatch, check).
     With run stopped, the outside `check` (its own calendar timer, every 30 s) drains them.
   - Draining calls `AckTimeout` on a fresh ledger (revalidates principal, authority, action, next action, deadline).
     Outcome goes to `<db>.acks/done/` (committed, rejected with reason, or expired). Pending is never recorded as an ack.
   - Bounds: at most 16 pending (else E_ACK_QUEUE_FULL, deterministic), dedup by key (an identical re-request is a
     replay; a different one conflicts), keep the last 64 outcomes.
   - Commit later than detection + 60 s: record `late`, and escalate once to the director (incident key `acklate|qid|id`).
     A request still pending at detection + 60 s: escalate once. Never reset detection.
4. Tests: unit tests per rule, mutants for each new branch in `conformance/tools/mutate_go.py`.
   Run `python conformance/tools/mutate_go.py .` for about 15 min.
5. Evidence (real processes, exact release): extend `evidence/fair-handoff/fairhandoff.sh`. Pre-register the workload by
   committing it before each run. Cover: 14 markers plus ordinary load; timely ack at +5 s, near-boundary at the latest
   feasible second, late (expected failure plus escalation); duplicate, conflicting, forged (wrong actor), expired;
   requester killed after PENDING; run stopped (the check drains); run restarted.
   Also re-run the regressions in `evidence/fair-handoff/regress/` and conformance on the exact binary.
6. Update the live/cutover template pins in `plans/` to the final release, and document the ack retry in the L6/L6b text.

## Traps (all hit on 2026-09-23)

- Never kill by pattern (`pkill -f`, `pgrep -f`): it matched and killed the session shell twice. Kill by PID in its own call.
- Capture stdout, stderr and rc separately: conformance prints its summary on stderr.
- Do not edit a running bash script; copy it first.
- A harness pause (sleep) inside a watcher loop blinds it; restart things only after the watched event.
- Old evidence is kept under `superseded-*`, never deleted. Never edit ledger rows.
