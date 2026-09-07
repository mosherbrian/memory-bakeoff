"""Score what the system DID with a stale record, not whether it returned one.

DECISION_MEMO.md row 6. Adapted from FAMA (Supersede, arXiv:2606.27472), which
penalises reliance on superseded or deleted memory. The paper's code was not
locatable; the metric is a scoring rule and needs none of it.

WHY THIS EXISTS. Round 3 established that every engine co-returns the superseded
record alongside the current one - 192 of 192 observations. So "did it return
a prohibited record" no longer separates anything: they all do. What separates
them is what happens next, and nothing in this project has measured that.

Gen124 looked at it once, by hand, on fourteen items. This makes it a rule.

THE DISTINCTION THIS DRAWS, which the existing prohibited@k does not:

    returned stale, answered current   -> tolerated. Noise the reader survived.
    returned stale, answered stale     -> USED. The failure that matters.
    returned stale, answered neither   -> confused, and counted separately.
    returned no stale, answered stale  -> the answer came from somewhere else,
                                          which is a provenance bug, not a
                                          supersession one.

Presence and use are different failures with different fixes: presence is a
retrieval-policy problem, use is a reader or ranking problem. Summing them, or
reporting only presence, is what made every engine look identical at 192/192.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StaleDisposition(StrEnum):
    CURRENT_ANSWERED = "current_answered"          # right answer; stale may or may not be present
    STALE_USED = "stale_used"                      # answered with the superseded value
    NEITHER = "neither"                            # answered with something else entirely
    STALE_USED_WITHOUT_RETRIEVAL = "stale_used_without_retrieval"


@dataclass(frozen=True)
class StaleUseScore:
    disposition: StaleDisposition
    stale_present_in_context: bool
    penalised: bool

    @property
    def tolerated(self) -> bool:
        """Stale was there and did no harm. Worth counting; not worth penalising."""
        return self.stale_present_in_context and not self.penalised


def score_stale_use(*, answer_id: str | None, current_id: str,
                    stale_ids: frozenset[str] | set[str] | tuple[str, ...],
                    returned_ids: frozenset[str] | set[str] | tuple[str, ...]) -> StaleUseScore:
    """One case. Ids, never text - text matching is what made the Gen124 scorer crude.

    `answer_id` is None when the system declined or produced nothing mappable.
    Declining is NOT penalised here: refusing to answer is a different behaviour
    from answering wrongly, and collapsing them would reward confident error.
    """
    stale, returned = set(stale_ids), set(returned_ids)
    present = bool(stale & returned)

    if answer_id is not None and answer_id == current_id:
        return StaleUseScore(StaleDisposition.CURRENT_ANSWERED, present, penalised=False)

    if answer_id is not None and answer_id in stale:
        # The distinction the metric exists for. If the stale record was never
        # retrieved, the answer came from somewhere else - parametric memory, a
        # cache, a leak - and calling that a supersession failure would send the
        # investigation to the wrong layer.
        disposition = (StaleDisposition.STALE_USED if present
                       else StaleDisposition.STALE_USED_WITHOUT_RETRIEVAL)
        return StaleUseScore(disposition, present, penalised=True)

    return StaleUseScore(StaleDisposition.NEITHER, present, penalised=False)


def aggregate(scores: list[StaleUseScore]) -> dict[str, float | int]:
    """Counts and two rates. Never one number.

    `stale_use_rate` is the metric. `stale_presence_rate` is reported beside it
    precisely so nobody quotes one as the other: Round 3 put presence at 1.0 for
    every engine, and a project that reports only presence cannot tell its
    contestants apart.
    """
    n = len(scores)
    if n == 0:
        return {"n": 0}
    used = sum(1 for s in scores if s.disposition is StaleDisposition.STALE_USED)
    used_no_retrieval = sum(1 for s in scores
                            if s.disposition is StaleDisposition.STALE_USED_WITHOUT_RETRIEVAL)
    present = sum(1 for s in scores if s.stale_present_in_context)
    return {
        "n": n,
        "current_answered": sum(1 for s in scores
                                if s.disposition is StaleDisposition.CURRENT_ANSWERED),
        "stale_used": used,
        "stale_used_without_retrieval": used_no_retrieval,
        "neither": sum(1 for s in scores if s.disposition is StaleDisposition.NEITHER),
        "stale_present": present,
        "tolerated": sum(1 for s in scores if s.tolerated),
        "stale_use_rate": (used + used_no_retrieval) / n,
        "stale_presence_rate": present / n,
    }
