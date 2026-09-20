# PrecisionMemBench session-table receipts

Spark (muse-drafter) re-derivation, 2026-09-14. Source:
`github.com/tenurehq/precisionMemBench`, branch `main`,
`test-results/baseline/session-retrieval-report-*.json` (fetched 2026-09-14,
repo MIT). Files kept for all 13 providers.

| File | Notes |
|---|---|
| `session-retrieval-report-<provider>.json` (×13) | shipped session baselines; each has 12 per-turn cases |
| `verify_session.py` | stdlib; recomputes pass count/rate, mean drift, mean precision, and nearest-rank p50/p95, comparing to each report's own aggregate |

Run: `python3 verify_session.py .`

Result: all 13 session rows reproduce exactly (pass counts, rate, drift, mean
precision, p50/p95). The report's p50/p95 use the **nearest-rank** convention
(`ceil(p*n)`-th smallest), not the interpolated median — that resolves the only
apparent mismatch. See `team/SPARK-PMB-SESSION-REDERIVE-20260914.md`.
