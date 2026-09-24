# P12-live-2 — independent live review (corvid)

- **Action:** `P12-livereview-2`, start `03:41:00Z`, deadline `04:06:00Z`.
- **Inputs:** `live-review-receipt-2.json`, `live-2-review-manifest.json`
  (**41/41** hashes match), `live-p12live2/`, signed `live-signature-2.json`.
- **Verdict: PASS** — raw **17 PASS / 0 FAIL / 0 INCOMPLETE** and every case is
  independently consistent with the signed plan, the new helpers and the restart
  ruling. (Raw PASS is not itself acceptance; the classification below is.)

## Signed plan / pins

- `live-signature-2.json`: `P12-live-2`, binary `97a57db1…`, `latest_start`
  `02:40:00Z`, `absolute_end` `03:52:00Z`. Host run `02:37:15Z` → `03:40:00Z`, all
  before `absolute_end`; driver `cleanup_done` `03:03:48.355Z`.
- Product `97a57db1…` (frozen `8ad12b86`); helpers bound in the signed set
  (`live-checks.sh 19085856…`, `live-driver.sh f6afd9e0…`); archive binary
  `97a57db1…` matches.

## Independent case verification (all 17)

- **L1** closed; one dispatch per seat across restart.
- **L5-rest** 6 checks all `rest`; **L5-stopped** 9 checks all `stopped` (UTC
  windows hold).
- **L2** restarted by systemd, outbox held, no resend; **L2-settle** timed-out by
  its deadline, one /cancel, one director wake, no open work.
- **L3a** `watchdog timeout and result watchdog inside the onset..restart window`
  (onset `02:44:07`, restart after 96 s, pass after 20 s) — the SIGPIPE grep defect
  is fixed.
- **L7c** `starting` quiet inside the window, **`rest` after the new run's pass** —
  the idle-`rest` baseline and fresh-pass `healthy_after` hold.
- **L3b** hung after 121 s (bound 180), duty woken.
- **L4a** restart-loop causal evidence proven (`5 scheduled restarts, 6 failed
  starts, then the start limit`, burst 5) → duty ack (owner/next/deadline) →
  recovered on a fresh pass; the product alarm subtype reads `crashed`, accepted
  per the ruling with the proven restart-loop injection.
- **L7-checker** handler told duty 41 s after the hold; recovered 16 s after
  release (independent owner/recovery).
- **L7a** bytes preserved, duty woken once over ≥3 checks; **L7b** future pass →
  unknown alarm.
- **L5-stray** exit 64, stray start rc 1 recorded, marker kept, no scheduled
  restart.
- **L6-timing** detection 0.0 s, **ack 4.0 s after detection (≤60)**, 4.0 s after
  deadline (≤90); ack by the director fixture at `02:56:36Z`.
- **L6** `interrupted once while run was stopped: one /cancel, one director wake;
  replay ran (rc 0): already-handled, no new /cancel or director wake`. The replay
  used the **exact captured production argv**
  (`timer-callback --config …/fxp12live2.json --qid L6-p12live2 --action
  L6-p12live2-w1 --execution ex-L6-p12live2-w1`) under `AGENTDECK_PROFILE=campaign4`
  and returned `already-handled` — the previously **unexecuted** replay is now
  genuinely exercised (at-most-once).
- **L6b** duty 83 s after settlement (60..95), director 143 s (120..155),
  `ack None`.
- **L4b** duty wake failed → director woken in the same check → director ack
  recorded (restart-loop evidence proven at `03:03:08`).

## Cleanup / side effects

- `4 exact IDs absent, no active owned units/scope`; `units-after-director.txt`
  shows the driver scope, wall timer and run unit **inactive**; `04:30` fallback
  retired. (The failed `p12test-cadence-1615323.service` is a known earlier-round
  leftover, not this run's.)

## Deviations / residuals

- **Handoff deviation (preserved separately):** completion was not recorded/routed
  until sponsor-side notification at `03:39`; the director reconciled at `03:40`.
  This is a **manual controller failure**, not a candidate result; keep separate.
- Residuals unchanged: L4a/L4b subtype depends on the frozen product (`crashed` on
  this host's systemd; ruling permits `crashed` or `restart-loop` with proven
  restart-loop evidence); 143 s non-priority contention and empirical local commit
  remain declared live-test limits; host timer/manager outage is the stated
  boundary. L6b duty/director latencies (83/143 s) sit inside the declared
  60..95/120..155 bounds.

No edits/retry/live/cutover by corvid. **PASS** returned to Tern and cairn
immediately; the held 45 m cutover + 10 m post-review remain Tern's signed
decision, not automatic adoption.
