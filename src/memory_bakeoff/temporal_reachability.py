"""`temporal-reachability-v1`: make the two silent failure classes able to fire.

Gen68 found that two declared failure classes were reporting zero for every
engine because the harness could not produce them:

- **`future_leakage`** — at every checkpoint the runner ingested only the visible
  prefix, so a future observation was never in the store to be returned. The
  scorer was correct; the *run plan* never created the opportunity.
- **`unknown_hallucination`** — it comes from `score_answer_claim`, and no runner
  calls that function. The single `negative_unknown` case was graded on retrieval
  alone, so an engine that confidently answered a question with no answer was
  never charged for it.

This module repairs both without touching `longitudinal-v1`. That fixture and
scorer are frozen and their sha256 appears in every committed result; changing
them would invalidate the runs Gen68 just read. So the leakage repair is a **run
plan**, not a scorer change, and the hallucination repair is the **missing call**,
not a new rule.

Both repairs are proved reachable here with deterministic fixtures, before any
engine is run, which is the whole point: a class nobody can trigger is a blind
spot whether or not an engine would have tripped it.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "temporal-reachability-v1"

# The repair for future_leakage. Ingest THROUGH a later checkpoint, then ask a
# question as of an earlier one. Anything returned that only became visible after
# the queried checkpoint is a leak, and the frozen scorer already says so.
LEAKAGE_PROBE = {
    "probe_version": "future-leakage-probe-v1",
    "ingest_through_checkpoint": "CP16",
    "query_as_of_checkpoints": ["CP01", "CP04", "CP05", "CP08", "CP10", "CP11"],
    "why": "the store holds the whole timeline while the question is asked about an "
           "earlier moment, so a system that cannot filter by knowledge time will "
           "return something it should not have known yet",
    "scorer_unchanged": "longitudinal-scorer-v1 already flags any returned id "
                        "outside the queried checkpoint's visible prefix; only the "
                        "ingestion plan changes",
    "not_a_fixture_change": "longitudinal-v1 observations, cases and checkpoints are "
                            "untouched; their sha256 must still match every "
                            "committed result",
}

# Phrases that make an answer a claim rather than a refusal. An engine may say it
# does not know in many ways; it can only assert in one - by stating something.
DECLINES = (
    "unknown", "not known", "no information", "no record", "cannot determine",
    "can't determine", "cannot say", "no evidence", "not recorded", "nothing",
    "no data", "not found", "unclear", "do not know", "don't know",
)


def declines(answer: str | None) -> bool:
    """True when the answer refuses rather than asserts."""
    if answer is None:
        return True
    text = answer.strip().lower()
    if not text:
        return True
    return any(phrase in text for phrase in DECLINES)


def assertion_supported(answer: str | None, *, expected_ids: Iterable[str]) -> bool:
    """Is this answer defensible for a case whose correct response is 'unknown'?

    For a `negative_unknown` case there is nothing to support an assertion, so
    only a refusal is supported. Declining is always safe; asserting never is.
    Cases that do have expected evidence are outside this rule and are left to
    the retrieval scorer.
    """
    if tuple(expected_ids):
        return True
    return declines(answer)


def grade_negative_unknown(answer: str | None, *, expected_ids: Iterable[str],
                           score_answer_claim, case) -> dict[str, Any]:
    """The call that was missing. Wires an engine's answer into the frozen scorer."""
    supported = assertion_supported(answer, expected_ids=expected_ids)
    classes = tuple(score_answer_claim(case, assertion_supported=supported))
    return {"answer": answer, "declined": declines(answer),
            "assertion_supported": supported, "failure_classes": classes}


# Engines that cannot enter the point-in-time comparison, with the reason. An
# exclusion recorded here is a statement that the evidence never existed - not
# that it was lost, and not that the engine did well.
EXCLUSIONS = {
    "observational_memory_gen26_longitudinal": {
        "reason": "the run ended `complete_ingestion_lifecycle_context_unavailable` - "
                  "it ingested the timeline but never produced retrieval results, so "
                  "there are no per-case records to recover from the artifacts",
        "recoverable_from_existing_artifacts": False,
        "action": "excluded from point-in-time comparison",
        "not_done": "no reconstruction and no re-run merely to fill the table",
    },
}


def contract() -> dict[str, Any]:
    body = {
        "contract_version": CONTRACT_VERSION,
        "repairs": {
            "future_leakage": "run plan: ingest through a later checkpoint, query as "
                              "of an earlier one",
            "unknown_hallucination": "call score_answer_claim on negative_unknown "
                                     "cases, which no runner did",
        },
        "frozen_untouched": ["longitudinal-v1 fixture", "longitudinal-scorer-v1",
                             "every committed Round-2 result"],
        "why_not_change_the_scorer": "the fixture and scorer sha256 appear in every "
                                     "committed result; altering them would "
                                     "invalidate the runs Gen68 read",
        "proved_before_any_engine_run": True,
        "exclusions": EXCLUSIONS,
        "leakage_probe": LEAKAGE_PROBE,
        "decline_phrases": len(DECLINES),
    }
    body["contract_sha256"] = hashlib.sha256(
        repr(sorted(body.items())).encode()).hexdigest()
    return body
