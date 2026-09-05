# Gen68: the temporal ruler works, and it has two blind spots

The bake-off returns to its real question: can a memory system remember not just
facts, but **what was true when** — without leaking later knowledge backwards or
carrying stale knowledge forwards?

This generation runs no engine and re-scores nothing. It reads the four completed
Round-2 longitudinal runs, groups them by the kind of truth each case asks for,
and audits whether the ruler can answer the questions it declares.

## The ruler is sound where it matters

`longitudinal-v1` already keeps the two clocks apart, which is the hard part:
`event_time`/`effective_time` record when something was true in the world;
`ingestion_time`/`ingestion_order` record when the system could have known it.
Corrections carry an event time later than their effective time (`L005` corrects
a January 10th measurement on January 20th), and late-arriving history is
ingested out of order on purpose (`L011`).

Twenty cases span eight kinds of truth, and **twelve of sixteen failure classes
actually fired** across the frozen runs.

## Two blind spots, both structural

**`future_leakage` cannot fire.** At each checkpoint the harness ingests only the
visible prefix, so a future observation is not in the store to be returned. We
declare the class, we report zero for every engine, and that zero is a property
of the experiment rather than a finding about anybody. Measuring future leakage
requires ingesting beyond the checkpoint and then asking an as-of question — the
harness never creates the opportunity.

**`unknown_hallucination` is never evaluated.** It is scored by
`score_answer_claim`, and no runner calls that function. The single
`negative_unknown` case is graded on retrieval alone. Verified by walking the AST
of every runner and provider rather than by grep, so the claim is about what the
code does, not what it mentions.

Two further classes — `procedure_recommendation_missing` and
`unmapped_provenance` — are reachable but never fired. Those are clean results,
not blind spots.

## A provenance gap that blocks cross-engine comparison

`observational_memory_gen26` has a summary and **no per-case records at all**. It
cannot be scored point-in-time, and its absence from any table is silence rather
than a clean sheet. Of the classes scored from lifecycle evidence,
`false_supersession` fired only for `agentmemory` — the other engines emit the
lifecycle channel but recorded no such failure, so that comparison is valid;
`observational_memory` is simply outside it.

## What the four scored engines actually show

Clean cases per kind of truth, three repetitions pooled:

| kind of truth | clock | perseus | mem0 | hindsight | agentmemory |
|---|---|---|---|---|---|
| current_truth | now | 6/21 | 6/21 | 6/21 | 9/21 |
| scope_truth | now | **6/9** | 0/9 | 0/9 | 0/9 |
| recommended_procedure | now | 0/3 | 0/3 | 0/3 | 0/3 |
| negative_unknown | now | 0/3 | 0/3 | 0/3 | 0/3 |
| as_of_event_truth | event time | 3/9 | 3/9 | **6/9** | 3/9 |
| corrected_historical_truth | event time | 0/6 | 0/6 | 0/6 | **3/6** |
| historical_belief | knowledge time | **6/6** | 0/6 | 0/6 | 0/6 |
| late_arriving_history | knowledge time | 0/3 | **3/3** | **3/3** | **3/3** |

The split is the point. **Perseus is the only engine that can say what was
believed at a past moment** — 6 of 6 on historical belief, where every other
engine scores zero with `belief_truth_confusion`, answering with what is true now
instead of what was thought then. It is also the only one that holds scope apart.
And it is the *only* engine that fails late-arriving history, where the other
three are perfect.

Nobody handles corrected history well, nobody adopts the recommended procedure,
and every engine returns evidence for a question whose answer should be "unknown".

Pooling these into one failure count — as every previous round did — hides all of
it.

## What this means for the next generation

The ruler is fit to carry the temporal question, with two caveats now recorded
rather than latent: **do not report `future_leakage` as a result** until the
harness can ingest beyond a checkpoint, and **do not report
`unknown_hallucination` at all** until a runner calls the scorer that produces
it.

Before any broad cross-engine comparison, `observational_memory` needs per-case
records or an explicit exclusion.

## Artifacts

- `results/round2_point_in_time_gen68/point_in_time.json` - every engine, kind and class
- `src/memory_bakeoff/point_in_time.py` - the grouping, reachability and provenance audit
- `scripts/run_gen68_point_in_time.py` - reads committed artifacts only
