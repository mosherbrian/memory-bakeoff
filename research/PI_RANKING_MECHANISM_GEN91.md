# Gen91 — Stale-Before-Current Ranking Mechanism Audit

**Contract:** `stale-before-current-ranking-gen91-v1`
**No engine runs.** The nine no-prefix ranking failures from Gen90, read from the
committed records.

## The question

Gen90 left nine failures that no prefix window can rescue: the superseded record
outranks the current one, so cutting above the stale record loses the current fact
with it. Eight of the nine are `LQ11`, where a replaced branch name beats its
replacement. What produces that order?

## How the judgement is made

**Scores are never normalised across engines.** A gap of 0.006 in one scale and
0.073 in another are not the same quantity, and treating them as one would
manufacture a cross-engine claim the data cannot support.

Each engine is judged **within its own list**, unit-free: the gap between the two
revisions, as a share of the gap from that pair to the next record in the **same**
result. A pair under 5% of that distance is a near tie — its order is decided in
the noise. Where an engine reports score components, the comparison is also made
component by component, again internal to it.

**Repetition identity is preserved.** Each repetition is classified on its own.

## The result: each engine lands in a different bucket

| engine | failures | mechanism | evidence |
|---|---|---|---|
| perseus | 3 | **OPAQUE_RANKING_SURFACE** | no score of any kind is recorded |
| mem0 | 3 | **NEAR_TIE** | pair gap is **1.2%** of the distance to the field |
| hindsight | 3 | **MEANINGFUL_PREFERENCE** | pair gap is **9.1%**, and the reranker produces it |

Three failures, three engines, three different causes. A single "bad ranking"
verdict would have been wrong for all of them.

### mem0 — a near tie, decided in the noise

`L009` scores `0.9097` and `L010` scores `0.9033`: a gap of **0.0063**, while the
next record in the same list sits at `0.389` — **0.514 away**. The two revisions
are eighty times closer to each other than to anything else the query returned.

The scores are byte-identical across all three repetitions, so this order is
stable — but it is stable at a margin that carries no information about which
record is current.

### hindsight — the reranker produces the order

The gap here is real within hindsight's scale, and the component breakdown says
exactly where it comes from:

| component | stale `L009` | current `L010` | gap |
|---|---|---|---|
| keyword | 0.30000001 | 0.30000001 | **0.000000** |
| semantic | 0.867734 | 0.866079 | 0.001655 |
| **reranker** | 0.893654 | 0.815389 | **0.078265** |
| final | 0.878275 | 0.805378 | 0.072897 |

**The keyword score is identical and the semantic score is a near tie.** The
reranker gap is **47× the semantic gap**, and the final ordering follows it. So
hindsight's embedding layer sees these two revisions as almost the same, and its
**reranker** is what places the superseded one first.

That is a specific, checkable statement about one component of one engine.

## Perseus: the test Sol asked for cannot be run

The brief asked explicitly whether perseus's flip is consistent with tied scores
rather than being filed as generic nondeterminism. **The test cannot be run, and
that is the finding.**

The committed records carry `canonical_id`, `native_id`, `provenance_exact` and
`rank` — **and no score or tie metadata of any kind.** Gen84 measured the same
thing from the other direction: perseus's recall returns no score, which is why no
relevance floor is expressible on it either.

So the flip is recorded as it stands:

| repetition | order |
|---|---|
| 1 | `L009, L010` |
| 2 | `L010, L009` |
| 3 | `L009, L010` |

Same two records every time, two distinct orders. The tie hypothesis is **neither
confirmed nor rejected**. And "generic nondeterminism" is **not asserted** either
— that would name a cause the evidence does not carry.

**Prerequisite for any targeted rerun:** a perseus read path that surfaces per-hit
scores. Gen84 already measured that `recall` returns none, so this is something to
establish *before* scheduling a rerun, not a rerun that can simply be booked.

## What this changes about the nine

They are not one finding. They are:

- **three observations with no observable cause** (perseus) — `NOT_DEMONSTRABLE`,
  pending a scored read path;
- **three ties** (mem0) — the engine does not meaningfully prefer the stale record;
  it barely distinguishes them at all;
- **three genuine ranking preferences** (hindsight) — and localised to the
  reranker, not the embedding.

Only the third is a ranking-quality result in the sense Gen90's label suggested.

## What this does not say

It does not compare the engines' scores with each other; the three verdicts are
three independent within-engine judgements. It does not say mem0's tie would flip
on a rerun — its scores are identical across all three repetitions, and whether a
fresh run would differ is not established here. It does not diagnose hindsight's
reranker beyond locating it. And it does not close the perseus question: it
converts it from an unanswered question into a **named prerequisite**.
