# R20 baseline recheck — corvid-eval, read-only

- **Verdict: PASS** on the four targeted defects; one non-blocking narrative count
  mismatch noted below.
- **Reviewer:** corvid-eval; qid R20-baseline-recheck-1; receipt 19:34:40Z, deadline
  19:39:40Z. Only this file written; no production change, no network/services/Signal.
- **Intake:** `baseline-repair-claim.json` sha `5aab84efb2c4…` equals the receipt
  `claim_sha256`; **all 12 `files_sha256` recomputed exact**. Original `baseline/`
  is unchanged (superseded for use only). Contract pin `f6934033…` unchanged.

## Independent offline reproduction

- `python3 measure_v2.py 2026-09-24T19:00:00Z 2026-09-25T19:00:00Z snapshot` exits 0 and
  its output is **byte-identical** to `baseline-v2/metrics.json` (raw `diff` clean).
- `python3 test_measure_v2.py` → **7/7 OK**. The `test_offline_only` check confirms
  `measure_v2.py` contains no live-read surface (`/.local/`, `agent-loop status`,
  `subprocess`, `REST.jsonl`). Live reads occur only in the capture step, `snapshot.py`.

## Four-defect closure

1. **Window leakage — closed.** Snapshot max event is `2026-09-25T18:56:32Z` (< END);
   `events.json` excludes `>= END`. `R19-PY2-T` (start 18:56:32Z, deadline 19:01:32Z) is
   in `right_censored_open_at_end`, not in drops. `timeout_only = ["R19-PY2-C"]`,
   **0.45 per 10**; `ended_without_claim = UNKNOWN`, explicitly not inferred from later
   timeouts.
2. **Reproducibility — closed.** `snapshot/provenance.json` records `captured_at`
   19:32:33Z, `window_end`, per-source hashes and pre-end row counts (REST.jsonl
   `6cd4432d…`, 50 rows before end; escalations.jsonl `facaf8c2…`, 606 rows), plus file
   hashes; `measure_v2.py` recomputes solely from `snapshot/`. A reviewer can now recompute
   offline.
3. **(d) definition — closed.** `confirmed_delivery = UNKNOWN`, `stall_escalations =
   UNKNOWN`; 71 rows are labelled ledger notices, not deliveries; the unsupported zero is
   gone. Test pages excluded; T-103/T-104 remain.
4. **(a) stall — closed.** `primary_stall_minutes = UNKNOWN` with an explicit reason;
   the 583-min union is labelled a diagnostic that is **neither an upper nor a lower
   bound** (over-credits rest: 70 overlapping A pairs; under-credits out-of-loop work).

## Limits / minor defect

- **Format (non-blocking):** `REPORT.md` v2 says "(c) 14 intervals", but its own
  `metrics.json` contains **15** (the `R4-task-1` → `R4-task-repair-1` pair at
  `04:28:11Z` is omitted from the narrative count). One-number correction; the data and
  the long intervals listed (623.5 / 107.4 / 22 min) are correct.
- As before, (a) and (d) are not directly comparable after activation; only (b)
  timeout-only and (c) are. The v2 report already states this.

*Reviewed read-only: baseline-repair-claim.json, baseline-repair-receipt.json,
baseline-recheck-receipt.json, baseline-v2/REPORT.md, measure_v2.py, snapshot.py,
test_measure_v2.py, metrics.json, snapshot/* (events, rest, registry, escalations,
bindings, tickets, provenance); independent offline recompute and fixture run.*
