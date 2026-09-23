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

---

## Steering addendum (director-candidate-intake, same 25m pass, no reset)

Claim re-pinned: `completion-claim.json` = `24d3bc6c…`; 30/30 bound files match.
Additional independent checks below. **Verdict on F1/F2/F3 remains PASS**; two items
are recorded as **signature preconditions**, not waived.

### F2 measured from the authorized deadline (not only the wall row)

Re-ran the private scope/timer witness narrowly (stubs for all agent-deck/global
systemctl; real systemd only for the driver's own `p11live-driver-*.scope` and
`p11live-wallstop-*.timer`, which were removed after). Deadline `15:28:58Z`, wall
row `15:28:59.023Z` (AccuracySec=1s). **Effects after the deadline: 0; effects
after the wall row: 0.** Onset was not shifted: both origins agree. Scope inactive,
timer inactive, 0 descendants, second cleanup 0 effects. Baseline deviation
preserved (see below).

### L2 failed-settlement containment (offline, frozen binary)

Unresolved L2 = `ok` (not rest). With L2 left open, a later case (L6) settles
independently to `timed-out`, and liveness **stays `ok`** — unresolved L2 work is
not masked by later settlement; `rest` is reachable only after L2 resolves
(`rest`). 6/6 PASS. This is the containment the intake asked for: later stages do
not proceed to a false REST over a failed L2 settlement.

### Host-effect deviation (preserved, not repeated uncontained)

My earlier baseline reproduction of the P10 wall ran the pinned driver with the
host's real PATH: it issued a real `systemctl --user daemon-reload` and
`agent-deck stop/remove` lookups for nonexistent fx units/seats (all "not found").
No real unit/seat was affected; no leftover `p10live-*`/`p11live-*` units remain
(checked). Per the intake I did **not** repeat that baseline uncontained; the
corrected P11 witness was run only in the allowed narrow scope.

### Signature preconditions (unresolved; no speculative acceptance)

1. **Cleanup profile resolution.** `cleanup()` calls `agent-deck session stop/
   remove "$id"` with **no `-p`/`--profile`**, and the driver never exports
   `AGENTDECK_PROFILE`; it only writes `PROFILE` into the agent-loop JSON. agent-deck
   default is `default`; the live fixtures are `campaign4`. A missing/incorrect
   inherited profile makes stop/remove return "not found" (rc 2, logged, **not
   fatal**) and leaks the four seats. **Must be established before signature:**
   pin `AGENTDECK_PROFILE=campaign4` (or pass `-p "$PROFILE"`) and add a pre-live
   check that `agent-deck list` resolves the four fixture IDs; do not accept on the
   ambient environment alone.
2. **Real step-timer accuracy.** Frozen Go deadline timers set no `AccuracySec`
   (`internal/host/host.go:370`); systemd may fire up to ~60 s late. L6's 2 min
   deadline inside the 185 s quiet window leaves ~5 s margin. This is a **live
   timing risk, not waived and not assumed**; the signer must accept it explicitly
   or widen the window. No Go change is authorized.
3. `plans/README.md` changed beyond the four renames and is not listed in
   `rename.diff`/`rename-only-check.txt` (descriptive only; no behavior).

No source/live/cutover change made by corvid. Verdict unchanged: **PASS on
F1/F2/F3**, candidate may proceed to live signature only with preconditions 1–2
explicitly accepted.

### Steer closure (7 focus points, same pass)

1. F1/F2/F3 old-vs-corrected, non-DRY: F1 10/19 P10 vs 29/0 P11; F2 P10
   `DRIVER_ALIVE=1/CLEANUPS=0` vs P11 `LATE_EFFECTS=0/WALLSTOP=1/DRIVER_ALIVE=0`;
   F3 15/0. DRY rows are DRY, never PASS.
2. Host-effect deviation preserved (see above); leftover `p10live-*`/`p11live-*`
   units checked: none.
3. Narrow private scope/timer witness was safe (stubbed globals/seats, exact
   cleanup); not INCOMPLETE.
4. No-effects measured from **both** the authorized deadline and the wall row: 0/0.
5. Go frozen; `AccuracySec` gap recorded as a live timing risk, not waived.
6. L2: restart/no-resend retained (worker woken once across SIGKILL), one /cancel +
   one director wake reconciled at settle, unresolved L2 never counted as REST
   (6/6 containment).
7. Cleanup profile resolution recorded as an unresolved **signature precondition**
   (pin `AGENTDECK_PROFILE=campaign4`/`-p` + pre-live exact-ID resolve check).

### Deadline-origin evidence assessment (read-only)

Read both preserved witnesses under `deadline-origin-evidence/`; all **11/11 file
hashes** match `manifest.json`. Onset is measured against the true authorized
deadline, not shifted to the wall row.

- **C535** (deadline `15:20:55Z`): driver-scope commands after the deadline — **0**.
  Last driver command `expose` at `15:20:51.137Z`; wall row `15:20:56.033Z`;
  driver terminated by signal.
- **TzQQ** (deadline `15:12:29Z`): driver-scope commands after the deadline — **1**,
  a read-only `agent-loop … expose … --json` at `15:12:29.807Z` (+0.807 s), then the
  wall row at `15:12:30.025Z`; the driver was in `sleep 5` and killed by the wall
  ("driver terminated by signal (wall stop)"). The late command is a read-only poll,
  **not** a mutating dispatch/wake/decide/systemctl.

**Assessment — no general effect-exclusion, gate not weakened.** The driver has **no
internal deadline guard**: its wait loop keeps polling `expose` (and would keep
issuing whatever step it is in) until the external wall stops `$SCOPE.scope`. The
bound is enforced only by the wall scope kill, so a command can land in the
~`AccuracySec` (1 s) overshoot window — TzQQ proves this. C535's zero is a
timing artifact of the 5 s poll cadence, **not** a demonstrated invariant. The gate
is honest: `LATE_EFFECTS` counts driver-scope commands after the bound and did catch
TzQQ's one, so it is not silently weakened; but "zero effects after bound" must be
reported as observed-for-that-run, never as guaranteed. The same absence of
exclusion applies to mutating steps if a deadline lands inside one. For a general
guarantee the signer would need a driver-side deadline check or a wider wall margin;
no edit is made here. Preserved both, did not rerun the leaked baseline.
