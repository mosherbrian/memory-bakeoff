"""`current-truth-decomposition-gen89-v1`: what the last foundational row measures.

`current_truth` is the plainest question the benchmark asks — *what is true now?* —
and the only Round-2 row never given the treatment that dissolved the others.
Its pooled counts were 6/21, 6/21, 6/21 and 9/21, and pooling is exactly what
hides a mechanism.

Four mechanisms are distinguished, because they have different causes and
different fixes:

- **missing current fact** — the present truth was not returned at all.
- **stale returned** — the superseded version came back and the current one did not.
- **conflicting versions co-returned** — both came back. The store did not lose the
  current fact; it also handed over the version it replaced.
- **retrieval-window effect** — a special case of the above where the current fact
  **outranks** every prohibited record, so a window tight enough to exclude the
  old version still contains the new one. The failure is the size of the window,
  not the ranking.

The distinction that matters most is the third against the first. "Cannot find
what is true now" and "finds it, and hands you the old one alongside it" are
different products.

**And a prior question, asked before any of that.** Does each `current` case
actually ask only for present truth? Three of the seven do not: one is failed by a
configuration distinction, one by a late-history distinction, and one can only be
passed by returning nothing at all — which Gen84 established no retrieval surface
can express. Those cells are `NOT_DEMONSTRABLE` at this layer rather than another
zero.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

CONTRACT_VERSION = "current-truth-decomposition-gen89-v1"

MISSING = "missing_current_fact"
STALE_ONLY = "stale_returned_current_absent"
CONFLICTING = "conflicting_versions_co_returned"
WINDOW = "retrieval_window_effect"
CLEAN = "clean"
NOT_DEMONSTRABLE = "NOT_DEMONSTRABLE"

CASES = ("LQ01", "LQ02", "LQ11", "LQ12", "LQ14", "LQ15", "LQ17")
ENGINES = ("perseus", "mem0", "hindsight", "agentmemory")

# Does the case ask ONLY for present truth? Read from the fixture, and the reason
# is recorded where it does not.
PURITY = {
    "LQ01": {"pure": True, "note": "one record for the truth key, nothing prohibited"},
    "LQ17": {"pure": True, "note": "same store state as LQ01"},
    "LQ11": {"pure": True, "note": "current versus its own superseded predecessor"},
    "LQ14": {"pure": True, "note": "current versus its own invalidated predecessor"},
    "LQ02": {"pure": False, "layer": "configuration",
             "note": "the prohibited record differs by CONFIGURATION, so the scorer "
                     "charges configuration_collapse inside a current-truth row; "
                     "Gen80 measured configuration isolation as its own bindable axis"},
    "LQ12": {"pure": False, "layer": "temporal",
             "note": "prohibits a historical_only record and charges "
                     "late_history_corruption, a temporal class, inside a "
                     "current-truth row"},
    "LQ15": {"pure": False, "layer": "abstention",
             "note": "expects the EMPTY set, so it can only be passed by returning "
                     "nothing; Gen84 established no retrieval surface here can "
                     "express abstention"},
}


def classify(expected: Sequence[str], prohibited: Sequence[str],
             returned: Sequence[str]) -> dict[str, Any]:
    """One case, one engine, one repetition. Rank is used, not just membership."""
    got_expected = [i for i in expected if i in returned]
    got_prohibited = [i for i in prohibited if i in returned]
    if not expected:
        return {"mechanism": NOT_DEMONSTRABLE, "reason": "abstention required",
                "tighter_window_would_pass": False}
    if not got_expected:
        mechanism = STALE_ONLY if got_prohibited else MISSING
        return {"mechanism": mechanism, "tighter_window_would_pass": False}
    if not got_prohibited:
        return {"mechanism": CLEAN, "tighter_window_would_pass": None}
    expected_rank = min(returned.index(i) for i in got_expected) + 1
    prohibited_rank = min(returned.index(i) for i in got_prohibited) + 1
    window = expected_rank < prohibited_rank
    return {
        "mechanism": WINDOW if window else CONFLICTING,
        "expected_rank": expected_rank,
        "prohibited_rank": prohibited_rank,
        # A window of exactly `expected_rank` holds the current fact and excludes
        # every prohibited one. That is a limit of N, not necessarily 1.
        "tighter_window_would_pass": window,
        "passing_limit": expected_rank if window else None,
    }


def controls(score_case, fixture, cases: Mapping[str, Any]) -> dict[str, Any]:
    """Prove each current-truth failure class can fire and can stay silent."""
    lq11 = cases["LQ11"]
    return {
        "clean_on_current_alone": {
            "returned": ("L010",),
            "classes": tuple(score_case(fixture, lq11, ("L010",)).failure_classes)},
        "stale_persistence_on_co_return": {
            "returned": ("L010", "L009"),
            "classes": tuple(score_case(fixture, lq11, ("L010", "L009")).failure_classes)},
        "stale_persistence_on_stale_alone": {
            "returned": ("L009",),
            "classes": tuple(score_case(fixture, lq11, ("L009",)).failure_classes)},
        "missing_on_empty": {
            "returned": (),
            "classes": tuple(score_case(fixture, lq11, ()).failure_classes)},
        "rank_is_ignored_by_the_scorer": {
            "current_first": tuple(score_case(fixture, lq11, ("L010", "L009")).failure_classes),
            "stale_first": tuple(score_case(fixture, lq11, ("L009", "L010")).failure_classes)},
    }


def decompose(records: Mapping[str, Mapping[str, Sequence[Sequence[str]]]],
              expected: Mapping[str, Sequence[str]],
              prohibited: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    """`records[case][engine]` is one returned-id list per repetition."""
    rows, tally = [], {}
    for case in CASES:
        for engine in ENGINES:
            for repetition, returned in enumerate(records[case][engine], start=1):
                verdict = classify(expected[case], prohibited[case], list(returned))
                rows.append({"case": case, "engine": engine, "repetition": repetition,
                             "returned": list(returned), **verdict})
                tally[verdict["mechanism"]] = tally.get(verdict["mechanism"], 0) + 1
    return {"rows": rows, "mechanism_totals": tally}


def purity_audit() -> dict[str, Any]:
    impure = {c: PURITY[c] for c in CASES if not PURITY[c]["pure"]}
    return {
        "pure_current_truth_cases": [c for c in CASES if PURITY[c]["pure"]],
        "cases_carrying_another_layer": impure,
        "verdict": "3 of 7 current_truth cases are failed by a distinction that "
                   "belongs to another layer; their cells are NOT_DEMONSTRABLE at "
                   "this layer rather than another zero",
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "mechanisms": [MISSING, STALE_ONLY, CONFLICTING, WINDOW, CLEAN],
        "why": "'cannot find what is true now' and 'finds it and hands you the old "
               "one alongside it' are different products, and pooling hides which",
        "window_rule": "a window effect is recorded when the current fact OUTRANKS "
                       "every prohibited record, so a limit of expected_rank holds "
                       "the new version and excludes the old - a limit of N, not "
                       "necessarily 1",
        "pooled_counts_status": "6/21, 6/21, 6/21 and 9/21 are NOT preserved as "
                                "meaningful; they are decomposed here and reported "
                                "only by mechanism",
        "no_engine_runs": True,
    }
