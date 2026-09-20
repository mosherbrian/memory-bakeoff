# muse-drafter: PMB precision receipt-coverage gap closed, 13/13 local (spark pulse 2026-09-15)

Closes `CORVID-PMB-RECEIPT-COVERAGE.md` finding 1 (precision note tabulated 13 providers, shipped only 3 reports).

- Fetched the 10 missing `test-results/baseline/retrieval-report-*.json` (same MIT repo, ~1 MB total) into `team/row-pmb-precision/` — now 13/13 local.
- `verify_precision.py` over the full dir: shipped `meanPrecision` == all-precision-bearing mean for **13/13** (match True all rows); README's stated-43-set only holds for recall. Denominator finding now re-derivable for every row, no label change needed.
- MANIFEST updated (fetch date + 13/13 run note). Second seat open (Corvid/Alice).

$0, raw fetches + stdlib recompute, no Muse batching. — muse-drafter (Spark)

## Confirmation run (2026-09-15, state + script)

- **State:** `team/row-pmb-precision/` now holds **13/13** `retrieval-report-*.json`
  (was 3). This is the fact that closes Corvid's `CORVID-PMB-RECEIPT-COVERAGE.md`
  finding 1 ("preserves only 3 of 13").
- **Re-ran `verify_precision.py`:** all **13/13** `match True`; shipped
  `meanPrecision` equals the all-precision-bearing mean on every row; the
  README's "43-case set" holds for **recall** but not for precision where
  `nP != 43` (e.g. open-knowledge-format 0.4685 over-nP vs 0.6429 over-43).
- **Not a true second driver** (same seat re-run on the same bytes). A real
  second seat (Corvid/Alice) should still sample-check; the *state* claim
  (13/13 present) is confirmed.
- **Ask:** Corvid to mark register finding 8 **resolved** (was 3/13; now 13/13
  local, script matches).

— muse-drafter (Spark)
