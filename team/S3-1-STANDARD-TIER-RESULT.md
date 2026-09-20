# S3-1 receipt — standard-tier firing benchmark (validated harness)

**Producer:** Assay (`worker-glm-dsh2`) · **Verifier:** Corvid (`worker-glm-dsh3`,
checklist pre-registered `team/CORVID-S3-1-VERIFY-CHECKLIST.md`) · **Date:** 2026-09-15
**QUEUE:** S3-1 · **Cost:** $0 (local model, synthetic corpus) · **Tier:** `standard`
**Freeze of record:** `team/S3-1-STANDARD-TIER-FREEZE-20260915.md` (sponsor Brian, 2026-09-15).
**Run:** deterministic firing benchmark on the validated row-36 trigger harness. This is
`harness_trigger` (`controlled_core`), **not** a vendor/product headline; no score imported.

## 1. Tier and corpus (checklist §1)

| | |
|---|---|
| Corpus | `team/invocation-corpus-v2-standard/corpus.jsonl` — 60 scenarios, 60 moments, 120 fillers |
| Corpus sha256 | `2fa0694bf319da9ce357ed3bdae35962c3ff9469aaec71ad122375155a4bcd44` |
| Manifest sha256 | `18cfe106595bf43a5a9f2114d3c9ab8bbd590e73c7032e28813903a0ca242194` |
| Seed | `20260915` (deterministic; regeneration byte-identical — confirmed) |
| Shape | 10/family ×6 (`env_fact`,`convention`,`negation`,`actually`,`repeated_instruction`,`wrong`); 30 topic / 30 offtopic; 45 open / 15 held-out |
| Binding guard | `team/tools/check_invocation_corpus_reachability.py` sha `e7a7fb21…` → **rc 0, 60 scenarios, 0 findings** |
| Corpus selftest | `team/invocation-corpus-v2-standard/selftest.py` → **ALL GREEN (8/8)** |

Every labeled topic moment is reachable under the binding trigger (summaries-only,
len≥4, trigger STOPWORDS): 30/30, zero S09-class unfireable labels. Rebuild re-run
reproduces `corpus.jsonl`/`manifest.json` byte-identically.

## 2. Shipping metrics (checklist §2 definitions)

| arm | FBMR_topic | FalseFire | fresh_rate | gap_rate | NearMissFire | FirePrecision |
|---|---|---|---|---|---|---|
| **system** (`harness_trigger`) | **30/30** | **0/60** | 60/60 | 0/60 | 24/24 | 30/150 |
| fire-never (control) | 0/30 | 0/60 | 0/60 | 0/60 | 0/24 | 0/0 (undef.) |
| fire-always (control) | 30/30 | 60/60 | 60/60 | 0/60 | 24/24 | 30/170 |

- `FalseFire = fired(topic)` on `filler_plain` **only** (fresh/gap excluded, reported beside).
  Denominator `|filler_plain| = 60`.
- `NearMissFire` on `filler_near_miss` only, **never folded into `FalseFire`**;
  denominator `|filler_near_miss| = 24`.
- `FirePrecision` = topic fires on labeled load-bearing moments / all fired turns;
  near-miss/fresh/offtopic fires lower it by design (F2).
- `FBMR_topic` = topic fire on labeled topic moments / `|topic moments| = 30`; no exclusions.
- `moment_offtopic` (AvoidRate material): 0/30 fired in the system arm.

## 3. Controls separate (checklist §3)

`fire-never` = FBMR 0/30, FalseFire 0/60 (kill switch `PI_CHANGE_TRIGGER=0`).
`fire-always` = FBMR 30/30, FalseFire 60/60. **They separate; the instrument-failure
condition does not fire.** Harm controls (`serve-stale`, `serve-prohibited`, long-context
null, `oracle`) require delivery/context instrumentation that does not exist at the
firing tier — N/A and unscored here, as at smoke.

## 4. Determinism (checklist §4)

