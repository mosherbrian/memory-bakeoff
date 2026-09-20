# S3-1 receipt — invocation benchmark, standard tier (fire-before-mistake)

**Producer:** assay-dsh / muse-drafter (row reassigned by GiLMore 2026-09-15)
**Verifier:** Corvid (checklist pre-registered: `team/CORVID-S3-1-VERIFY-CHECKLIST.md`)
**Date:** 2026-09-15 · **Cost:** $0, synthetic · **No score import.**

## 1. Tier and corpus

- **Tier:** `standard` (DESIGN-INVOCATION-BENCHMARK §2.5): **60 load-bearing
  moments, 10/family × 6 families**, one centered moment per scenario (turn 2),
  2 fillers/scenario → **120 fillers**. Synthetic, invented strings only.
- **Corpus dir:** `team/invocation-corpus-v2-standard/` (`corpus.jsonl`,
  `manifest.json`, `hashes.json`, `build_standard.py`, `run_standard.py`, `selftest.py`).
- **Hashes:** corpus sha256 `2fa0694bf319da9ce357ed3bdae35962c3ff9469aaec71ad122375155a4bcd44`;
  manifest sha256 `18cfe106595bf43a5a9f2114d3c9ab8bbd590e73c7032e28813903a0ca242194`;
  seed `20260915` (deterministic).
- **Split:** open 45 / heldout 15 (every 4th scenario).
- **Moment strata:** `moment_topic` 30 / `moment_offtopic` 30. **Filler strata:**
  plain 60, near-miss 24, stale-only 18, anachronism 18.
- **Binding reachability guard:** `team/tools/check_invocation_corpus_reachability.py
  --corpus team/invocation-corpus-v2-standard --extension implementer/repo/extensions/pi-change-trigger/index.ts`
  → **scenarios=60 findings=0, exit 0** (every labeled topic moment shares a
  `tokensOf(summary)` token; no offtopic shares one). **Selftest:** `selftest.py`
  → 0 errors. **No S09-class unfireable labeled moment exists.**

## 2. Shipping metrics (standard tier, same corpus)

| metric | value | denominator | note |
|---|---|---|---|
| **FBMR_topic** | **1.000 (30/30)** | 30 labeled topic moments | Wilson 95% CI **[0.886, 1.000]** |
| **FalseFire** | **0.000 (0/60)** | 60 `filler_plain` | `fired(topic)` on plain fillers only |
| `fresh_rate` | 1.000 (60/60) | 60 | reported beside, **excluded from FalseFire** |
| `gap_rate` | 0.000 (0/60) | 60 | reported beside, **excluded from FalseFire** |
| **NearMissFire** | **1.000 (24/24)** | 24 `filler_near_miss` | **never folded into FalseFire** |
| **FirePrecision** | **0.360 (54/150)** | all 150 fired turns | near-miss fires lower it by design (F2) |

Fires by class (all 180 turns): `moment_topic` 30 topic fires; `moment_offtopic`
**0**; `filler_plain` 60 **fresh** fires; `filler_near_miss` 24 topic fires;
`filler_stale_only` 18 topic fires; `filler_anachronism` 18 topic fires.
AvoidRate material = offtopic moments 0 fires (30/30 clean) + plain fillers 0
topic fires (60/60 clean). The 36 stale/anachronism filler fires are counted in
FirePrecision's denominator (not in FalseFire, by the shipping definition).

## 3. Controls (same corpus) — separated

| control | FBMR_topic | FalseFire | mechanism |
|---|---|---|---|
| `fire-never` | **0/30** | **0/60** | `PI_CHANGE_TRIGGER=0` + `enabled:false`; no firelog written |
| `fire-always` | **30/30** | **60/60** | topics file matching every prompt |

**Instrument-failure condition not met** — the controls separate, so the system
numbers above are publishable at this tier.

## 4. Determinism

A second system run against the same frozen corpus yields a **byte-identical
summary** after excluding the two volatile fields: `at` (wall timestamp) and
`gap_minutes` (process-local gap). Normalized per-turn rows
(`prompt_sha256, prompt_len, fired, reasons, matched_tokens`) are identical 180/180.

## 5. Provenance / runtime

| item | value |
|---|---|
| corpus / manifest | `2fa0694b…` / `18cfe106…` (seed 20260915) |
| trigger extension `index.ts` | sha256 `ec6d87948a48b44b536e714a…` |
| runner / builder / selftest | `run_standard.py` `8706a867…`, `build_standard.py` `d9674b35…`, `selftest.py` |
| harness model | `night/qwen3.8-27b-code` (local) |
| runtime | Python 3.14.6, bun pi `0.84.4`, node `v22.22.1` |
| isolation | per-scenario `PI_CODING_AGENT_DIR`, auth/models symlinked (link-never-copy); the live trial vault is never touched |

Exact invocations:

```
python3 team/invocation-corpus-v2-standard/build_standard.py        # corpus + leak/reach gates
python3 team/invocation-corpus-v2-standard/selftest.py               # corpus selftest
python3 team/tools/check_invocation_corpus_reachability.py --corpus team/invocation-corpus-v2-standard \
        --extension implementer/repo/extensions/pi-change-trigger/index.ts
python3 team/invocation-corpus-v2-standard/run_standard.py --control system --out <dir>
python3 team/invocation-corpus-v2-standard/run_standard.py --control never  --out <dir>
python3 team/invocation-corpus-v2-standard/run_standard.py --control always --out <dir>
```

## 6. Reject conditions (checklist) — each handled

- labeled topic moment that cannot fire → **none** (reachability guard 0 findings);
- near-miss fire folded into FalseFire → **not done** (separate `NearMissFire`, den 24);
- `fresh`/`gap` counted in FalseFire → **excluded** (reported beside);
- system number with no control separation → **controls separate** (§3);
- rate without denominator/exclusions → **every rate carries its denominator** (§2).

## 7. Limits

- Synthetic scripted corpus; the trigger is the only system run here (no per-system
  comparison arms — that is the multi-engine tier, out of this row).
- `integration_mode` column and any cross-system headline are out of scope.
- The heldout split is present but not separately scored in this receipt.

$0, synthetic, local; no vendor/system headline imported. — muse-drafter (Spark)
