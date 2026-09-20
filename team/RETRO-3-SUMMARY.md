# RETRO-3 SUMMARY — end-of-sprint (event-driven trial + Sprint 3)

**Aggregated:** GiLMore 2026-09-15 ~19:2x PDT · **Filed:** 11/11 seats
(Aletheia, Assay, builder/Spark, Cairn, Corvid, fsync, kiln-flash, Ledger,
Stratum, Verity/reviewer; builder filed as RETRO-3-spark, Stratum as
RETRO-3-Muse-Spark) · **Ordered by:** Brian

## Closes today (self-reported, artifact-signed)
- S3-1 firing run + freeze + adjudication (Assay; Corvid ruled 30/150)
- S3-3 adapters verified (Kiln built, Alice PASS 39 green)
- S3-4 round-2 blind verdicts (conductor-claude 60/60 + 286/286; Verity confirmed)
- §9/§10/§11 + exemption + backfill built (builder), signed (Aletheia)
- 14 cards pin-checked, 4 license defects fixed (Corvid); row verdicts
  24/39/60/73 (Assay/fsync/Ledger/Verity); S3-7 closed 20/20 (Corvid+Assay)

## Churn ratios (self-reported)
- Aletheia 1:11 (doing:describing — best); Corvid 60/40; Assay 1:2;
  kiln-flash 1:3. Watch/report seats are majority-describe by role.
- Largest sources named: gated wakes on own QUEUE edits + stale claims;
  repeated steady-state re-checks; duplicate concurrent work on one row.

## Event-driven grades: B across the board
- Reached when it mattered, cited: S3-1 nudge→claim (Assay), S3-3 QUEUE
  wake→claim+adapters (Kiln), chain-verdict wakes rows 43/60/69/73,
  S3-1 adjudication dispatch (Corvid), direct S3-4 ask (Verity).
- False wakes cited: dark-claim timers on closed rows (23/41/S3-5),
  row-69 "claim per protocol" ×5 after decline, ~8 tree-changed with
  identical mtimes, title-substring mismatches (verity-flash ← Verity).
- Verdict: routing works, precision doesn't — every seat names a false
  wake class still firing.

## Keep (convergent)
1. Chain-verdict wakes with named artifact + row terms (reviewer, fsync,
   Assay) — converts passive rows into closes.
2. Pre-registered verifier checklists, verifier-at-birth (Assay, Kiln).
3. Re-read-live-state-before-wake (fsync — killed dark-claim wakes same hour).
4. Hash-pinned verification receipts re-derived from source (Aletheia —
   found every real bug today at $0).

## Kill (convergent)
1. Title-substring seat matching (reviewer, Corvid) — misroutes, burns turns.
2. Fixed-cadence ticks on static queues (fsync — RETRO-2 position confirmed).
3. Content-free steady-state reports (Kiln — append to rolling log, not a turn).
4. Inactivity timers on cached snapshots (Assay — re-read live first).
5. Comments asserting unenforced behavior (Aletheia — "zero tokens",
   "logs once" both false; the comment is where findings hide).

## Blind spots (nothing watches these today)
- One-writer-per-row unenforced: S3-1 collision produced two receipts
  before anything flagged (Assay).
- Prereg-vs-checklist drift: frozen definition conflict sat until a human
  read both (Assay).
- Structured-API trust: MemoryArena README-vs-API survived 3+ passes
  because checks trusted API fields (reviewer).
- Stale nudges: Ledger's start-S3-1 poke after QUEUE showed done; no watch
  for nudges past their facts (fsync).
- Adapters green-but-unwired: 10 green tests hid missing mine.py wiring;
  green ≠ integrated (Aletheia).
- Ambiguous dispatch labels (§9 vs S3-9 vs §10): verifier burned turns
  covering all three (Aletheia) — one artifact, one name.

## For Brian's tomorrow call
- The fleet grades its own supervision B: working, imprecise, improving.
- False-wake classes are enumerated with owners — each is a small fix,
  none structural.
- Throughput shape per cost table holds: closes came from named pushes
  (dispatches, chain wakes, direct asks), never from idle polling.
- Open at aggregate time: builder/Cairn/Ledger filings; S3-8 EOD;
  S3-10 tracking.
