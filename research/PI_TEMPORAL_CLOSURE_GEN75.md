# Gen75: three clocks, not one score

Eight generations on temporal memory, closed. No engine was run here; this
re-synthesises Gen68–74 under the corrected clock model and records what
survives.

## The lesson that organises everything else

"Temporal accuracy" is not one property. An engine can keep a perfect record of
**what it believed and when**, and have no way to record **when a fact was
actually true**. Those are not points on a scale — they are different mechanisms
with different failures and different fixes. Averaging them destroys the only
information worth having, which is exactly what the pooled leakage totals did
before Gen71 pulled them apart.

## The bounded result

| engine | transaction-time history | effective-time history | temporal query surface |
|---|---|---|---|
| **perseus** 2.23.2 | **kept** | **not demonstrable** | present; `as_of` holds |
| **hindsight** 0.9.2 | not kept | not kept | **present and fails** |
| **mem0** 2.0.19 | not kept | not kept | none |
| **agentmemory** 0.9.29 | not kept | not kept | none |

Three things in that table matter more than the rest:

**`not demonstrable` is not a failure.** Perseus's effective-time behaviour was
never tested and cannot be tested through this interface: the store sets
`valid_from` to the write instant and the write path exposes no validity flag
(Gen74, measured). Scoring that as a failure would be as wrong as scoring it as a
pass.

**A failing surface is worse than no surface.** Hindsight accepts a
`query_timestamp` and ignores it — 15 of 15 leaked. mem0 and agentmemory offer
nothing and are honest about it. A caller can work around a missing feature; it
cannot work around one that silently does not do what it says.

**Perseus's strength is real and narrower than we said.** It preserves belief
history — 6 of 6 — because belief history *is* a transaction-time question, and
transaction time is the clock it keeps.

## What is retracted

| generation | claim | status |
|---|---|---|
| Gen71 | `recall_hybrid_valid_at` is effective-time capable | **RETRACTED** — the adapter fed it a transaction-time instant, so the capability was never exercised |
| Gen72 | Perseus makes backfilled event-time facts unreachable | **RETRACTED** — Perseus was asked what its store held before the fact was written |
| Gen70 | Perseus's temporal operations never leaked, 0 of 15 | **QUALIFIED** — an empty or pre-write snapshot cannot leak |
| Gen68 | Perseus fails late-arriving history | **REATTRIBUTED** — harness question through the wrong clock, compounded by a store with no validity coordinate |

Every one of these was a Perseus effective-time claim resting on `valid_at`. They
are listed rather than edited away, and the original results stay on record.

## What survives

- **Perseus preserves what was believed at a past moment.** Gen68, 6 of 6, on
  `as_of` cases — genuine transaction-time questions, correctly mapped.
- **Hindsight's `query_timestamp` is accepted and ignored.** Gen70, 15 of 15, on
  its own parameter and its own path. No Perseus adapter involved.
- **mem0 and agentmemory expose no temporal surface.** Gen71 — every temporal
  question routed to current-state search because there is nowhere else to send
  it.
- **No engine tested keeps both clocks.** Gen72, asserted in a test, and
  unchanged by the retractions since no engine gained a capability.

## Scope

perseus-vault 2.23.2, hindsight 0.9.2, mem0 2.0.19, agentmemory 0.9.29, in the
tested Round-2 configurations, on `longitudinal-v1` and `backfill-v1`, three
repetitions. `observational_memory` excluded since Gen69 for having no per-case
records.

This is a statement about four builds behind four adapters, not about the
products in general, and certainly not a ranking.

## What the programme should carry forward

The methodological result is more durable than the engine result: **a benchmark
must prove its failure classes can fire before it reports them as zero.** Gen68
found two that could not, Gen69 repaired them, Gen73 found a third defect that
made a whole axis untestable, and each was caught by asking what the harness
actually did rather than what it was supposed to do.

## Artifacts

- `results/temporal_closure_gen75/closure.json` - the three-axis table, retractions and surviving claims
- `src/memory_bakeoff/temporal_closure.py` - the classification and the retraction record
- `scripts/run_gen75_closure.py` - reads nothing but its own contract; no engine, no re-score
