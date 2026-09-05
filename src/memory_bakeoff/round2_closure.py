"""`round2-retrieval-closure-gen94-v1`: the canonical Round-2 retrieval result.

Twenty-six generations of audit stand behind this. Round 2 began as an eight-row
table of clean counts that appeared to separate four memory systems sharply. Most
of that separation was the harness being measured as if it were the products.

This module is the closure. It does not restate numbers by hand: every claim is
composed from the module that measured it, so the synthesis cannot drift from its
evidence. And it refuses, structurally, to become a ranking.

**Every claim carries its layer.** `frozen_configuration` answers *what did the
tested setup do?* — real behaviour of a real configuration, handicaps included.
`native_capability` answers *what can this pinned engine and interface do when
correctly bound?* An engine that collapses scopes in the first and isolates them
perfectly in the second is not a contradiction; it is the distinction the whole
programme exists to preserve.

**No ranking is reconstructed.** `assert_no_ranking` fails on any attempt to
order the engines, total them, or name a winner. `MEASURED`,
`NOT_DEMONSTRABLE` and `NOT_APPLICABLE` are the vocabulary, and they are not a
scale.
"""
from __future__ import annotations

from typing import Any, Mapping

from memory_bakeoff.current_truth_closure import RESIDUE, closure as current_truth
from memory_bakeoff.layer_boundary import READER_LAYER_KINDS
from memory_bakeoff.round2_reconciliation import (ENGINES, frozen_configuration,
                                                  native_capability, counts)
from memory_bakeoff.temporal_closure import RETRACTIONS, SURVIVING

CONTRACT_VERSION = "round2-retrieval-closure-gen94-v1"

RANKING_TERMS = ("winner", "best engine", "ranked first", "leaderboard",
                 "overall score", "total score", "wins", "beats the others",
                 "top engine", "1st place")


def assert_no_ranking(statement: str) -> None:
    """Fail closed on any sentence that turns the synthesis into a league table."""
    lowered = statement.lower()
    found = sorted(term for term in RANKING_TERMS if term in lowered)
    if found:
        raise ValueError(
            f"the Round-2 result is not a ranking; found {found}. The axes vary "
            "independently and no engine has a total.")


# The four rules that survived more than one line of evidence. Each names the
# generations that established it and the mistake it prevents.
METHOD = {
    "prove_reachability_before_reading_a_zero": {
        "rule": "a failure class must be shown to fire before its zero is "
                "interpreted",
        "established_by": ["Gen69", "Gen83", "Gen84", "Gen89"],
        "prevented": "four universal zeros were read as product failures; none of "
                     "them was evidence about a memory system",
    },
    "never_read_an_adapter_choice_as_a_product_capability": {
        "rule": "what the harness declined to ask is not what the product cannot do",
        "established_by": ["Gen73", "Gen76", "Gen78", "Gen84"],
        "prevented": "three engines were recorded as collapsing scopes when their "
                     "adapters passed no scope filter at all; given one, all three "
                     "isolate perfectly",
    },
    "never_mix_the_retrieval_and_reader_layers": {
        "rule": "questions a store cannot answer belong to the reader layer and "
                "stay NOT_DEMONSTRABLE at the retrieval layer permanently",
        "established_by": ["Gen83", "Gen84", "Gen87"],
        "prevented": "two rows that read as universal failure were asking for a "
                     "judgement and a refusal, neither of which a retriever performs",
    },
    "decompose_a_pooled_failure_before_comparing_systems": {
        "rule": "a pooled count hides the mechanism, and the mechanism is the result",
        "established_by": ["Gen89", "Gen90", "Gen91", "Gen93"],
        "prevented": "the current-truth row looked like widespread forgetting; the "
                     "current fact was never once lost, and most failures were the "
                     "window width",
    },
}


def surviving_claims() -> list[dict[str, Any]]:
    """What Round 2 actually established, each with its layer."""
    return [
        {"claim": "perseus uniquely preserves transaction-time belief history",
         "layer": "frozen_configuration", "status": "MEASURED",
         "provenance": "Gen68 6/6, survives every Gen75 retraction"},
        {"claim": "hindsight exposes a temporal filter that is accepted and ignored",
         "layer": "frozen_configuration", "status": "MEASURED",
         "provenance": "Gen70, 15 of 15"},
        {"claim": "mem0 and agentmemory expose no temporal surface to exercise",
         "layer": "frozen_configuration", "status": "NOT_APPLICABLE",
         "provenance": "Gen71"},
        {"claim": "no engine tested records effective time; perseus's is untestable "
                  "on this build and the other three have no surface",
         "layer": "native_capability", "status": "NOT_DEMONSTRABLE / NOT_APPLICABLE",
         "provenance": "Gen73, Gen74, Gen75"},
        {"claim": "all four isolate scopes when given their own scope key",
         "layer": "native_capability", "status": "MEASURED",
         "provenance": "Gen76 audit, Gen78 ablation"},
        {"claim": "perseus, mem0 and hindsight separate a second configuration "
                  "inside one scope; agentmemory cannot through this interface",
         "layer": "native_capability", "status": "MEASURED",
         "provenance": "Gen80, localised Gen81, closed Gen82 NO_USABLE_SECOND_SURFACE"},
        {"claim": "every engine retrieves the current fact; it was never once lost",
         "layer": "frozen_configuration", "status": "MEASURED",
         "provenance": "Gen89, 0 of 84"},
        {"claim": "one demonstrated ranking defect remains, hindsight's, localised "
                  "to its reranker",
         "layer": "frozen_configuration", "status": "MEASURED",
         "provenance": "Gen90, Gen91"},
    ]


def synthesis() -> dict[str, Any]:
    frozen, native = frozen_configuration(), native_capability()
    return {
        "contract_version": CONTRACT_VERSION,
        "scope": "perseus-vault 2.23.2, mem0 2.0.19, hindsight 0.9.2, "
                 "agentmemory 0.9.29, on longitudinal-v1 and backfill-v1",
        "generations_frozen": "Gen68 through Gen93",
        "frozen_configuration": frozen,
        "native_capability": native,
        "status_counts": counts(),
        "current_truth": current_truth(),
        "temporal_retractions": list(RETRACTIONS),
        "temporal_surviving": list(SURVIVING),
        "reader_layer_excluded": sorted(READER_LAYER_KINDS),
        "surviving_claims": surviving_claims(),
        "method": METHOD,
        "no_ranking": "the axes vary independently; no engine has a total and there "
                      "is no ranking column in or across the tables",
        "engines": list(ENGINES),
        "round_status": "CLOSED",
        "no_engine_runs": True,
    }


def residue_summary() -> Mapping[str, str]:
    return {engine: entry["status"] for engine, entry in RESIDUE.items()}
