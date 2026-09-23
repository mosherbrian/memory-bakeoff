# P11-live-driver-qualification — candidate review (independent)

- **Reviewer:** corvid-dsh; action `P11-review-1`, start `15:22:45Z`, deadline `15:47:45Z`.
- **Claim:** `completion-claim.json` (`P11-initial-1`, COMPLETE) on corrected contract
  `ca512b21…`; checklist `acceptance-checklist.md`.
- **Method:** independent offline reproduction. No source/live/cutover change.

## Verdict: PASS (bounded, with residuals)

The F1/F2/F3 corrections hold under independent execution. Old P10 failures are
reproduced, corrected real helpers/processes and the frozen Go sequence pass, one
unshared negative per family passes, and the Go source/binary are unchanged.

## Pins and integrity (all OK)

- Contract `package.md` = `ca512b21…`; frozen source `1341f04…` worktree clean;
  binary `c1c49a29…` unchanged.
- Claim's `plan_files_sha256` + `evidence_sha256` = **30/30 recomputed equal**
  (11 plans, 19 evidence). P10 driver `912b55b2…` confirmed as the old pin.
- Rename proof re-derived independently: applying the four P10→P11 substitutions to
  each P10 file yields 9 **byte-identical** rename-only files. `live-driver.sh` is
  the only substantive plan change (F1/F2/F3), pinned at `1f4bc4d4…`.

## Executable checks (I reran these)

- **F1** — `f1-helpers.sh` extracts the real `ts()`…`state_is()` from each driver:
  P11 = **29 PASS / 0 FAIL**; P10 = **10 PASS / 19 FAIL** (valid rest/ok/starting/
  unknown all broken: log line on stdout, empty verdict, false `state_is`). Confirms
  the old failure and the fix. DRY rows are forced DRY; failed wait returns 1 and
  writes `wait:<label> INCOMPLETE`; parse errors go to `driver.log`.
- **F2** — `f2-wallstop-witness.sh plans/live-driver.sh 10 25` (my run): after the
  wall fired during the blocked L1 wait — `LATE_EFFECTS=0 WALLSTOP_ROWS=1 CLEANUPS=1
  DRIVER_ALIVE=0`, scope inactive, 0 children, second cleanup 0 effects. P10 witness
  with the same harness: `DRIVER_ALIVE=1 CLEANUPS=0 WALLSTOP_ROWS=` (old defect).
  `f2-arm-failure.sh`: `SETUP FAIL wall-stop not armed: no effect started`, no root,
  no effects. Identity is cgroup membership (`/proc/$$/cgroup`), no PID file.
- **F3** — `f3-go-settlement.sh` on the frozen binary: **15 PASS / 0 FAIL** — open
  L2 is `ok` (not rest, the P10 failure); deadline callback → `interrupted`,
  `timed-out`, one /cancel, one director wake, then `rest`; replay `already-handled`
  with 0 effects; `decide` refused `E_PHASE_MISMATCH`; L6 sees no L2 effect.
- **Unshared negatives (mine, `/tmp`, not shared with author) — 13 PASS / 0 FAIL:**
  F1 non-string / null / empty `state` → `PARSE-ERROR`; F2 cgroup identity present,
  no pidfile, cleanup stops the owned scope first; F3 an **early** deadline callback
  returns `no-op-early` and leaves L2 in `worker`/not-rest (no premature settle), and
  two extra replays stay `already-handled`.

## Required outcomes / adverse paths

- Every results row inspected: P11 DRY run writes 14 `DRY` rows (no false PASS);
  a failed wait writes INCOMPLETE and the driver exits 1 on any FAIL/INCOMPLETE row.
- Construction `DRY=1` is treated as construction only, never behavioral evidence.
- P10 matrix retained (L1–L7) with the added `L2-settle` F3 case; original L2
  restart/no-resend assertion preserved.

## Residuals (disclosed; carry to live signature)

1. Frozen Go deadline timers set no `AccuracySec`; worst-case 60 s late. L6's 2 min
   deadline inside a 185 s quiet window leaves ~5 s margin. **Live-run risk; signer
   must accept or widen.**
2. `plans/README.md` changed beyond the four renames and is **not covered** by
   `rename.diff` or `rename-only-check.txt` (descriptive header only; no behavior).
   Minor completeness gap in the diff listing.
3. Cleanup's `agent-deck session stop/remove` pass no profile (inherited P10,
   outside F1–F3).
4. Witnesses use stub transport / stub `agent-loop`; real systemd only for the
   driver's own scope and wall timer. Real units are exercised only in the signed
   live run. The P10 F2 reproduction touched real `systemctl`/`agent-deck` on
   nonexistent fx units/seats (all "not found").
5. `EV_DIR` is passed to the wall only when set (offline rehearsal hook).

## Effect

**PASS** on F1/F2/F3 for `P11-initial-1`; candidate may proceed to Tern's live
signature. Residual 1 (L6 timer margin) should be acknowledged before the live run.
No source/live/cutover change made by corvid. Returned to Tern.
