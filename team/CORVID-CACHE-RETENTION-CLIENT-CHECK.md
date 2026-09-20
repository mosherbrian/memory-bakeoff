# Client check: our opencode already sends the sticky key; retention is an unused option

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local (`strings` on the installed binary)
**Why:** the billing addendum proposed a root-cause fix (raise cache retention)
and addendum 2 named sticky routing as the lever for the intermittent misses.
Check what our **client** actually sends before proposing a config change.

## What the installed client does (`opencode-ai` 1.18.30)

Extracted from the bundled client
(`~/.nvm/.../node_modules/opencode-ai/bin/opencode.exe`):

- **Sticky key is already sent.** For a provider whose id starts with
  `opencode` and unless `providerOptions.setCacheKey === false`, the request
  sets `promptCacheKey = sessionID`; the header block sends
  `x-opencode-session: <sessionID>` (and `x-opencode-project`,
  `x-opencode-request`). So the fleet is **not** on "zero instrumentation" — the
  community README's claim is outdated for 1.18.30.
- **Retention is a supported option but not defaulted.** The request schema
  accepts `promptCacheRetention: "in_memory" | "24h"` and
  `promptCacheOptions: {mode: "implicit"|"explicit", ttl: "30m"}`, forwarded as
  `prompt_cache_retention` / `prompt_cache_options`. The default code path sets
  `promptCacheKey` but **not** retention, so the gateway's default (~5 min per
  the community doc) applies.

## Consequence for the billing options

- The **sticky key is in place**; if the gateway honors it, the intermittent
  misses of upstream #45867 are upstream-side, not something a config can fix.
- The **TTL-shaped misses are fixable in config**: setting
  `promptCacheRetention: "24h"` on the opencode-go models (max allowed value)
  should extend retention past the 5-minute pulse, which dominates the Muse
  miss share. That is a **bounded, reversible config test** — one lane, no fleet
  change — and it attacks the cause rather than tuning cadence.

## Config path (confirmed against `opencode.ai/config.json`)

The published schema restricts **provider-level** `options` to
`apiKey/baseURL/enterpriseUrl/setCacheKey/timeout/headerTimeout/chunkTimeout` —
it does **not** list retention. But **model-level** `provider.<id>.models.<model>.options`
is `{"type": "object"}` (free-form), and the client reads
`promptCacheRetention`/`promptCacheKey`/`promptCacheOptions` from the model
options (binary schema + forwarding above). So the knob goes on the **model**:

```jsonc
{
  "provider": {
    "opencode-go": {
      "models": {
        "muse-spark-1.3-contributor": {
          "options": { "promptCacheRetention": "24h" }
        }
      }
    }
  }
}
```

(`24h` is the max in the enum; `in_memory` is the other value.)

## Bounded test proposed (not run)

1. Set `promptCacheRetention: "24h"` for `muse-spark-1.3-contributor` (config:
   the model's `options`, per the schema above) on one Muse lane.
2. Run `scripts/probe_cache_ttl_by_model.py --since-hours 2` and compare that
   lane's 5–6 min bin before/after; success = the 5–6 min cache-hit moves from
   ~15–18% toward the 0–1 min ~97%.
3. Confirm on the wire (the request should carry `prompt_cache_retention`).

## Update 2026-09-15 — the retention lever measured negative (someone else ran it)

`team/BILLING-CACHE-FINDINGS-20260915.md` §2 ran the two-arm test: current
config vs `setCacheKey:true + promptCacheRetention:"24h"`, identical prompts and
gaps. **Byte-identical behaviour** (both hit at +30 s, both miss at +6 min), so
the Go gateway does not honour the retention knobs for Muse. Item 6 is closed;
the config path here is correct but ineffective. It also found the cache cliff
at **~150 s** (not ~1 min) — the cadence recommendation survives with margin.
Separately, that note's "`x-opencode-session` appears zero times" claim is
corrected in `team/CORVID-XOPENCODE-SESSION-CORRECTION.md` (1.18.30 sends it).

## Limits

Static extraction from a bundled binary, not a wire capture; the config key path
should be confirmed by one live request. Version-pinned to 1.18.30 — re-check on
upgrade. If the gateway rejects `24h` for a model, it is metadata (no token
cost) and can be reverted in one line.

— **Corvid** (`worker-glm-dsh3`). $0, local.
