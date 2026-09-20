# RETRO-3 — Assay (`worker-glm-dsh2`), 2026-09-15

## 1. Close count (artifacts/verdicts/fixes I personally finished)
- S3-1 standard-tier producer run: `team/S3-1-STANDARD-TIER-RESULT.md` + `team/invocation-corpus-v2-standard/` (system arm FBMR_topic 30/30, FalseFire 0/60; controls separate; deterministic).
- S3-1 freeze-of-record override: `team/S3-1-STANDARD-TIER-FREEZE-20260915.md` (sponsor Brian, direct).
- Row-24 verifier verdict: `team/ASSAY-ROW24-INVOCATION-BENCHMARK-VERDICT.md` — PASS, R1 closed.
- S3-7 second-seat close: meta-guard from canonical @ `be2bfa9` = 20/20 hold, map-hash 0 (recorded QUEUE S3-7; no standalone file).
- FirePrecision adjudication evidence for S3-1 (BOARD, from the run + smoke 6/19 precedent). [memory only]

## 2. Churn
- Rough ratio: ~2 described/coordinated : 1 did. Most turns were wakes, claims, status edits, and waiting on runs.
- Largest churn source: duplicate concurrent work on one row — a parallel lane ran the same S3-1 `never` control and filed a competing receipt while I ran it independently (`team/S3-1-STANDARD-TIER-RECEIPT.md` vs `…-RESULT.md`).

## 3. Event-driven, honest grade
- Reached when it mattered: S3-1 inactivity nudge (row genuinely unclaimed) → I claimed and produced. Row-24 chain-verdict wake → verdict filed same turn.
- Stayed silent when it didn't: after the S3-7 second-seat close, no follow-up wake (nothing pending) — correct.
- Grade: good for me today; the stale-snapshot timer trips hit other lanes, not this one. [memory only]

## 4. One keep, one kill
- **Keep:** pre-registered verifier checklists (verifier-at-birth). Corvid's `CORVID-S3-1-VERIFY-CHECKLIST.md` made my check mechanical and blocked definition drift after the numbers existed.
- **Kill:** inactivity timers that read a cached status snapshot. They woke Ledger/others about already-closed rows 23/41/S3-5; re-read live state before waking.

## 5. Blind spots (no timer/gate/verifier would have caught)
- Two producers on one row: the S3-1 collision produced two receipts before anything flagged it — one-writer-per-row is a rule with no enforcement.
- A frozen definition conflict (prereg-table `FirePrecision` vs checklist) sat until a human read both; no guard compares a prereg against its own checklist.

— Assay (`worker-glm-dsh2`). Retro only, $0, no new work.
