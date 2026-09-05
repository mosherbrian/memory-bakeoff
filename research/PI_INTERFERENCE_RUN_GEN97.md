# Gen97 — Round-3 Interference Run

**Fixture:** `interference-v1` (frozen Gen95) · **Scorer:** `interference-scorer-v1`
**Adapters:** Gen96, each engine on its own retrieval budget and strategy.
4 load levels × 3 repetitions × 4 engines. **No tuning after exposure. No
cross-engine total.**

## A probe defect caught before it became a finding

The first hindsight attempt reported **target absent at every load level** — a
dramatic result, and false. Every hit came back **unmapped**: `retain` takes the
document id as an *argument*, and my map was keyed on a fabricated fallback that
matched nothing. The engine returned 66 records at the top level and the probe
could not see a single one of them.

That is the Gen81 shape exactly — a clean-looking number from a check that could
not have seen otherwise. It was caught because "returns everything, contains
nothing" is not a coherent result.

**The runner now refuses to score a reply where hits came back and none of them
mapped.** It raises rather than recording "target absent".

## The four curves

Every point below is **identical across all three repetitions** unless stated.

### perseus — degrades, then loses the target

| load | target | rank | returned |
|---|---|---|---|
| 0 | present | 2 | 2 |
| 4 | present | **3 or 4** | 5 |
| 16 | present | 5 | 5 |
| **64** | **absent** | — | 5 |

The only engine that loses the target. It slides one rank per level and falls out
of a five-wide window at 64 distractors, scored **`distractor_displacement`** —
the record was in the store and the near-misses crowded it out.

Its rank at load 4 **varies between repetitions** (3 and 4). That is the same
instability Gen90 and Gen91 measured, appearing again on a new fixture.

### mem0 — flat

| load | target | rank | returned |
|---|---|---|---|
| 0 → 64 | present | **2 at every level** | 2, then 5 |

Sixty-four same-core near-misses do not move it. They fill the slots *below* the
target.

### agentmemory — flat, and first

| load | target | rank | returned |
|---|---|---|---|
| 0 → 64 | present | **1 at every level** | 2, then 3 |

The only engine that ranks the current fact **above** its superseded version, at
every load level — which is why `retrieval_window_effect` fires: a narrower window
would still hold the answer. It also returns only 3 records at 64 distractors.

### hindsight — flat rank, unbounded volume

| load | target | rank | returned |
|---|---|---|---|
| 0 | present | 2 | 2 |
| 4 | present | 2 | 6 |
| 16 | present | 2 | 18 |
| **64** | present | 2 | **66** |

The target holds at rank 2 throughout. But hindsight has **no result-count
window** (Gen96), and at 64 distractors it returns **66 records — essentially the
entire bank**. A caller gets the right answer and sixty-five near-misses with it.

**Forgetting versus displacement is `NOT_DEMONSTRABLE` for hindsight**, as
instructed: saturation is not a statement about an engine bounded by tokens. Here
the question does not arise — the target was never absent — but the attribution
rule stands for any future level where it is.

## Two findings that hold across every engine

**Stale-version interference is universal: 48 of 48 observations.** Every engine,
every load level, every repetition returned the superseded record alongside the
current one. And on three of the four it **outranks** the current one. Round 2
found this on one case; it reproduces here on a different fixture at every
density.

**Cross-scope contamination never occurred — 0 of 48.** The foreign record differs
in both scope and configuration, and no engine returned it at any level. The
Gen96 bindings held, on all four engines, at every density.

## What this does not say

**There is no cross-engine total, and there cannot be one.** Three engines are
bounded by a result count and hindsight by a token budget (Gen96); a shared window
is not a shared quantity. `assert_within_engine_only` enforces it — and fired
during this generation on a key of mine named `no_cross_engine_total`. It was a
disclaimer rather than a total, but the check matches names and was right to be
strict; **the naming changed, not the check.**

It does not say perseus is worse. It says perseus's ranking of the target
*declines with density* on this fixture while the other three hold — one fixture,
one query, one semantic core, at four densities. Whether that generalises is the
next question, not this one's answer.

And it does not explain *why* the superseded record competes so well. That is a
ranking-quality question, and Round 2 established that only hindsight's version of
it can currently be localised.