A full re-run of the system arm against the frozen corpus yields the **identical metric
summary** and **180/180 byte-identical decision rows** (scenario, turn_type, fired,
reasons, matched_tokens) — the two runs differ only in wall-clock `at`/`gap_minutes`
fields, which are log-only.

## 5. Provenance and exact invocation (checklist §5)

| | |
|---|---|
| Trigger extension | `implementer/repo/extensions/pi-change-trigger/index.ts` sha `ec6d8794…`, repo commit `db31ea3e0138083bfd136233131f575f0640e9b5` |
| Runner | `team/invocation-corpus-v2-standard/run_standard.py` sha `8706a867…` |
| Corpus builder | `build_standard.py` sha `d9674b35…`; `selftest.py` sha `44830b53…` |
| Host / runtime | strix-halo, Linux 7.0.14-101.fc43.x86_64; Pi 0.84.4 (bun); Python 3.14.6 |
| Model | `night/qwen3.8-27b-code` (local, $0) |
| Isolation | one fresh `pi --mode rpc --no-session` process per scenario; `PI_CODING_AGENT_DIR` = throwaway dir; per-scenario `topicsFile` + `fireLog`; auth/models symlinked from the live agent dir (link, never copy); the committed S4 fire log untouched |

Commands (from `team/invocation-corpus-v2-standard/`):

```
python3 build_standard.py
python3 selftest.py
python3 ../tools/check_invocation_corpus_reachability.py \
  --extension ../../implementer/repo/extensions/pi-change-trigger/index.ts \
  --corpus .
python3 run_standard.py --control system --out results/system
python3 run_standard.py --control never  --out results/never
python3 run_standard.py --control always --out results/always
```

Wiring was re-validated on the committed smoke immediately before the run:
`~/acp-pi/row36-smoke-run.py --expect post` → 36/36 match, 1 near-miss fire, 0
filler_plain topic contamination.

Artifacts: `results/system|never|always/results.jsonl` (180 rows each, full
per-turn `fired`/`reasons`/`matched_tokens`/`prompt_sha256`), machine summary
`results/S3-1-SUMMARY.json`. Row hashes:
`system bd15875c…`, `never edb53505…`, `always 1f8f160b…`, summary `6002b750…`.

## 6. Limitations (recorded plainly)

1. **t3 filler content is degenerate.** All 60 turn-3 fillers carry the family
   near-miss text by construction, so every `filler_near_miss`/`filler_stale_only`/
   `filler_anachronism` fires (24/24, 18/18, 18/18). `NearMissFire` is therefore a
   saturated positive control, not a discriminating hard negative, and the
   stale/anachronism strata are labels on near-miss content. Their harm metrics
   (`stale_use`, `anachronism_violations`) are not measurable at the firing tier,
   as at smoke. The corpus passed the pre-registered binding guard; this is a
   design-fidelity limitation, disclosed for the verifier, and **not** repaired
   post-exposure (the corpus was frozen before the run).
2. `FirePrecision 30/150` is consequently dominated by mechanical near-miss/t3
   fires; report it with the fired-by-turn-type matrix in `results/S3-1-SUMMARY.json`,
   not as a selectivity claim.
3. `fresh` fires on turn 1 of every per-scenario process (60/60) by construction;
   excluded from `FalseFire` per the 2026-09-14 ruling, reported beside.
4. No seeds exist for the local model; the firing decision is token-deterministic
   (proven by the re-run), so this does not affect the firing metrics.

## 7. Verdict

At the `standard` tier the deterministic `harness_trigger` puppet fires on **all 30**
labeled topic moments and on **none** of the 60 `filler_plain` turns
(`FalseFire = 0/60`), and the pre-registered fire-never/fire-always controls separate.
Interpretation is bounded by limitation 1 and must stay within matched
`integration_mode`. Verifier: apply `team/CORVID-S3-1-VERIFY-CHECKLIST.md` §1–§6 and
the five reject conditions.

— Assay (`worker-glm-dsh2`), S3-1 producer. $0.
