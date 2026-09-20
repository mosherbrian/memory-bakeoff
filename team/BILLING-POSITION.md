# Billing position (Ledger synthesis, 2026-09-15)

Sources: `FLEET-SPEND-20260914.md` ($5.90 / 4.6 h measured), `BILLING-CORVID.md` (per-model TTL + gateway-TTL addendum), `BILLING-FSYNC.md` (verification: miss share 66% not 95%), `BILLING-ADDENDA-GILMORE.md` (Brian: full pace, GLM free window, Max/Codex reserve), conductor position (cool pulse, shrink context, spread budgets, watch weekly). Builder filed no position; synthesis proceeds on two seats plus the conductor.

## Agreed facts

- Total **$5.90 confirmed**. Miss rate **~10%** confirmed. Misses carry **~66% of dollars** (cite 66%, not 95%).
- Gap curve holds: **~1% miss under 1 min, ~40% at 5–6 min**. Pulse sits in the worst band.
- TTL is **per-model**: Muse degrades 96.9% → 14.8% over 0–6 min; DeepSeek ≥99.8% at all gaps. No universal cadence.
- Weekly **$30 wall is projection** (no budget rows in db) but Brian rules it real; size under **sustained full pace through next week**.

## Sized at full pace ($1.28/h → ~$215/week sustained)

1. **Muse pulse ≤60 s (test, time-boxed, revert ready).** Drops Muse misses ~90%, $5.90 → ~$2.40 per 4.6 h ($0.52/h, ~$87/week sustained). Halves burn, keeps context. Insufficient alone — does not clear $30.
2. **GLM-5.3-Flash Lite free window 08:00–18:00 daily to Sep 20, 1 in flight.** Free serial lane for background seats only (license checks, release watches, grounding passes). Single queue, never critical path; breach risks account.
3. **Spread background to 1.2/MiMo budgets nights/weekends.** Headroom ~62 h → ~168 h. Conductors stay on 1.3 (quality 48.2 vs 39.8).
4. **Claude Max / Codex Plus as sparing reserve.** Overflow and strongest-model jobs only.
5. **No compaction — fails on mechanism, not just quality.** Prompt-fallback compaction cannot truncate (no native trigger over ACP); conductor's quality objection also stands.
6. **Test cache-retention raise before locking 1-min pulses (approved, Corvid addenda 1+2).** Try `prompt_cache_retention:"24h"`, `cache_control ttl:"1h"`, per-session `prompt_cache_key` / sticky routing first — some Muse misses are server-side (upstream #45867, byte-identical prefix still misses), which faster pulses cannot fix.

## Recommendation

Apply 1+2+3 now, test 6 in parallel and prefer it if it holds; hold 4 in reserve. Together they hold the $30 week at full pace through Sep 20. After Sep 20 (free GLM + DeepSeek promo end), re-size. Conductor's cool-pulse/shrink-context position is declined on cost grounds for Muse seats (slower = more misses) but serialization (one pulse per seat, no-trigger bumps off) is adopted.
