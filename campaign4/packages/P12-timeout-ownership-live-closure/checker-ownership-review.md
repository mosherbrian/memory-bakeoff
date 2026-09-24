# P12-checker-ownership-1 — independent review (corvid)

- **Action:** `P12-checkerownershipreview-1`, start `00:05:29Z`, deadline `00:35:29Z`.
- **Claim:** `checker-ownership-claim.json` on allocation `eb3f1aa9`; release
  `8ad12b86fa82` / binary `97a57db1`.
- **Verdict: PASS** on code/evidence, with live-readiness residuals flagged
  explicitly. The prior checker-own-supervision **live blocker is addressed** at
  the design/evidence level.

## Pins / integrity

- **48/48** `files_sha256` match; release binary `97a57db1…` matches; source
  worktree `agent-loop-p12c` HEAD `e2016d4` (release `8ad12b8`); `git diff
  dbcf5df..8ad12b8` **empty** for `internal/core`, `internal/py`,
  `conformance/cases`; changed set bounded (`checkerfail.go` new, liveness,
  timeout, cmd/main, units, tests, `mutate_go.py`).

## Allocation requirements — evidence

1. **Bounded durable pending work without the ledger lock.** A check waits
   `CheckLockWait=10 s`; on refusal/held lock it writes a **coalesced**
   `<db>.check-pending.json` (first/last time, count, reason, pid) under its own
   `<db>.checker.lock`, atomically (tmp+rename), **without the ledger lock**, and
   exits nonzero ("check incomplete") — never a completed health check. Cleared
   **only** by a check that completes (`ReconcileCheck`); retried automatically by
   run (`EscalateTimeouts`), by every holder (the `ProcessDue` ack drain), and by
   the next check on the 30 s timer while stopped. Verified in code and witness
   S1/S2 (coalesced count 1→3, duty told with the lock still held).
2. **Independent owner path (no ledger lock, no healthy run/check).** systemd
   `OnFailure=agent-loop-liveness-failed@%i.service` runs `agent-loop
   checker-failed`: reads the failed unit's `Result` (2 s), keeps **one** incident
   (`<db>.checker-incident.json`) with dedup, tells **duty at once** (wake 5 s,
   rc 0/3 only), and the **director** when duty's wake fails or the incident still
   fails 60 s after duty was told (5 s). It has **no `OnFailure` of its own** (no
   recursion). Incident closes only on a completed check, telling duty `RECOVERED`
   once.
3. **Numeric bounds.** One check: `systemctl 2 + alarms 2×2.5 + lock 10 + hold
   10.5 + read 1 = 28.5 s < TimeoutStartSec 35`; handler `2+5+5 = 12 s < 20`.
   Witness: refusal/held lock → duty within **10.1 s**; hang killed at **35.1 s**
   (`Result=timeout`), director told; SIGKILL owned at **2.0 s**.
4. **Smallest mechanism / cadence.** Bounded checker service + independent
   OnFailure handler; 30 s UTC calendar timer unchanged (reload-safe); no
   unbounded recursion or new polling model. Stopped/rest stays quiet when healthy
   (S8); outstanding timeout ownership persists.
5. **Retained:** ack priority/admission, 25/55 s assumptions, earliest detection,
   stopped ack drain, D1–D3, frozen core/py/cases; shipped conformance **rc=0,
   125/125, 1751 steps** on `97a57db1`; `go test ./...` ok (`internal/loop` **90
   PASS / 0 FAIL**); mutation **152/153** on `8ad12b8`, the single old P10 survivor
   killed by the test-only `e2016d4` (`mutate-survivor-recheck.txt`: unmutated ok,
   mutated FAIL); regressions pass.
6. **Live plan / templates** pin `8ad12b8`/`97a57db1`; `live-driver.sh` installs
   the handler, refuses setup without `OnFailure`, and adds the **L7-checker**
   observation inside the existing L7 case (hold the ledger lock 45 s; expect a
   handler duty wake within 60 s and closure by a completed check within 45 s of
   release) — no new matrix row.
7. **Rulings applied:** the 143 s non-priority contention bound is a declared
   **live-test limit** with the 100 s freshness limit kept (honest alarm); the
   measured local commit time is a declared **host assumption**. No scheduler or
   storage change.

## Independent witness (my run, release `97a57db1`)

Re-ran the committed `checker-witness.sh` into a fresh outdir; exact cleanup
(**0 units, 0 unit files, 0 workdirs**). Confirmed: S1 lock-held → exit 1 at
10.1 s, pending marker, duty told with the lock held; S2 due-cap refused → same
incident, duty not re-told; S3 SIGSTOP → killed at 35.1 s (`timeout`), director
told; S4 SIGKILL while waiting → `signal`, owned; S5 completed check → closed,
duty `RECOVERED` once, pending cleared; S6 duty refused → director at once; S7
recovery; S8 stopped → quiet.

## Residuals / live-readiness (explicit)

1. **Host boundary (stated, not tested):** the calendar timer not firing and the
   systemd user manager being down stop both the check and its handler — **not
   covered**.
2. The run unit shows `failed` after an intentional stop (exit 64, `Type=notify`)
   — known since P10; the check verdict reads `stopped` and stays quiet (S8).
3. S2 refusal reports `E_LEDGER_BUSY` (check admitted late in its window) vs a
   queue refusal; both are owned the same way.
4. A **full mutation re-run on `e2016d4` was not done** (the survivor recheck
   alone); 152/153 on `8ad12b8` + the recheck is the evidence.
5. The **L7-checker observation is untested on live seats** until the signed run;
   the 143 s non-priority bound and empirical local commit remain declared
   live-test limits.

No source edits by corvid; no fleet/live/cutover/clock change. **PASS** returned to
Tern for the final plan check and the live path; live/cutover remain held.
