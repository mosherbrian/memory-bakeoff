# Gen98 — Interference Generalization Fixture

**Fixture:** `interference-v2` · **Scorer:** `interference-scorer-v1`, unchanged
**No engine runs.** 4 independent semantic cores, 268 observations, 16 cases.
Fixture and contract both hashed **before** any product sees them.

## Why this exists

Gen97 produced four clean curves — Perseus's target sliding out at 64 distractors,
three engines holding rank, stale-version interference everywhere, hindsight
returning the whole bank. **Every one of those could be a property of one
semantic neighbourhood rather than of the engines.**

`interference-v2` is the replication. Four independent cores — a throughput
figure, a release branch, an on-call rota, a storage allocation — each with its
own subject, metric and sentence family.

**What is held identical inside every core:** four load levels (0/4/16/64), the
same current-versus-superseded structure, its own scope and configuration with a
foreign record differing on **both** axes, and the same retrieval policy.

**What varies between cores:** the subject and its wording, and nothing else.
That is the replication factor.

## The questions are declared before the data exists

Written into the contract and hashed with the fixture, so which pattern counts as
replicated cannot be decided once the numbers arrive:

**Q1 — does Perseus's target rank decline with density in every core?**
Gen97 saw rank 2 → 3/4 → 5 → absent, in one core. Replicated if the rank is
monotonically non-improving with load in **every** core and the target is lost at
the top level in **every** core. Fixture-specific if it holds in one only.

**Q2 — does stale-version interference recur across cores and loads?**
Gen97 saw 48 of 48, in one core. Replicated if it appears at every load level of
every core for every engine. Fixture-specific if any core is free of it.

**Q3 — do mem0, agentmemory and hindsight keep their Gen97 shapes?**
Flat at rank 2, flat at rank 1, and flat at rank 2 with unbounded volume.
Replicated if each engine's rank is constant across loads in every core, at the
rank Gen97 recorded.

## Cores replicate; they never pool

`assert_no_core_pooling` raises on "mean across cores", "pooled across", "all
cores combined" or "core mean". A pattern either **recurs in each core** or it is
`FIXTURE_SPECIFIC` — a property of that neighbourhood, not of the engine. The
verdict rule is mechanical: all cores → `REPLICATED_ACROSS_CORES`; one core →
`FIXTURE_SPECIFIC`; in between → `PARTIAL_REPLICATION`.

## Every mechanism still fires — in every core

Reachability is not inherited from Gen95. Controls are driven **per core**, and
all of them fire in all four, with the clean control silent in each. A class that
fired in one neighbourhood and not another would make replication
uninterpretable before it began.

## A cross-core bleed the tests caught

The v1 `visible_ids` helper takes every non-distractor record plus the first
`load` distractors **globally**. Across four cores that ingests **another
neighbourhood's records** into every case — 12 core records instead of 3, and
distractors from whichever core happened to sort first.

Cross-core bleed would have destroyed the entire point of the replication: four
"independent" cores all seeing each other. The structural test — *does every load
level hold exactly its own records?* — failed, and `interference_v2.visible_ids`
is now core-aware. A second test asserts directly that **no case ever sees another
core's records**.

The frozen fixture is the corrected one; nothing has been run against either.

## What this generation does not do

It does not run anything. The point of writing the questions and the verdict rule
first is that the run cannot then be read to suit them.
