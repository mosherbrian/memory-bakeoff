# Gen81: the boundary is written correctly and ignored at search

Gen80 found that agentmemory's `project` does not separate two configurations
inside one agent. This localises where that boundary disappears. AgentMemory
only, one minimal fixture, no alternative isolation schemes attempted.

## The probe

Two projects, **one fixed `agentId`**, one distinct marker each:

1. write `Alpha marker…` to project A and `Beta marker…` to project B, recording
   the exact request bodies;
2. read the stored records back and check whether `project` survived ingestion;
3. query each project separately and see what returns.

Three outcomes were distinguishable in advance: write-time loss, search-time
ignoring, or both.

## The answer: search-time ignoring

**`project` survives ingestion perfectly.** Every stored record carries a
`project` field with the right value — `gen81-project-a` and `gen81-project-b`
respectively. Write-time is not where the boundary is lost.

**Search ignores it completely.** Querying project A returns *both* markers.
Querying project B returns *both* markers. The same two rows come back
regardless of which project is asked for:

```
QUERY gen81-project-a  ->  "Alpha marker: …project A is 111 units."
                           "Beta marker:  …project B is 222 units."
QUERY gen81-project-b  ->  "Alpha marker: …project A is 111 units."
                           "Beta marker:  …project B is 222 units."
```

A supporting detail: the search hits carry `obsId, score, sessionId, timestamp,
title, type` — **no `project` field at all**. The response is not merely
unfiltered; it is opaque to project. The stored rows have it, the search results
never mention it.

So Gen80's `configuration_collapse` is fully explained: the write path honours
`project`, and `smart-search` neither filters on it nor reports it.

## A probe defect I caught, and how

The first pass reported `NO_CROSSING_OBSERVED` — apparently clean isolation. It
was wrong. I had assumed the search response used `content` and
`sourceObservationIds`; it uses `title`, and returns `sourceObservationIds:
null`. So the detector was comparing blank strings and finding no crossing,
because it could not see anything at all.

That result looked like good news and did not match Gen80, which is what made it
suspect. The fix was to detect crossing by **marker text**, which survives, and
to add an explicit `UNDETERMINED_RESPONSE_OPAQUE` verdict so a future run that
genuinely cannot attribute a hit says so instead of reporting a boundary result
it cannot see. `attribution_possible` is now recorded and asserted.

This is the same failure this programme has caught repeatedly: a clean number
produced by a check that could not fail. It is worth stating that it happened
again, in a probe written specifically to avoid it.

## What this establishes, and what it does not

It establishes **where** the boundary is lost for this interface: at search, not
at write. That makes it a retrieval-filter gap rather than a storage-model gap —
the data needed to filter is present and unused.

It does not establish that agentmemory cannot isolate configurations by any
means. No alternative scheme was tried, by instruction. It also says nothing
about scope isolation, which Gen78 measured working via `agentId`.

## Artifacts

- `results/project_boundary_gen81/boundary.json` - requests, stored records, query results, verdict
- `scripts/run_gen81_project_boundary.py` - the probe, with the opacity guard
- `tests/test_project_boundary_gen81.py` - 8 checks, including that attribution was possible
