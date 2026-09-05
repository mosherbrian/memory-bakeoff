# Gen82: the configuration axis closes for this interface

Gen80 found agentmemory's `project` does not separate configurations. Gen81
localised it — `project` is stored correctly and ignored at search. Gen82 asks
the closing question: does the pinned build expose **any other** native retrieval
filter, independent of `agentId`, that could carry a second identity
**symmetrically**? No engine was run.

## What the pinned build actually accepts

Read from source, not documentation:

- `/agentmemory/smart-search` whitelists exactly `query, expandIds, limit,
  project, includeLessons, agentId, sessionId, source`.
- `/agentmemory/remember` whitelists exactly `content, type, concepts, files,
  ttlDays, sourceObservationIds, project, agentId`.
- the MCP `remember` tool exposes only `project` and `agentId`, and sets
  `sessionIds: []`.

**Exactly two fields appear on both paths: `agentId` and `project`.**

## Every candidate, and why each fails

| candidate | symmetric | usable | why |
|---|---|---|---|
| `agentId` | yes | **no** | already carries scope (Gen78); reusing it collapses the two axes into one |
| `project` | yes | **no** | Gen81 measured search ignoring it entirely |
| `sessionId` | **no** | no | accepted at **search only**; no write path sets it, MCP hardcodes it empty |
| `type`, `concepts`, `files` | no | no | write only; not search filters |
| `ttlDays` | no | no | write only, and a lifetime rather than an identity |
| `expandIds`, `includeLessons`, `limit`, `source` | — | no | search only, and not identity filters |

`sessionId` is the near miss worth naming: it is exactly the kind of second
identity this axis needs, and it is **queryable but not writable**. A filter you
cannot set at write time cannot separate what was stored.

## Verdict: `NO_USABLE_SECOND_SURFACE`

Configuration isolation closes for this interface. Not because the idea failed,
but because the pinned build offers no second identity that both paths accept.

Symmetry was the test throughout, and it mattered: approximating a one-sided
field would have manufactured exactly the false symmetry that Gen76–79 spent four
generations removing. It would have produced a number, and the number would have
meant nothing.

## What stays intact

- **Scope isolation is unaffected.** `agentId` isolates scopes correctly and
  Gen78 stands unchanged.
- **The other three engines are unaffected.** perseus (`category`), mem0
  (`agent_id`) and hindsight (`tags`) each separate configurations cleanly —
  Gen80.
- **This is bounded to the pinned agentmemory 0.9.29 build and the three surfaces
  examined.** It is not a claim about the product in general; a later release, or
  a surface not exposed here, could carry a writable second identity.

## The shape of the conclusion

Three generations produced a properly narrow result: agentmemory separates
scopes and does not separate configurations within one, because its only
symmetric second field is ignored by search and its only other candidate cannot
be written. That is a specific, checkable limitation of an interface — not a
verdict on a product, and not a ranking.

## Artifacts

- `results/agentmemory_surface_gen82/surface.json` - both whitelists, every candidate, the verdict
- `src/memory_bakeoff/providers/agentmemory_surface.py` - the surface audit
- `tests/test_agentmemory_surface_gen82.py` - 9 checks, including that no one-sided field is accepted
