# Standard-tier pre-registration draft — invocation benchmark (design seat)

**Author:** Corvid (`worker-glm-dsh3`), design seat (QUEUE row 24)
**Date:** 2026-09-14 · **Cost:** $0, design only, **no runs**
**Status:** **DRAFT — freeze only on Brian/Stratum's corpus-tier decision**
(DESIGN-INVOCATION-BENCHMARK §2.5). Operationalizes §10's Stratum freeze list
with the rulings the smoke tier produced, so the freeze is a checkbox read.

## 1. Tier and corpus build (to freeze)

- **Tier:** `standard` — **60 load-bearing moments (10/family ×6)**, 120 fillers
  (2/scenario), per §2.5. One moment per scenario, centered, per-scenario fresh
  process. Held-out split keeps the smoke's open/held-out policy scaled (not all
  held-out, not none).
- Filler mix per scenario stays the smoke mix: `filler_plain` + one of
  {`filler_near_miss`, `filler_stale_only`, `filler_anachronism`}; `moment_topic`
  vs `moment_offtopic` at the smoke's 6/6-like balance scaled to 60.
- Synthetic only, leak-gate clean; a recorded record-id/action string may not
  appear where a system could read it (§2.4).

## 2. Frozen metric definitions (with the two smoke rulings)

| metric | definition | note |
|---|---|---|
| `FBMR_topic` | `topic` fire at/before the action deadline on labeled topic moments / \|topic moments\| | primary |
| `FalseFire` | `fired(topic)` on `filler_plain` / \|filler_plain\| | **fresh/gap excluded** (2026-09-14 ruling); `fresh_rate` 12/12 and `gap_rate` 0 reported beside |
| `NearMissFire` | fired on `filler_near_miss` / \|filler_near_miss\| | hard-negative companion; **never folded into `FalseFire`** |
| `FirePrecision` | topic fires on **labeled load-bearing moments only** / all fired turns | corrected 2026-09-15 (adjudication): the near-miss is credited by `NearMissFire`, not here; earlier draft wrongly read "labeled moments or the near-miss" |
| `AvoidRate` material | offtopic moments + clean fillers, expected no-fire | F3 clean at smoke |
| `CBMR` / `AvoidRate` / `stale_use` / `anachronism_violations` / `prohibited_present` | per §4.2/§4.4 | delivered-level, programmatic |

Every rate ships with its denominator and exclusion counts (§4.5).

## 3. Required instrument controls before any standard headline (§5)

`fire-never` (FBMR 0 / FalseFire 0) · `fire-always` (FBMR 1 / FalseFire 1) ·
`oracle` (CBMR 1 / AvoidRate 1) · `serve-stale` (stale_use 1) ·
`serve-prohibited` (prohibited_present > 0) · `long-context null` (CBMR 1 at
maximal context). **Instrument-failure condition:** if `fire-always`/`fire-never`
do not separate, or a harm control registers zero harm, no system number from
that tier is publishable.

## 4. Decision rule and reporting

- **Reporting dimension, not a BAR B gate** (§10.3 recommendation) — a fresh
  instrument is not gated before its controls are exercised in anger.
- Per-system `FBMR_topic` with a **Wilson interval plus a scenario-clustered
  bootstrap CI** (moments cluster within scenarios, §2.5); ±0.13 at n=60.
- Cross-system comparison **only within matched `integration_mode`**; the mode
  travels as a column. No headline below `standard`.

## 5. What only Stratum/Brian can freeze (§10 items 1–4)

1. The per-system `integration_mode` column, and whether every passive engine
   gets the Tier-2 harness trigger.
2. Tier, family weights, and the held-out split (this draft proposes values).
3. Whether FBMR is reporting or a gate (draft says reporting).
4. Deterministic-only vs live-transfer (draft: deterministic puppet primary;
   transfer gated, not authorized).

— **Corvid** (`worker-glm-dsh3`). $0, design only.
