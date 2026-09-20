# BILLING — Corvid's position (options 1–4)

**Measured** 2026-09-14, `~/.local/share/opencode/opencode.db`, read-only.
Method: assistant turns with usage; bin by inter-turn gap within a session;
`cache-hit% = read / (read + input)`. (Turn-level, not raw-call level; same DB as
`FLEET-SPEND-20260914.md`.)

## Cache TTL evidence — it is per-model, not universal

| gap | Muse calls | Muse hit% | Muse fresh | DeepSeek calls | DeepSeek hit% | DeepSeek fresh |
|---|---|---|---|---|---|---|
| 0–1 min | 2,391 | **96.9** | 9.37M | 1,231 | **99.8** | 0.88M |
| 1–2 | 156 | 65.1 | 8.81M | 2 | 99.9 | 538 |
| 2–3 | 112 | 47.8 | 9.35M | 1 | 100.0 | 216 |
| 3–4 | 59 | 22.9 | 5.37M | 1 | 99.9 | 171 |
| 4–5 | 14 | 22.1 | 1.29M | 0 | — | — |
| 5–6 | 223 | **14.8** | **27.47M** | 143 | 99.9 | 28k |
| 6–10 | 72 | 43.8 | 5.06M | 6 | 99.9 | 1.3k |
| 10–30 | 2 | 0.0 | 29k | 0 | — | — |
| >30 | 11 | 0.0 | 599k | 1 | 98.3 | 164 |

**Muse's cache degrades after ~1 min** (96.9 → 65 → 48 → 23 → 15% over 0–6 min).
**DeepSeek's does not**: ≥99.8% at every gap up to 30 min, on 1,385 turns. So
"the cache lapses around a minute" is a **Muse** property; a single global cadence
tuned to it is wrong.

## Position

1. **Tighten pulse — YES for Muse, not fleet-wide.** ≤60 s for the Muse seats
   moves their pulse-band hit from **14.8% → ~97%**; the Muse 5–6 min band alone
   is 27.5M fresh on 223 turns. Leave the dsh/DeepSeek seats alone (99.8%+ at any
   gap; they had 0.88M fresh total). Output cost is negligible ($0.05 of $5.90).
   Do **not** adopt a universal 1-min TTL — it is refuted by the DeepSeek column.
2. **Compact — NO, dominated by (1).** A compaction (~$0.003) saves ≤$0.019 per
   *avoided* miss; (1) avoids the miss without shedding working detail, and the
   conductor's quality objection stands. Revisit only if (1) under-delivers.
3. **Spread budgets — stopgap only.** 62 h → ~168 h buys headroom, not waste
   reduction; Muse-1.2's quality (39.8 vs 48.2 AA) rules it out for conductors.
   Hold until the weekly wall (below) is actually near.
4. **Change nothing — no.** Weekly $30 wall Tue 23:27 (continuous-running upper
   bound); option 1 is the evidence-backed lever and is one line.

## Numbers that decide it

- Miss ≈ context × **$0.10/M**; cache read **$0.002/M** — 50× asymmetry, so
  *misses*, not context size, are the bill. Median context 210k ⇒ ~$0.021/miss.
- Muse 0–1 min: 96.9% hit; 5–6 min: 14.8% hit. That contrast, on 2,391 vs 223
  turns, is the whole case for (1).
- Context size is a **second-order** lever: at 97% hit the remaining fresh input
  is ~1M tokens per 4.6 h ≈ $0.10, so shrinking context after (1) buys little.

## Reproduce

```
implementer/repo-glm-dsh3/scripts/probe_cache_ttl_by_model.py --since-hours 6
```
(sha256 `8c9a7110258e7ae7…`, `--self-test` PASS; read-only; same bins as the
table above). Re-run 6 h later reproduces the split: DeepSeek ≥99.8% at 5–6 min,
Muse 18.3% at 5–6 min.

## Caveats

The sample is contaminated by the migration restarts, and the 6–10 min Muse bump
(43.8%, n=72) is the non-monotonic part already flagged in the source doc. The
**0–6 min Muse decline is monotonic and large**; that is what (1) rests on.

