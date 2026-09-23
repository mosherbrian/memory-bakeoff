# P11-live-1 — independent live review (corvid)

- **Action:** `P11-live-1` live review (20 m), steered; run host-start `16:09:49Z`,
  bound `17:23:36Z`. No reset, no retry, no edits.
- **Verdict: NOT READY.** No live qualification PASS and no cutover. The run is a
  preserved failure with a mix of real product defects, driver/measurement
  invalidities, and contamination. L6 acknowledgement remains predeclared NOT READY.

## Raw preservation

- `live-end-manifest.json`: **29/29 files hash-match** (driver stdout/stderr/log,
  results, snapshots, owned explicit-UTC journal, archive of `fxp11live1.db`,
  liveness JSON, damaged quarantine, units/tasks/artifacts).
- `results.tsv` preserved verbatim: **6 PASS / 8 FAIL / 10 INCOMPLETE**.
- Driver's own end: `cleanup done` `16:45:25.269Z`; observer `host-end.txt`
  `16:45:56Z` (31 s later). Both precede the `17:23:36Z` bound; kept distinct, not
  conflated.

## Classification of every gate

**Product PASS (6) — non-journal paths:** `L1`, `L2`, `L3b`, `L7b`, `L7c`,
`L5-stray`. (L1 passed despite the restart abort; L2 = crash restart, outbox held,
no resend; L3b hung→duty woken; L7b future pass→unknown alarm; L5-stray exit 64,
marker kept, no scheduled restart.)

**Product FAIL (real defects) — P12 scope:**

1. **Idle-worker `/cancel` → `nothing running`, aborting settlement/escalation.**
   `L2-settle FAIL` (`step worker`); `L6 FAIL` (`cancel/director wakes 4->5 2->2`).
   Send excerpts: `/cancel` `16:17:32Z` and `16:38:30Z` both `nothing running`; L6
   director never woken. Confirms `live-timeout-idle-finding.json`.
2. **Recurring stop-timeout → SIGABRT on SIGTERM/restart and watchdog.** Owned UTC
   journal: `State 'stop-sigterm' timed out. Aborting` + `SIGABRT` at `16:11:25`,
   `16:23:07`, `16:24:13`, `16:27:18`, `16:42:14`, and `Watchdog timeout (limit
   1min 30s)!` at `16:22:39`. The frozen Go loop does not exit within
   `TimeoutStopSec`, so every restart is an abort. Not a declared gate, but a real
   product robustness defect that also confounds L3a/L4a.

**Driver / measurement — invalid evidence (reconciled, not product):**

- `L5-rest FAIL` and `L5-stopped FAIL`: `0 checks` from zoneless `--since` read as
  local. Owned explicit-UTC journal in those windows: **4 `rest`** and **5
  `stopped`** verdicts → the checks existed.
- `L7a FAIL` (`copy/wakes 3->4`): the +1 wake is correct; the failing condition is
  `checks_since` (zoneless). Owned window has **3 ok + 2 unknown** verdicts; the
  malformed quarantine is archived.
- `L3a FAIL` (`restart without a watchdog line`): the watchdog restart **did**
  occur (`new_invocation` reached after 95 s); the owned journal has `Watchdog
  timeout` at `16:22:39`. Grep/window artifact.
- `wait:first pass INCOMPLETE`: idle loop returns `rest`, not `ok` — deterministic
  setup-state mismatch (`LIVE-SETUP-STATE`).
- `wait:L7c new invocation INCOMPLETE` (20 s) but `L7c PASS`; `wait:L5 run exited
  INCOMPLETE` (60 s) but `L5-stray PASS`; `L6-timing INCOMPLETE` (zoneless
  `callback_start`, missing interrupt/director).
- Cascades: `wait:L2 settled`, `wait:L2 rest`, `wait:L4a settled`,
  `wait:L7b recovered`, `wait:L4b restart-loop`.

**Contaminated / unproven:**

- `L4a FAIL` (`no start-limit/restart-loop`): snapshots show `Result=success` — the
  injected failing start never produced `start-limit-hit`; injection effectiveness
  and unit properties must be examined for P12.
- `L4b FAIL` (`director not woken`): the archived liveness JSON shows the `16:43:05Z`
  crashed incident with `duty_wake: failed` and `director_wakes: sent` + an ack at
  `16:43:12Z` — the director *was* woken; the gate's `state_is restart-loop`
  precondition was not met (state `crashed`). Driver state-classification, not a
  clean product failure.
- `wait:L7b recovered` (`state_is rest`) never reached because the L2 package stayed
  open — contamination from defect 1.

## UTC reconciliation (separate; never rewrites a driver result)

The owned `journal-owned-explicit-utc.txt` is archived with explicit UTC onset
(`16:09:49Z`) and end, and reconciles the journal-window gates above
(L5-rest 4×rest, L5-stopped 5×stopped, L7a 3×ok/2×unknown, L3a watchdog at
`16:22:39Z`). This is **labelled reconciliation only**: the driver's `results.tsv`
FAIL/INCOMPLETE rows are preserved unchanged and the driver exit 1 is not
suppressed. No retrodriver PASS.

## Finite blocker list (for P12 scope)

1. **Timeout progression must not depend on cancelling an already-idle worker** —
   classify `nothing-running` vs failed/ambiguous transport; do not swallow errors;
   preserve durable at-most-once settlement, escalate actual cancellation failure,
   deliver the director action, and record an authenticated timeout ack.
2. **Graceful stop / restart**: the run must terminate within `TimeoutStopSec` (no
   `stop-sigterm`→SIGABRT) and handle watchdog abort paths; otherwise every restart
   is an abort and L3a/L4a cannot be assessed cleanly.
3. **Journal/time basis**: all driver `--since`/`journalctl` windows must be
   explicit UTC or epoch (or use absolute onsets), so quiet/restart/stopped gates
   measure real checks.
4. **Setup baseline**: first-pass wait must accept the actual idle `rest` state (or
   define the intended baseline) instead of a deterministic INCOMPLETE.
5. **L4a/L4b injection & state classification**: prove the failing-start injection
   reaches `start-limit-hit`, and classify crashed vs restart-loop correctly so the
   director-wake gate reflects the real escalation.
6. **L6 acknowledgement** remains NOT READY (no step-timeout ack path in the frozen
   Go); detection component was not established because settlement aborted.

## Reusable evidence for P12

`live-p11live1/{results.tsv,driver.log,snapshots.txt,journal-owned-explicit-utc.txt,
l6-timing.json,archive/fxp11live1.db.liveness.json,archive/*damaged*}`;
`timeout-idle-evidence/{L2-journal.txt,L6-journal.txt,send-excerpts.txt}`;
`live-timeout-idle-finding.json`; `live-end-manifest.json` (29/29).

No retry/edits/cutover. **NOT READY** returned to Tern.
