# Gen87 — Reader-Layer Closure

**Contract:** `layer-boundary-gen87-v1`
**No new model calls. No engine re-runs.** Gen85 and Gen86 are frozen and read.

## The bounded conclusion for `retrieval_plus_reader`

One pinned reader (`qwen3.6-35b-vulkan-nothink`, temperature 0), two cases, six
distinct evidence sets, **every feasible ordering of each — 506 orderings, no
sampling**. With an explicit decision channel: `ADOPT: <id|NONE>` and
`ANSWER: UNKNOWN|ASSERTED`, scored alone, with supporting and contrasting
citations recorded and never scored.

**Unknown abstention: 100% correct and order-stable on every tested evidence
set.** 24 of 24 on the set perseus, mem0 and hindsight share; 2 of 2 on
agentmemory's. **No engine difference** — nothing distinguishes them here.

**Procedure adoption: nearly universal — 470 of 480 orderings correct.** Only
perseus's evidence set is **fully order-stable at 120/120**. hindsight and
agentmemory reach 118/120, mem0 114/120, and those three are order-sensitive, so
**the 114/118/118 spread is inside ordering noise and is not reported as an engine
difference.**

**`failed_procedure_adoption` fired zero times in 480 orderings.** The class the
axis was built around never once occurred.

## What is deliberately not concluded

**The Gen85→86 improvement is not attributed causally.** That contract changed the
scoring *and* the elicitation in one step. Perseus's procedure result is
attributable to the repair alone — its Gen85 answer was already correct and
unchanged — but the other three engines declined in Gen85 and decide now, which
is elicitation. Separating the two would need a fourth contract, and none was run.
The attribution is recorded as `WITHHELD` in the frozen closure rather than
guessed.

## Two retracted findings, kept rather than erased

Gen85's citation contract **failed a correct recommendation** for citing the
counterexample it argued against. Gen85's `ORDER_EFFECT` verdict on abstention
**did not survive the repaired channel**: the same 24 orderings that gave 10
abstentions give 24. Both reports stand as the record of the defective contract,
qualified in place.

## The rule this leaves, enforced

`recommended_procedure` and `negative_unknown` are **reader/full-product
capabilities, not retrieval-engine metrics.** Neither can be answered by a store:
one needs a reader to weigh two records and choose, the other to decide to
decline.

They therefore stay **`NOT_DEMONSTRABLE` at the retrieval layer permanently** —
not pending better adapters, but by construction, because a retriever was never
the thing being asked.

This is not left as prose. `layer_boundary.py` tags every target kind with the
layer that can answer it, and `assert_no_layer_mixing` **fails closed** on a
retrieval-only table that carries either reader kind — and equally on a
reader-layer table that smuggles in retrieval kinds, since the reader ran on two
cases only. Four generations said this in text; this one makes it a check that can
fail.

`ARCHITECTURE.md` carries the same closure.

## Layer separation preserved

The reader work stays on `reader-layer-gen85` and **main is not amended by it**.
Every retrieval-only result stands exactly as committed. Nothing in Gen85, Gen86
or Gen87 is a correction to any engine.

## Where this leaves Round 2

Gen68's table had eight rows. Six are retrieval-layer questions and stand as
measured. The two that read as universal failure were the two that no retriever
could answer, and they now sit at the layer that can — with a bounded, controlled
result and an explicit refusal to over-claim from it.

The detour is closed. The broader memory-system evaluation resumes at the
retrieval layer, with the boundary now enforced.
