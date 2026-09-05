"""`scope-bound-adapters-v1`: bind each engine's own isolation primitive to the scope.

Gen76 found that only Perseus was ever asked to isolate scopes. The other three
adapters bind their namespacing concept to a constant, so a scope violation in
those runs is the harness's, not the product's. Gen77 asks the prior question:
**does each engine have a native primitive that can be bound symmetrically on
write and retrieval?**

Symmetry is the whole test. A primitive that only exists on write cannot isolate
a query, and a filter that only exists on read cannot separate what was stored.
Anything less than both paths is recorded `NO_USABLE_SCOPE_SURFACE` rather than
approximated - inventing a scope the API does not offer would manufacture exactly
the false symmetry this generation exists to avoid.

What the pinned builds actually expose:

- **mem0 2.0.19** - `add(user_id=...)` and `search(filters={"user_id": ...})`.
  A first-class identity on both paths. `agent_id` and `run_id` are also
  available; `user_id` is chosen because the frozen Gen32 adapter already uses it
  as its constant, so binding it per scope changes exactly one thing.
- **hindsight 0.9.2** - `retain(bank_id=...)` and `recall(bank_id=...)`.
  `bank_id` is a **required positional** on both, which is as symmetric as an
  isolation primitive gets.
- **agentmemory 0.9.29** - `/agentmemory/remember` and
  `/agentmemory/smart-search` both accept `agentId` and `project`. `agentId` is
  the candidate. A caveat travels with it: Gen13 measured that `project` alone
  did not isolate, which is a behaviour finding, not an absent surface - whether
  `agentId` isolates is the isolation run's question, not feasibility's.

These mappings are frozen here, before any isolation run. The original Round-2
configurations are untouched and remain the record of what was actually tested.
"""
from __future__ import annotations

import hashlib
from typing import Any

ADAPTER_VERSION = "scope-bound-adapters-v1"

SUPPORTED = "native_primitive_bound_on_both_paths"
UNSUPPORTED = "NO_USABLE_SCOPE_SURFACE"


def scope_token(scope: str) -> str:
    """A stable, collision-resistant identifier derived from the public scope.

    Hashed rather than passed raw so the token carries no fixture wording into a
    store that might match on it textually.
    """
    return hashlib.sha256(scope.encode()).hexdigest()[:32]


# --- mem0 -----------------------------------------------------------------
def mem0_write(scope: str) -> dict[str, Any]:
    return {"user_id": f"scope-{scope_token(scope)}"}


def mem0_query(scope: str) -> dict[str, Any]:
    return {"filters": {"user_id": f"scope-{scope_token(scope)}"}}


# --- hindsight ------------------------------------------------------------
def hindsight_write(scope: str, run: str) -> dict[str, Any]:
    return {"bank_id": f"{run}-scope-{scope_token(scope)}"}


def hindsight_query(scope: str, run: str) -> dict[str, Any]:
    return {"bank_id": f"{run}-scope-{scope_token(scope)}"}


# --- agentmemory ----------------------------------------------------------
def agentmemory_write(scope: str, run: str) -> dict[str, Any]:
    return {"agentId": f"{run}-scope-{scope_token(scope)}"}


def agentmemory_query(scope: str, run: str) -> dict[str, Any]:
    return {"agentId": f"{run}-scope-{scope_token(scope)}"}


BINDINGS = {
    "mem0": {
        "primitive": "user_id",
        "write_call": "Memory.add(user_id=...)",
        "query_call": "Memory.search(filters={'user_id': ...})",
        "status": SUPPORTED,
        "write": mem0_write,
        "query": mem0_query,
        "note": "frozen Gen32 adapter binds user_id to a constant; this binds it "
                "per scope and changes nothing else",
    },
    "hindsight": {
        "primitive": "bank_id",
        "write_call": "Hindsight.retain(bank_id=...)",
        "query_call": "Hindsight.recall(bank_id=...)",
        "status": SUPPORTED,
        "write": hindsight_write,
        "query": hindsight_query,
        "note": "bank_id is a required positional on both calls - the strongest "
                "symmetry of the three",
    },
    "agentmemory": {
        "primitive": "agentId",
        "write_call": "POST /agentmemory/remember {agentId}",
        "query_call": "POST /agentmemory/smart-search {agentId}",
        "status": SUPPORTED,
        "write": agentmemory_write,
        "query": agentmemory_query,
        "note": "both endpoints accept agentId and project; Gen13 measured that "
                "PROJECT alone did not isolate, so agentId is the candidate and "
                "whether it isolates is the isolation run's question",
    },
}


def distinct_coordinates(engine: str, scope_a: str, scope_b: str,
                         run: str = "r1") -> dict[str, Any]:
    """Two scopes must produce different write AND query coordinates."""
    binding = BINDINGS[engine]
    kwargs = {} if engine == "mem0" else {"run": run}
    writes = (binding["write"](scope_a, **kwargs), binding["write"](scope_b, **kwargs))
    queries = (binding["query"](scope_a, **kwargs), binding["query"](scope_b, **kwargs))
    return {
        "engine": engine,
        "write_a": writes[0], "write_b": writes[1],
        "query_a": queries[0], "query_b": queries[1],
        "writes_differ": writes[0] != writes[1],
        "queries_differ": queries[0] != queries[1],
        "symmetric": binding["status"] == SUPPORTED,
    }


def contract() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "question": "does each engine have a native isolation primitive bindable "
                    "symmetrically on write and retrieval?",
        "requirement": "both paths, or NO_USABLE_SCOPE_SURFACE; a primitive on one "
                       "path only cannot isolate and will not be approximated",
        "bindings": {name: {k: v for k, v in entry.items()
                            if k not in ("write", "query")}
                     for name, entry in BINDINGS.items()},
        "frozen_before_any_isolation_run": True,
        "original_configurations_untouched": "the Round-2 adapters remain the record "
                                             "of what was actually tested",
        "not_yet_measured": "feasibility only; whether a bound primitive actually "
                            "isolates is the next generation's question",
    }
