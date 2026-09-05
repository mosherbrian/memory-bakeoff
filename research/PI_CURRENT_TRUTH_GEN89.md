# Gen89 — Current-Truth Failure Decomposition

**Contract:** `current-truth-decomposition-gen89-v1`
**No engine runs.** 84 committed observations re-read: 7 cases × 4 engines × 3
repetitions.

## The row being examined

`current_truth` is the plainest question the benchmark asks — *what is true now?* —
and the last foundational Round-2 row never given the treatment that dissolved the
others. Its pooled counts were **6/21, 6/21, 6/21 and 9/21**, and pooling is
exactly what hides a mechanism.

## Controls first

Every contributing class fires, and the case can stay silent:

| returned | classes |
|---|---|
| the current record alone | *(clean)* |
| current + its superseded predecessor | `stale_persistence` |
| the predecessor alone | `stale_persistence` + `missing_required_truth` |
| nothing | `missing_required_truth` |

And a property that shapes everything below: **the scorer ignores rank.** Current
first and stale first score identically.

## The decomposition

84 observations, by mechanism:

| mechanism | count |
|---|---|
| clean | 27 |
| **retrieval-window effect** | **21** |
| conflicting versions co-returned | 15 |
| stale returned, current absent | 9 |
| NOT_DEMONSTRABLE (abstention required) | 12 |
| **missing current fact** | **0** |

### The current fact was never simply lost

`missing_current_fact` is a reachable class — the control fires it — and it
**occurred zero times in 84 observations**. In **63 of the 72 scoreable
observations the present truth was returned.** No engine, in any repetition, ever
just failed to find what was true now.

### Most failures are co-return, not loss

Of the 36 failures where both versions came back, **21 are window effects**: the
current fact **outranks** every prohibited record, so a window tight enough to
exclude the old version still contains the new one. Each such row names the limit
that would pass — a limit of *N*, not necessarily 1.

The remaining 15 are genuine ranking failures: the superseded record outranks the
current one, and no window can separate them.

So the honest statement about this row is **"finds what is true now, and hands you
the version it replaced alongside it"** — and for well over half of those, only
because the window was five records wide.

Per case, at repetition 1:

| case | perseus | mem0 | hindsight | agentmemory |
|---|---|---|---|---|
| LQ01 | clean | clean | clean | clean |
| LQ17 | clean | clean | clean | clean |
| LQ02 | window | ranking | window | clean |
| LQ11 | ranking | ranking | ranking | window |
| LQ12 | ranking | stale only | stale only | stale only |
| LQ14 | ranking | window | window | window |
| LQ15 | NOT_DEMONSTRABLE | NOT_DEMONSTRABLE | NOT_DEMONSTRABLE | NOT_DEMONSTRABLE |

## Three of seven cases are failed by another layer

Asked before any of the above: does each `current` case actually test only present
truth?

- **`LQ02`** — the prohibited record differs by **configuration**, and the scorer
  charges `configuration_collapse` inside a current-truth row. Gen80 measured
  configuration isolation as its own bindable axis; this cell belongs there.
- **`LQ12`** — prohibits a `historical_only` record and charges
  `late_history_corruption`, a **temporal** class, inside a current-truth row.
- **`LQ15`** — expects the **empty set**. It can only be passed by returning
  nothing, and Gen84 established that no retrieval surface here can express
  abstention. This is the same structure as `LQ16`.

Those twelve `LQ15` cells are **`NOT_DEMONSTRABLE` at this layer, not another
zero**. Only `LQ01`, `LQ11`, `LQ14` and `LQ17` ask purely for present truth.

## A repetition observation worth recording

Perseus is the only engine whose current-truth results vary across repetitions,
and the variation is **rank order only** — the same record set each time,
reordered. Because the scorer ignores rank, no score changes. It is recorded
because it is real, and because it is the same instability Gen86 measured at the
reader layer.

## The pooled counts are retired

**6/21, 6/21, 6/21 and 9/21 are not preserved as meaningful.** They are kept only
as a record of what is being replaced. The row is now reported by mechanism, and
the mechanism is the same for every engine: the current fact is found, and its
predecessor comes back with it.

## What this does not say

It does not say the engines are equivalent here — mem0 and hindsight lose the
current fact on `LQ12` where perseus keeps it, and 15 genuine ranking failures
remain. It does not say a tighter window is a fix; a limit of 1 would have failed
`LQ14` outright for three engines, whose current fact sits at rank 2. And it does
not close the row: what it establishes is that the mechanism is co-return and
ranking, not retrieval loss, so the next question about `current_truth` is a
question about ranking and window policy.
