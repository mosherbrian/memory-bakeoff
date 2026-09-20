# PrecisionMemBench receipts

Spark (muse-drafter) re-derivation, 2026-09-14. Source:
`github.com/tenurehq/precisionMemBench`, branch `main`,
`test-results/baseline/` (fetched raw at 2026-09-14T~23:40Z, repo MIT).

| File | Source | Note |
|---|---|---|
| `retrieval-report-agentmemory.json` | `test-results/baseline/retrieval-report-agentmemory.json` | 79,495 B; aggregate `meanPrecision` 0.1729 |
| `retrieval-report-mem0.json` | same dir | 162,778 B |
| `retrieval-report-tenure.json` | same dir | 77,631 B; the one provider whose `nP` == 43 |
| `retrieval-report-{a-mem,atomicmemory,cognee,gbrain,hindsight,open-knowledge-format,supermemory,vector,yourmemory,zep}.json` | same dir | fetched 2026-09-15 to close Corvid's receipt-coverage gap (`CORVID-PMB-RECEIPT-COVERAGE.md` finding 1); all 13 now local |
| `verify_precision.py` | this pulse | stdlib; recomputes `meanPrecision` over (a) all precision-bearing cases and (b) the 43 recall-bearing cases |

Reproduce the full 13-provider table: download all
`test-results/baseline/retrieval-report-*.json` into one directory and run
`python3 verify_precision.py <dir>` — or use this directory as-is (13/13 local;
`verify_precision.py` run 2026-09-15: shipped == all-precision mean for 13/13).

`meanPrecision` in the shipped report equals the mean over **all
precision-bearing cases** (`nP`, 43–70 depending on provider), not over the
README's stated 43 active-retrieval cases — see
`team/SPARK-PMB-PRECISION-DENOMINATOR-20260914.md`.
