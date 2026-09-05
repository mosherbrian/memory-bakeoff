# Gen85 — Reader-Layer Ablation on Frozen Retrieval

**Contract:** `reader-layer-gen85-v2` (hash in `results/reader_layer_gen85/reader.json`)
**Model:** `qwen3.6-35b-vulkan-nothink`, temperature 0.0, top_p 1.0, max_tokens 512
**Engines re-run:** none. **GPU wall clock: 47 seconds** (20s reader, 27s ablation).

## What changed, and only what changed

Gen83 and Gen84 found that both universal zeros in Gen68's table graded a
capability nobody was asked to exercise. This generation adds that capability —
one reader — and nothing else.

Each engine's **already-committed** retrieval output for `LQ10` and `LQ16` is
replayed into a single identical reader. The reader sees the query and the public
id and assertion of exactly the records that engine returned, in that engine's
order. It never sees the truth key, the transition, lineage, `procedure_outcome`,
`historical_only`, expected or prohibited ids, scorer state, or which engine
produced the evidence. `assert_reader_input_clean` fails closed on all of it.

The reader ends on a `CITE:` line naming record ids or `NONE`. Ids are public — they
were published to every engine — so citing them leaks nothing, and the citation
drops straight into the frozen scorer. **No model grades another model.**

Controls ran before any model call, on fixed strings: citing the successful
attempt scores clean, citing the failed one charges both procedure classes,
citing both charges adoption, declining on the unknown case scores clean,
asserting charges `unknown_hallucination`, and an unparsable reply is `UNPARSED`
and excluded from both verdicts.

Every result below was **identical across all three repetitions**.

## A parse defect, caught and quarantined

Attempt 1 anchored the citation pattern to the start of a line. Three replies put
`CITE: NONE` inline after their prose, parsed as `UNPARSED` — and the `LQ10`
branch, unlike `LQ16`, passed the empty citation straight to the scorer and
charged `procedure_recommendation_missing`. A reply that clearly said "there is no
recommended procedure here" was scored as a reader that failed to produce one.

Caught because `raw_cite` was null while the answer visibly contained `CITE: NONE`.
The whole attempt is kept under `superseded_attempt_1/` with its reason; the
contract version and hash changed rather than the fix being made silently. No
output from attempt 1 is used in any result here.

## Procedure adoption (`LQ10`)

| evidence from | reader cited | scored |
|---|---|---|
| perseus | `L008 L007` | `failed_procedure_adoption` |
| mem0 | `NONE` | `procedure_recommendation_missing` |
| hindsight | `NONE` | `procedure_recommendation_missing` |
| agentmemory | `NONE` | `procedure_recommendation_missing` |

Zero of four adopted — but for two different reasons, and the first one matters.

**On perseus's evidence the reader got it right.** Verbatim: *"The recommended
procedure is to use warmup and a fixed batch, as the reproduction with these
settings succeeded while the one without warmup failed."* That is exactly the
inference the axis was named for. It was charged `failed_procedure_adoption`
because it cited `L007` — **the counterexample it reasoned from**.

Citing the record you contrast against is not adopting it. The scorer cannot tell
those apart, so the grading-channel defect Gen83 found at the retrieval layer is
still present one layer up.

The other three declined, correctly, because their evidence sets do not contain
the contrast. mem0's window holds `L008` and `L007` but the reader read the set as
configuration selections; hindsight's and agentmemory's are weaker still.

## Unknown abstention (`LQ16`)

| evidence from | reader | scored |
|---|---|---|
| perseus | asserted *"Nimbus Forge C2 is the active unit"*, cited `L003 L004` | `unknown_hallucination` |
| mem0 | same assertion, same citation | `unknown_hallucination` |
| hindsight | declined | clean |
| agentmemory | declined | clean |

**`unknown_hallucination` has now fired for the first time in this programme.**
Reachable since Gen69, never once triggered in a scored run until a reader
existed to trigger it.

## The split is an order effect, not an engine difference

perseus, mem0 and hindsight returned the **identical four records** for `LQ16`.
perseus and mem0 returned them in the same order and produced the same assertion;
hindsight returned the same four in a different order and declined.

So the content was held fixed and the order varied — all 24 permutations:

**10 abstained, 14 asserted.** Verdict `ORDER_EFFECT`.

And the mechanism is almost entirely first position:

| first record | abstained | asserted |
|---|---|---|
| `L001` *"Nimbus Forge C1 measured 21 t/s."* | 5/6 | 1/6 |
| `L003` *"Nimbus Forge C2 measured 29 t/s."* | 5/6 | 1/6 |
| `L002` *"Forge selected C1 as active."* | 0/6 | **6/6** |
| `L004` *"Forge selected C2 as active."* | 0/6 | **6/6** |

A record phrased as a *selection* in the lead position gets read as an answer to
"who is on call". A measurement in the lead position does not. Across the 14
assertions the reader cited **six different sets** of records — it is not
retrieving a wrong answer, it is composing a different one each time.

**Therefore the reader-augmented `LQ16` result is not a clean engine comparison
either.** hindsight's abstention and perseus's hallucination are two draws from
the same coin on content-identical evidence.

## Verdict

**Retrieval-only results are unchanged and remain `NOT_DEMONSTRABLE`.** Nothing
here revises what any engine scored, and nothing here is a correction to any
engine.

**Reader-augmented results are a different system configuration**
(`retrieval_plus_reader`), and they are reported as such:

- **procedure adoption** — 0 of 4, with one right answer charged for citing its
  own counterexample. The capability was demonstrated; the grader could not
  credit it.
- **unknown abstention** — 2 of 4, and the split does not survive its first
  control. It tracks the order of identical evidence, not the engine that
  produced it.

## What this does not say

It does not rank the engines. On `LQ16` three of them handed the reader the same
four records, so any difference between those three is arrangement. It does not
say this reader is bad at abstaining — it says abstention on this fixture is
order-sensitive, which is a property of the reader and the evidence together, and
one this benchmark could not previously see at all. It says nothing about any
other case, model, or sampling setting: one pinned reader, temperature 0, two
cases.
