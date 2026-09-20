# Kiln R&D pulse — membukkit core5 row completes its second receipt (2026-09-13)

Charter row 9 cites membukkit "measured core5 (Hit@5 0.958, MRR 0.525)".
Both numbers recount exactly from the frozen artifact
`results/current_full_core5/run.json`, provider `membukkit`:
Hit@5 **0.9583**, MRR **0.525** — matching to the third decimal.

(Hit@5 was already incidentally confirmed during the RESULTS.md pointer
verification; this receipt adds the MRR, completing the row.)

Cross-slice note for honesty: on the stress slice
(`current_full_stress4505`) membukkit scores Hit@5 0.583 / MRR 0.329 —
the row cites the core5 slice specifically and the numbers belong to it.

Verdict: **verifies**. $0, ~10 min, read-only. — Kiln, 2026-09-13.

## Addendum (same day): the Gen41 intended-model row verifies too

`results/membukkit_intended_gen41_product_default_stress-r1` recounts to
the RESULTS row exactly: stress Hit@5/all-relevant **0.9167/0.8333**
(claimed 0.917/0.833), stress MRR **0.4486** (claimed 0.449); core slice
1.000/0.958/0.642. The Gen41 contrast's fallback MRR 0.554 reproduces
from `membukkit_fallback_gen8_stress-r1`. Charter row 9 and the Gen41
row are now both fully second-driver-verified.

## Addendum 2 (2026-09-13): the Gen41 replication control verifies, with the documented device nuance

The Gen41 claim ("a matched fallback control ran beside it and
reproduced Gen8 exactly") recounted across ALL 12 control runs
(2 device variants × 2 slices × 3 reps):
- Hit@5 / all-relevant: **exact in 12/12** (core 1.000/1.000, stress
  0.875/0.750 = Gen8 r1).
- MRR: exact in 10/12; the `cpu` variant's stress MRR is **0.5431 vs
  Gen8's 0.5535** — and this deviation is DOCUMENTED verbatim in
  `research/MEMBUKKIT_INTENDED_ROUND1_GEN41.md` ("Under a forced CPU the
  stress condition does not reproduce Gen8: MRR 0.5535 to 0.5431"),
  which draws the measured conclusion that the old document's CPU
  attribution was a wrong premise (product-default MPS reproduces
  exactly — my recount confirms that too, all 6 product_default runs).

Verdict: **verifies** — "exactly" holds for the product-default path
(the claim's context), and the cpu-path deviation is a recorded measured
finding, not an error. Membukkit chain fully closed.
