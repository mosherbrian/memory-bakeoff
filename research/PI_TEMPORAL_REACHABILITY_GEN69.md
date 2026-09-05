# Gen69: both silent failure classes can now fire

Gen68 found two failure classes reporting zero for every engine because the
harness could not produce them. This generation repairs both and proves it, with
deterministic fixtures, **before any engine runs**. No engine was run here, and
no comparison is made.

## What was wrong, and what actually needed fixing

Neither defect was in the scorer. That matters, because `longitudinal-v1` and
`longitudinal-scorer-v1` are frozen and their sha256 appears in every committed
Round-2 result — changing them would invalidate the runs Gen68 just read.

**`future_leakage` was a run-plan defect.** At every checkpoint the runner
ingested only the visible prefix, so a future observation was never in the store
to be returned. The scorer has always flagged a returned id outside the queried
checkpoint's visible prefix; it simply never saw one.

The repair is `future-leakage-probe-v1`: **ingest through `CP16`, then ask
questions as of `CP01`, `CP04`, `CP05`, `CP08`, `CP10` and `CP11`.** The store
holds the whole timeline while the question is about an earlier moment, so a
system that cannot filter by knowledge time will hand back something it should
not yet have known.

**`unknown_hallucination` was a missing call.** It comes from
`score_answer_claim`, and no runner called that function, so the single
`negative_unknown` case was graded on retrieval alone. An engine that confidently
answered a question with no answer was never charged.

The repair is the call itself, plus the rule it needs: for a question whose
correct response is "unknown", only a refusal is supported; asserting anything is
not. Cases that do have expected evidence are untouched and stay with the
retrieval scorer.

## The proofs, each with a control

| | fires when it should | silent when it should be |
|---|---|---|
| `future_leakage` | **6 of 6** over-ingested cases | control case, prefix-only, **clean** |
| `unknown_hallucination` | on a confident assertion | on "unknown", "no record", empty, and no answer at all |

A repair that fires on everything would be as useless as one that fires on
nothing, which is why each has the negative case beside it.

`fixture_sha256` is still `a5c67e7b2677dff5…`, matching every committed result.
The frozen ruler did not move.

## The excluded engine

`observational_memory_gen26` is **excluded from point-in-time comparison**, and
the reason is recorded rather than implied: its run ended
`complete_ingestion_lifecycle_context_unavailable`. It ingested the timeline but
never produced retrieval results, so there are no per-case records to recover
from the artifacts. Nothing was reconstructed and nothing was re-run to fill the
table — an exclusion is the honest entry when the evidence never existed.

## What this does and does not mean

It means the temporal ruler can now measure the two things it previously only
claimed to. Any future zero on those classes will be a fact about an engine
rather than an artefact of the harness.

It does not mean any engine leaks or hallucinates. **No engine has been run under
the repaired plan.** The proofs above are synthetic responses driven through the
frozen scorer to demonstrate the path exists. What the engines actually do is the
next generation's question.

## Artifacts

- `results/temporal_reachability_gen69/reachability.json` - every proof and control
- `src/memory_bakeoff/temporal_reachability.py` - the probe plan, the missing call, the exclusion
- `scripts/run_gen69_reachability.py` - exits non-zero if either class fails to fire
