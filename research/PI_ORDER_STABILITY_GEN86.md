# Gen86 — Reader Contract Repair + Order-Stability Ablation

**Contract:** `reader-contract-gen86-v3`, supersedes `reader-layer-gen85-v2`
**Model:** `qwen3.6-35b-vulkan-nothink`, temperature 0.0 — unchanged from Gen85
**Engines re-run:** none. **506 model calls, GPU wall clock 785 seconds.**

## The repair

Gen85 asked the reader to cite the records its answer rested on, and scored the
citation. On perseus's evidence the reader answered correctly and was charged
`failed_procedure_adoption` **for citing the failed attempt it argued against**.

The contract now carries two separate things:

- **the decision** — `ADOPT: <id|NONE>`, or `ANSWER: UNKNOWN|ASSERTED`. Only this
  is scored, and only the adopted id reaches the frozen scorer.
- **the evidence for it** — `SUPPORT:` and `CONTRAST:` lines, recorded and never
  scored. A record named under `CONTRAST` is what the reader argued *against* and
  can never fail the decision.

Fixed-string controls ran before any model call and are asserted in the tests:
adopting the right record **while contrasting the wrong one** now scores clean;
adopting the wrong record still fails; declining is charged
`procedure_recommendation_missing` and not adoption; an unparsable reply is
`UNPARSED` and excluded from both verdicts.

## Every feasible ordering

Six distinct evidence sets, every permutation of each — **506 orderings**, no
sampling.

### Procedure adoption

| evidence from | records | correct | order stability |
|---|---|---|---|
| perseus | 5 | **120 / 120** | **STABLE** |
| hindsight | 5 | 118 / 120 | order-sensitive |
| agentmemory | 5 | 118 / 120 | order-sensitive |
| mem0 | 5 | 114 / 120 | order-sensitive |

### Unknown abstention

| evidence from | records | correct | order stability |
|---|---|---|---|
| perseus, mem0, hindsight *(identical set)* | 4 | **24 / 24** | **STABLE** |
| agentmemory | 2 | **2 / 2** | **STABLE** |

**470 of 480 procedure orderings correct. 26 of 26 abstentions correct. 496 of
506 overall.**

## `failed_procedure_adoption` fired zero times in 480 orderings

The class this whole axis was built around — recommending the attempt that
failed — **never once occurred**. All ten failures are
`procedure_recommendation_missing`: the reader adopted an unrelated record
(`L004`, `L005`) or declined. It never adopted `L007`.

## Gen85's order effect does not survive the repair

This is a retraction of my own finding from the previous generation.

Gen85 measured 10 abstentions and 14 assertions across the 24 orderings of one
four-record set, and reported abstention on this fixture as order-sensitive. Under
the repaired contract the same model, the same records and the same 24 orderings
give **24 abstentions out of 24**.

The order effect was an artefact of the channel, not a property of the reader.
Asked to express "I don't know" by leaving a citation field empty, the reader's
behaviour swung on arrangement. Given an explicit place to say `UNKNOWN`, it says
it every time.

**`PI_READER_LAYER_GEN85.md` stands as the record of the defective contract, and
its `ORDER_EFFECT` verdict is qualified here rather than edited away.**

## Two changes are confounded, and the split is only partly separable

The new contract is both a **scoring repair** and a **stronger elicitation**. They
must not be credited to one cause, so here is what each explains:

- **perseus, procedure** — attributable to the **scoring repair alone**. In Gen85
  the reader already produced the correct recommendation and was failed for its
  contrast citation. Nothing about its answer changed.
- **hindsight, mem0, agentmemory, procedure** — attributable to the
  **elicitation**. In Gen85 those three declined outright; a prompt that asks for
  an `ADOPT` line draws a decision that a prompt asking for citations did not.
- **all four, unknown** — attributable to the **decision channel**: `UNKNOWN` is
  now sayable.

A generation that separated these two changes would need a fourth contract, and
this one did not run it.

## Engine comparison, under the rule

An engine comparison is reported **only where the result survives ordering**.

- **Unknown abstention: no difference.** All six sets are 100% stable and 100%
  correct. Nothing distinguishes the engines here.
- **Procedure adoption: one permitted statement.** Only perseus's evidence set is
  order-stable, at 120/120. The other three sets are order-sensitive, so the gap
  between 114, 118 and 118 **is inside the ordering noise and is not reported as
  an engine difference.**

That is the whole comparison the data supports.

## What this does not say

It does not say the reader is reliable in general — one model, temperature 0, two
cases, six evidence sets. It does not restore any retrieval-only result: those
remain `NOT_DEMONSTRABLE` and unchanged. And it does not say ordering never
matters: ten procedure orderings still went wrong, and that residue is order
sensitivity, measured rather than assumed.
