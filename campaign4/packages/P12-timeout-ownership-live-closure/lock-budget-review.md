# P12-lock-budget-1 — independent review (corvid)

- **Action:** `P12-lockbudgetreview-1`, start `19:20:58Z`, deadline `19:50:58Z`.
- **Claim:** `lock-budget-claim.json` on allocation commit `4dc82958`; candidate
  `487cb92ce9d3`, binary `b70665f5`.
- **Verdict: bounded FAIL** — the per-hold budget works and is reproduced on the
  released binary, but the **candidate contention evidence was produced with a
  different, unpersisted binary** (`8ec5c12e…`), so it does not pin the release.

## Pins / integrity

- **37/37** claim hashes match (11 plans + 24 evidence + 2 decision); decision and
  receipt match. Source `487cb92c…`; `git diff f86daf9..487cb92` **empty** for
  `internal/core`, `internal/py`, `conformance/cases`; calendar template unchanged
  (`502745ac`). Changed set bounded (cmd/loop, host runner, loop/due/timeout, tests,
  `mutate_go.py`). Binary `b70665f5…` matches.

## Mechanism (verified in source + reproduced)

- **Budgeted Runner per holder:** `HoldDeadline` caps every subprocess to
  `min(timeout, time left)`; a subprocess is not started with <1.5 s left
  (`ErrBudget`, and the wake transport returns owned `E_BUDGET_EXHAUSTED` with **no
  receipt for an unsent wake**). `ExecRunner.WaitDelay=0.5s` stops a lingering child
  from stretching the call. **B = 10 s.**
- **Yield/reacquire:** `Tick` starts a unit only with ≥6 s left, else yields
  between units (`Yielded`, "yield: …"; run continues next pass and retries on
  `E_LEDGER_BUSY` instead of exiting). Never mid-transition.
- **Due work:** `ProcessDue` on acquire and before release, **oldest first, within
  the budget**, leftovers to the next holder; unsettled >20 s → **SATURATED** report
  to duty (once/min); callback waits 8 s then writes the marker and keeps trying to
  22 s, settling due work itself.

## Independent reproduction (released binary `b70665f5`)

- **Hold scaling (my run):** `hold-scaling.sh <released> 20` → holder **10.5 s**,
  second writer waited 9.5 s. Baseline `f86daf9` (`2656bb97`) → holder **20.0 s**,
  writer waited 19.0 s. The 20 s send no longer stretches the hold.
- **`hold-scaling.txt`** (author) is on the **released** `b70665f5` (10.5 s at slow
  20 s and 40 s) — correct pin.
- **`go test ./...` all ok**; budget/due/lock tests pass
  (`TestDueMarkersAreBudgetedOldestFirstAndSaturationIsReported`,
  `TestLedgerLockIsExclusiveAndBounded`, `TestDueMarkerIsSettledByTheNextHolder`,
  `TestDueMarkerHintsAreCheckedAgainstTheLedger`); shipped conformance **rc=0,
  125/125**; mutation **123/123**.

## BOUNDED FAIL — contention evidence does not pin the release

- `evidence/lock-budget/contention-candidate-capacity-15s.txt` and
  `contention-candidate-overload-4s.txt` both begin `== 8ec5c12e4199f207 …`, i.e.
  they were produced by binary **`8ec5c12e…`**, which is **not** the released
  `b70665f5…` (nor any persisted release in `agent-loop-releases/`). The baseline
  file correctly uses `2656bb97` (f86daf9).
- So the headline contention numbers (MAX_HOLD **10.51 s**, settlements **0/1/17 s**
  capacity, **17/18 s** overload, refusals) are **not** evidenced on the shipped
  binary. The **per-hold bound itself is** independently confirmed on the release
  via `hold-scaling` (10.5 s), but the settlement-lateness/capacity claims are not.
- **Smallest correction:** re-run `contention.sh` capacity and overload on the
  released `b70665f5`, persist the binary hash in each evidence file, and re-pin the
  claim; or repin the release to `8ec5c12e` if that is the intended binary. Do not
  accept the contention numbers as release evidence as-is.

## Arithmetic assessment (sound as stated)

- per-hold ≤ 10 s + 0.5 s WaitDelay + local SQLite/CPU; **measured 10.51 s**.
- detection: marker by D+1+8 = **D+9 s** (trusted/durable/action-correlated — a
  detection hint, never ownership/ack).
- settlement head-of-queue ≤ D+9+10.5+10.5 ≈ **D+30 s**; measured ≤18 s (on
  `8ec5c12e`; see FAIL).
- capacity: ≥1 due settlement per hold; backlog k ≈ k holds; beyond → **SATURATED**;
  new dispatches under overload get visible `E_LEDGER_BUSY`. No finite latency for
  unbounded arrivals — honestly stated, not claimed as a bound.
- ack within 60 s of detection is human and **live-only**.

## Residuals (honest, non-blocking)

- Local SQLite/file ops inside a hold are **not budgeted** (only subprocesses); the
  10.51 s max includes them, so the per-hold bound is empirical, not hard.
