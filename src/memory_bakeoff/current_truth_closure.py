"""`current-truth-closure-gen93-v1`: the row replaced by what was measured.

Five generations took the plainest row in the benchmark apart. What it looked
like at the start — 6/21, 6/21, 6/21, 9/21, four systems that mostly cannot say
what is true now — was almost entirely wrong.

The corrected row is a mechanism, not a score:

- **the current fact was never simply lost.** `missing_current_fact` is a
  reachable class and it fired **zero times** in 84 observations (Gen89).
- **24 of 48** observations on the four pure cases were already clean (Gen90).
- **15 of 48** failures are attributable to **retrieval-window policy** — the
  current fact outranks its predecessor and a narrower window would pass (Gen90).
- **9 of 48** survive every prefix, and they are three different things, one per
  engine (Gen91, Gen92).

**The k=2 peak is not a recommendation and this module refuses to let it become
one.** The curve peaked there on four cases and 48 observations; adopting it as
policy would be fitting the harness to its own results.

**Perseus's repetition instability is preserved, not averaged.** The same query
against the same store returns the same two records in different orders across
repetitions, and that flip changes the verdict. Pooling would have hidden it.
"""
from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "current-truth-closure-gen93-v1"

OBSERVATIONS = 48
ALREADY_CLEAN = 24
WINDOW_POLICY = 15
NO_PREFIX = 9

DEMONSTRATED = "DEMONSTRATED_RANKING_DEFECT"
UNRESOLVED = "UNRESOLVED_ORDERING_OF_TIED_REVISIONS"
UNDIAGNOSABLE = "NOT_DIAGNOSABLE_THROUGH_THE_MEASURED_SURFACE"
NONE_OBSERVED = "NONE"

# The nine, split. Only one of these is a ranking-quality result.
RESIDUE = {
    "hindsight": {
        "count": 3,
        "status": DEMONSTRATED,
        "finding": "a real preference for the stale revision, localised to the "
                   "reranker: keyword identical, semantic gap 0.001655, reranker "
                   "gap 0.078265",
        "provenance": "Gen91",
    },
    "mem0": {
        "count": 3,
        "status": UNRESOLVED,
        "finding": "the two revisions are separated by 1.2% of the distance to the "
                   "next record in the same list; the engine does not meaningfully "
                   "prefer the stale one, it barely distinguishes them",
        "provenance": "Gen91",
    },
    "perseus": {
        "count": 3,
        "status": UNDIAGNOSABLE,
        "finding": "no read on the pinned build returns per-hit relevance scores "
                   "while preserving the Round-2 retrieval semantics; the product "
                   "refuses the scored trace on that mode",
        "provenance": "Gen91, Gen92",
    },
    "agentmemory": {
        "count": 0,
        "status": NONE_OBSERVED,
        "finding": "no irreducible ranking failure on this row",
        "provenance": "Gen90",
    },
}

# Preserved verbatim: the same two records, three repetitions, two orders.
PERSEUS_INSTABILITY = {
    "case": "LQ11",
    "orders": {1: ["L009", "L010"], 2: ["L010", "L009"], 3: ["L009", "L010"]},
    "verdicts": {1: "no-prefix ranking failure", 2: "window policy, clean at k=1",
                 3: "no-prefix ranking failure"},
    "why_kept": "the flip changes the verdict, not just the order; pooling the "
                "repetitions would have produced one confident wrong answer",
    "provenance": "Gen90",
}

WINDOW_CURVE = {1: 31, 2: 35, 3: 24, 4: 24, 5: 24}
WINDOW_IS_NOT_A_RECOMMENDATION = (
    "the curve peaks at k=2 on four cases and 48 observations. That is a property "
    "of this fixture. Adopting it as policy would be fitting the harness to its own "
    "results, and a narrower window is not free: at k=1 the current fact is lost "
    "outright in 17 of 48 observations."
)


def assert_not_a_recommendation(statement: str) -> None:
    """Fail closed if the window curve is written up as advice.

    A guard rather than a note, because 'k=2 scored best' is exactly the sentence
    that would slip into a summary and become a setting.
    """
    lowered = statement.lower()
    prescriptive = ("recommend", "should use", "we use", "adopt k", "set k",
                    "best k", "optimal k", "use k=")
    found = sorted(term for term in prescriptive if term in lowered)
    if found:
        raise ValueError(
            f"the window curve must not be stated as advice; found {found}. "
            "The curve is a measurement of this fixture, not a policy.")


def closure() -> dict[str, Any]:
    residue_total = sum(entry["count"] for entry in RESIDUE.values())
    assert residue_total == NO_PREFIX
    assert ALREADY_CLEAN + WINDOW_POLICY + NO_PREFIX == OBSERVATIONS
    return {
        "contract_version": CONTRACT_VERSION,
        "replaces": "the pooled current_truth row (6/21, 6/21, 6/21, 9/21)",
        "current_fact_never_lost": {
            "observed": 0, "of": 84,
            "note": "missing_current_fact is reachable - a control fires it - and "
                    "never occurred",
            "provenance": "Gen89"},
        "decomposition": {
            "observations": OBSERVATIONS,
            "already_clean": ALREADY_CLEAN,
            "retrieval_window_policy": WINDOW_POLICY,
            "no_prefix_can_succeed": NO_PREFIX,
            "provenance": "Gen90"},
        "residue": RESIDUE,
        "only_one_is_a_ranking_quality_defect": "hindsight",
        "perseus_instability": PERSEUS_INSTABILITY,
        "window_curve": WINDOW_CURVE,
        "window_is_not_a_recommendation": WINDOW_IS_NOT_A_RECOMMENDATION,
        "excluded_from_this_row": {
            "LQ02": "failed by a configuration distinction (Gen80's axis)",
            "LQ12": "failed by a late-history distinction, a temporal class",
            "LQ15": "expects the empty set; abstention is NOT_DEMONSTRABLE at the "
                    "retrieval layer (Gen84)",
            "provenance": "Gen89"},
        "line_status": "CLOSED",
        "no_engine_runs": True,
    }


def replacement_cells() -> dict[str, dict[str, Any]]:
    """What the `current_truth` row of the Round-2 table now says, per engine."""
    cells = {}
    for engine, entry in RESIDUE.items():
        cells[engine] = {
            "status": "MEASURED",
            "finding": "retrieves the current fact; the row's failures are window "
                       "policy plus an engine-specific residue",
            "residue": entry["status"],
            "residue_count": entry["count"],
            "provenance": f"Gen89, Gen90, {entry['provenance']}",
        }
    return cells
