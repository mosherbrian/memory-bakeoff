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
