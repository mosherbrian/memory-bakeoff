# Gen74: the query was repairable; the store has no clock to repair it against

Gen73 retracted Perseus's late-arrival result because the adapter fed `valid_at`
a transaction-time coordinate. Gen74 builds the repair, proves it works at the
argument level before any engine call, runs Perseus alone — and finds the
repaired query still cannot answer, for a reason underneath the adapter.

## The repair

`perseus-adapter-v2` changes exactly one thing:

- **`valid_at`** now carries the case's own `effective_time`, straight to unix
  milliseconds. No ingestion times are consulted.
- **`as_of_unix_ms`** is untouched. It asks a genuine knowledge-time question and
  mapping it through ingestion order was always correct.

The frozen Gen29 adapter is not imported, edited or reinterpreted — asserted in a
test. Its hash stays valid for every committed Round-2 result, and the old
numbers remain on record as evidence of the defect rather than being restated.

**Proved before any engine ran**, as required: seven deterministic tests show the
two mappings produce different instants on every `valid_at` case, in both
`backfill-v1` and `longitudinal-v1`, and that current-state cases still carry no
temporal argument at all.

## What the repaired adapter actually did

Perseus only, `backfill-v1`, old adapter versus new:

| case | old returned | new returned |
|---|---|---|
| BQ03 | B001 | B001, B002 |
| BQ04 | B001 | — |
| BQ05 | B002 | B002 |
| BQ06 | B002 | — |
| BQ07, BQ08, BQ10, BQ11 | — | — |

Clean `valid_at` cases: **0 before, 0 after.** The behaviour changed; the outcome
did not. And across every case, under either adapter, **no backfilled observation
was ever returned** — B004, B006, B008 and B011 never appear.

## Why: the store's validity dimension is the write clock

Measured directly, not inferred. Two entities written to Perseus 2.23.2, the
second declaring `effective_time` of 2020-01-01 in its body:

```
key=a created=1788608258156 valid_from=1788608258156 equal=True
key=b created=1788608259354 valid_from=1788608259354 equal=True
```

`valid_from_unix_ms` is the write instant in both cases. The declared effective
time is ignored, and `perseus-vault write --help` exposes **no flag** for
validity — no `--valid-from`, no effective time, nothing.

So `valid_at` filters on a validity coordinate that equals write time. Asking it
about 9 March returns rows written before that instant, which is exactly what the
new results show, and a fact backfilled on 11 March can never match a question
about 9 March however the query is phrased.

## What this establishes

**Perseus 2.23.2's temporal surface, as reachable through this interface, is
transaction-time only.** Both `as_of` and `valid_at` range over write-derived
instants. There is no caller-settable effective time, so there is nothing for an
effective-time query to match.

That strengthens Gen73's retraction rather than reversing it. Gen71 classified
`recall_hybrid_valid_at` as `effective_time_capable`; Gen73 said that was
untested; Gen74 says it is **untestable on this build** — the capability has no
storage behind it.

It also explains the original anomaly cleanly. Perseus preserves *belief* history
because belief history is a transaction-time question, and transaction time is
the clock it keeps. Its apparent late-arrival weakness was never a retrieval
failure: a fact learned late simply has no way to be filed under when it
happened.

## What I did not do

- I did not modify the frozen adapter, and a test asserts the new module does not
  import it.
- I did not restate the old results. They stand as recorded, now labelled
  invalid-for-effective-time.
- I did not run the other three engines. Gen74 was Perseus-only by instruction,
  and the storage finding does not transfer — mem0 and agentmemory have no
  temporal surface at all, and Hindsight's is its own.

## What would settle it beyond this build

Either a Perseus release whose write path accepts a validity coordinate, or
confirmation from its documentation that `valid_at` is defined over transaction
time. Both are outside what a harness can decide.

## Artifacts

- `src/memory_bakeoff/providers/perseus_effective_time.py` - the repaired adapter
- `tests/test_perseus_effective_time.py` - divergence proved before any engine call
- `results/backfill_gen73/perseus.json`, `perseus_v2.json` - old and new, side by side
