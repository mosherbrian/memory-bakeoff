# muse-drafter: PrecisionMemBench session table re-derived, clean (spark pulse 2026-09-14)

Completes the second-driver check started in
`team/SPARK-PMB-PRECISION-DENOMINATOR-20260914.md`. That pass found the
**single-turn** table's `Mean precision` column is averaged over all
precision-bearing cases (nP 43–70), not the stated 43 active cases. This pass
checks the **session** table the same way, from the benchmark's own shipped
`session-retrieval-report-*.json`. Receipts + script:
`team/row-pmb-session/`. $0, shipped rows only, no harness run.

## Result: the session table is faithful

All 13 provider rows reproduce exactly from the shipped per-turn cases:

| provider | turns passed /12 | pass rate | mean drift | mean prec | p50 ms | p95 ms |
|---|---|---|---|---|---|---|
| tenure | 12 | 1.0000 | 0.0000 | 1.0000 | 47.79 | 134.63 |
| open-knowledge-format | 2 | 0.1667 | 0.2153 | 0.5694 | 3349.45 | 59290.82 |
| supermemory | 1 | 0.0833 | 0.7493 | 0.1825 | 172.32 | 252.14 |
| yourmemory | 1 | 0.0833 | 0.7365 | 0.1965 | 430.49 | 793.40 |
| cognee | 1 | 0.0833 | 0.8459 | 0.0772 | 4222.62 | 8781.03 |
| gbrain | 1 | 0.0833 | 0.0000 | — (null) | 535.61 | 556.13 |
| agentmemory | 0 | 0.0000 | 0.8087 | 0.1913 | 98.49 | 153.98 |
| atomicmemory | 0 | 0.0000 | 0.8449 | 0.1551 | 355.08 | 2854.39 |
| zep | 0 | 0.0000 | 0.8888 | 0.1112 | 418.13 | 659.99 |
| vector | 0 | 0.0000 | 0.9142 | 0.0858 | 256.75 | 727.68 |
| a-mem | 0 | 0.0000 | 0.9259 | 0.0741 | 25.66 | 67.84 |
| hindsight | 0 | 0.0000 | 0.9285 | 0.0715 | 1880.60 | 6162.57 |
| mem0 | 0 | 0.0000 | 0.9398 | 0.0602 | 377.93 | 692.35 |

Method note resolved: the report's `p50LatencyMs` / `p95LatencyMs` are
**nearest-rank** percentiles (`ceil(p*n)`-th smallest), not the interpolated
median. With that convention every latency matches to 0.01 ms; before realising
it, straight medians disagreed on 12/13 rows (e.g. agentmemory 98.49 vs 108.23) —
a convention difference, not a defect. The `gbrain` footnote also checks out:
all 12 turns return no beliefs, so its drift is 0 *by construction* while its
correct belief is also absent (hence 1/12, not a good score).

## Net for the PrecisionMemBench thread

- **Session table: verified** — pass/rate/drift/precision/p50/p95 all reproduce.
- **Single-turn table: one documented caveat** — the `Mean precision` column is
  the all-cases mean, not the stated 43-active-case mean, and is therefore
  provider-dependent in denominator (prior artifact).
- Together these are a complete second-driver pass over the published tables
  from shipped artifacts. The `agentmemory` row (our control arm) is confirmed
  as recorded: single-turn active precision **0.28** on the stated active set
  (0.17 as published), session drift **0.81**, 0/12 session turns passed.

Hand-off unchanged: Alice (claim class) + Corvid (evidence integrity). No score
import.

$0, web reads + stdlib recompute, no Muse batching. — muse-drafter (Spark)
