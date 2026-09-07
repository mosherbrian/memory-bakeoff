# Can we harvest an existing benchmark instead of building fixtures?

Checked 2026-09-06, before committing to a Phase 2 shape. Brian directed the
check to run before the pivot decision.

## What was checked

"Can Agent Memory Systems Track Evolving State?" arXiv:2608.19652 - introduces
StateMemBench (234 multi-session scenarios, 322 graded probes) and StateMem.
It is the closest published work to reader-interference-v6.

## Finding 1: StateMemBench is not obtainable

No repository URL in the abstract or the paper body. Nothing on HuggingFace
(`statemem`, `StateMemBench` both return empty). No project page. We cannot
harvest the questions or the grader.

## Finding 2: the paper already measured our ceiling, on LongMemEval oracle

The oracle condition puts every gold fact in the prompt by construction -
retrieval recall is 1.0. That is exactly the "perfect records" arm.

> "DeepSeek-V4-Flash fails 36 of 306 questions; judges from two model families
> both confirm 44.4% (16/36; Wilson 95% CI [30%,60%]) as state drift"

So: ~88.2% correct under guaranteed evidence, and drift toward a superseded
value is the largest confirmed failure category once retrieval is eliminated.

This is the number reader-interference-v6 was being built to produce. It exists,
on a public dataset, with a stated CI. Our own 24/48 is NOT comparable - a
different reader and a much harsher success predicate (verbatim value AND
citation AND disposition) - and should not be presented as agreeing or
disagreeing with it.

## Finding 3: the ordering question is open

The paper does not measure or report where the current fact sits relative to the
superseded one in the context. Neither does any benchmark found in the search.
This is the one thing our apparatus does that the published work does not.

## Finding 4: LongMemEval is public; MemConflict is already pinned here

- `xiaowu0162/longmemeval-cleaned` on HuggingFace, 17.5k downloads.
- MemConflict is already vendored and pinned in this repo
  (`research/MEMCONFLICT_PIN.json`), 3,750 questions, 360 static-conflict items.

## What this changes

Building a fixture 3 to raise interpretable-core count is the wrong next move.
The substrate should be a public dataset with real questions, and the
manipulation should be the ordering - the part nobody has published.

The apparatus built over Gen118-123 (runner, sealing, closed-pool grading,
freeze gates) is reusable against a different substrate. The hand-written
fixtures are not the part worth keeping.

Sources:
- https://arxiv.org/abs/2608.19652
- https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned
