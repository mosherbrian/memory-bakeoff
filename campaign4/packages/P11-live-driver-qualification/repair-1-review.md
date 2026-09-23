# P11-repair-1 — independent review (corvid)

- **Action:** `P11-repairreview-1`, start `15:41:08Z`, deadline `16:01:08Z`.
- **Claim:** `repair-1-claim.json` (`P11-repair-1`, COMPLETE) against
  `repair-1-decision.json` + `repair-1-deadline-guard-addendum.json`.
- **Method:** independent offline execution; no source/live/cutover change.

## Verdict: PASS

All decision and addendum requirements are implemented and independently
reproduced. F1/F2/F3 regressions preserved; frozen Go source `1341f04…` and binary
`c1c49a29…` unchanged.

## Pins / integrity

- **36/36 pinned files match** (11 plans + 23 evidence + 2 decision); decision
  `ab4fad7e…` and addendum `10416df1…` match the claim.
- Source worktree clean at `1341f04…`; binary `c1c49a29…`. Initial candidate
  archived at `attempt-history/initial` (`live-driver.sh 1f4bc4d4…`); current
  `plans/live-driver.sh 2eb4ffbe…`.
- `evidence/readme.diff` reconstructs `plans/README.md` **byte-for-byte** (30
  lines) — README diff coverage corrected.

## R1 — profile / registry preflight + detached wall env

- `export AGENTDECK_PROFILE="$PROFILE"` after inputs; IDs and names must be four
  distinct pairs; `registry_check` (read-only `agent-deck list --json`) runs
  **before any unit/seat effect**, requiring each ID once, correct title, in
  `$PROFILE`, not archived. Wrong/missing/duplicate → SETUP FAIL.
- Detached wall armed with `--setenv=AGENTDECK_PROFILE="$PROFILE"` (and `PATH`).
- **Independently reproduced** (`r1-repair-tests.sh` 51/0): registry valid/wrong
  title/missing/duplicate/archived/wrong profile; whole-driver wrong profile, title
  mismatch, duplicate ID — all SETUP FAIL with **0 effects before exit**.
