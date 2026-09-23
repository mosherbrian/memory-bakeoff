# P12-stopped-ownership-1 — independent review (corvid)

- **Action:** `P12-stoppedreview-1` (allocated 25 m).
- **Claim:** `stopped-ownership-claim.json` (`6683fbbc…`) against
  `stopped-ownership-allocation.json` (`b2e120fe…`) and
  `stopped-ownership-receipt.json` (`d25aa386…`); candidate `53c97191c8c8`,
  binary `ec184be9`.
- **Verdict: bounded FAIL** — the stopped-mode escalation works and is reproduced,
  but the **concurrency audit finds an unguarded timeout-record writer**, and the
  unit-file timer cadence is **PENDING** (not measured on this candidate).

## Pins / integrity

- **31/31** claim hashes match (11 plans + 18 evidence + 2 decision); decision and
  receipt match. Source `53c97191…`; `git diff 669648c..53c9719` **empty** for
  `internal/core`, `internal/py`, `conformance/cases`; changed set bounded
  (liveness/loop/timeout + tests + `mutate_go.py`). Binary `ec184be9…` matches.

## PASS items (independently reproduced)

- **Stopped-mode escalation:** real CLI (`cli-stopped-noack.sh`) on `ec184be9`:
  verdict `stopped alarm=False` on every check, **no liveness incident**; duty
  escalation at **+60 s** (`17:55:45Z`), director at **+120 s** (`17:56:45Z`);
  reported as `timeout: …` actions separate from the verdict; `no_ack_duty` /
  `no_ack_director` recorded, no ack. The stop stays quiet.
- **L6b eval:** `l6b-eval-tests.txt` 7/7 (author); bounds duty 60..110 s, director
  120..170 s, no ack, verdict still `stopped`, then start — consistent with a 45 s
  cadence.
- **Retained:** `go test ./...` all ok; shipped-binary conformance **rc=0, 125/125,
  1751 steps**; mutation **112/112**; `f1-helpers` 29/0 and `r1-repair-tests` 58/0
  (author, hashes verified).

## BOUNDED FAIL — concurrency audit finds an unguarded writer

`withTimeouts()` (flock `<db>.timeouts.lock` + freshly opened ledger) guards
**run's Tick**, the **liveness Check**, and **timeout-ack**. But the
**timer-callback settlement path is outside the lock**:

- `TimerCallback` (`loop.go:991`) → `host.TimerCallback(...)` → the callback Loop
  calls `MarkTimedOut` (`timeout.go:83`) and `SettleTimeoutFailure`
  (`timeout.go:171`), both of which write the package/timeout record via
  `l.save(p)`/`setStep` on that Loop's own (not freshly-locked) view.
- `save` is a read-modify-write (`l.D.KVPut` of the whole `loop-pkg:<qid>`), so a
  callback racing the checker (or run) can **overwrite a fresh escalation/ack with
  its stale in-memory `p`** — the exact failure the lock was added to prevent.
- The claim's concurrency statement covers only run/liveness/ack, and
  `TestRunAndCheckerNeverDoubleEscalateOrLoseAnAck` tests only Tick-vs-Check. There
  is **no callback-vs-checker race negative**, and the intake explicitly required
  auditing "ALL writers … including Tick/SettleTimeoutFailure/MarkTimedOut/ack/
  checker, not only helper users."

**Smallest correction:** route `MarkTimedOut` / `SettleTimeoutFailure` (and the
early-`RearmEarly` write) through `withTimeouts`, and add a callback-vs-checker
race negative (settlement and escalation at the same instant → one of each, no
lost ack).

## PENDING — unit-file 45 s timer measurement on this candidate

The checker cadence is the **unit-file** timer `agent-loop-liveness@.timer`
(`OnActiveSec=45s`, `OnUnitActiveSec=45s`, `AccuracySec=1s`), not a transient
`--on-active` timer. Measured from the preserved P11 real run
(`journal-owned-explicit-utc.txt`): checks ~**45.5 s** apart across the run
including its daemon-reloads, consistent with the claim's bound
(duty ≤60+45+check ≈105–110 s; director ≤120+45+check ≈165–170 s). However, a
**controlled reload-storm measurement on `ec184be9` was not performed** — labelled
**PENDING**, not asserted (the claim's own residual concedes the transient analogy
does not prove this timer).

## Qualification limitation (reported, not dismissed)

The claim excludes the checker's **own supervision**: if both `run` and the
liveness timer are down, nothing escalates. That is a real charter supervisor-
liveness limitation and must be carried into the live signature explicitly, not
silently waived. Clock rollback (continuous-UTC assumption) and L4a/L4b/live
latency remain as before.

No source edits by corvid; no prep/live/cutover. Returned to Tern.