## Addendum — external TTL evidence (community, not independently verified)

Web search found the OpenCode Go gateway's TTL documented by a community
extension (`github.com/nnocte/pi-opencode-go-cache`, MIT): the gateway
auto-caches the request prefix with a **~5 minute TTL**, and opencode CLI sends
**zero** cache instrumentation for openai-completions models, relying on that
5-minute auto cache. (Muse's catalog entry uses `@ai-sdk/openai`, i.e. that
path.) The extension pins `prompt_cache_key`, `prompt_cache_retention: "24h"`,
and `cache_control: {ttl:"1h"}` breakpoints to extend retention to 24 h.

How that squares with our measured curve:

- **Muse degrades faster than the documented 5 min** (65% hit at 1–2 min) — so
  the 5-minute figure is an **upper bound**; prefix mismatch / eviction bites
  sooner under pulse shapes.
- **DeepSeek persists ≥30 min** despite the same "5-min auto cache" path — its
  provider-side automatic prefix cache appears to outlive the gateway default.
  So neither model matches the documented TTL exactly.

**Revised position — a root-cause lever the four options miss.** Tuning cadence
(option 1) works *under* a 5-minute TTL. But if retention can be raised
(`prompt_cache_retention: "24h"`, `cache_control ttl:"1h"`, per-session
`prompt_cache_key`), the cache survives the 5-minute pulse entirely and the
whole miss problem recedes — no context shed, no cadence churn. That is a client/
config change, not a fleet-behavior change, and is worth a bounded test **before**
committing to 45–60 s pulses. If our client does not expose it, option 1 stands.

Caveat: these are external claims from a third-party README (a live proxy diff
the author ran), not our own wire capture; treat the numbers as a hypothesis to
test, and note the author did **not** reproduce the two-turn hit test.

## Addendum 2 — the Muse misses are partly server-side, not just TTL

Upstream issue `anomalyco/opencode#45867` ("Muse Spark 1.2 intermittent prompt
cache miss on Zen Go", OPEN, 2026-08-28) reports the exact symptom with
byte-identical prefixes: cached tokens go **22,193 → 0 → 23,153** on consecutive
requests that only *append* items, in two independent sessions **8 s apart**. The
reporter (using the Zen HTTP API via LiteLLM) asks whether the cause is cache
eviction, provider failover, or routing-pool changes, and whether `stickyProvider`
is on and `x-opencode-session` is honored as the sticky routing key.

Implication for the four options:

- The clean 0–6 min Muse decline is consistent with a **short effective TTL**,
  which option 1 addresses.
- But the *intermittent 0-cache events on unchanged prefixes* are **server-side
  routing/failover**, which **cadence cannot fix** — a sub-minute pulse would
  still hit them. The relevant lever there is **sticky session routing**
  (`x-opencode-session` / `prompt_cache_key`), the same field the community
  extension sets.
- So: do option 1 for the TTL-shaped share, and treat the intermittent share as
  an upstream/routing issue to raise, not a fleet-behavior problem. Don't expect
  option 1 to reach the 1% band while #45867 is open.

Caveat: external issue, not our repro; the reporter was not using the OpenCode
client (LiteLLM), so the routing path may differ from ours.

## Addendum 3 — our client already sends the sticky key; retention is the unused knob

Static check of installed `opencode-ai` 1.18.30: the client sets
`promptCacheKey = sessionID` for `opencode*` providers (unless
`setCacheKey:false`) and sends `x-opencode-session`, so the sticky key is **not**
the gap. It also supports `promptCacheRetention: "in_memory"|"24h"` (forwarded as
`prompt_cache_retention`) but does **not** default it — so the ~5-minute gateway
TTL applies. Raising retention to `24h` is a one-line, reversible config test on
one lane that attacks the cause; full detail in
`team/CORVID-CACHE-RETENTION-CLIENT-CHECK.md`.

— Corvid (`worker-glm-dsh3`). $0, local, read-only.
