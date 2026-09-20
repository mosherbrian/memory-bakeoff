# S3-3 turn 1: green-lane adapter plan (kiln-flash, 2026-09-15)

**Row:** QUEUE S3-3 (Sprint 3 open, PO Ledger) · **Verifier:** Alice · **Cost:** $0, read-only plan.

## Green-lane roster (both lanes licensed, from seat license passes)

| Benchmark | Code | Data | Adapter shape |
|---|---|---|---|
| GateMem | MIT (`rzhub/GateMem`) | CC-BY-4.0 (`Ray368/GateMem`) | episode/checkpoint rows → operator turns per principal + leak-target annotations preserved |
| STALE | MIT (`icedreamc/STALE`) | CC-BY-4.0 (`STALEproj/STALE`, +LongMemEval MIT distractors) | M_old/M_new pairs → implicit-conflict probes; premise-resistance labels |
| HANDBOOK | Apache-2.0 (`surge-ai/handbook`) | Apache-2.0 (repo-bundled) | standing-policy + step trace → stale-premise probes |
| SWE-Together | Apache-2.0 (`Togetherbench/SWE-Together`) | Apache-2.0 (`yifannnwu/SWE-Together`) | user-sim replay turns → correction/nudge events (User Correction metric) |
| ACM | MIT (`lixiaochuan2020/agentic-context-management`) | repo-bundled | compression decisions → context-management events |
| CodeTracer | MIT (`NJU-LINK/CodeTracer`) | MIT (`NJU-LINK/CodeTraceBench`) | stage/step failure-onset labels → failure-localization events |
| CSTM-Bench | paper CC-BY-4.0 | MIT (`intrinsec-ai/cstm-bench`) | kill-chain × operation classes → threat-field rows (matches the threat-field proposal) |

Excluded (not both lanes green): StreamMemBench (EgoLife data non-commercial),
MemSecBench (no artifact), StateMemBench (unreleased), EvoMemBench/EvoArena
(code ARR), MemOps (data generated — N/A), HaluMem (ND bars adapted sharing),
MemoryArena (both ARR), Compaction Cliff data (DUA-gated, human signature).

## Adapter interface (extends the row-30 pattern)

Each adapter = `source` value for `mine.py operator_texts()` + record→text
mapping + operator-voice DEFINITION, detector unchanged. Verification per
adapter: unit test in `tests/test_external_corpus_adapters.py` style
(synthetic sample → expected operator turns) + a real-data smoke count.
Receipts per adapter; Alice verifies.

## Turn-2 plan

Implement adapters in priority order: GateMem (governance arm needs it) →
STALE (implicit-conflict class) → SWE-Together (correction events feed M4).
Others on owner call.

## Status 2026-09-15 (turn 2+)
- GateMem + STALE + SWE-Together adapters DONE (`benchmark_adapters.py`, 7 tests green).
- ACM DEFERRED: `mem_operations` is empty in all sampled rollout runs
  (run_1/run_10/run_1002, memtool); no human operator voice either (agent
  rollouts). Cannot define the decision-event shape without a run where it is
  non-empty — next: grep the train-side logs or a longer run before writing the
  adapter. No schema fabricated.

$0, no downloads, no score import. — kiln-flash (Spark)
