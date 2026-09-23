# P12-writer-safety-1 — independent review (corvid)

- **Action:** `P12-writersafetyreview-1`, start `18:19:09Z`, deadline `18:44:09Z`.
- **Claim:** `writer-safety-claim.json` (`cb89137b…` allocation, `d9c52ce5…`
  receipt); candidate `844d15670aeb`, binary `ab3cfc22`.
- **Verdict: PASS.** Every allocation requirement is met and independently
  reproduced; remaining unsupported obligations are stated precisely below.

## Pins / integrity

- **30/30** claim hashes match (11 plans + 17 evidence + 2 decision); decision and
  receipt match. Source `844d15670aeb…`; `git diff 53c9719..844d156` **empty** for
  `internal/core`, `internal/py`, `conformance/cases`; changed set bounded
  (cmd/loop, loop/timeout, tests, `mutate_go.py`). Binary `ab3cfc22…` matches.

## Allocation requirement — evidence

1. **All competing writers serialized (no `step_at` CAS).** One ledger lock
   (`<db>.lock`, `flock`) is taken **before** opening the ledger and held for the
   whole operation. I audited the CLI/entry writers: `runDispatch`, `runClaim`,
   `runDecide` (`openLocked`), `runRun` (per-pass lock), `runTimerCallback`
   (120 s), `runTimeoutAck` (60 s), and the liveness `Check` (`withTimeouts`, 30 s).
   `Tick` and `AckTimeout` no longer re-lock (they run on the caller's fresh,
   locked view) → **no nesting**. `runStatus`/`expose` are read-only and unlocked
   (as claimed). No stale write can start.
2. **Consistency boundary (core transition + record + effect intent).** The
   critical section spans core transition, package save and effect sends;
   `MarkTimedOut` now keys on the **core's current `action_id`**, not the loop step,
   so a step the loop marked blocked/recovery is still timed out by its deadline.
   Existing intent/reconciliation semantics govern crash replay.
3. **Deadlock-safe bounds.** `LockLedger` is `LOCK_NB` polling with a bounded wait;
   timeout is the owned fault `E_LEDGER_BUSY`. A callback that cannot lock **tells
   duty the exact rerun command** and does not settle. No recursive acquisition.
4. **Deterministic real multi-process race — reproduced (my run).**
   `race-callback-vs-run.sh` (two processes, input-pipe barrier):
   - **Candidate `ab3cfc22`:** A (`run --once`) frozen after loading the ledger;
     B (deadline callback) **WAITS > 3 s** while A holds the lock; A takes the
     `blocked()` path; **FINAL `step=timed-out`, timeout intact**.
   - **Baseline `ec184be9`:** B **finishes while A is frozen**; A's stale write →
     **`step=blocked`, `timeout=null`** — the bug reproduced on the pre-fix binary.
   `same` mode keeps the timeout on both. Go: `TestLedgerLockIsExclusiveAndBounded`,
   `TestMarkTimedOutOnlyForTheCoresCurrentAction`,
   `TestRunAndCheckerNeverDoubleEscalateOrLoseAnAck` all pass.
5. **Controlled real unit-file 45 s timer across reloads — independently measured.**
   Real `p12test-cadence-*` unit-file timer (`OnActiveSec=45s`,
   `OnUnitActiveSec=45s`, `AccuracySec=1s`), candidate `liveness`, exact cleanup:
   - control (no reload): checks at **45.83, 91.83 s**, `MAX_GAP=46.0`;
   - reload every 60 s (3 real reloads): checks at **45.39, 91.4, 137.4 s**, gaps
     **46.0, 46.0** — reloads at 60 s did not move the cadence.
6. **Retained / frozen.** Shipped-binary conformance **rc=0, 125/125, 1751 steps**;
   `go test ./...` all ok; mutation **113/113**; host parity 316/321 + 5; CLI
   regressions (`cli-stopped-noack`, `a-cli-timeout idle/refused`) pass. No
   main/install/live/host-clock change.

## Remaining unsupported obligations (precise)

1. **Reload storm < 45 s:** a `daemon-reload` less than 45 s apart restarts the
   liveness timer's first `OnActiveSec` countdown (measured: **0 checks in 300 s**
   with 20 s reloads); after the first firing, 60 s reloads did not move it. Not
   fixed (unit template unchanged) — a **checker-cadence qualification limit**.
2. **Stalled transport:** a writer holding the lock during a stalled send delays
   others up to 30 s per send; a callback waits ≤120 s then tells duty the rerun
   command (the deadline is **not settled until rerun**) — owned but a latency risk.
3. **Checker own-supervision / systemwide failure:** if `run` and the liveness timer
   are both down, nothing escalates (qualification limit, not solved here).
4. **Clock:** continuous host UTC assumed (unchanged; FakeClock loop-side only).
5. **Read-only `status`/`expose`** are unlocked and may show a state mid-operation.
6. **Live-only:** L4a/L4b, live ack latency, L6b cadence on real seats.

## Effect

**PASS.** The writer-safety allocation is satisfied: all writers serialized by a
fresh-state lock, consistency boundary correct, deadlock-safe, real process race
reproduced (candidate keeps the timeout; baseline loses it), and the real 45 s
unit-file cadence measured across reloads. Residuals 1–6 are carried precisely to
the live/qualification decision. No source edits by corvid; no main/install/live.
Returned to Tern.