- A unit started with ≥6 s left can still hit `ErrBudget` on later I/O → package
  goes **blocked** (owned, visible), not lost.
- The yield path is **unit-tested only**; real-process runs never needed a yield.
- Crash/reopen under contention not rerun this round (marker durability from the
  prior round).
- Checker own-supervision, continuous UTC, unlocked `status`/`expose`, L4a/L4b and
  live ack latency: unchanged / live-only.

No source edits by corvid; no new allocation/prep/live. Returned to Tern.

---

## Lock-budget intake classification (same pass, no reset)

Claim `c3b75e28…`; 37 paths + binary `b70665f5` verified. Requirements addressed as
**supported / blocker**, not blanket PASS.

### 1. All allocation requirements — subprocess caps vs the rest

- **Supported:** the budgeted Runner caps **subprocesses** per hold; measured
  per-hold ≤10.51 s (release binary via `hold-scaling`).
- **Blocker/gap:** **SQLite, file and CPU work inside a hold are not budgeted.**
  The per-hold bound is therefore **empirical** (max 10.51 s), resting on a bounded
  host assumption (local SQLite/CPU), not a hard cap. **Unbounded algorithmic
  backlog** (a deep due queue) has **no finite latency** — `SATURATED` is reported,
  not bounded.

### 2. Stress already-accepted due actions; fairness; SATURATED ≠ ack

- The contention runs stressed **new dispatches** (refused) plus 3 accepted
  deadlines (T1/T2/T3). **Deeper accepted-backlog fairness and recovery are not
  stress-tested**; "≥1 settlement/hold, oldest-first" is a construction claim, not
  evidenced at depth.
- **`SATURATED` sent to duty is NOT an authenticated ownership acknowledgement** —
  it is a report; the ack remains separate and human. Preserve that distinction.

### 3. Actual yield/resume, crash/reopen, slow/failed transport

- **Slow transport: supported** (`hold-scaling` slow=20 s → hold 10.5 s).
  **Failed transport (`ErrBudget`): unit-tested.**
- **Blocker:** **actual yield/resume is not exercised in real process runs** (the
  author states real runs never yielded) — the composition yield→reacquire→
  `ProcessDue` is unit-only.
- **Blocker:** **crash/reopen under contention was not rerun** this round; marker
  durability is inherited, not composed with the budget path.

### 4. Fairness, every holder, refused I/O, heartbeat truth, detection/settlement/ack

- Lock is `flock` `LOCK_NB` + 50 ms polling — **not FIFO-fair**; sustained
  contention can starve a waiter, mitigated only by bounded holds + `E_LEDGER_BUSY`.
- Every holder runs `ProcessDue` on **acquire and before release** (source-verified).
- Unsent I/O → `E_BUDGET_EXHAUSTED`, **no receipt for an unsent wake** (owned,
  visible); a later refused I/O → package **blocked** (owned, visible).
- Heartbeat: the `yielded` pass record is set only when `Tick` actually yielded
  (source-verified); **truthfulness on the real path is unit-only** (never yielded).
- **Detection (marker, D+9) vs settlement (head-of-queue ≤D+30, measured ≤18) vs
  ack (live, human, 60 s) kept distinct.**

### 5. Supported vs blockers (explicit); no live readiness from unit evidence

- **Supported:** per-hold subprocess budget; marker detection hint; `SATURATED`
  reporting; conformance 125/125 and retained regressions.
- **Blockers:** (a) contention candidate evidence off-binary (`8ec5c12e` vs
  `b70665f5`); (b) SQLite/file/CPU unbudgeted → empirical bound; (c) yield/resume
  not exercised in real runs; (d) crash/reopen under contention not rerun;
  (e) deep-backlog fairness/recovery unproven; (f) unbounded backlog has no finite
  latency.
- **No live readiness from unit evidence**; live ack remains for the live witness.

Consolidated verdict unchanged: **bounded FAIL** on blockers (a)–(f). No author
edits during review; no new allocation/prep/live.

---

## Evidence-selection correction (Tern, same 19:50:58Z bound, no reset)

`contention-evidence-selection-correction.json` (19:35:04Z): the **release** files
`contention-release-capacity-15s.txt` (`5f650d12…`) and
`contention-release-overload-4s.txt` (`722d7713…`) match the original claim and
identify **`b70665f5`** (verified headers above by Cairn). Capacity settles 17/1/7
over 27 holds; overload T1 settles 17 over 14 holds.

**Correction:** the off-binary objection is **withdrawn for these release files**
— the contention numbers ARE evidenced on the shipped binary. The earlier
`contention-candidate-*.txt` files (binary `8ec5c12e`) are not release evidence,
and the README still mislabels the older numbers. Blocker (a) above is therefore
corrected to a **README-labelling defect**, not a missing-evidence defect.
Blockers (b)–(f) and all other intake assessments stand independently; no blanket
PASS. Original verdict otherwise preserved; no source/claim/README edits, no new
pass. Returned to Tern.
