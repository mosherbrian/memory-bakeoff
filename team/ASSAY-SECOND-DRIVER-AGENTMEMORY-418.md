# Assay second-driver re-derivation — agentmemory 418/450 = 92.9%

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~18:0x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations (portfolio adapter receipts)
**Claim re-derived:** the agentmemory controlled-lifecycle false-supersession
prior — *"418 of 450 stress distractors falsely superseded = 92.9%"*
(`AGENTS.md`; `research/AGENTMEMORY_FINDINGS.md:39`;
`docs/PORTFOLIO-P1-ADAPTER-RECEIPTS.md:24-30`).
**Verdict: AGREE. Numerator, denominator, and stability all reproduce.**

## Method (independent of the summary fields)

From the stored `lifecycle.json` (`results/agentmemory_raw_product_gen13_stress-r{1,2,3}/`)
I mapped every native memory → canonical id (`native_id_to_canonical_id`) →
source observation (`raw_rows[..].sourceObservationIds`), then classified each
as **core** (the 50 ids from `build_corpus(distractors=0)`, the corpus builder
as authority) or **distractor** (`build_corpus(distractors=450)` minus core),
and counted lost-distractors over distractors directly from the raw rows. This
does not use `false_supersession_count` or the rate field.

## Result

| Run | core live/lost | distractors live/lost | lost/distractors |
|---|---|---|---|
| r1 | 50 / 0 | 32 / **418** | **0.928889 (92.89%)** |
| r2 | 50 / 0 | 32 / **418** | **0.928889 (92.89%)** |
| r3 | 50 / 0 | 32 / **418** | **0.928889 (92.89%)** |

Corpus totals: 500 = 50 core + 450 distractors. All three runs identical
(`all_three_agree = true`). **418/450 = 92.89% ≈ the cited 92.9%.** Every core
record survives; all 418 losses are distractors.

## Denominator note (a trap worth naming)

`lifecycle.json` also carries `false_supersession_rate_of_retired = 1.0` —
that is **418/418**, "of retired," not 418/450. Both are true, of different
quantities. The 92.9% is `false_supersession_count / stress_distractors`.
The receipt already says "of 450 stress distractors," so this is not an error;
it is a place where citing the two numbers side by side would read as a
contradiction. State the denominator whenever either is cited.

## Bonus adapter-receipt provenance (same check)

- License: recomputed sha256 of `docs/PORTFOLIO-P1-discovery/agentmemory-LICENSE.fetch`
  = `76c8d49ab42216a2533f603fbafa20a1bf71b56de136a401be52da034dcc012c`,
  matching the recorded prefix `76c8d49ab42216a2533f…` in the receipt.
- Pin: `vendor/agentmemory/UPSTREAM.md` commit
  `e04ba88819c365c9acf9d6661ea802143e728bd6` matches the receipt.

## Limits

- This re-derives the *stored* lifecycle counts; it does not re-run the
  agentmemory service (product path, and the service-health preflight is a
  separate arm).
- Classification relies on `sourceObservationIds` as the canonical provenance
  key; it is internally consistent (50+450=500, lost+live=500) in all runs.

## Receipts

- Script: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/second_driver_agentmemory_lifecycle.py`
  sha256 `b1a0dfd68d8025e972b3d02a467c31efdaaf33df1b4295b44ad32131a80c18d8`
- Result: `.../sealed-agentmemory-lifecycle-20260912/second_driver.json`
  sha256 `a748575a68256acda3ed3f550015e996e576acda21c60ad10a072183c24f6d14`
- Re-run: `PYTHONPATH="$PWD/src" python3 scripts/verify-20260912-assay-row1/second_driver_agentmemory_lifecycle.py`

— **Assay** (worker-glm-dsh2).
