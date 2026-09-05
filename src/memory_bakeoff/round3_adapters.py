"""`round3-adapters-v1`: fair bindings, unchanged strategies, and an honest budget audit.

Round 3 needs four adapters that ask the same question of four engines without
manufacturing an equality that does not exist. Two things are reused rather than
reinvented, because Round 2 already paid for them:

- **scope bindings** from `scope_bound` (Gen77, measured in Gen78);
- **configuration bindings** from `configuration_bound` (Gen79, measured Gen80).

Each engine keeps **its own retrieval strategy**. No mode is swapped for one that
happens to report more, which is the substitution Gen92 declined.

**The audit this generation exists for.** The interference scorer distinguishes
*true forgetting* from *distractor displacement* by asking whether the result
window was **saturated**. That question only means something if the engine was
actually given a window it could fill. So: how does each surface express a
result-window or budget limit?

| engine | window surface | kind |
|---|---|---|
| perseus | `limit` | native result count |
| mem0 | `limit` | native result count |
| agentmemory | `limit` | native result count |
| **hindsight** | `max_tokens` | **token budget — no result count exists** |

**Hindsight cannot express "return at most N results."** Its recall takes
`bank_id`, `query` and `max_tokens`. The Round-2 adapter accepted a `limit`
argument and **never passed it**; the harness then truncated the reply with
`[:LIMIT]`. Every `requested_limit: 5` recorded for hindsight is the harness's
scissors, not the engine's window — and the frozen adapter contract's
`post_filtering: "none; native order and native limit are preserved"` is
therefore inaccurate for that engine, because there is no native limit to
preserve.

That is recorded here rather than papered over, and it has a consequence:
**`saturated` is `NOT_DEMONSTRABLE` for hindsight**, so the forgetting /
displacement distinction cannot be drawn for it from a result count alone.

**Therefore the run is designed around within-engine scale curves.** Comparing a
count-bounded engine with a token-bounded one at "the same window" would be
comparing two different quantities. `assert_within_engine_only` refuses a
cross-engine pooled count.
"""
from __future__ import annotations

from typing import Any, Mapping

from memory_bakeoff.providers.configuration_bound import (BINDINGS as CONFIGURATION_BINDINGS,
                                                configuration_token)
from memory_bakeoff.providers.scope_bound import BINDINGS as SCOPE_BINDINGS, scope_token

ADAPTER_VERSION = "round3-adapters-v1"

NATIVE_RESULT_COUNT = "native_result_count"
TOKEN_BUDGET = "token_budget"
NOT_EXPRESSIBLE = "RESULT_WINDOW_NOT_EXPRESSIBLE"
NOT_DEMONSTRABLE = "NOT_DEMONSTRABLE"

BUDGET_SURFACE = {
    "perseus": {
        "parameter": "limit", "kind": NATIVE_RESULT_COUNT,
        "read_path": "perseus_vault_recall(mode=hybrid, limit=N)",
        "window_expressible": True,
        "evidence": "recall_arguments passes limit to the engine",
    },
    "mem0": {
        "parameter": "limit", "kind": NATIVE_RESULT_COUNT,
        "read_path": "Memory.search(query, filters, limit=N, threshold)",
        "window_expressible": True,
        "evidence": "search_arguments passes limit to the engine",
    },
    "agentmemory": {
        "parameter": "limit", "kind": NATIVE_RESULT_COUNT,
        "read_path": "POST /agentmemory/smart-search {limit: N}",
        "window_expressible": True,
        "evidence": "search_arguments passes limit to the engine",
    },
    "hindsight": {
        "parameter": "max_tokens", "kind": TOKEN_BUDGET,
        "read_path": "recall(bank_id, query, max_tokens=4096)",
        "window_expressible": False,
        "evidence": "recall_arguments accepts a `limit` argument and NEVER PASSES "
                    "IT; the Round-2 harness truncated the reply with [:LIMIT] "
                    "afterwards, so requested_limit was the harness's scissors",
        "contract_defect": "the frozen adapter contract says post_filtering "
                           "'none; native order and native limit are preserved' - "
                           "accurate for the other three, inaccurate here, because "
                           "no native limit exists to preserve",
    },
}


