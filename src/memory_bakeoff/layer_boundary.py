"""`layer-boundary-gen87-v1`: which layer a result belongs to, enforced not asserted.

Gen83 through Gen86 established one structural conclusion, and it is easy to lose
the next time a table gets built: **`recommended_procedure` and `negative_unknown`
are not retrieval-engine metrics.** Neither can be answered by a store. One asks
which of two attempts to adopt; the other asks whether to decline. Both need a
reader, and Round 2 never had one.

Reporting them in an engine column is the mistake this module exists to prevent -
not by saying so in prose, which the previous four generations already did, but by
failing a check.

Two layers, and results never mix:

- **`retrieval_only`** — what a store returned. Comparable across engines.
- **`retrieval_plus_reader`** — what a store plus one pinned reader decided. A
  different system configuration, and never a correction to any engine.

A target kind is tagged with the layer that can actually answer it. Anything asked
of the reader layer stays `NOT_DEMONSTRABLE` at the retrieval layer, permanently
and by construction, because a retriever was never the thing being asked.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "layer-boundary-gen87-v1"

RETRIEVAL_ONLY = "retrieval_only"
RETRIEVAL_PLUS_READER = "retrieval_plus_reader"
NOT_DEMONSTRABLE = "not_demonstrable"

# Which layer can answer each kind of question. Derived from Gen83 and Gen84.
ANSWERABLE_AT = {
    "current_truth": RETRIEVAL_ONLY,
    "scope_truth": RETRIEVAL_ONLY,
    "as_of_event_truth": RETRIEVAL_ONLY,
    "historical_belief": RETRIEVAL_ONLY,
    "corrected_historical_truth": RETRIEVAL_ONLY,
    "late_arriving_history": RETRIEVAL_ONLY,
    "recommended_procedure": RETRIEVAL_PLUS_READER,
    "negative_unknown": RETRIEVAL_PLUS_READER,
}

READER_LAYER_KINDS = frozenset(
    k for k, v in ANSWERABLE_AT.items() if v == RETRIEVAL_PLUS_READER)


def retrieval_layer_status(target_kind: str) -> str:
    """What the retrieval layer may claim about a kind of question."""
    if ANSWERABLE_AT[target_kind] == RETRIEVAL_PLUS_READER:
        return NOT_DEMONSTRABLE
    return "measurable"


def assert_no_layer_mixing(table: Mapping[str, Any], *, layer: str) -> None:
    """Fail closed if a table reports one layer's rows under the other's heading.

    `table` maps target kind to whatever the row holds. A retrieval-only table
    that carries a reader-layer kind is the error; a reader-layer table that
    carries retrieval kinds is equally wrong, because the reader was only ever
    run on two cases.
    """
    if layer not in (RETRIEVAL_ONLY, RETRIEVAL_PLUS_READER):
        raise ValueError(f"unknown layer {layer!r}")
    wrong = sorted(k for k in table if ANSWERABLE_AT.get(k, RETRIEVAL_ONLY) != layer)
    if wrong:
        raise ValueError(
            f"{layer} table carries rows belonging to the other layer: {wrong}. "
            "recommended_procedure and negative_unknown are reader/full-product "
            "capabilities and must not appear as retrieval-engine metrics.")


def closure() -> dict[str, Any]:
    """The bounded conclusion for `retrieval_plus_reader`, frozen from Gen85-86."""
    return {
        "contract_version": CONTRACT_VERSION,
        "configuration": RETRIEVAL_PLUS_READER,
        "scope": "one pinned reader (qwen3.6-35b-vulkan-nothink, temperature 0), "
                 "two cases, six distinct evidence sets, every feasible ordering "
                 "of each - 506 orderings, no sampling",
        "unknown_abstention": {
            "result": "100% correct on every tested evidence set",
            "order_stability": "fully order-stable - 24/24 on the set three engines "
                               "share, 2/2 on agentmemory's",
            "engine_difference": "none; nothing distinguishes the engines here",
        },
        "procedure_adoption": {
            "result": "nearly universal - 470 of 480 orderings correct",
            "order_stability": "only perseus's evidence set is fully order-stable "
                               "(120/120); hindsight and agentmemory 118/120, mem0 "
                               "114/120",
            "engine_difference": "the 114/118/118 spread is inside ordering noise and "
                                 "is NOT reported as an engine difference",
            "failed_procedure_adoption": "fired zero times in 480 orderings; the "
                                         "reader never once adopted the failed attempt",
        },
        "causal_attribution": "WITHHELD. The Gen85 to Gen86 improvement cannot be "
                              "split between the scoring repair and the stronger "
                              "elicitation, because the contract changed both at "
                              "once. No fourth contract was run to separate them.",
        "branch_policy": "the reader work stays on its own branch; retrieval-only "
                         "main is not amended by it",
        "retrieval_only_status": "unchanged - every retrieval-only result stands as "
                                 "committed, and the two reader-layer kinds remain "
                                 "NOT_DEMONSTRABLE there permanently",
        "rule_for_future_tables": "recommended_procedure and negative_unknown are "
                                  "reader/full-product capabilities, not "
                                  "retrieval-engine metrics; assert_no_layer_mixing "
                                  "enforces it",
        "no_new_model_calls": True,
        "no_engine_reruns": True,
    }
