# Gen77: all three engines have a native scope primitive, and it is bindable

Gen76 found that only Perseus was ever asked to isolate scopes. Before any
comparison, Gen77 asks whether the other three *can* be asked — whether each
pinned build exposes a native isolation primitive bindable **symmetrically on
write and retrieval**. No engine was run.

## Symmetry is the whole test

A primitive that exists only on write cannot isolate a query. A filter that
exists only on read cannot separate what was stored. Anything less than both
paths is recorded `NO_USABLE_SCOPE_SURFACE` rather than approximated —
manufacturing a scope the API does not offer would create exactly the false
symmetry this generation exists to prevent.

## What the pinned builds actually expose

| engine | primitive | write call | query call | status |
|---|---|---|---|---|
| **mem0** 2.0.19 | `user_id` | `add(user_id=…)` | `search(filters={"user_id": …})` | supported |
| **hindsight** 0.9.2 | `bank_id` | `retain(bank_id=…)` | `recall(bank_id=…)` | supported |
| **agentmemory** 0.9.29 | `agentId` | `POST /remember {agentId}` | `POST /smart-search {agentId}` | supported |

Read from the installed signatures, not from documentation:

- mem0's `add` takes `user_id`, `agent_id` and `run_id`; `search` takes
  `filters`. **`user_id` is chosen because the frozen Gen32 adapter already binds
  it to a constant** — binding it per scope changes exactly one thing.
- hindsight's `bank_id` is a **required positional on both** `retain` and
  `recall`. That is the strongest symmetry of the three.
- agentmemory's `smart-search` payload accepts `agentId` and `project`, as does
  `remember`.

**No engine needed `NO_USABLE_SCOPE_SURFACE`.** That was a real possible outcome
and I would have recorded it; it simply did not arise.

## The caveat that travels with agentmemory

The frozen adapter says *"smart-search does not isolate by project anyway"* —
a Gen13 measurement. That is a **behaviour** finding, not an absent surface, and
it applies to `project`, not `agentId`. So `agentId` is the candidate, and
whether it actually isolates is the isolation run's question rather than
feasibility's. Recording it as feasible is not a prediction that it will work.

## Proved before any isolation run

16 deterministic tests, all passing:

- two scopes produce **distinct write and distinct query coordinates**, for every
  engine;
- the same scope produces **stable** coordinates across calls — a key that drifts
  between write and query isolates nothing;
- write and query carry the **same scope token**, which is symmetry asserted
  rather than described;
- hindsight and agentmemory bindings are **run-scoped**, so repetitions cannot
  share a bank or agent and leak scopes across runs;
- the scope token is hashed, carrying **no fixture wording** into a store that
  might match on it textually.

## What is frozen, and what is untouched

The three mappings are frozen here, before any isolation run. The original
Round-2 adapters are untouched and remain the record of what was actually tested
— Gen76's finding that those configurations collapse scopes stands unchanged.

## What this does not establish

Nothing about whether any engine isolates. This is feasibility: the question can
now be asked fairly of all four. Whether the answers differ is the next
generation's work, and the smallest legitimate comparison is now possible instead
of one manufactured from APIs that do not support it.

## Artifacts

- `src/memory_bakeoff/providers/scope_bound.py` - the three bindings and their contract
- `tests/test_scope_bound.py` - 16 symmetry and stability proofs
