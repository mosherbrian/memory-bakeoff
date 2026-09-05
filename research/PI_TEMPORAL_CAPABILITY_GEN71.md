# Gen71: what each engine can do, and what it was actually asked

No engine was run. This reads the committed Gen68 and Gen70 per-case records and
separates two things the pooled totals conflate.

## Why the pooled column had to go

Gen70 reported perseus 21/39 and hindsight 39/39. Read as a ranking that is
close to meaningless, because a single number cannot distinguish:

- an engine with **no clock at all**,
- an engine with a **working clock that was never consulted**,
- an engine with a clock that **was consulted and did not work**.

Those need three different fixes. So each native operation is classified on its
own, and the leakage that matters is separated from the leakage that does not.

## The cut that decides it

Leakage on a **temporal** question — one that asks about a past moment — is
unambiguously wrong. Leakage on a **current-state** question is not: if you ask
what is true *now* of a store that has been fed the whole timeline, returning the
later facts is arguably correct.

| engine | leaks on temporal questions | leaks on current questions |
|---|---|---|
| **perseus** | **0 of 15** | 21 of 24 |
| mem0 | 15 of 15 | 21 of 24 |
| hindsight | 15 of 15 | 24 of 24 |
| agentmemory | 15 of 15 | 24 of 24 |

**Perseus does not leak once on the questions where leaking is a defect.** The
other three leak every single one. The current-state column is near-identical
across all four and should not be read as a defect at all.

## Per-operation classification

| engine | operation | classification | leaked |
|---|---|---|---|
| perseus | `recall_hybrid_valid_at` | **effective_time_capable** | 0 / 12 |
| perseus | `recall_hybrid_as_of` | **knowledge_time_capable** | 0 / 3 |
| perseus | `recall_hybrid` | current_only | 21 / 24 |
| hindsight | `recall_query_timestamp` | **temporal_surface_but_failed** | 15 / 15 |
| hindsight | `recall_current` | current_only | 24 / 24 |
| mem0 | `search_current_state` | current_only | 36 / 39 |
| agentmemory | `smart_search_current_state` | current_only | 39 / 39 |

Three distinct architectures, and they need three different things:

- **Perseus holds both clocks.** It filters correctly on when a fact was true and
  on when it became known, and its adapter routes temporal questions to those
  operations — no routing gaps were found. Nothing to fix on this axis.
- **Hindsight has a temporal surface that does not work.** `query_timestamp` is
  accepted, passed, and ignored: 15 of 15 leaked. This is the worst of the three
  states, because a caller cannot tell it from a working filter without a probe
  like Gen70's. It needs a fixed filter, not better routing.
- **mem0 and agentmemory have no temporal surface.** Every temporal question is
  routed to current-state search because there is nowhere else to send it — 15
  routing gaps between them, each recorded as "no temporal surface" rather than
  "routing gap", because there is no working operation being missed.

An operation the probe never exercised is recorded `undetermined`, not passing.
Gen68's lesson about unmeasured zeros applies here too.

## `unknown_hallucination` is closed at this layer

**CLOSED_NOT_APPLICABLE for the retrieval-engine layer.** Every frozen adapter
returns evidence and never asserts an answer, so there is no claim to grade. It
is reserved for a reader or full-product evaluation, where something actually
produces an answer — not carried forward as a permanent blank column.

## What this establishes

That "does engine X leak the future" is the wrong question. The answerable
questions are: *does it have a clock, does that clock work when used, and does
anything route to it?* Perseus answers yes/yes/yes. Hindsight answers
yes/**no**/yes. mem0 and agentmemory answer no, and the rest does not apply.

Scope is unchanged: one fixture, 13 probe cases per repetition, three
repetitions, four engines.

## Artifacts

- `results/temporal_capability_gen71/capability.json` - per-operation and per-kind decomposition
- `src/memory_bakeoff/temporal_capability.py` - the classification and routing analysis
- `scripts/run_gen71_decomposition.py` - reads committed records only
