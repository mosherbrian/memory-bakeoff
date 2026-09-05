"""`scope-reachability-audit-v1`: can the scope ruler fire, and was scope ever asked?

Gen75 closed the temporal line with a method, not a table: **prove a failure class
can fire before reporting it as zero**, and separate what an engine cannot do
from what the harness never asked it to do. Gen68's scope numbers - Perseus 6 of
9 clean, everyone else 0 of 9 - have never had that treatment.

Two questions, kept apart because they have different answers:

**Reachability.** Can `scope_collapse` and `configuration_collapse` actually
fire? Both sit in an `elif` chain behind several other classes, so a case can
satisfy the condition and still be charged something else. That is a property of
the scorer and is checked here against the frozen fixture.

**Exercise.** Does each adapter actually pass a scope filter? This is the harder
question and the one the temporal work taught us to ask. An engine that is never
given a scope cannot honour one, and calling that a scope failure would repeat
the Gen73 mistake exactly.

The distinction this module enforces:

- **`scope_isolated`** - the adapter passes a scope filter on write and query, so
  the engine's behaviour is genuinely being measured.
- **`scope_not_exercised`** - the adapter passes no scope filter. The tested
  configuration does collapse scopes, and that is a true statement about the
  configuration. The engine's scope *capability* is `NOT_DEMONSTRABLE`.

Both statements are true at once and must be reported separately, which is
precisely what Gen71 got wrong on the temporal axis by reading an adapter routing
decision as an engine property.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "scope-reachability-audit-v1"

ISOLATED = "scope_isolated"
NOT_EXERCISED = "scope_not_exercised"
NOT_DEMONSTRABLE = "not_demonstrable"
MEASURED = "measured"

# What "scope" is in each frozen adapter, quoted from the adapter contracts.
ADAPTER_SCOPE = {
    "perseus": {
        "mechanism": "workspace_hash = sha256(public scope)",
        "passed_on_write": True,
        "passed_on_query": True,
        "evidence": "body carries scope; write and recall both take "
                    "workspace_hash derived from the case scope",
    },
    "mem0": {
        "mechanism": "scope stored in metadata; queries filter on a constant user_id",
        "passed_on_write": False,
        "passed_on_query": False,
        "evidence": "adapter contract: 'scored_filter: constant user_id only, "
                    "exactly as Gen10'",
    },
    "hindsight": {
        "mechanism": "bank_id is per repetition; scope appears only inside a "
                     "context string",
        "passed_on_write": False,
        "passed_on_query": False,
        "evidence": "recall arguments are bank_id, query, max_tokens - no scope "
                    "term",
    },
    "agentmemory": {
        "mechanism": "one agentId and one project namespace for every scope",
        "passed_on_write": False,
        "passed_on_query": False,
        "evidence": "adapter contract: 'never a project or agent per scope', and "
                    "'smart-search does not isolate by project anyway'",
    },
}


def exercise_status(adapter: Mapping[str, Any]) -> str:
    return ISOLATED if (adapter["passed_on_write"] and adapter["passed_on_query"]) \
        else NOT_EXERCISED


def capability_verdict(adapter: Mapping[str, Any]) -> dict[str, Any]:
    """Separate the configuration's behaviour from the engine's capability."""
    if exercise_status(adapter) == ISOLATED:
        return {
            "scope_exercised": ISOLATED,
            "engine_scope_capability": MEASURED,
            "configuration_behaviour": "measured directly",
            "why": "a scope filter is supplied on both paths, so honouring or "
                   "violating it is the engine's own behaviour",
        }
    return {
        "scope_exercised": NOT_EXERCISED,
        "engine_scope_capability": NOT_DEMONSTRABLE,
        "configuration_behaviour": "collapses scopes, which is a true statement "
                                   "about the tested configuration",
        "why": "no scope filter is passed on either path, so the engine is never "
               "asked to isolate; a scope failure here is the configuration's, "
               "not evidence about the product",
    }


def reachable_classes(cases: Iterable[Mapping[str, Any]],
                      observations: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Which scope classes the frozen fixture can actually provoke.

    `scope_collapse` needs a prohibited observation in a DIFFERENT scope;
    `configuration_collapse` needs one in the same scope but a different
    configuration. Neither can fire without such a case existing.
    """
    cross_scope, cross_configuration = [], []
    for case in cases:
        for prohibited in case.get("prohibited_ids", ()):
            observation = observations.get(prohibited)
            if observation is None:
                continue
            if case.get("scope") and observation["scope"] != case["scope"]:
                cross_scope.append({"case": case["id"], "prohibited": prohibited})
            elif (case.get("configuration")
                  and observation["configuration"] != case["configuration"]):
                cross_configuration.append({"case": case["id"], "prohibited": prohibited})
    return {
        "scope_collapse": {"reachable": bool(cross_scope), "cases": cross_scope},
        "configuration_collapse": {"reachable": bool(cross_configuration),
                                   "cases": cross_configuration},
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "method": "the Gen75 rule applied to scope: prove a class can fire before "
                  "reporting its zero, and separate engine capability from what "
                  "the harness asked",
        "distinction": {
            ISOLATED: "scope filter supplied on write and query; engine behaviour "
                      "is measured",
            NOT_EXERCISED: "no scope filter supplied; configuration collapses "
                           "scopes and engine capability is not demonstrable",
        },
        "why_it_matters": "Gen71 read an adapter routing decision as an engine "
                          "property on the temporal axis; the same error is "
                          "available here and this module exists to prevent it",
        "no_engine_runs": True,
    }
