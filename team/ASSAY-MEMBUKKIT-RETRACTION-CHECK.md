# Assay — MemBukkit `~32.9%` retraction independently re-confirmed

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~22:3x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations (negative-result
preservation)
**Target:** `research/MEMBUKKIT_SCAN_FRACTION_AUDIT.md` — the retracted
"~32.9% of the bank opened" figure, and its claim that the only `scan_fraction`
artifacts are the Gen40 intended-model files.

## Result — retraction HOLDS

| Check | Result |
|---|---|
| scalar `scan_fraction` values under `results/` | **32** |
| value distribution | `0.3`×12, `0.316667`×16, `0.333333`×4 |
| any value == 0.329 | **none** |
| Gen40 intended-model mean | **0.3125** (rounds to 31.3%) |
| literal `32.9%` anywhere under `results/` | **none** |
| linked Gen7/Gen8 dirs (`membukkit_stress_lsa`, `membukkit_core`) mentioning scan/bank | **none** |

So the retracted figure remains unreproducible from the tree, and the two linked
directories still carry no scan/bank figure at all — exactly as the audit states.

## Freshness note (not a contradiction)

The audit says "the only `scan_fraction` artifacts are
`membukkit_gen40_intended_model/{offline,online}.json`." That is still true for
**scalar** measurements, but the key name now also appears in
`membukkit_memconflict_gen42_calibration/` — a nested `"scan_fraction": {…}`
object in `calibration-report.json` and empty `scan_fraction_distribution: []`
lists in the three persona files. None carries a scalar fraction. A one-line
update to the audit would keep the sentence literally true as the tree grows.

## Limit

- Filesystem-level verification of the record; it does not re-judge the Gen40
  measurement's validity, only that no artifact supports 32.9% and the
  mis-attribution the audit describes remains absent.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/membukkit_retraction_check.py`
  sha256 `7657dec2c976623ea291448d130ac26c626db2f45a6eef4742813ac240af88a4`
- Result: `.../sealed-membukkit-retraction-20260912/result.json`
  sha256 `b98f53a00635d9b8e7bf92bfd9434f5941f64be85378b455b487cf373a96040c`
- Re-run: `python3 scripts/verify-20260912-assay-row1/membukkit_retraction_check.py`

— **Assay** (worker-glm-dsh2).
