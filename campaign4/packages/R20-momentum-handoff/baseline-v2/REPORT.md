# R20 baseline v2 (supersedes baseline/ for use; the original is kept unchanged)

Window 2026-09-24T19:00Z to 2026-09-25T19:00Z. Computed OFFLINE from the frozen snapshot in baseline-v2/snapshot/ (provenance.json holds the capture time and source hashes). Nothing at or after 19:00Z is read. Recompute with `python measure_v2.py 2026-09-24T19:00:00Z 2026-09-25T19:00:00Z snapshot`; a rerun is byte-identical to metrics.json.

| Measure | Baseline | Status |
|---|---|---|
| (a) stall minutes | **UNKNOWN** | The snapshot lacks out-of-loop work records and the checker's historical verdicts. The diagnostic union (stream A: 583 min not covered by any loop work or rest row; longest stretch 19:00Z to 04:20Z) over-credits rest and under-credits work, so it is **not a bound** on true stalls. It is a diagnostic, not a measure. |
| (b) timeout-only drops | **1 of 22 started (0.45 per 10)**: R19-PY2-C | R19-PY2-T was still open at 19:00Z (right-censored); its later timeout is outside the window. |
| (b) ended without a claim | **UNKNOWN** | Needs per-phase runtime turn-end evidence; not inferred from later timeouts. |
| (c) decision to next same-stream dispatch | 14 intervals; most 0 to 2 min; R8 to R14 623.5 min, R14 to R18 107.4 min, R4-repair to R6 22 min; R15 censored | Explicit single-question bindings only (R1 to R3 unlabelled, excluded). |
| (d) stall escalations | Confirmed delivery **UNKNOWN**; 71 ledger notices (tern 63, agent-loop 6, fleet 2) | The ledger records attempted notices, not deliveries. No zero is claimed. Brian: 2 budget ticket files (T-103, T-104). The two synthetic Signal pages at about 15:52Z are excluded as test pages. |
| (e) stamp honesty | N/A before activation | |

The rest-row union counts 39 rows for A and 11 for B in the window, with 70 and 13 overlapping pairs. Superseded rows are included, which is why it cannot stand for the checker's verdict. Fixtures in test_measure_v2.py cover: an event after the end (ignored), an open package at the end (censored), an in-window timeout, ended-without-claim staying UNKNOWN, overlapping rest rows, notices vs delivery, decision censoring, and no live reads.

For the after-window comparison, only (b) timeout-only and (c) are directly comparable. (a) and (d) need better sources after activation, such as the stamp receipts and a delivery record, or they stay UNKNOWN.
