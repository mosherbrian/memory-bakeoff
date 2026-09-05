# Gen90 — Current-Truth Window Ablation

**Contract:** `current-truth-window-ablation-gen90-v1`
**No engine runs.** 48 observations: 4 cases × 4 engines × 3 repetitions, each
replayed through fixed prefix windows k=1…5.

## What was done, and what was not

Gen89 found that the current fact is almost always retrieved and that the
dominant failure is its superseded version coming back alongside it — often
because the harness asked for five results. This measures that directly.

**The transform is `returned[:k]` and nothing else.** No hidden-label-aware
stopping, no deduplication, no reader reasoning, no semantic post-filter, no
reordering. A guard asserts every window is a genuine prefix of the engine's own
ranked result, so any improvement is attributable to window policy alone.

**No k is selected.** Picking the best-scoring window would be tuning the harness
against the data it is scoring — the exact failure this programme keeps finding
elsewhere. The curve is the result.

**Repetitions are not pooled**, so rank instability stays visible. That decision
turns out to matter.

## The curve

Clean observations at each window, out of 48:

| k | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| clean | 31 | **35** | 24 | 24 | 24 |

**The curve is not monotonic, and both directions cost something.**

Going from k=5 to k=2 recovers 11 observations — those are the stale records
swept in by a five-wide window. Going from k=2 to k=1 **loses four**, because for
three engines the current fact sits at rank 2 behind the record announcing the
change. A narrow window is not free: **at k=1 the current fact is lost outright
in 17 of 48 observations.**

Truncation never breaks a result that was already clean — 0 of 24.

## The two outcomes

| verdict | count |
|---|---|
| already clean at the full window | 24 |
| **window policy** — some prefix scores clean | **15** |
| **ranking failure** — no prefix can succeed | **9** |

**15 of the 24 failures are the harness asking for five results.** They vanish
under a narrower window without any change to the engine.

**9 are real.** The stale record outranks the current one, so truncation cannot
help: cut above the stale record and the current fact goes with it. These are the
genuine retrieval-ranking problem in the whole `current_truth` row.

They are concentrated: **perseus 3, mem0 3, hindsight 3, agentmemory 0.** Eight of
the nine are `LQ11`, where the superseded branch record outranks its replacement.

## Perseus's rank instability flips a verdict

This is why repetitions were not pooled.

On `LQ11`, perseus returns the same two records every time and orders them
differently:

| repetition | order | verdict |
|---|---|---|
| 1 | `L009, L010` | ranking failure |
| 2 | `L010, L009` | **window policy** — clean at k=1 |
| 3 | `L009, L010` | ranking failure |

Same query, same store, same configuration — and whether the failure is fixable by
window policy or is a genuine ranking defect **depends on which repetition you
look at**. Pooling would have averaged that away into a single misleading verdict.

Gen89 noted this instability and correctly said it changed no score, because that
scorer ignores rank. Under an ablation that is *about* rank, it changes the
verdict. The observation was right; its consequence only appears here.

## What this establishes

The `current_truth` row splits cleanly into three parts:

1. **Half the observations were never failing** (24 of 48).
2. **Most of the rest is window policy** (15) — a harness/configuration result,
   not an engine result.
3. **A small, real retrieval-ranking problem remains** (9), on one engine-case
   combination that no window can rescue, absent from agentmemory entirely.

## What this does not say

It does not recommend a window. The curve peaks at k=2 on this fixture, with four
cases and 48 observations — that is a property of this data, and adopting it as
policy would be fitting the harness to its own results.

It does not say the nine ranking failures are equivalent across engines: eight are
one case, and perseus's are not even stable across repetitions of itself.

And it does not extend beyond the four pure cases. The other three
`current_truth` cases are failed by a configuration, temporal or abstention
distinction (Gen89) and are not in this ablation.
