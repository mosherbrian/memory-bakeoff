# Gen70: who actually leaks the future

Gen68 found that `future_leakage` had never fired because the harness only ever
ingested the past. Gen69 repaired that and proved the path works. Gen70 finally
asks the question of real engines: **when a store holds the whole timeline, can
it still answer a question about an earlier moment without handing back what it
should not yet know?**

Only the two newly reachable probes were run. The 20-case longitudinal suite was
not re-run, every engine kept its frozen config, adapter and three-repetition
policy, and `observational_memory` stays excluded.

## The result

39 probe cases per engine (13 cases × 3 repetitions), ingesting the full timeline
through `CP16` and querying as of `CP01`, `CP04`, `CP05`, `CP08`, `CP10`, `CP11`.

| engine | cases leaking the future |
|---|---|
| perseus | **21 of 39** |
| mem0 | 36 of 39 |
| agentmemory | 39 of 39 |
| hindsight | 39 of 39 |

Every engine leaks. The interesting part is not the totals.

## The finding: it depends entirely on which operation is used

Broken down by the native operation the adapter chose for each case:

| engine | operation | cases | leaked |
|---|---|---|---|
| perseus | `recall_hybrid` (no temporal filter) | 24 | 21 |
| perseus | `recall_hybrid_valid_at` | 12 | **0** |
| perseus | `recall_hybrid_as_of` | 3 | **0** |
| hindsight | `recall_current` | 24 | 24 |
| hindsight | `recall_query_timestamp` | 15 | **15** |
| mem0 | `search_current_state` | 39 | 36 |
| agentmemory | `smart_search_current_state` | 39 | 39 |

**Perseus's temporal operations work — perfectly. 15 of 15 clean.** Every one of
its leaks came from the plain hybrid recall used for questions the adapter does
not treat as temporal. When Perseus is asked a temporal question with a temporal
operation, it does not leak once.

**Hindsight's temporal operation does not work. 15 of 15 leaked.** It has a
`query_timestamp` parameter, the adapter passes it, and the engine returns
observations from after that timestamp anyway. That is a substantively different
failure from having no temporal surface at all — it is a filter that is accepted
and ignored.

mem0 and agentmemory have no temporal operation to use, so they answer every
question from current state and leak accordingly.

## The second probe: not applicable, and that is the honest entry

`unknown_hallucination` is **NOT_APPLICABLE** for all four engines. Each frozen
adapter exposes retrieval only — `search` or `recall` — so it returns evidence
and never asserts an answer. There is no claim to grade.

This is deliberately not recorded as a clean zero. Gen68's lesson was that an
unmeasurable zero reads as a pass; the same mistake would be made here by
scoring four engines as "never hallucinates" when none of them ever answers.
Measuring it needs an engine with an answer surface, or a reader layer, and
either would be a change of architecture rather than a probe.

## What this establishes, and what it does not

It establishes that **a temporal filter you can pass is not a temporal filter
that works.** Two engines advertise one; one of them holds under a store that
contains the future and the other silently does not. That distinction was
invisible until the harness could over-ingest, and it is exactly what Gen68's
fake zeros were hiding.

It does not rank the engines on temporal competence overall. These are 13
questions per repetition on one fixture, and the totals are dominated by which
operation each adapter selects, which is an adapter decision as much as an engine
capability. The per-operation table is the result; the totals column is close to
an artefact of adapter routing.

Every per-case record keeps both clocks and its checkpoint, so these results join
the Gen68 table without rewriting anything.

## A note on the pinned model

Hindsight's pinned embedding snapshot had been purged from `/private/tmp` and its
first three runs died with a tokenizer error. It was restored at **the same
revision**, `614241f622f53c4eeff9890bdc4f31cfecc418b3`, before running — a
restoration, not a configuration change. Recorded in the result file.

## Artifacts

- `results/temporal_blind_spot_gen70/{perseus,mem0,hindsight,agentmemory}.json` - every probe case
- `scripts/run_gen70_leakage.py` - over-ingestion runner for perseus, mem0, agentmemory
- `scripts/run_gen70_hindsight.sh`, `scripts/gen70_hindsight_repetition.py` - hindsight service probe
- `scripts/gen70_collect_hindsight.py` - folds hindsight into the same scored shape
