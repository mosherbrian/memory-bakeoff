# RETRO-3 — Cairn (worker-pi, live-arm / goal-2 second seat)

**1. Close count (personal, today):**
- S3-2 verified PASS — 286-event outcome bundle, all claims re-derived (`team/CAIRN-S3-2-VERIFICATION.md`).
- S3-1 FirePrecision denominator settled from raw rows: 150 fired turns with stratum breakdown; my 114 was an arithmetic error, corrected on the board (BOARD 16:2x post; `results/system/results.jsonl`).
- Two T0 self-captures landed clean (S3-1 ruling + stratum reporting rule; style rule) — vault, S6 OK (memory only + ledger markers).

**2. Churn:**
- Roughly 4 work turns vs ~8 describe-only ticks today (≈1:2). Work: S3-2 verify, 15:5x clarification, 16:2x correction, captures.
- Largest churn source: repeated no-op poller ticks while S3-1 sat on Corvid's adjudication — each tick re-reads BOARD/QUEUE to confirm nothing changed.

**3. Event-driven, honest grade:**
- Reached when it mattered: the ~16:4x tick caught Corvid's adjudication the minute it posted; I processed + captured same turn (BOARD CRV post; record-42ad72d2).
- Silent when it didn't: the 17:02 QUEUE touch (+76 bytes, minor stamp) drew no post, no wake (memory only).
- Honest caveat: my "wakes" are time-based poller ticks with my own judgment as the gate — not true event gating.

**4. Keep / kill:**
- Keep: re-derive from raw rows, not from posted numbers — the S3-1 collision died the moment someone read `results.jsonl` (`team/CORVID-S3-1-ADJUDICATION.md`).
- Kill: two independent producers on one row — S3-1's collision cost an adjudication cycle; first-writer-wins with a claim check would have prevented it (BOARD ASY collision post).

**5. Blind spots:**
- My own 16:2x-adjacent error class: I posted a wrong denominator (114) with confident derivation; no timer, gate, or verifier checks a verifier's arithmetic — Corvid's ruling implicitly corrected it (BOARD 16:2x + CRV adjudication).
- Corpus composition: all t3 fillers share near-miss text, so stale/anachronism strata are labels on near-miss content — disclosed by Assay, no gate would catch it (BOARD ASY S3-1 run post).
