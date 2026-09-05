# Gen99 — Interference Replication Run

**Fixture:** `interference-v2` (frozen Gen98) · **Scorer:** unchanged
**Adapters:** Gen96, unchanged. 4 cores × 4 loads × 3 repetitions × 4 engines.
**No tuning. No core pooling. No cross-engine total.** The Q1–Q3 verdict rules were
frozen before any of this ran and are applied, not rewritten.

## The verdicts

### Q1 — does Perseus's rank decline with density? **`FIXTURE_SPECIFIC`**

| core | holds |
|---|---|
| throughput:atlas | **yes** |
| branch:vega | no |
| oncall:kestrel | no |
| budget:solstice | no |

**Gen97's headline does not generalise.** Perseus loses the target in the atlas
core — the one Gen97 used — and **keeps it at every level in all three other
cores**, including 64 distractors:

- vega: ranks 1/2 → 3 → 3 → **2**
- solstice: 1/2 at every level
- kestrel: 2 at every level

The declining curve was a property of that vocabulary, not of the engine. This is
exactly what the replication was built to find out, and the frozen rule says so
without argument.

### Q2 — does stale-version interference recur? **`REPLICATED_ACROSS_CORES`**

Every engine, every core, every load level, every repetition — **192 of 192**. The
superseded record comes back alongside the current one everywhere, and the
Gen97 finding is now a general property rather than a single observation.

This is the one result of Round 3 so far that has earned the word "general".

### Q3 — do the other three hold their Gen97 shapes? **`PARTIAL_REPLICATION`**, all three

None holds its Gen97 rank everywhere, and they fail in different places — mem0 and hindsight in three of four cores, agentmemory in only two:

| engine | Gen97 rank | holds in | fails in |
|---|---|---|---|
| mem0 | 2 | atlas, kestrel, solstice | vega (rank **1**) |
| agentmemory | 1 | atlas, vega | kestrel, solstice (rank **2**) |
| hindsight | 2 | atlas, kestrel, solstice | vega (2 → 9 → **43**) |

**The exact rank is neighbourhood-dependent; the presence of the target mostly is
not.** mem0 does *better* in vega than Gen97 predicted. Hindsight degrades sharply
in vega — rank 43 of 66 returned records at the top load — while holding rank 2 in
the other three.

## The finding the replication uncovered

**AgentMemory cannot retrieve the current fact at all in the kestrel core — at
zero distractors.**

With three records in the store and nothing competing, it returns **one** record:
the superseded version. Scored `true_forgetting`, which is precisely the class the
fixture separates from displacement. At higher loads it becomes displacement
because the window then fills with distractors.

Every hit is provenance-mapped; `unmapped` is 0 at every level. This is not a
probe defect.

The engine that ranked the current fact **first at every level** in Gen97 is the
engine that **never finds it at all** in one of four neighbourhoods. Only the
replication could have surfaced that.

## Two harness defects caught during the run

**A cross-core name collision.** The per-case working names — Perseus's vault
directory, mem0's collection, agentmemory's state dir, hindsight's bank — were
keyed on the load alone. Across four cores, core C1's load-0 case hit core C0's
existing key file, and Perseus refused to overwrite it. Keyed on `case.id` now,
which is unique in both fixtures. The engine refused rather than silently
reusing another core's store, which is the good failure mode.

**The pooling guard flagged its own frozen contract.** `assert_no_core_pooling`
listed the bare phrase `"across cores"`, and Gen98's own frozen Q2 asks whether
interference appears *"across cores and loads"* — descriptive prose, not a pooled
number. The term list is now the **averaging** phrasings only, two more were
added, and the guard is applied to the summary rather than to the contract,
because a contract is not a claim. Every averaging phrasing still raises, asserted
in the tests.

Unlike Gen97's rename, this one is a genuine loosening, and it is recorded as
such: the guard was catching the concept rather than the act.

## What this does not say

It does not say Perseus is fine at density — it says the decline observed in
Gen97 does not recur, on three other cores, and one core is not a rule either
way. It does not rank the engines: four budgets, no shared quantity, no total. And
it does not explain **why** the superseded record competes everywhere; that
remains the open ranking-quality question Round 2 left, now measured across four
neighbourhoods instead of one.
