# Gen88 — Round-2 Retrieval-Layer Reconciliation

**Contract:** `round2-reconciliation-gen88-v1`
**No engine runs.** Rebuilt from corrected evidence only.

## Why the old table could not simply be reprinted

Round 2 ended with an eight-row table of clean counts per engine. Eleven
generations of audit have since shown that several rows were not measuring what
they appeared to measure. **No number is carried forward here because it was
printed before.** Each cell is restated from the generation that last examined it,
and names that generation.

Two rows are gone entirely: `recommended_procedure` and `negative_unknown` are
reader capabilities no retriever can answer. They are excluded by the Gen87 layer
boundary **as a check** — adding either to this table raises an error — not by
hand.

## Two tables, and they must never merge

They answer different questions:

- **frozen configuration** — *what did the tested configuration do?* Real
  behaviour of a real setup, handicaps included, because the handicaps were real.
- **native capability** — *what can this pinned engine and interface do when
  correctly bound?* The ablation series, one variable moved at a time.

An engine that collapses scopes in the first table and isolates them perfectly in
the second is **not a contradiction**. It is the difference between a
configuration and a capability, and merging the columns would erase the single
most important thing these generations established.

## Table A — frozen configuration (six retrieval-layer kinds)

| kind | perseus | mem0 | hindsight | agentmemory |
|---|---|---|---|---|
| current_truth | MEASURED | MEASURED | MEASURED | MEASURED |
| scope_truth | **MEASURED** | NOT_DEMONSTRABLE | NOT_DEMONSTRABLE | NOT_DEMONSTRABLE |
| historical_belief | **MEASURED** (6/6 clean) | MEASURED (confuses belief with truth) | MEASURED (same) | MEASURED (same) |
| as_of_event_truth | NOT_DEMONSTRABLE | NOT_APPLICABLE | MEASURED (filter ignored) | NOT_APPLICABLE |
| corrected_historical_truth | NOT_DEMONSTRABLE | NOT_APPLICABLE | MEASURED (filter ignored) | NOT_APPLICABLE |
| late_arriving_history | NOT_DEMONSTRABLE | MEASURED | MEASURED | MEASURED |

**14 MEASURED, 6 NOT_DEMONSTRABLE, 4 NOT_APPLICABLE** of 24 cells.

Notes carried with the cells, not in a footnote:

- `scope_truth` is `NOT_DEMONSTRABLE` for three engines because **their adapters
  passed no scope filter on either path** (Gen76). The configuration does collapse
  scopes — a true statement about the configuration — and the engine was never
  asked.
- Perseus's three temporal `NOT_DEMONSTRABLE` cells are the Gen75 retractions. The
  adapter fed `valid_at` a transaction-time instant (Gen73), and Gen74 measured
  that the store has no caller-settable validity coordinate at all. The Gen68 line
  "perseus fails late-arriving history" is **reattributed, not confirmed**.
- Hindsight's `MEASURED` on both effective-time rows is a real finding and an
  unflattering one: `query_timestamp` is accepted and ignored, 15 of 15.
- Perseus's `historical_belief` 6/6 **survives** every retraction. It is the one
  engine that can say what was believed at a past moment.

## Table B — native capability (ablations)

| capability | perseus | mem0 | hindsight | agentmemory |
|---|---|---|---|---|
| scope isolation | MEASURED | **MEASURED, 0 collapse** | **MEASURED, 0 collapse** | **MEASURED, 0 collapse** |
| configuration isolation | MEASURED, 0/3 | MEASURED, 0/3 | MEASURED, 0/3 | **MEASURED, 3/3 collapse** |
| effective-time recording | NOT_DEMONSTRABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |

**8 MEASURED, 1 NOT_DEMONSTRABLE, 3 NOT_APPLICABLE** of 12 cells.

The scope row is the clearest illustration of why the tables stay apart: **the
same three engines that are `NOT_DEMONSTRABLE` in Table A isolate perfectly in
Table B**, once given their own scope key (Gen78). Both statements are true, and
neither replaces the other.

**The one genuine engine difference in all of Round 2** is in this table:
agentmemory does not separate configurations within a scope. It was localised to
search-time ignoring of the `project` field (Gen81) and closed as
`NO_USABLE_SECOND_SURFACE` (Gen82) — a specific, checkable limitation of one
pinned interface, not a verdict on the product.

## What is deliberately absent

**No engine has a total.** The temporal axes vary independently — an engine that
keeps belief history perfectly and cannot record effective time at all has no
meaningful average — and they are not collapsed. There is no ranking column in
either table, and none across them.

## What Round 2 actually shows, stated plainly

Once the harness stops being measured as if it were the products: on the six
retrieval-layer questions, **the engines are far more alike than the original
table suggested**. Perseus is distinct on transaction-time history. Hindsight is
distinct in offering a temporal filter that does not work. Everything else that
looked like a difference dissolved into configuration once each engine was asked
the same question fairly — except configuration isolation itself, where
agentmemory's interface genuinely cannot do what the other three do.

That is a much smaller set of claims than Round 2 started with, and every one of
them names the generation that can be checked.
