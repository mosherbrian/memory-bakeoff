# P12-bounded-deadline-1 — independent review (corvid), partial

- **Action:** existing `P12-writersafetyreview-1` 25 m pass, re-scoped to the
  partial `bounded-deadline-1` output (explicit director release; no new grant).
- **Claim:** `bounded-deadline-claim.json` (`facfdecd…`) against
  `bounded-deadline-allocation.json` (`438c81f3…`) and
  `bounded-deadline-receipt.json` (`f8e58d50…`); candidate `f86daf91be58`, binary
  `2656bb97`.
- **Verdict: INCOMPLETE preserved** (the claim governs, not any generic completion
  wake). Aggregate contention remains unresolved → **no live PASS**. Delivered
  pieces are verified and reusable.

## Pins / integrity

- **36/36** claim hashes match (11 plans + 23 evidence + 2 decision); decision and
  receipt match. Source `f86daf91…`; `git diff 844d156..f86daf9` **empty** for
  `internal/core`, `internal/py`, `conformance/cases`; changed set bounded
  (cmd/loop, timer template, `due.go`+test, timeout, `mutate_go.py`). Binary
  `2656bb97…` matches; timer template `502745ac…` matches.

## Verified delivered pieces (reusable)

1. **Reload-proof calendar template.** `OnCalendar=*-*-* *:*:00,30 UTC`,
   `Persistent=false`, `AccuracySec=1s`, monotonic triggers removed. Independent
   cadence test (new template, 15 real reloads / 20 s over 300 s): **old template
   0 checks; new template 10 checks, gaps 29.7–30.3 s**.
2. **Due markers (detection only).** A callback waits `DueWait=5 s`; on
   `E_LEDGER_BUSY` it writes an **atomic** marker (temp + `fsync` + rename) carrying
   qid/action/execution/written_at/pid/invocation. Every lock holder runs
   `ProcessDue` on acquire and before release; each marker is **re-validated under
   the lock** against the ledger identity; it is removed only after the deadline is
   **settled or explicitly rejected** (rejected kept as
   `<name>.rejected-<time>.json` with reason); unreadable/malformed/unsafe/mismatched
   hints are rejected. A marker is a **trusted, durable, action-correlated
   detection hint** — `deferred_callback` records detection — and it **never**
   proves ownership/recovery; the ack is still separate.
3. **Busy-callback race reproduced (my run).** A run pass frozen holding the lock;
   callback B **deferred after 5.07 s**, wrote the marker; A on release settled it
   (`due L-w1.json: settled (interrupted)`); FINAL `step=timed-out`, timeout intact,
   `deferred_callback: 18:44:44Z`, one cancel, no verifier dispatch.
4. **Retained:** writer-safety race (baseline loses timeout, candidate keeps it);
   `go test ./...` ok; due/lock tests pass
   (`TestDueMarkerIsSettledByTheNextHolder`,
   `TestDueMarkerHintsAreCheckedAgainstTheLedger`, `TestLedgerLockIsExclusiveAndBounded`,
   `TestMarkTimedOutOnlyForTheCoresCurrentAction`); shipped-binary conformance
   **125/125**; mutation **116/116**; CLI/shutdown/wall/f1/r1 regressions pass.

## Calendar-proof limitation (recorded, then closed independently)

The author's cadence proof ran the **prior `844d156` checker binary** as the checked
command (cadence is the template's; the release carries the same template bytes).
That is **not** a full new-binary end-to-end. I verified **candidate compatibility
separately**: new binary `2656bb97` + new template, 4 real reloads / 20 s over 70 s →
**3 checks, gaps 30.0/30.0 s** (old template 0). Candidate is compatible; the
limitation is recorded, not hidden.

## Unresolved blocker — aggregate lock-hold bound

- A run pass holds the lock for its whole operation; its hold grows with the number
  of **wake sends × the 30 s transport timeout**. `ProcessDue` on acquire/release
  can **itself lengthen the hold** with a marker backlog (each settlement may send
  wakes bounded 30 s). So the critical section has **no fixed end-to-end bound**.
- Consequence: a busy callback defers at 5 s (detection recorded via the marker),
  but **settlement/ownership waits for the current holder to release**. Detection
  ≤30 s therefore holds only when holders release within ~25 s; the callback's
  120 s wait and the duty rerun path are **not** a settlement or an ack.
- Crash/replay: markers are durable until settled/rejected (no deletion before a
  durable outcome), so a crash leaves a due marker for the next holder — but the
  hold-time growth remains.

## Smallest coherent remaining fix (described, not implemented)

Bound **work per lock hold** rather than the whole pass: stop starting new sends
after a per-hold budget and **yield/release** (re-acquire on the next pass), and run
`ProcessDue` under the same budget, so a holder cannot exceed the detection window.
This is a change to the run-pass scheduling, not to the marker/template pieces,
which are already sound. Reusable pieces: the calendar template and the due-marker
detection mechanism. No implementation, allocation or live authorization by corvid.

**Consolidated: INCOMPLETE** — no live PASS; reusable pieces verified; aggregate
bound blocker preserved with the smallest coherent fix above.
