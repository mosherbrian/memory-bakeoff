# Gen95 — Round-3 Interference / Scale Ruler Design

**Fixture:** `interference-v1` · **Scorer:** `interference-scorer-v1`
**No engine runs.** The ruler is built, frozen and demonstrated **before any
product sees the fixture**.

## The question Round 3 asks

Round 2 asked what these systems remember. Round 3 asks the harder one: **what
happens when the store contains many plausible distractors and competing
memories?** Retrieval quality is not a property of a store alone — it is a
property of a store at a given density of things that look like the answer.

## Scale is the only independent variable

Every load level is generated from **one semantic core**: the same subject, the
same metric, the same sentence shape. Levels **0, 4, 16 and 64** distractors sit
between the query and its answer, and *nothing else changes* — same query, same
scope, same configuration, same target record.

A level that varied the vocabulary as well would confound density with
difficulty, and the resulting curve would be uninterpretable.

67 observations, 4 cases, `fixture_sha256` recorded.

## Five mechanisms, and the pair that matters

| mechanism | meaning |
|---|---|
| **`true_forgetting`** | the current fact is absent **and the window was not filled** by same-core competitors |
| **`distractor_displacement`** | the current fact is absent **and the window is saturated** with same-core distractors |
| `stale_version_interference` | the superseded version came back |
| `cross_scope_contamination` | a record from another scope **and** configuration came back |
| `retrieval_window_effect` | the current fact is present and **outranks** every prohibited record |

**The first two are the point.** In any pooled count they are the same
observation — "the answer was missing". They are completely different problems:
one is a store that lost the record, the other is a store that kept it and let
sixty-four near-misses crowd it out. Gen89 taught this the hard way on a row where
the answer was never lost at all.

## Every class is proved reachable, first

Synthetic controls drive each mechanism deliberately. All five fire; the clean
control is silent:

| control | mechanisms |
|---|---|
| the current record alone | *(clean)* |
| one distractor, window not full | `true_forgetting` |
| five distractors, window full | `distractor_displacement` |
| current + superseded | `stale_version_interference`, `retrieval_window_effect` |
| current + foreign record | `cross_scope_contamination`, `retrieval_window_effect` |

And two controls prove the discriminations are real rather than incidental:

- **stale record first** → `stale_version_interference` **without** the window
  effect. The window effect measures rank, not membership.
- **two distractors, window with room to spare** → `true_forgetting`, **not**
  displacement. Displacement requires saturation.

## The four Round-2 rules, built in rather than remembered

**1 — Reachability before interpretation.** Every class fires under a control
before a product is involved. A class that cannot fire reports a zero that means
nothing, and Round 2 found four of those.

**2 — Fair scope and configuration bindings from the start.** Every observation
carries both, and the contract requires the adapter to bind both on write and
query. Round 2 spent five generations discovering that three adapters were never
given a scope to honour; that will not be rediscovered here. The foreign record
differs on **both** axes, so contamination cannot be confused with a
single-axis leak.

**3 — Retrieval and reader layers stay apart.** Every case is answerable by a
store. No case asks for a judgement, and none can be passed only by returning
nothing — the two shapes that turned out to be reader questions in Round 2. A test
asserts every case has an expected record.

**4 — No pooled score.** `score_case` returns mechanisms, never a mark, and
`assert_no_pooled_accuracy` **raises** on "accuracy at scale", "overall accuracy",
"pooled score" or "mean accuracy". A test feeds it four such phrasings. There will
be no single number for Round 3 until the mechanisms are decomposed.

Per-case rank, provenance, saturation state and the distractors actually returned
are all recorded on every result.

## What this generation deliberately does not do

It does not run anything. No product has seen this fixture, no adapter has been
written against it, and no result exists. That is the design: Round 2's most
expensive lesson was that a ruler validated *after* the fact cannot tell you which
of its zeros were real.
