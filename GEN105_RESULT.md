# Gen105 — Gen102 Supersession Re-verification

**Scope kept:** Perseus and Hindsight only, `interference-v3`, the frozen Gen102
paired arms, unchanged scorer, retrieval setup, repetitions and lifecycle
bindings. AgentMemory and Mem0 not rerun.

## Both Gen102 conclusions survive correct ingestion order

| engine | kind | cells | stale removed | current newly lost |
|---|---|---|---|---|
| perseus | EXPLICIT_LINEAGE | 16 | **16** | **0** |
| hindsight | STATE_TRANSITION | 16 | **0** | 0 |

Per core/load, 48 paired cells each (4 cores × 4 loads × 3 repetitions):

**Perseus** — stale removed in **48 of 48**, current lost in **0**. The current
record's rank moves in 41 of 48 cells, which is the *expected consequence* of the
stale record leaving the window, not a cost. Explicit lineage does what Gen102
said it does, on the order Gen102 only claimed to be using.

**Hindsight** — **not one of the 48 cells differs between the arms.** Same
mechanisms, same `target_present`, same ranks. This is stronger than Gen102's
result: `update_memory(state="invalidated", reason=...)` is accepted and recall
returns the identical decision at every core, every load, every repetition.

Whether the state changed in the store is still not established here. What is
established is that recall is unchanged — the same shape as Gen70's
`query_timestamp`, now measured on a corrected fixture.

## The Gen104 defect had five sites, not one

Enforcing the invariants meant looking for the pattern rather than the instance.
`set(visible_ids(...))` followed by a loop over `fixture.observations` had been
written independently at **five** places: the main interference runner, three
hindsight side-scripts (`gen97_`, `gen99_`, `gen102_hindsight_arms.py`), and the
Gen100 audit.

Four of the five read v1 or v2, where resolver order coincides with construction
order, so they were harmless. **`gen102_hindsight_arms.py` reads v3, so
Hindsight's Gen102 arms ran the wrong order too** — the same defect, a second
engine, found by looking for the pattern.

Fixed once, in `interference.ordered_observations`, now used by all five. An AST
test fails if any script re-derives ingest order from a set again.

## The invariants now cover every engine path

- `ingest()` wraps the write loop for all four engines and checks what was
  actually **consumed**, since `ordered_observations` returns the right order by
  construction and the residual risk is a caller reordering after the fact.
- `assert_hits_map_to_live_identity` now also guards **perseus and hindsight**,
  which previously appended `None` for an unmapped hit and scored it.

Both fired clean on every arm in this generation.

## What I damaged, stated plainly

The runners write to fixed paths, so **rerunning overwrote the pre-correction
Gen102 artefacts**, and `results/` is untracked. The aggregate comparison is
sound — Gen102's 16/16 and 0/16 are in the committed report and both reproduce
exactly — but a **cell-level rank diff between the old and new runs is no longer
recoverable**. I can say the conclusions survive; I cannot say from artefacts
whether any individual cell moved.

That is a bookkeeping loss I caused this generation, and the fix is to write
per-generation artefact paths rather than reusing a directory named for the
generation that first created it.

## State

`1073 tests passing`.
