# Gen93 — Current-Truth Retrieval Closure

**Contract:** `current-truth-closure-gen93-v1`
**No engine runs.** Gen89–92 frozen; the pooled row replaced by what was measured.

## What the row said, and what it says now

Round 2 reported `current_truth` as **6/21, 6/21, 6/21 and 9/21** — four systems
that mostly cannot say what is true now. Five generations of audit have replaced
that with a mechanism, and the old counts are **not restated in any form**. A test
asserts they appear nowhere in the rebuilt row.

**The current fact was never simply lost.** `missing_current_fact` is a reachable
class — a control fires it — and it occurred **zero times in 84 observations**
(Gen89).

On the four cases that ask purely for present truth, across four engines and
three repetitions — **48 observations**:

| | count |
|---|---|
| already clean | **24** |
| attributable to **retrieval-window policy** | **15** |
| no prefix can succeed | **9** |

The 15 are a harness result, not an engine result: the current fact outranks its
predecessor, and a narrower window would have passed without touching any engine.

## The nine, split one way per engine

| engine | count | status |
|---|---|---|
| hindsight | 3 | **demonstrated ranking defect** |
| mem0 | 3 | unresolved ordering of effectively tied revisions |
| perseus | 3 | not diagnosable through the measured surface |
| agentmemory | **0** | none |

**Only hindsight's residue is a demonstrated ranking-quality defect.** A real
preference for the stale revision, localised to the reranker: keyword identical,
semantic gap 0.001655, reranker gap 0.078265 (Gen91).

**mem0's is not a preference at all.** The two revisions are separated by 1.2% of
the distance to the next record in the same list. The engine barely distinguishes
them; the order is decided in the noise (Gen91).

**Perseus cannot be diagnosed through the surface that was measured.** No read on
the pinned build returns per-hit relevance scores while preserving the Round-2
retrieval semantics, and the product refuses the scored trace on that mode. That
is a product constraint, not an adapter omission (Gen92).

**agentmemory had no irreducible ranking failure on this row at all.**

## Two things this closure deliberately protects

**Perseus's repetition instability is preserved, not averaged.** The same query
against the same store returns the same two records in different orders:

| repetition | order | verdict |
|---|---|---|
| 1 | `L009, L010` | no-prefix ranking failure |
| 2 | `L010, L009` | window policy, clean at k=1 |
| 3 | `L009, L010` | no-prefix ranking failure |

The flip changes the **verdict**, not just the order. Pooling the repetitions
would have produced one confident wrong answer.

**The k=2 peak is not a recommendation, and a guard enforces it.** The curve —
31, 35, 24, 24, 24 — peaks at k=2 on four cases and 48 observations. That is a
property of this fixture. `assert_not_a_recommendation` **raises** on any
prescriptive phrasing of it, because "k=2 scored best" is exactly the sentence
that would slip into a summary and become a setting. And a narrower window is not
free: at k=1 the current fact is lost outright in **17 of 48** observations.

## Not in this row

Three of the original seven cases are failed by a distinction that belongs
elsewhere and are excluded (Gen89): `LQ02` by a **configuration** distinction,
`LQ12` by a **late-history** one, and `LQ15` by requiring the **empty set** —
abstention, which no retrieval surface here can express.

## The `current_truth` line is CLOSED

What began as the benchmark's most alarming row ends as its most ordinary one:
these systems retrieve what is true now. They also hand back the version it
replaced, mostly because the harness asked for five results — and beneath that
sits one demonstrated ranking defect, one tie, one thing that cannot be seen, and
one engine with nothing to report.
