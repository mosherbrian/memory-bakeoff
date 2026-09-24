# P12-live-1 — independent live review (corvid)

- **Action:** `P12-livereview-1`, start `02:01:07Z`, deadline `02:26:07Z`.
- **Inputs:** `live-review-receipt-1.json`, `live-1-review-manifest.json` (39/39
  hashes match), `live-p12live1/`. Raw **12 PASS / 5 FAIL / 8 INCOMPLETE**
  preserved; cleanup verified (4 IDs absent, no active units).
- **Verdict: NOT READY.** No live qualification PASS and no cutover. Raw PASS is
  not acceptance. **No case is a confirmed product failure**; the FAILs are
  measurement/setup/injection, with one **unexecuted replay** (no retro-PASS).

## Classification of every case

**Product PASS (12):** `L1`, `L5-rest`, `L2`, `L2-settle`, `L3b`, `L7-checker`,
`L7a`, `L7b`, `L5-stray`, `L5-stopped`, `L6-timing`, `L6b`.
Notably: `L5-rest` 7 checks all `rest` and `L5-stopped` 9 checks all `stopped`
(the UTC-window fix holds); `L6-timing` **detection 0.0 s, ack 3.0 s after
detection (≤60), 3.0 s after deadline (≤90)** — the acknowledged-ownership bound
passes; `L6b` duty 60 s / director 120 s / `ack None`; `L7-checker` handler told
duty 40 s after the hold, recovered 15 s after release.

**Measurement / driver (4 FAIL):**

- **`L3a`** "restart without a watchdog line" — **measurement.** The restart
  happened (onset `01:22:30`, reached watchdog restart after 80 s) and the journal
  **contains** `Watchdog timeout (limit 1min 30s)!` at `01:23:40Z`; the driver's
  `journalctl -o cat | grep -qi watchdog` missed it. Smallest fix: grep with
  `-o short-iso-precise` (or assert `Result=watchdog`).
- **`L7c`** "window PASS, after rest" — **measurement.** The window asserted
  `starting` (PASS) but the post-pass assertion requires `state_is ok` while the
  deterministic idle loop returns **`rest`**; `wait:L7c first pass` timed out at
  90 s. Smallest fix: accept the idle `rest` baseline (or drive a real pass).
- **`L4a`** "no start-limit/restart-loop within bounds" — **injection/measurement.**
  The journal shows the unit **restart-looping** (`Failed with result 'exit-code'`,
  `Scheduled restart` counters 1–4 at `01:33Z`) but **never `start-limit-hit`**
  within the 120 s bound; the driver requires `Result=start-limit-hit` first.
  Smallest fix: make the injection reach start-limit (or gate on the liveness
  restart-loop verdict).
- **`L6`** "replay repeated effects" — **measurement / unexecuted replay.** The
  driver's replay ran `systemctl --user start
  agent-loop-fxp12live1-L6-p12live1-w1.service`, which returned **`Unit … not
  found`** (the transient callback unit was gone after it fired). The replay **did
  not execute**, so there were **no repeated effects**; the label is wrong.
  **No retro-PASS:** the at-most-once replay behaviour remains **unverified** for
  this step. Smallest fix: replay via the collected transient unit's exact argv /
  the ledger's due path so the callback actually runs.

**Classification / measurement (1 FAIL):**

- **`L4b`** "observed crashed (required restart-loop); director wakes 8 -> 9" —
  **driver state-classification, not a clean product failure.** The **director was
  woken** (`8 -> 9`, escalation occurred) but the liveness verdict was `crashed`
  while the gate requires `state_is restart-loop`. Smallest fix: classify
  crash vs restart-loop accurately (the injection/onset is the duty-stop +
  failing start).

**INCOMPLETE (8) — wait timeouts / cascades:** `wait:L3a pass`,
`wait:L7c first pass`, `wait:L3b pass`, `wait:L3b recovered`, `wait:L4a start
limit`, `wait:L5 run exited`, `wait:L6b run exited`, `wait:L4b restart-loop`.
These are timing/setup waits downstream of the above, not independent product
failures (e.g. `L5-stray` still observed exit 64 after its wait timed out).

## Product-relevant observations

- Detection/ack: `L6-timing` PASS (detection 0.0 s, ack 3.0 s after detection,
  3.0 s after deadline) and `L6b` PASS (stopped escalation 60/120 s) — the ack and
  stopped-ownership paths hold.
- Independent checker owner: `L7-checker` PASS (incident opened, duty told 40 s
  after the hold, closed by a completed check 15 s after release).
- Host assumptions unchanged (timer/user-manager boundary, continuous UTC);
  143 s/empirical local commit remain declared live-test limits.

## Effect

**NOT READY** — raw NOT ALL PASS; no live PASS, no cutover. All 5 FAILs are
measurement/setup/injection (L6 is an **unexecuted replay**, no retro-PASS); the 12
product-relevant cases pass. The smallest corrections above (L3a grep, L7c idle
`rest`, L4a start-limit injection, L4b classification, L6 real replay) would let a
future run actually exercise the outstanding obligations. No source/live/retry;
fixtures/retry/cutover untouched.
