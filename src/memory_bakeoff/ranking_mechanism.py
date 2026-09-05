"""`stale-before-current-ranking-gen91-v1`: why the old version ranks first.

Gen90 left nine failures that no prefix window can rescue: the superseded record
outranks the current one, so cutting above the stale record loses the current
fact with it. Eight of the nine are `LQ11`, where a replaced branch name beats its
replacement. This asks what produces that order.

Three mechanisms are distinguished, and they call for different responses:

- **`MEANINGFUL_PREFERENCE`** — the engine scores the stale record clearly higher,
  and the separation is real within its own scale. A ranking-quality result.
- **`NEAR_TIE`** — the two records are far closer to each other than to anything
  else in the same result list. The order is decided in the noise, and a rerun
  could plausibly flip it.
- **`OPAQUE_RANKING_SURFACE`** — the adapter records no score at all. Nothing about
  *why* is observable, so the mechanism is `NOT_DEMONSTRABLE`.

**Scores are never normalised across engines.** A gap of 0.006 in one scale and
0.073 in another are not comparable numbers, and treating them as one would
manufacture a cross-engine claim the data cannot support. Every judgement here is
made *within* one engine, using a unit-free comparison: the gap between the two
records against the gap from that pair to the next record in the **same** list.
Where an engine reports score components, the comparison is also made component
by component, which is again internal to it.

**Repetition identity is preserved.** Gen90 found perseus's order flips between
repetitions; the question of whether that flip is a tie-break is asked
explicitly here rather than filed as nondeterminism.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

CONTRACT_VERSION = "stale-before-current-ranking-gen91-v1"

MEANINGFUL_PREFERENCE = "MEANINGFUL_PREFERENCE"
NEAR_TIE = "NEAR_TIE"
OPAQUE = "OPAQUE_RANKING_SURFACE"
NOT_DEMONSTRABLE = "NOT_DEMONSTRABLE"

# A pair whose separation is under this share of the distance to the rest of its
# own result list is called a near tie. Unit-free, and applied within one engine.
NEAR_TIE_SHARE = 0.05


def separation(stale: float | None, current: float | None,
               others: Sequence[float]) -> dict[str, Any]:
    """Within one engine's own scale: how close is the pair, relative to the field?"""
    if stale is None or current is None:
        return {"observable": False}
    pair_gap = abs(stale - current)
    if not others:
        return {"observable": True, "pair_gap": pair_gap, "field_gap": None,
                "share_of_field": None}
    field_gap = abs(min(stale, current) - max(others))
    return {
        "observable": True,
        "pair_gap": pair_gap,
        "field_gap": field_gap,
        "share_of_field": (pair_gap / field_gap) if field_gap else None,
    }


def classify(stale: float | None, current: float | None,
             others: Sequence[float]) -> dict[str, Any]:
    gap = separation(stale, current, others)
    if not gap["observable"]:
        return {"mechanism": OPAQUE, "verdict": NOT_DEMONSTRABLE,
                "why": "the adapter records no score for any hit, so nothing about "
                       "the ordering is observable", **gap}
    share = gap["share_of_field"]
    if share is not None and share < NEAR_TIE_SHARE:
        return {"mechanism": NEAR_TIE, "verdict": "measured",
                "why": f"the pair is separated by {share:.1%} of the distance from "
                       "it to the next record in the same list; the order is "
                       "decided in the noise", **gap}
    return {"mechanism": MEANINGFUL_PREFERENCE, "verdict": "measured",
            "why": "the engine separates the two clearly within its own scale",
            **gap}


def component_attribution(stale: Mapping[str, float | None],
                          current: Mapping[str, float | None]) -> dict[str, Any]:
    """Which score component produces the ordering, for an engine that reports them.

    Internal to that engine: the components are compared with each other, never
    with another engine's numbers.
    """
    gaps = {}
    for key in sorted(set(stale) | set(current)):
        a, b = stale.get(key), current.get(key)
        gaps[key] = None if a is None or b is None else a - b
    measurable = {k: v for k, v in gaps.items() if v is not None and k != "final"}
    dominant = max(measurable, key=lambda k: abs(measurable[k])) if measurable else None
    identical = sorted(k for k, v in measurable.items() if v == 0)
    return {"component_gaps": gaps, "dominant_component": dominant,
            "identical_components": identical,
            "why": "the component with the largest gap is what produces the order; "
                   "components that are identical cannot have produced it"}


def perseus_flip_test(orders_by_repetition: Mapping[int, Sequence[str]],
                      scores_observable: bool) -> dict[str, Any]:
    """Is perseus's order flip consistent with a near tie, or untestable?

    Gen90 measured that the same two records come back in a different order across
    repetitions. Whether that is tie-breaking cannot be decided without scores, and
    saying "nondeterminism" would be naming a cause the evidence does not carry.
    """
    orders = {r: list(o) for r, o in orders_by_repetition.items()}
    same_set = len({frozenset(o) for o in orders.values()}) == 1
    distinct_orders = {tuple(o) for o in orders.values()}
    if scores_observable:
        return {"same_record_set": same_set, "distinct_orders": len(distinct_orders),
                "verdict": "testable", "orders": orders}
    return {
        "same_record_set": same_set,
        "distinct_orders": len(distinct_orders),
        "orders": orders,
        "verdict": NOT_DEMONSTRABLE,
        "hypothesis": "the flip is a tie-break between near-tied scores",
        "why_untestable": "the committed records carry canonical_id, native_id, "
                          "provenance_exact and rank - and no score or tie metadata "
                          "of any kind, so the hypothesis can be neither confirmed "
                          "nor rejected",
        "not_claimed": "'generic nondeterminism' is NOT asserted; that would name a "
                       "cause the evidence does not carry",
        "rerun_prerequisite": "a perseus read path that surfaces per-hit scores. "
                              "Gen84 measured that recall returns none, so this is a "
                              "prerequisite to establish before any targeted rerun, "
                              "not a rerun that can simply be scheduled",
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "mechanisms": [MEANINGFUL_PREFERENCE, NEAR_TIE, OPAQUE],
        "near_tie_share": NEAR_TIE_SHARE,
        "near_tie_definition": "pair gap as a share of the gap from the pair to the "
                               "next record in the SAME list - unit-free and internal "
                               "to one engine",
        "no_cross_engine_normalisation": "score gaps are never compared between "
                                         "engines; a gap in one scale and a gap in "
                                         "another are not the same quantity",
        "repetition_identity": "preserved; each repetition is classified on its own",
        "no_engine_runs": True,
    }