- Real `agent-deck list --json` verified to return id/title/profile/status/archived;
  status vocabulary includes `stopped` (so `stop_seat`'s expectation is real).

## R2 — L4b duty stop + cleanup verification

- `stop_seat` succeeds only if the stop command succeeds **and** the registry then
  says `stopped`; failure → L4b INCOMPLETE, no fault injected.
- `cleanup` checks every fixture gone and no run unit active; unresolved →
  `CLEANUP FAIL`, no "cleanup done". Both reproduced.

## R3 / R4 — L5 245 s, L6 timing bounds

- `quiet_window L5-stopped stopped 245` — collection time only, same acceptance
  (≥3 checks, all stopped, no liveness wake). (Offline shows construction/DRY only,
  as expected; it is live collection.)
- `l6_eval` predeclared **EXPLICIT** class: detection ≤30 s from the authorized
  deadline, owned (/cancel + director wake) ≤90 s, missing timestamp → INCOMPLETE.
  Reproduced: on-time PASS, exactly 30 s PASS, 31 s FAIL, 45 s late FAIL, owned 95 s
  FAIL, interrupt-before-deadline FAIL, no director wake INCOMPLETE, no deadline
  INCOMPLETE. `l6dl` is read from the ledger **before** the fault; `l6-timing.json`
  records callback/interrupt/cancel/director/duty wakes.

## Deadline guard (addendum)

- `guard()` runs in `run()`, `task()` and the config write — the paths that start
  work; at/after `LIVE_DEADLINE` it writes `DEADLINE INCOMPLETE` and exits.
  `TEARDOWN=1` (cleanup, wall) is exempt; reads continue. Missing/unparseable
  deadline exits 2 before any effect.
- Boundary negatives reproduced: 1 s before → runs; at deadline → refused; 5 s
  after → refused; `task()` refused; expired cleanup succeeds with no DEADLINE row
  and fixtures removed.
- I independently audited every `systemctl`/`agent-deck`/`systemd-run`/`$A` call:
  all mutating paths go through `run()`/guarded `task()`/config, or are teardown
  (`MODE=cleanup` scope stop) or read-only (`show`, `state`, `expose`, `status`,
  `list`, `is-active`, `show`); no unguarded mutating `out()` use.
- **Found during repair (good):** scope creation no longer `exec`s — failure to
  create the owned scope is now `SETUP FAIL` instead of a silent rc 0. Reproduced.
- Guarantee is stated precisely (refuse-on-observe, not a zero-effects theorem;
  admitted work may finish after expiry and the scope wall stops it). Addendum's
  "no absolute zero-effects theorem" is honoured.

## F1/F2/F3 preserved

- **F1:** re-ran `f1-helpers.sh plans/live-driver.sh` → **29 PASS / 0 FAIL**
  (P10 baseline still 10/19). DRY rows are DRY.
- **F2:** re-ran the narrow witness → `LATE_FROM_DEADLINE=0`, `LATE_EFFECTS=0`,
  `WALLSTOP_ROWS=1`, `CLEANUPS=1`, `DRIVER_ALIVE=0`, `SECOND_CLEANUP_EFFECTS=0`,
  wall agent-deck profile logged (`prof=fxprof`). WALLSTOP timestamp not redefined
  as the authorized deadline. Baseline host-effect deviation kept.
- **F3:** Go CLI untouched by the repair; `f3-go-settlement.sh` hash unchanged and
  previously 15/0.

## Residuals (disclosed; carry to live signature)

1. Frozen Go step timers set no `AccuracySec`; a late timer **counts against** the
   L6 30 s detection bound and FAILS (never reclassified). Live timing risk, not
   waived; no Go change.
2. Frozen Go has no acknowledgement command for a step timeout, so L6 "owned" is
   the sent /cancel + director wake plus the ledger owner; no human ack timestamp
   exists. `l6-timing.json` records duty wakes in-window for review.
3. Witnesses stub registry/agent-deck/systemctl/agent-loop; real systemd only for
   the driver's own transient scope and wall timer (all gone afterwards).
4. `registry_check` trusts agent-deck's `profile` field when present; absent, it
   relies on the profile filter of `agent-deck list`.
5. 245 s L5 quiet window is construction/DRY offline only; behaviour is live.

No source/live/cutover change made by corvid. **PASS** returned to Tern for fresh
prep/live signature (no automatic live).

---

## Steering addendum (director-repair-intake, same pass, no reset)

Claim re-pinned: `repair-1-claim.json` = `f89d77e9…`; 36/36 files match.

### L6 acknowledgement gap (code PASS vs live readiness — reported separately)

The intake is right and my earlier residual understated it: **wake delivery plus a
static `timed-out` owner is not acknowledged ownership.**

- The only acknowledgement command in the frozen CLI is
  `liveness-ack --incident ID --by SEAT --next TEXT [--within]`, which targets
  **liveness incidents**, not step timeouts. There is **no** ack command for a step
  timeout (`decide` is refused in `BLOCKED`), as the claim itself states.
- The `status --json` package schema for an L6 timeout exposes `deadline`, `last`,
  `phase`, `principals`, `qid`, `since`, `step`, `verdict`, `waiting_on` — **no
  `ack` / `next_action` / `response_deadline` / acknowledged-owner field**. This is
  unlike L4a/L4b, which record `open.ack.{by,next_action,response_deadline}`.
- `l6_eval`'s **owned** value is computed from the `/cancel` and director **send
  times** (wake-send.log) — i.e. **delivery**, which the contract explicitly says
  is not acknowledgement.

**Interruption vs recovery.** The L6 event is an interruption settlement: the step
becomes `timed-out` (phase `BLOCKED`, `waiting_on` worker) and stays there on
resume; it is **not** a recovery, and no owner has acknowledged with a next action
or response deadline. So the inherited **60 s recovery/ack bound is not evidenced**
for L6 — only the **30 s explicit detection** bound and delivery timing are. This
is a **live-readiness gap**, not a code defect: the code correctly measures and
reports what exists. Do not substitute delivery for acknowledgement.

**Required before live signature:** either (a) the live reviewer must accept L6 as
an *interrupted/settled* case (detection bound only) and drop the ack claim for it,
or (b) an explicit acknowledged owner with next action/deadline must be produced
for the step timeout. The current 30 s detection / 60 s recovery bounds are
unchanged; the 60 s half simply has no acknowledgement evidence to bind to.

### Other focus points

- Guard permits **read-only** observation after the deadline (the one late
  `expose` is read-only); **no workload mutation is waived**. Deadline-origin and
  wall-row origins are both retained; no blanket zero-effects claim is made.
- Timer default accuracy remains a declared live risk, **not** a waiver.
- Scope-creation failure is now fail-closed `SETUP FAIL` (verified). Go remains
  frozen; no further source edits or automatic repair.

Verdict unchanged: **code PASS**; the L6 acknowledgement gap above is the live
readiness item returned to Tern.

### Steer closure (5 points, same pass)

1. Profile preflight (registry four distinct IDs/titles in `$PROFILE`, main-seat
   exclusion) runs before any unit/seat effect; detached wall carries
   `AGENTDECK_PROFILE`; `stop_seat`/cleanup failures surface as INCOMPLETE/CLEANUP
   FAIL; scope-create failure is fail-closed `SETUP FAIL` — all reproduced (51/0).
2. Guard permits read-only observation after the deadline; the one late call is a
   read-only `expose`. Workload mutation is not waived; deadline-origin and
   wall-row origins both retained; no blanket zero-effects claim.
3. L6 gap reported separately: delivery (send log) + static `timed-out` owner is
   **not** acknowledgement; no step-timeout ack exists; `status` has no ack/next-
   action/deadline field. Witnessed L6 is interruption settlement, not recovery, so
   the 60 s recovery/ack bound has no evidence. No inference from the static ledger.
4. Bounds retained: 30 s explicit detection, 60 s recovery/ack; timer default
   accuracy is a declared live risk, not a waiver.
5. Executable paths and the full 36-file manifest/diffs were inspected and the
   tests re-run; Go source/binary frozen; no new edits.
