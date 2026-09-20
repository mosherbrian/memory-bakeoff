# Billing verification (fsync) — vs `FLEET-SPEND-20260914.md`

Recomputed from `~/.local/share/opencode/opencode.db` (`part.step-finish` tokens+cost), window 16:21–20:59 PDT 2026-09-14 unless noted.

## Headline checks

- **293 calls / 9.9%: CONFIRMED with a tail.** Strict window gives 2,661 calls / 266 misses (10.0%). Extending the end +25–30 min gives 2,919–2,978 calls / 289–294 misses (9.9%) — i.e. the 293 counts in-flight calls stamped after 20:59. Miss *rate* ~10% is robust either way.
- **"94.6% of the bill": NOT confirmed — true figure ≈66%.** By the db's own `cost` column, miss rows carry 66.1% (strict) to 66.6% (wide) of dollars; rate-table recompute gives 74%. The 94.6% equals the *fresh-token* share (45.3M/47.9M), not the bill — it ignores ~$1 of cache-read cost plus output cost concentrated in hit rows (dsh: 325M cache reads). Direction right (misses dominate), magnitude overstated ~28pp. Total **$5.90 CONFIRMED** ($5.893).
- **Gap curve: shape CONFIRMED, numbers approximate.** Mine: 0–1 min 1.5% miss (2,392 calls) climbing to 70–75% at 3–5 min, dipping to 40% at 5–6 min. The 1-min-vs-5-min contrast the decision rests on stands.
- **Weekly wall Tue: projection, not db-verifiable.** No budget/limit/usage-reset rows exist in `opencode.db` (only `account_state` ids); the wall comes from burn rate × published table. Mark INFERRED.

## Position on options 1–4

1. **Tighten pulse to ~45–60 s: support testing.** The 1%-vs-40% contrast is real in-db, and it sheds no context. Caveat: rests on an undocumented TTL; approve as a time-boxed test with a revert, not a permanent setting.
2. **Compact: oppose.** Conductor's quality objection stands on its own (mid-verification detail loss), and the cost case is weaker than stated once the miss share is 66% not 95%.
3. **Spread across model budgets: support for background seats only.** Headroom math is fine; it treats the symptom. Keep conductors on 1.3.
4. **Change nothing: acceptable fallback.** 5-hour bucket genuinely plateaus; only the weekly wall forces action, and these are 4.6 h of migration-contaminated data (note's own gap #2).

Net: the note's *decision-relevant* claims hold (misses dominate, pulse sits in the worst band, 1-min is safe); its headline number does not — cite **66%, not 95%**.

$0, local reads. — fsync
