"""`configuration-bound-adapters-v1`: a second axis, without touching the first.

Gen78 showed every engine isolates scopes once given its own scope key. The
remaining question is narrower: can a system separate **two configurations inside
the same scope**?

The constraint that shapes this module is that the scope key may not be
repurposed. Reusing it would make two configurations look like two scopes, and
the resulting "isolation" would be an artefact of relabelling rather than a
capability. So each engine needs a **second, independent** primitive, present on
both write and retrieval, that leaves the scope coordinate untouched.

What the pinned builds expose, read from the surfaces themselves:

- **perseus 2.23.2** - `category`. The MCP write gate takes
  `body_json, category, key, workspace_hash`; `perseus_vault_recall` takes
  `category` alongside `workspace_hash`. Two independent axes on both paths. The
  frozen Gen29 adapter pins `category` to a constant, so binding it per
  configuration changes exactly one thing and leaves the workspace alone.
- **mem0 2.0.19** - `agent_id`. `_build_filters_and_metadata` treats `user_id`,
  `agent_id` and `run_id` as independent session identifiers, writing them to
  metadata and accepting them as query filters. Gen78 bound `user_id` to scope;
  `agent_id` is free.
- **hindsight 0.9.2** - `tags`. `retain(tags=[...])` and
  `recall(tags=[...], tags_match=...)`. Independent of `bank_id`, which carries
  scope.
- **agentmemory 0.9.29** - `project`. Both `/agentmemory/remember` and
  `/agentmemory/smart-search` accept it alongside `agentId`, which Gen78 bound to
  scope.

**The agentmemory caveat, stated prominently because it is load-bearing.** Gen13
measured that `smart-search` does not isolate by `project`. That is a behaviour
finding about a surface that exists, not an absent surface - the same shape as
the caveat carried into Gen77, which Gen78 then showed was wrong about the
product. Feasibility is about whether the question can be asked symmetrically;
whether the answer is isolation is the run's question. Recording it feasible is
not a prediction.
"""
from __future__ import annotations

import hashlib
from typing import Any

ADAPTER_VERSION = "configuration-bound-adapters-v1"
SUPPORTED = "native_primitive_bound_on_both_paths"
UNSUPPORTED = "NO_USABLE_CONFIGURATION_SURFACE"


def configuration_token(configuration: str) -> str:
    """Hashed, so no fixture wording enters a store that might match it textually."""
    return hashlib.sha256(f"config::{configuration}".encode()).hexdigest()[:32]


def perseus_write(configuration: str) -> dict[str, Any]:
    return {"category": f"cfg-{configuration_token(configuration)}"}


def perseus_query(configuration: str) -> dict[str, Any]:
    return {"category": f"cfg-{configuration_token(configuration)}"}


def mem0_write(configuration: str) -> dict[str, Any]:
    return {"agent_id": f"cfg-{configuration_token(configuration)}"}


def mem0_query(configuration: str) -> dict[str, Any]:
    return {"filters": {"agent_id": f"cfg-{configuration_token(configuration)}"}}


def hindsight_write(configuration: str) -> dict[str, Any]:
    return {"tags": [f"cfg-{configuration_token(configuration)}"]}


def hindsight_query(configuration: str) -> dict[str, Any]:
    return {"tags": [f"cfg-{configuration_token(configuration)}"], "tags_match": "all"}


def agentmemory_write(configuration: str) -> dict[str, Any]:
    return {"project": f"cfg-{configuration_token(configuration)}"}


def agentmemory_query(configuration: str) -> dict[str, Any]:
    return {"project": f"cfg-{configuration_token(configuration)}"}


BINDINGS = {
    "perseus": {
        "primitive": "category",
        "write_call": "perseus_vault_write_gate {category}",
        "query_call": "perseus_vault_recall {category}",
        "scope_primitive": "workspace_hash",
        "status": SUPPORTED,
        "write": perseus_write, "query": perseus_query,
        "note": "the frozen adapter pins category to a constant; binding it per "
                "configuration leaves workspace_hash untouched",
    },
    "mem0": {
        "primitive": "agent_id",
        "write_call": "Memory.add(agent_id=...)",
        "query_call": "Memory.search(filters={'agent_id': ...})",
        "scope_primitive": "user_id",
        "status": SUPPORTED,
        "write": mem0_write, "query": mem0_query,
        "note": "_build_filters_and_metadata treats user_id, agent_id and run_id "
                "as independent session identifiers; Gen78 took user_id",
    },
    "hindsight": {
        "primitive": "tags",
        "write_call": "Hindsight.retain(tags=[...])",
        "query_call": "Hindsight.recall(tags=[...], tags_match='all')",
        "scope_primitive": "bank_id",
        "status": SUPPORTED,
        "write": hindsight_write, "query": hindsight_query,
        "note": "tags are independent of bank_id, which carries scope",
    },
    "agentmemory": {
        "primitive": "project",
        "write_call": "POST /agentmemory/remember {project}",
        "query_call": "POST /agentmemory/smart-search {project}",
        "scope_primitive": "agentId",
        "status": SUPPORTED,
        "write": agentmemory_write, "query": agentmemory_query,
        "note": "CAVEAT: Gen13 measured that smart-search does not isolate by "
                "project. That is a behaviour finding about a surface that "
                "exists, not an absent surface - the same shape as the Gen77 "
                "caveat that Gen78 disproved. Feasible to ask; not a prediction.",
    },
}


def distinct_coordinates(engine: str, configuration_a: str,
                         configuration_b: str) -> dict[str, Any]:
    binding = BINDINGS[engine]
    writes = (binding["write"](configuration_a), binding["write"](configuration_b))
    queries = (binding["query"](configuration_a), binding["query"](configuration_b))
    return {
        "engine": engine,
        "write_a": writes[0], "write_b": writes[1],
        "query_a": queries[0], "query_b": queries[1],
        "writes_differ": writes[0] != writes[1],
        "queries_differ": queries[0] != queries[1],
        "touches_scope_primitive": binding["scope_primitive"] in str(writes) + str(queries),
    }


def contract() -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "question": "can each engine distinguish two configurations inside one "
                    "scope, symmetrically, without repurposing the scope key?",
        "hard_constraint": "the scope primitive must not appear in any configuration "
                           "binding; reusing it would make two configurations look "
                           "like two scopes and the isolation would be relabelling",
        "bindings": {name: {k: v for k, v in entry.items()
                            if k not in ("write", "query")}
                     for name, entry in BINDINGS.items()},
        "gen78_scope_bindings_untouched": True,
        "frozen_before_any_run": True,
        "not_yet_measured": "feasibility only; whether a bound primitive isolates is "
                            "the next generation's question",
    }
