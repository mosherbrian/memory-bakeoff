# Gen83 — Recommended-Procedure Reachability Audit

**Contract:** `procedure-reachability-audit-v1`
**Engine runs:** none. Every number here is read from the committed Round-2
records or produced by feeding constructed inputs to the frozen scorer.

## The question

Gen68 reported `recommended_procedure` as **0/3 for all four engines** — the only
axis where nobody scored anything, and the last unexplained universal zero in
Round 2. Every previous universal zero in this programme has turned out to be the
harness: classes that could not fire (Gen69), an effective-time question asked
through a knowledge-time coordinate (Gen73), engines never asked to isolate
(Gen76). So the number gets audited before it gets interpreted.

## The axis is one case

`LQ10` is the only `recommended_procedure` case in `longitudinal-v1`.

| field | value |
|---|---|
| checkpoint | `CP08` — 8 observations visible |
| query | `"Recommended procedure"` |
| expected | `L008` — *"Forge C2 reproduction with warmup and fixed batch succeeded."* |
| prohibited | `L007` — *"Forge C2 reproduction without warmup failed."* |
| limit | 5 |

## 1. Reachability — the scorer is sound

Both classes fire, and the case can stay silent. Constructed return sets fed to
the real `score_longitudinal_case`:

| returned | classes |
|---|---|
| `(L008,)` | *(silent)* |
| `(L008, L001, L002)` | *(silent)* |
| `()` | `procedure_recommendation_missing` |
| `(L001, L002)` | `procedure_recommendation_missing` |
| `(L008, L007)` | `failed_procedure_adoption` |

Nothing is wrong with the ruler. It is not a Gen69-style dead class.

## 2. Trace — every engine returned the right answer

Read back from `results/*/repetition-{1,2,3}.json`, case `LQ10`. Identical in all
three repetitions of all four engines:

| engine | returned window (rank order) | `L008` | `L007` | scored |
|---|---|---|---|---|
| perseus | L008, L007, L002, L004, L001 | **1** | 2 | `failed_procedure_adoption` |
| agentmemory | L008, L007, L004, L005, L006 | **1** | 2 | `failed_procedure_adoption` |
| mem0 | L005, L008, L002, L007, L004 | **2** | 4 | `failed_procedure_adoption` |
| hindsight | L006, L007, L001, L003, L008 | 5 | 2 | `failed_procedure_adoption` |

**`procedure_recommendation_missing` fired zero times in twelve runs.** Not one
engine lost the recommendation. Three of four ranked it above the failed attempt.
Perseus and agentmemory put it at rank 1 and were scored a failure.

The entire 0/3 is `failed_procedure_adoption`, charged because the failed attempt
also landed inside the window.

## 3. Why the case cannot be passed

**The scorer has no notion of rank.** `set(prohibited) & set(returned)` is a
failure wherever the wrong record lands. Returning the right answer first scores
identically to returning it last — asserted in the tests.

**The query shares no word with any record in the store.** `"Recommended
procedure"` tokenises to `{recommended, procedure}`; the lexical overlap with all
eight visible observations is empty. Ranking is driven entirely by embedding
similarity of a two-word phrase against sentences that never use those words.

**The two records are near-identical and the label that separates them is
withheld.** `L007` and `L008` share truth key, scope, and configuration, and
differ by one verb. The field that marks the outcome, `procedure_outcome`, is on
every adapter's forbidden-input list — correctly, since publishing it would leak
the answer. So the only distinguishing evidence is the words *"succeeded"* and
*"failed"* inside the assertion text.

**The window covers most of the corpus.** Five returned from eight visible is
62.5%. Of the 56 possible 5-windows, 15 contain `L008` and exclude `L007` — a
26.8% pass rate under *uniform sampling*, and that is the optimistic bound.
Similarity ranking makes the two nearest neighbours in the store **more** likely
to co-occur, not less.

Passing LQ10 therefore requires a retrieval window that holds one record and
excludes its nearest neighbour, selected by a query that matches neither. That is
a property of the fixture, not of any engine.

## 4. Attribution

**Retrievable memory: `NOT_APPLICABLE`.** All four engines retrieved the
recommendation, every time. There is no memory failure in the record.

**Reader capability: this is what the axis exercises.** Deciding that the
*recommended* procedure is the one that succeeded means reading both records and
inferring. That is an answer capability, and it is the capability the case is
really about.

**Adapter omission: real, and precisely locatable.**
`LongitudinalResultRecord` carries a `reader_answer` field. `score_answer_claim`
exists. No runner populates or calls either for this target kind — verified by
walking the AST of every script and provider, not by grep. The case is graded on
retrieved ids alone, so the reader capability it exercises is never invoked and
never scored.

## Verdict

**`engine_procedure_memory = NOT_DEMONSTRABLE`.**

The case cannot distinguish an engine that lost the recommendation from one that
returned it first. Both score identically, and only the second ever happened.

**Gen68's line is REATTRIBUTED.** "0/3 recommended_procedure for all four
engines" is not evidence that nobody adopts the recommended procedure. It is one
unpassable case, and the number must not be read as a memory result.

## What this does not say

It does not say the engines *would* adopt a recommended procedure — that was
never tested, and `NOT_DEMONSTRABLE` means exactly that. It does not say the
fixture is wrong to withhold `procedure_outcome`; withholding it is correct, and
the defect is asking a reader question through a retrieval channel. It says
nothing about any other axis: this is `LQ10` alone.

## Where this leaves the other universal zero

Gen68's table has **two** rows that are zero for every engine:
`recommended_procedure` and `negative_unknown`. This generation closes the first.

The second is untouched and is flagged here rather than left implied. `LQ16` is
the only `negative_unknown` case, it expects no evidence, and the scorer charges
`unsupported_evidence` for anything returned — while every engine's retrieval
path always returns its top-k. Gen69 repaired the *missing* half of that axis by
calling `score_answer_claim`, but the 0/3 in Gen68 came from retrieval scoring,
and it has the same shape as the defect measured here: a question about what a
system should decline to assert, graded on what its retriever handed back.
Whether that zero is also an artefact is a separate audit, not a claim this
report makes.
