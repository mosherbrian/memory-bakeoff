"""The long-context null: no retrieval at all, the whole history in the window.

DECISION_MEMO.md row 4. Both independent accountants ranked this first, and the
reason is uncomfortable: this project has compared five engines to each other
and to lexical retrieval, and never to the option of not retrieving.

EvoMemBench (arXiv:2605.18421) reports long-context baselines remain highly
competitive with memory systems, and that memory helps most only where context
is insufficient or the task is hard. If that holds here, rows 5 and 6 of the
memo are moot and the memo closes early. That is why this runs first.

WHAT THIS IS NOT. It is not a memory system and must never be scored as one. It
has no ingestion, no supersession, no scope, no provenance and no lifecycle - it
cannot express any of the properties the project exists to measure. It answers
exactly one question: **does retrieval need to happen at all, on our workload?**

CONTRACT. It satisfies the same `search(question_text) -> (items, latency_ms)`
shape the engine adapters use, so the existing scorer can run it unchanged. The
"retrieval" is a passthrough: every observation, in ingestion order, ranked by
position. Anything downstream that treats rank as relevance will read this
correctly as "no ranking was performed".
"""
from __future__ import annotations

import time
from typing import Any

ARM_VERSION = "longcontext-null-v1"


class LongContextNull:
    """Returns the entire history, unranked, in ingestion order.

    The token cost is the finding, not an implementation detail: an arm that
    wins on accuracy while spending 40x the context is not a free win, and the
    scorer records both.
    """

    def __init__(self, observations: list[dict[str, Any]], limit: int | None = None):
        """`observations` is the full ingested history in ingestion order.

        `limit` exists ONLY to model a real context ceiling. It is not a
        retrieval budget and must not be tuned per question - doing so would
        make this a retrieval system with a bad ranker, which is the one thing
        it must not become. Set it once, from the reader's real window, or leave
        it None.
        """
        self._obs = list(observations)
        self._limit = limit
        self.tokens_offered = sum(len(str(o.get("text", "")).split()) for o in self._obs)

    def open_read_snapshot(self) -> None:
        """No state to snapshot. Present so the harness can treat this like an engine."""

    def close_read_snapshot(self) -> None:
        """No state to release."""

    def search(self, question_text: str) -> tuple[list[dict], float]:
        """Every observation, in ingestion order. The question is not consulted.

        That is the point: if this arm scores well, the ranking done by every
        other arm was not what produced their score.
        """
        started = time.perf_counter()
        window = self._obs if self._limit is None else self._obs[-self._limit:]
        items = [
            {"rank": rank,
             "native_id": str(o.get("id", "")),
             "score": None,                     # nothing was scored; never impute one
             "text": o.get("text", "")}
            for rank, o in enumerate(window, start=1)
        ]
        latency = (time.perf_counter() - started) * 1000
        return items, latency

    def inventory(self) -> dict[str, Any]:
        return {"arm": ARM_VERSION,
                "observations_held": len(self._obs),
                "observations_offered": len(self._obs) if self._limit is None else min(self._limit, len(self._obs)),
                "approx_tokens_offered": self.tokens_offered,
                "retrieval_performed": False,
                "supersession_expressible": False,
                "scope_expressible": False,
                "provenance_expressible": False,
                "note": "Not a memory system. Answers only whether retrieval is necessary."}
