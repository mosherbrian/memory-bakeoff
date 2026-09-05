# Gen78: every engine isolates scopes once it is actually asked

Gen76 found that only Perseus was ever given a scope filter. Gen77 established
that the other three each have a native isolation primitive bindable on both
write and retrieval, and froze those mappings. Gen78 runs the ablation.

**One variable moves:** the frozen Gen77 binding replaces the constant namespace
the Round-2 adapter used. Nothing else changes. Perseus is not rerun — its
scope-bound cases were already measured in Gen68.

## The result

Two genuinely cross-scope cases, three repetitions, six case-runs per engine:

| engine | original Round-2 configuration | with its native scope binding |
|---|---|---|
| perseus | 0 of 6 collapse, 6 clean | reused, not rerun |
| **mem0** | **6 of 6 collapse** | **0 of 6** |
| **hindsight** | **6 of 6 collapse** | **0 of 6** |
| **agentmemory** | **6 of 6 collapse** | **0 of 6** |

**Every engine isolates scopes correctly when given its own primitive.** The
failure was total before and is absent after, on all three, in every repetition.

## The cleanliness is real, not empty

An empty answer also avoids `scope_collapse`, so that was checked rather than
assumed, and is asserted in tests:

- each case returns the observation it asked for — `L003` for the forge query,
  `L006` for the anvil query;
- the foreign scope's observation never appears in either;
- the two scopes received **different** bound identities within each run, so a
  clean result cannot come from both queries hitting one partition.

For example mem0's forge query returns `L001, L002, L003, L004, L005` — all
forge — and its anvil query returns `L006` alone.

## What this retracts

Gen68 reported scope truth as Perseus 6 of 9 clean and the other three 0 of 9,
and it read as a capability difference. It was not. **It was a configuration
difference**, and the second Gen68 headline to fall to the same error as the
temporal one: an adapter decision read as a fact about a product.

`agentmemory` is the sharpest case. Its frozen adapter records that
*"smart-search does not isolate by project anyway"* — a true Gen13 measurement
about `project`. Bound to `agentId` instead, it isolates perfectly. The original
note was right about the parameter it tested and wrong as a statement about the
product.

## What this does not establish

- **Not a ranking.** All four now behave identically on this axis; there is
  nothing to order.
- **Nothing about same-scope configuration.** `LQ03` — same scope, different
  configuration — was deliberately excluded, because Gen77 froze mappings for
  scope and not for configuration, and including it would move two variables at
  once. `configuration_collapse` remains untested under the new bindings.
- **Nothing about the original configurations' users.** Gen76's finding stands:
  those configurations do collapse scopes, and that is what someone running them
  would experience.

## A runner defect I caught and fixed before reporting

The first mem0 run ingested the whole timeline before querying, which charged
`future_leakage` on the forge case — Gen70's over-ingestion, imported by accident
into a run that had nothing to do with it. Ingestion is now limited to the
queried checkpoint's prefix, asserted in the result file and in a test. The
figures above are all post-fix.

## Artifacts

- `results/scope_isolation_gen78/{mem0,hindsight,agentmemory}.json` - every case run
- `scripts/run_gen78_scope_isolation.py` - mem0 and agentmemory, prefix-limited
- `scripts/run_gen78_hindsight.sh`, `scripts/gen78_hindsight_repetition.py` - per-scope banks
- `tests/test_scope_isolation_gen78.py` - 23 checks, including that cleanliness is not emptiness
