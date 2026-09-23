# P12-fair-handoff-1 — independent review (corvid)

- **Action:** `P12-fairhandoffreview-1`, start `21:28:51Z`, deadline `21:58:51Z`.
- **Claim:** `fair-handoff-claim.json` on allocation `b1b1d65a`; release `5da2b36f`
  / binary `842e44d6`; predecessor `real-process-claim.json` INCOMPLETE retained.
- **Verdict: PASS** on the allocation, with the **returned capacity restriction**
  and residuals flagged as live-readiness items (no blanket PASS).

## Pins / integrity

- **286/286** `files_sha256` match; release binary `842e44d6…` matches; source
  worktree `agent-loop-p12f` HEAD `0a38a8a` with `git diff 487cb92..5da2b36`
  **empty** for `internal/core`, `internal/py`, `conformance/cases`; changed set
  bounded (queue.go, notice.go, due/loop/timeout, tests, `mutate_go.py`). No
  private-harness references in the evidence (committed `fairhandoff.sh`,
  `analyse.py`, `run-all.sh`).

## Allocation requirements — evidence

- **D1 (saturation stamp):** stamped only on wake rc 0/3 (transport accepted, never
  an ack); rc 1/error/budget refusal retried by the next holder; every attempt kept
  in `.saturation-attempts`; stamp-write error reported. Unit-tested
  (`TestSaturationIsStampedOnlyOnAnAcceptedWake`).
- **D2 (FIFO admission queue):** numbered `<db>.queue/`, only the oldest live entry
  may try the flock; entry dropped on lock, so a re-locking holder re-queues.
  **Numeric caps run 1 / due 3 / ordinary 2**; full class refused at once with
  `E_LEDGER_SATURATED`. `AdmittedWait = 6 × 11 s = 66 s`. Dead/pid-reused/stale/
  malformed entries reaped (`TestDeadReusedStaleAndMalformedEntriesCannotWedgeTheQueue`);
  caps visible (`TestAdmissionIsCappedAndRefusalIsVisible`); ledger lock before a
  fresh load; 10 s hold budget retained.
- **D3 (notice semantics):** durable notice record written **before** the wake with a
  stable incident key; at most **ONE** labelled `REPEAT` per incident across
  restarts; then `unresolved` (visible, never marked delivered/acked); no extra
  cancel/dispatch/settlement; cancel wording stays correct.
- **Frozen / retained:** core/py/cases frozen; shipped conformance **rc=0, 125/125,
  1751 steps**; `go test ./...` ok (internal/loop **81 PASS / 0 FAIL**); mutation
  **137/137** on `0a38a8a`; calendar templates, writer races, stopped escalation,
  prompt stop all retained in `regress/`.

## Independent unshared real-process check (my run)

Committed harness, **release binary `842e44d6`**, my own variation
(`ARRIVE_EVERY=3 FAIL_EVERY=4 QUEUED_EVERY=3`, `SLOW_ORDINARY=1`, drain):

- **14/14** accepted due markers settled; **MAX settlement latency 59.9 s** after
  the deadline; max marker age 51.4 s; drain near-FIFO (3 pairwise inversions at
  0.5 s sample resolution).
- **Queue:** 66 admitted / 65 refused; admitted→acquire max wait **47.25 s**
  (dispatch), **44.86 s** (run) — under the 66 s bound; ordinary arrivals 10 rc=0,
  20 `SATURATED`.
- **Yield/hand-off:** 2 yield lines, 65 `yielded=true` heartbeats, run→dispatch
  hand-offs 5; longest run hold 9.12 s.
- **D3:** max **1 effect per incident**, 0 identical notice effects twice; durable
  notice records states accepted/failed/not-started, **repeats used 0**; ambiguous
  slow dispatches landed without a receipt.
- **Local non-subprocess time** max 0.084 s; heartbeat max age 50.9 s.
  `analysis rc=0`.

## Returned capacity restriction (explicit; needs a Tern ruling)

`timeout-ack` and the liveness **check** are in the **due** class (cap 3) with the
deadline callbacks. Under a due burst of 3, an ack or a check is **refused at once**
with `E_LEDGER_SATURATED` and must be retried (check: next 30 s timer; ack: a human
retry). **Detection is not lost** (a refused callback writes its due marker), but
**ack latency under a deadline burst depends on this cap** — a live-readiness gap
for the 60 s ack bound. The author returned it explicitly and did not change it;
options (separate `ack` class, or exempt ack/check from the due cap) require a
grant. **No blanket PASS of the live ack criterion.**

## Residuals (honest, carried)

- PID reuse and malformed entries shown by **unit test only** (real reuse cannot be
  forced here); runner-error SATURATED and stamp-write-error message are
  unit/code-only.
- A writer refused at admission is **not ordered** against other refused writers on
  retry (ordering guaranteed only among admitted writers).
- A holder **outside the queue** (the `flock(1)` stall fixture, or a pre-queue
  binary) is not ordered; admitted waits stayed ≤47.25 s with a 40 s stall here, but
  that is **not guaranteed** for arbitrary outside holders.
- **Finite observed drain only**; host-local empirical timings; not a universal
  latency guarantee. Detection/recovery/**ack live criteria unchanged**.
- **Leftover from an earlier round:** `p12test-cadence-1615323.timer` still active
  (writer-safety cadence test); not touched without a ruling. This round's roots
  were removed by exact path.

No source edits by corvid; no fleet/live/cutover or host-clock change. **PASS**
returned to Tern, with the capacity restriction and residuals as the items for the
live decision.
