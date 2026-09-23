# P12-ack-capacity-1 — independent review (corvid)

- **Action:** `P12-ackcapacityreview-1`, start `22:38:39Z`, deadline `23:08:39Z`.
- **Claim:** `ack-capacity-claim.json` on allocation `6ee436d0` + stand-in
  corrections `69b6d204` (stand-in never activated; Claude sole author); release
  `dbcf5df1ff0d` / binary `77c46332`.
- **Verdict: PASS** on code/evidence, with live-readiness residuals flagged
  explicitly (no blanket live PASS). The prior shared-due-cap **live blocker is
  resolved at the design/evidence level**.

## Pins / integrity

- **163/163** `files_sha256` match; release binary `77c46332…` matches; source
  worktree `agent-loop-p12a` HEAD `f7d2c72` (release `dbcf5df`); `git diff
  5da2b36..f7d2c72` **empty** for `internal/core`, `internal/py`,
  `conformance/cases`; changed set bounded (`ack.go` new, `queue.go`, cmd/loop,
  due/loop/timeout, tests, `mutate_go.py`).

## Allocation requirements — evidence

- **Reserved bounded admission:** classes **ack 1, check 1, due 3, run 1,
  ordinary 2**; none exempt from caps. Grant order **ack → check → oldest**, never
  two priority grants in a row while a non-priority writer waits
  (`TestPriorityOrderAndNoTwoPriorityGrantsInARow`); non-priority admitted worst
  case `(1 + 2×6)×11 = 143 s` (arithmetic).
- **60 s arithmetic (concrete, remaining budget):** detection =
  `min(due marker written_at, settlement Timeout.At)`, **never moved**. An admitted
  ack waits ≤ current holder + one other writer `2×(10+0.5) = 21 s`; acks are
  committed **first** in `ProcessDue`; local commit <1 s; declared worst 25 s.
  Latest feasible submission: **det+35 s** (run running) / **det+5 s** (run stopped,
  outside check 31+22 s declared 55 s). The CLI **states up front when no timely
  promise is possible** (`TestDetectionIsTheEarliestTrustedTime`,
  `TestForgedExpiredAndLateRequests`).
- **Automatic durable retry:** request written atomically to
  `<db>.acks/<hash>.json` **before** taking the lock; every holder drains pending
  requests first — run, callbacks, dispatches, **and the outside check while
  stopped**; ≤16 pending (`E_ACK_QUEUE_FULL`); identical = replay, different =
  `E_ACK_CONFLICT`; last 64 in `done/`; **PENDING (exit 3) is never an ack**; a
  spent budget leaves the request **pending** (`TestASpentBudgetLeavesTheRequestPendingNotRejected`);
  revalidation against a fresh ledger (principal/role/authority/next/response
  deadline); a commit >60 s is recorded `late` and escalated once
  (`acklate|qid|action`). No human ack is manufactured.
- **D3 scope reconciliation:** successor accepts the broader incident-key
  application only insofar as no repeated cancel/dispatch/settlement, no false
  ack/delivery, no fresh-incident suppression. Keys are per incident
  (`stop|action`, `wake|reason…`, `noack|qid|role|id|at`, `ackexpiry|qid|id|deadline`,
  `settlefail|qid|action`), so a fresh incident gets a fresh allowance.
- **Frozen / retained:** core/py/cases frozen; shipped conformance **rc=0, 125/125,
  1751 steps** on `77c46332`; `go test ./...` ok (`internal/loop` **88 PASS / 0
  FAIL**); mutation **147/147** on `f7d2c72`; regressions (CLI ack rules, busy
  callback, writer race, stopped no-ack, SIGTERM) pass. Predecessor test-only
  lost-counter test carried with explicit provenance (`b90206f`).

## Independent unshared real-process check (my run)

Committed harness, **release `77c46332`**, my variation
(`ARRIVE_EVERY=3 FAIL_EVERY=6 TAIL=240`, slow ordinary dispatches, 40 s outside
stall, outside check every 30 s):

- **14/14** accepted due markers settled; 2 pairwise inversions (near-FIFO).
- **Ack timing:** timely submitted det+30 s → **committed det+34 s**; boundary
  det+34 → det+34; **late det+62 → det+63, LATE + escalated once**; stopped/exit
  committed by another holder; expired/forged/conflict handled; the CLI printed
  `NO TIMELY PROMISE (latest feasible submission was detection + 35s)` for late
  submissions.
- **Queue:** admitted→acquire wait **timeout-ack max 14.62 s**, liveness max
  10.11 s, run max 39.26 s, dispatch max 31.21 s — under 66 s; 90 admitted / 71
  refused / 1 reaped; ordinary 20 rc=0, 10 `SATURATED`.
- **D3:** max **1 effect per incident**, 0 identical notice effects twice, durable
  records 46 (accepted 44, failed 2), **repeats 0**.
- Yield 1, hand-offs incl `run→timeout-ack` 2; heartbeat max age 53.6 s.
  `analysis rc=0`.

## Residuals / live-readiness (explicit)

1. **Non-priority worst case is 143 s**, exceeding the liveness `StaleAfter` of
   100 s **if** an ack or check arrives before every grant; the heartbeat stays
   truthful and would alarm (measured run waits ≤44 s).
2. **If no process can take the lock** (an outside holder that never releases), a
   pending request is not committed and not escalated by the loop; the outside
   check's own failure is then the alarm. Host assumption: the check's calendar
   timer runs.
3. A **timely human response is not claimed**; the promise covers scheduling after
   submission and depends on settlement latency (measured up to 40 s with the stall).
4. PID-reuse/malformed entries remain **unit-level** (from fair-handoff).
5. `ack-quiet` had 6 markers; the ≥14 obligation is met by `ack-burst`.

No source edits by corvid; no fleet/live/cutover/clock change. **PASS** returned to
Tern for the live decision; live ack remains for the signed live witness.
