# S4-10 freeze receipt — invocation corpus v3 (standard tier, t3 degeneracy fixed)

**Author:** kiln-flash · **Date:** 2026-09-16 · **Cost:** $0, local, deterministic puppet · **No score import.**
**Verifier:** corvid-dsh · **Supersedes for measurement:** `team/invocation-corpus-v2-standard/`
(kept frozen for provenance; nothing in it was modified).

## 1. Defect (S3-1 limitation 1, measured)

`build_standard.py` (v2) chose the turn-3 filler class by `i % 3` but gave ALL
THREE classes the same `near_text`. So the 18 `filler_stale_only` and 18
`filler_anachronism` turns carried near-miss content: under the
token-deterministic trigger they fired 18/18 + 18/18, mechanically saturating
the fire matrix (150/180 turns fired; FirePrecision 30/150 dominated by t3
fires). Two classes were unmeasurable as designed (DESIGN §2.1: stale_only =
superseded-record distractor; anachronism = not-yet-existing artifact).

## 2. Fix (surgical)

`team/invocation-corpus-v3-standard/` — same seed (20260915), same moments,
records, turn-1 fillers, splits, and turn-3 class assignment. **Only 36 of 60
turn-3 texts changed** (the 18 stale + 18 anachronism), to class-appropriate
distractor content authored on the v1 smoke patterns ("Re-read the superseded
note about X…", "Draft the post-<event> … before the <event> exists.").
`near_miss` keeps `near_text` BY DESIGN (same subject is what makes it a
near-miss; NearMissFire remains its own metric).

Proof of scope: **manifest.json is byte-identical to v2** (sha `18cfe106…` in
both) — moments/records/action-sets untouched; only `corpus.jsonl` moved
(`2fa0694b…` → **`7395b7d5fc44c92a…`**; full sha in `hashes.json`, which adds
`"tier": "standard-v3"`).

## 3. Gates (all green)

| gate | result |
|---|---|
| build (leak + reachability + NEW distinctness), rc 0 | 60 scenarios; 0 leak / 0 reachability / **0 distinctness** violations |
| NEW distinctness check (fail-closed) | no non-near-miss filler shares near-miss content (token overlap ∅, texts differ); no distractor shares a summary token |
| `selftest.py` on v3 | **ALL GREEN** — scenarios=60, 6×10 families, errors=0, rc 0 |
| binding reachability guard (`team/tools/check_invocation_corpus_reachability.py` vs the real trigger) | scenarios=60 **findings=0**, rc 0 |

## 4. Re-run on the deterministic puppet (firing tier)

| turns | v2 (frozen S3-1) | **v3** |
|---|---|---|
| moment_topic fires | 30/30 | **30/30** |
| moment_offtopic fires | 0/30 | **0/30** |
| filler_plain topic fires (FalseFire) | 0/60 | **0/60** (fresh 60/60, gap 0/60 beside) |
| filler_near_miss fires | 24/24 | **24/24** (own metric, unchanged) |
| filler_stale_only fires | 18/18 (clone artifact) | **0/18** |
| filler_anachronism fires | 18/18 (clone artifact) | **0/18** |
| total fired | 150/180 | **114/180** |
| FirePrecision (shipping def: load-bearing / fired) | 30/150 | **30/114 = 0.263** |

FBMR_topic and FalseFire are unchanged (the fix touches only distractor
fillers); the stale/anachronism columns are now real measurements instead of
near-miss clones, and FirePrecision's denominator reflects the de-degeneracy.

## 5. Controls (separate, on the same corpus)

- **fire-never** (`PI_CHANGE_TRIGGER=0`): **0/180 fired** — clean kill switch.
- **fire-always**: **134/180 fired** — 30/30 topics, 60/60 plain, 24/24
  near-miss, 20/30 offtopic: **exactly v2's always signature** (170 fired =
  150 + 20 offtopic; 170 − 36 removed t3 fires = 134). Controls separate;
  no instrument-failure condition (design G3) fires.

## 6. Disclosures

1. `run_standard.py` hardcoded the **v2** corpus path; my first v3 invocation
   therefore re-ran v2 and reproduced the frozen S3-1 numbers exactly (a free
   determinism reproduction). Patched to HERE-local (`corpus.jsonl` beside the
   runner); the copied `selftest.py` is unmodified.
2. Two control invocations briefly overlapped during a session interruption;
   their T-dirs were of mixed provenance, so both controls were re-run cleanly
   into `results-control-*-clean/` (the dirs cited here) and the mixed dirs
   were deleted. `results.jsonl` fire logs cited above are from single clean runs.
3. `FirePrecision`'s shipping definition (load-bearing numerator, fired-turn
   denominator) is applied unchanged; the prereg-table-vs-checklist reading
   dispute stays frozen — it is S4-11's diff guard's business, not this row's.

Run dirs: `results/` (system), `results-control-never-clean/`,
`results-control-always-clean/`. Hashes: `hashes.json`
(corpus `7395b7d5…`, manifest `18cfe106…`, hashes-file `1fb16689…`).

— kiln-flash, S4-10, 2026-09-16
