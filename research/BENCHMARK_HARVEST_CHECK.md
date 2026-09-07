# Can we harvest an existing benchmark instead of building fixtures?

Checked 2026-09-06, before committing to a Phase 2 shape. Brian directed the
check to run before the pivot decision.

## What was checked

"Can Agent Memory Systems Track Evolving State?" arXiv:2608.19652 - introduces
StateMemBench (234 multi-session scenarios, 322 graded probes) and StateMem.
It is the closest published work to reader-interference-v6.

## Finding 1: StateMemBench was not FOUND. That is weaker than "not released".

No repository URL in the abstract or the paper body. Nothing on HuggingFace for
`statemem` or `StateMemBench`. No project page in two web searches.

What was NOT done, and must be before this negative is treated as settled: a
GitHub code search, papers-with-code, the authors' other repositories, or an
email. The network was working - a 15.4 MB HuggingFace file downloaded the same
evening. This is an unfinished search, recorded as one.

## Finding 2: the paper already measured our ceiling, on LongMemEval oracle

The oracle condition puts every gold fact in the prompt by construction -
retrieval recall is 1.0. That is exactly the "perfect records" arm.

> "DeepSeek-V4-Flash fails 36 of 306 questions; judges from two model families
> both confirm 44.4% (16/36; Wilson 95% CI [30%,60%]) as state drift"

Note the denominator: 306, on a paper that elsewhere reports 234 scenarios and
322 probes. Which subset the oracle condition ran on is NOT recorded here and
must be read from the paper before the figure is cited again.

So: ~88.2% correct under guaranteed evidence, and drift toward a superseded
value is the largest confirmed failure category once retrieval is eliminated.

This is the SHAPE of number reader-interference-v6 was being built to produce.
It is not ours and cannot stand in for ours: different model, different judge,
different success predicate. It tells us the question is answerable and roughly
where the ceiling sits for a strong model. It does not calibrate our arm. Our own 24/48 is NOT comparable - a
different reader and a much harsher success predicate (verbatim value AND
citation AND disposition) - and should not be presented as agreeing or
disagreeing with it.

## Finding 3: the ordering question is open IN THIS PAPER

The paper does not measure or report where the current fact sits relative to the
superseded one in the context. That much is checked.

The broader claim - that no published work measures it - is FALSE, and was
checked the same night it was written. Two searches found it immediately:

- **ConflictQA** (arXiv:2604.11209, `github.com/Tianzhe26/ConflictQA`) runs
  exactly this manipulation: it "records results when conflicting evidence is
  present before and after the correct evidence", and reports that for models
  vulnerable to conflicting evidence, putting the correct evidence FIRST
  improves performance. Data and code are released.
- **Position bias** is a measured, benchmarked phenomenon: across 36 models the
  first-shown option is picked 64.3% of the time, a 15.7 point lift, and the
  median model flips its choice on 41.3% of decisive swapped-order pairs
  (`github.com/lechmazur/position_bias`).
- **evolveQA** (arXiv:2510.19172) probes models on evolving knowledge.

So "the one thing our apparatus does that the published work does not" was
wrong when written. What survives is narrower and must be stated as the narrow
thing it is:

  ConflictQA orders CONTRADICTORY evidence in a RAG setting. The conflicts are
  counterfactual - two sources disagreeing. It does not order a SUPERSEDED
  earlier value against the CURRENT one, where both are true statements made by
  the same user at different times, and where the task is to report the current
  state rather than to pick a trustworthy source.

That distinction is real but it is a niche inside a studied problem, not virgin
ground, and the next handoff must present it that way. Before any claim of
novelty: read ConflictQA's ordering ablation properly, and check the Phase-B
harvest list (HaluMem, STALE, Supersede, EvoMemBench, GateMem, LongMemEval-V2)
and whether the pinned MemConflict generator ablates order.

## Finding 4: LongMemEval is public; MemConflict is already pinned here

- `xiaowu0162/longmemeval-cleaned` on HuggingFace, 17.5k downloads.
- MemConflict is PINNED but NOT vendored. `research/MEMCONFLICT_PIN.json` records
  the upstream commit and dataset sha256, and says in its own `checkout` field:
  `external/MemConflict (gitignored; not vendored)`. That directory does not
  exist in this tree. An earlier version of this document called it vendored;
  that was wrong, and AGENTS.md records 16 test failures caused by its absence.

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
