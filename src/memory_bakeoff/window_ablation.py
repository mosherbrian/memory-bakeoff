"""`current-truth-window-ablation-gen90-v1`: the whole curve, not a chosen k.

Gen89 established that these engines almost always retrieve the current fact and
that the dominant failure is returning the version it replaced alongside it — and
that for 21 of 36 such failures the current fact **outranked** its predecessor, so
a narrower window would have excluded the old one.

That was an observation about ranks. This measures it directly: replay every
committed ranked result through fixed prefix windows k=1..5 and report **the full
curve**.

**No k is selected.** Choosing the window that scores best would be tuning the
harness against the data it is scoring, which is the failure this programme keeps
finding in other people's benchmarks and would be embarrassing to commit here.
The curve is the result.

**Nothing but truncation happens.** No hidden-label-aware stopping, no
deduplication, no reader reasoning, no semantic post-filter. `prefix(k)` is
`returned[:k]` and nothing else, so any improvement is attributable to window
policy alone.

**Repetitions are not pooled.** Each repetition keeps its own ranked order, so
Perseus's rank instability stays visible rather than being averaged away.

Two outcomes are separated, and the second is the real finding:

- **`WINDOW_POLICY`** — some prefix in 1..5 scores clean. The failure was the
  harness asking for five results.
- **`RANKING_FAILURE`** — no prefix scores clean, because the stale record
  outranks the current one. Truncation cannot help: cut above the stale record and
  you lose the current fact with it.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

CONTRACT_VERSION = "current-truth-window-ablation-gen90-v1"

# The four cases Gen89 found ask purely for present truth.
PURE_CASES = ("LQ01", "LQ11", "LQ14", "LQ17")
ENGINES = ("perseus", "mem0", "hindsight", "agentmemory")
WINDOWS = (1, 2, 3, 4, 5)

WINDOW_POLICY = "WINDOW_POLICY"
RANKING_FAILURE = "RANKING_FAILURE"
ALREADY_CLEAN = "ALREADY_CLEAN"

FORBIDDEN_TRANSFORMS = ("deduplication", "label_aware_stopping", "reader_reasoning",
                        "semantic_post_filter", "reordering")


def prefix(returned: Sequence[str], k: int) -> tuple[str, ...]:
    """Truncation, and only truncation. The order is the engine's own."""
    return tuple(returned[:k])


def curve(score_case, fixture, case, returned: Sequence[str]) -> dict[str, Any]:
    """Score every window from 1 to 5 for one committed ranked result."""
    points = []
    for k in WINDOWS:
        window = prefix(returned, k)
        classes = tuple(score_case(fixture, case, window).failure_classes)
        points.append({"k": k, "returned": list(window), "classes": list(classes),
                       "clean": classes == ()})
    clean_windows = [p["k"] for p in points if p["clean"]]
    full = points[-1]
    if full["clean"]:
        verdict = ALREADY_CLEAN
    elif clean_windows:
        verdict = WINDOW_POLICY
    else:
        verdict = RANKING_FAILURE
    return {
        "points": points,
        "clean_windows": clean_windows,
        "smallest_clean_window": min(clean_windows) if clean_windows else None,
        "verdict": verdict,
    }


def assert_truncation_only(returned: Sequence[str], window: Sequence[str]) -> None:
    """Fail closed if a window is anything other than a prefix of the input."""
    if list(window) != list(returned[:len(window)]):
        raise ValueError("a window must be a prefix of the engine's own ranked "
                         "result; no reordering, filtering or deduplication")


def summarise(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Per verdict, and per window, without choosing a window."""
    rows = list(rows)
    verdicts: dict[str, int] = {}
    per_window = {k: 0 for k in WINDOWS}
    for row in rows:
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
        for point in row["points"]:
            if point["clean"]:
                per_window[point["k"]] += 1
    return {
        "observations": len(rows),
        "verdicts": verdicts,
        "clean_count_at_each_window": per_window,
        "no_k_is_selected": "the curve is the result; picking the best-scoring "
                            "window would be tuning the harness against the data "
                            "it is scoring",
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "cases": list(PURE_CASES),
        "why_these_four": "Gen89 found the other three current_truth cases are "
                          "failed by a configuration, temporal or abstention "
                          "distinction and do not belong to this row",
        "windows": list(WINDOWS),
        "transform": "returned[:k], and nothing else",
        "forbidden": list(FORBIDDEN_TRANSFORMS),
        "repetitions_pooled": False,
        "repetition_note": "each repetition keeps its own ranked order so Perseus's "
                           "rank instability stays visible",
        "verdicts": {
            ALREADY_CLEAN: "clean at the full window; no ablation needed",
            WINDOW_POLICY: "some prefix scores clean - the failure was the harness "
                           "asking for five results",
            RANKING_FAILURE: "no prefix scores clean - the stale record outranks the "
                             "current one, and truncation cannot help",
        },
        "no_engine_runs": True,
    }
