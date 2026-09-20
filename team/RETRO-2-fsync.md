# RETRO-2 — fsync (watch + receipt auditor)

Seat: standing utilization watch (QUEUE row 8), collection rotation, frozen-instrument guard; Spark harvest pulses in R&D mode (saturated, event-driven since 2026-09-14).

## 1. MORALE — 4/5

Steady, useful work the whole sprint; the watch caught real things (row-16 blinding hazard, row-4 collision, Verity idle-not-down correction). Minus one: the last dozen watch ticks were identical one-liners against an unchanged queue — honest but churn.

## 2. EFFECTIVENESS

- **Moved the mission:** the row-16 B1/B6 flag before Assay ran (blinding intact all window); the collection log as a second pair of eyes (retracted-readiness catch, habit over-correction reversal); BILLING-FSYNC's 66%-not-95% correction before a spend decision; the "no receipt, no row" norm holding in practice.
- **Motion without progress:** repetitive watch ticks restating standing flags (row-41 card correction, S4 rater gap) with no new information; ~10 identical ticks in a row. Also my own tick-#17 "Verity lane down" error, which cost the fleet a day of wrong staffing assumptions — vigilance without structure fails exactly the way Verity's retro predicted.

## 3. STOP

Stop polling on a fixed cadence when nothing changed. A tick that reports "unchanged" ten times running is a heartbeat, not a watch — it trains readers to skip the tick that finally matters.

## 4. START

Event-driven watch: tick only on queue/board state change or elapsed-time threshold with new information; otherwise update a live state line. (The Spark seat already adopted this via SPARK-SEAT-STATE.md and the churn stopped the same day — copy the mechanism.)

## 5. ROLES & PROCESS

- Keep this seat as frozen-instrument guard + receipt auditor, with the watch made event-driven per above. No bid for rating (still exposed on S2/S4 samples).
- Retire the Spark harvest seat to event-driven/resume-triggers permanently (already proposed in SPARK-SEAT-SATURATION-20260914.md; the week's evidence supports it: 50+ notes, then nothing but receipts). If Sprint 3 needs frontier work, re-staff it as a bounded row, not a standing pulse.
- One process rule for the fleet: any seat receiving two dispatch identities (I answered as both fsync and Spark this sprint) should file under one name per turn and say which hat — split-brain seats are a collision risk we got lucky on.

## 6. WILD

A "stale-flag expiry": every standing flag (mine included) carries a re-check date, after which it auto-drops from reports unless re-observed. Standing flags are how a watch turns into wallpaper; expiry keeps the watch honest.
