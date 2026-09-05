"""`agentmemory-configuration-surface-v1`: is there a second identity to bind at all?

Gen80 found agentmemory's `project` does not separate configurations. Gen81
localised it: `project` is stored correctly and ignored by `smart-search`. Gen82
asks the closing question - does the pinned build expose **any other** native
retrieval filter, independent of `agentId`, that can carry a second identity
**symmetrically** on write and search?

Symmetry is again the whole test. A filter accepted only at search cannot label
what was stored; a field accepted only at write cannot be queried. Either way it
cannot isolate, and approximating one would manufacture the false symmetry this
programme has spent six generations removing.

Read from the pinned source, not from documentation:

- `/agentmemory/smart-search` whitelists exactly
  `query, expandIds, limit, project, includeLessons, agentId, sessionId, source`.
- `/agentmemory/remember` whitelists exactly
  `content, type, concepts, files, ttlDays, sourceObservationIds, project,
  agentId`.
- the MCP `remember` tool exposes only `project` and `agentId`, and sets
  `sessionIds: []`.

Cross the two lists and every candidate fails:

- **`agentId`** - symmetric and working, but already carrying scope (Gen78). Using
  it for configuration too would collapse the two axes into one.
- **`project`** - symmetric on paper, and Gen81 measured search ignoring it.
- **`sessionId`** - accepted at **search only**. No write path sets it; MCP
  hardcodes it empty. Asymmetric.
- **`type`, `concepts`, `files`, `ttlDays`** - write only. Not search filters.
- **`expandIds`, `includeLessons`, `limit`, `source`** - search only, and not
  identity filters in any case.

That exhausts both surfaces, so configuration isolation closes for this
interface as `NO_USABLE_SECOND_SURFACE`.
"""
from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "agentmemory-configuration-surface-v1"
NO_SECOND_SURFACE = "NO_USABLE_SECOND_SURFACE"

SEARCH_ACCEPTS = ("query", "expandIds", "limit", "project", "includeLessons",
                  "agentId", "sessionId", "source")
WRITE_ACCEPTS = ("content", "type", "concepts", "files", "ttlDays",
                 "sourceObservationIds", "project", "agentId")
MCP_WRITE_ACCEPTS = ("project", "agentId")

CANDIDATES = {
    "agentId": {
        "symmetric": True,
        "usable_as_second_identity": False,
        "why": "symmetric and working, but already carries scope (Gen78); reusing "
               "it would collapse the two axes into one",
    },
    "project": {
        "symmetric": True,
        "usable_as_second_identity": False,
        "why": "symmetric on paper; Gen81 measured smart-search ignoring it "
               "entirely, and the search response never mentions it",
    },
    "sessionId": {
        "symmetric": False,
        "usable_as_second_identity": False,
        "why": "accepted at search only; no write path sets it and the MCP tool "
               "hardcodes sessionIds to empty",
    },
    "type": {"symmetric": False, "usable_as_second_identity": False,
             "why": "write only; not a search filter"},
    "concepts": {"symmetric": False, "usable_as_second_identity": False,
                 "why": "write only; not a search filter"},
    "files": {"symmetric": False, "usable_as_second_identity": False,
              "why": "write only; not a search filter"},
    "ttlDays": {"symmetric": False, "usable_as_second_identity": False,
                "why": "write only, and a lifetime rather than an identity"},
}


def symmetric_fields() -> set[str]:
    """Fields the pinned build accepts on both paths."""
    return set(SEARCH_ACCEPTS) & set(WRITE_ACCEPTS)


def verdict() -> dict[str, Any]:
    usable = [name for name, entry in CANDIDATES.items()
              if entry["usable_as_second_identity"]]
    return {
        "contract_version": CONTRACT_VERSION,
        "surfaces_examined": ["REST /agentmemory/remember",
                              "REST /agentmemory/smart-search",
                              "MCP remember tool"],
        "search_accepts": list(SEARCH_ACCEPTS),
        "write_accepts": list(WRITE_ACCEPTS),
        "mcp_write_accepts": list(MCP_WRITE_ACCEPTS),
        "symmetric_fields": sorted(symmetric_fields()),
        "candidates": CANDIDATES,
        "usable_second_identity": usable,
        "verdict": NO_SECOND_SURFACE if not usable else "SECOND_SURFACE_AVAILABLE",
        "scope_axis_unaffected": "agentId still isolates scope; Gen78 stands",
        "bounded_to": "the pinned agentmemory 0.9.29 build and the surfaces listed; "
                      "not a claim about the product in general",
        "no_engine_run": True,
    }