def saturation_meaning(engine: str) -> dict[str, Any]:
    """Is `window saturated` a statement about the engine, or about the harness?"""
    surface = BUDGET_SURFACE[engine]
    if surface["window_expressible"]:
        return {"engine": engine, "saturated_is": "meaningful",
                "because": f"the engine was given {surface['parameter']}=N and "
                           "filled it or did not"}
    return {
        "engine": engine, "saturated_is": NOT_DEMONSTRABLE,
        "because": "the engine was given a token budget, not a result count; a "
                   "count equal to the harness limit would describe the truncation, "
                   "not the engine",
        "consequence": "true_forgetting and distractor_displacement cannot be "
                       "separated for this engine from a result count alone",
    }


def bindings(engine: str, scope: str, configuration: str, run: str = "r3") -> dict[str, Any]:
    """Reused, not reinvented: Gen77 scope binding plus Gen79 configuration binding."""
    scope_entry = SCOPE_BINDINGS.get(engine)
    configuration_entry = CONFIGURATION_BINDINGS[engine]
    if engine == "perseus":
        scope_write = {"workspace_hash": scope_token(scope)}
        scope_query = dict(scope_write)
        scope_primitive = "workspace_hash"
    else:
        kwargs = {} if engine == "mem0" else {"run": run}
        scope_write = scope_entry["write"](scope, **kwargs)
        scope_query = scope_entry["query"](scope, **kwargs)
        scope_primitive = scope_entry["primitive"]
    return {
        "engine": engine,
        "scope_primitive": scope_primitive,
        "configuration_primitive": configuration_entry["primitive"],
        "write": {**scope_write, **configuration_entry["write"](configuration)},
        "query": {**scope_query, **configuration_entry["query"](configuration)},
        "provenance": "scope binding from Gen77/78, configuration binding from "
                      "Gen79/80; neither is re-derived here",
    }


def assert_no_mode_substitution(engine: str, read_path: str) -> None:
    """The strategy each engine was measured on is the strategy it keeps."""
    expected = BUDGET_SURFACE[engine]["read_path"]
    if read_path != expected:
        raise ValueError(
            f"{engine} must keep its own retrieval strategy: expected {expected!r}, "
            f"got {read_path!r}. Swapping a mode to make the engines look "
            "comparable manufactures an equality the data does not have.")


def assert_within_engine_only(summary: Mapping[str, Any]) -> None:
    """Refuse a cross-engine pooled count over incomparable windows."""
    pooled = [k for k in summary if "pooled" in k.lower() or "cross_engine" in k.lower()]
    if pooled:
        raise ValueError(
            f"Round 3 is reported as within-engine scale curves; found {sorted(pooled)}. "
            "One engine is bounded by a result count and another by a token budget, "
            "so a shared window is not a shared quantity.")


def preflight() -> dict[str, Any]:
    """What must hold before any engine call. Stated, and checkable."""
    return {
        "adapter_version": ADAPTER_VERSION,
        "scale_is_the_only_fixture_variable": "one semantic core, identical query, "
                                              "scope and configuration at every "
                                              "level; only the distractor count "
                                              "changes (asserted in the Gen95 tests)",
        "identical_records_and_query_per_engine": "every engine receives the same "
                                                  "observation texts and the same "
                                                  "query string; only the binding "
                                                  "primitives differ, and those are "
                                                  "the Gen77/79 ones",
        "saturation": {engine: saturation_meaning(engine) for engine in BUDGET_SURFACE},
        "budget_surface": BUDGET_SURFACE,
        "comparable_windows_expressible": False,
        "why_not": "hindsight expresses a token budget and the other three express a "
                   "result count; those are different quantities and no setting of "
                   "one equals a setting of the other",
        "run_design": "within-engine scale curves, not cross-engine pooled counts",
        "strategies_unchanged": True,
        "no_engine_runs": True,
    }
