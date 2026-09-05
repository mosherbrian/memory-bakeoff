"""`procedure-reachability-audit-v1`: what "0/3 recommended_procedure" actually measures.

Gen68 reported `recommended_procedure` as 0/3 for all four engines - the only axis
on which nobody scored anything. Every other universal zero in this programme has
turned out to be the harness rather than the products: Gen69 found classes that
could not fire, Gen73 found an effective-time question asked through a
knowledge-time coordinate, Gen76 found engines that were never asked to isolate.
This module applies the same treatment before the number is interpreted.

Three questions, answered without any engine call.

**Reachability.** Can `procedure_recommendation_missing` and
`failed_procedure_adoption` each fire, and can the case stay silent under a
correct answer? A class that cannot fire reports a zero that means nothing, and a
case that cannot be passed reports a failure that means nothing either.

**Trace.** What did each frozen adapter actually write and retrieve for the single
procedure case, LQ10? This is read from the committed Round-2 records, not
re-run.

**Attribution.** Is the resulting zero evidence about retrievable memory, about an
answer/reader capability the harness never invokes, or about an adapter omission?
These have different fixes and must not be collapsed.

The distinction that organises the answer: **retrieving the record and choosing
between two records are different capabilities.** LQ10 holds `L007` (an attempt
that failed) and `L008` (an attempt that succeeded). They share a truth key, a
scope, a configuration, and nearly all of their wording. Ranking one above the
other is retrieval; knowing that the successful one is the *recommended* one is
reading. The scorer grades only the first and charges the second.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "procedure-reachability-audit-v1"

CASE_ID = "LQ10"
CHECKPOINT_ID = "CP08"
EXPECTED = "L008"
PROHIBITED = "L007"

# Attribution values. Not a scale, and deliberately not mutually exclusive.
RETRIEVABLE_MEMORY = "tests_retrievable_memory"
READER_CAPABILITY = "tests_reader_capability"
ADAPTER_OMISSION = "adapter_omission"
NOT_DEMONSTRABLE = "not_demonstrable"
NOT_APPLICABLE = "not_applicable"

# Measured from the committed Round-2 records: results/<engine>/repetition-N.json,
# case LQ10, three repetitions each. Ranks are 1-based positions in the returned
# window; `None` means the id was outside it.
OBSERVED = {
    "perseus": {"limit": 5, "expected_rank": 1, "prohibited_rank": 2,
                "returned": ("L008", "L007", "L002", "L004", "L001")},
    "hindsight": {"limit": 5, "expected_rank": 5, "prohibited_rank": 2,
                  "returned": ("L006", "L007", "L001", "L003", "L008")},
    "mem0": {"limit": 5, "expected_rank": 2, "prohibited_rank": 4,
             "returned": ("L005", "L008", "L002", "L007", "L004")},
    "agentmemory": {"limit": 5, "expected_rank": 1, "prohibited_rank": 2,
                    "returned": ("L008", "L007", "L004", "L005", "L006")},
}
REPETITIONS = 3
# Every repetition of every engine returned the same window; recorded so a reader
# knows the table above is not one sample dressed up as four.
OBSERVED_IS_STABLE_ACROSS_REPETITIONS = True


def retrieved_the_answer(engine: str) -> bool:
    return OBSERVED[engine]["expected_rank"] is not None


def outranked_the_wrong_answer(engine: str) -> bool:
    entry = OBSERVED[engine]
    if entry["expected_rank"] is None:
        return False
    if entry["prohibited_rank"] is None:
        return True
    return entry["expected_rank"] < entry["prohibited_rank"]


def controls(score, fixture, case) -> dict[str, Any]:
    """Prove each class can fire, and that a correct answer scores silent.

    `score` is the frozen scorer. Nothing here is asserted about engines - these
    are constructed return sets fed to the real scoring function.
    """
    def classes(returned):
        return tuple(score(fixture, case, returned).failure_classes)
    return {
        "silent_on_correct_answer": {
            "returned": (EXPECTED,), "classes": classes((EXPECTED,))},
        "missing_fires_on_empty": {
            "returned": (), "classes": classes(())},
        "missing_fires_on_unrelated": {
            "returned": ("L001", "L002"), "classes": classes(("L001", "L002"))},
        "adoption_fires_on_both": {
            "returned": (EXPECTED, PROHIBITED),
            "classes": classes((EXPECTED, PROHIBITED))},
        "silent_with_correct_plus_unrelated": {
            "returned": (EXPECTED, "L001", "L002"),
            "classes": classes((EXPECTED, "L001", "L002"))},
    }


def discriminability(fixture, query: str) -> dict[str, Any]:
    """Can the query text separate the two procedure records at all?

    The scorer has no notion of rank: `prohibited & returned` is a failure wherever
    the wrong record lands. So passing LQ10 requires a retrieval window that holds
    the right record and excludes its nearest neighbour - which is a property of
    the query and the corpus, not of any engine.
    """
    import re
    tokens = set(re.findall(r"[a-z]+", query.lower()))
    visible = fixture.prefix(CHECKPOINT_ID)
    overlaps = {
        o.id: sorted(tokens & set(re.findall(r"[a-z]+", o.assertion.lower())))
        for o in visible
    }
    by_id = {o.id: o for o in visible}
    expected, prohibited = by_id[EXPECTED], by_id[PROHIBITED]
    return {
        "query": query,
        "query_tokens": sorted(tokens),
        "corpus_size_at_checkpoint": len(visible),
        "lexical_overlap": overlaps,
        "observations_sharing_a_query_token": sorted(k for k, v in overlaps.items() if v),
        "pair_shares_truth_key": expected.truth_key == prohibited.truth_key,
        "pair_shares_scope": expected.scope == prohibited.scope,
        "pair_shares_configuration": expected.configuration == prohibited.configuration,
        "distinguishing_evidence": "the words 'succeeded' and 'failed' inside the "
                                   "assertion text; nothing structural",
        "outcome_label_published": False,
        "why": "procedure_outcome is on every adapter's forbidden-input list, so no "
               "engine is told which attempt succeeded; and the query shares no "
               "word with any record, so ranking cannot separate two sentences that "
               "differ by one verb",
    }


def window_pressure(corpus_size: int, limit: int) -> dict[str, Any]:
    """How much of the store a limit-N window covers, and what that costs.

    Recorded because the scored quantity is set membership. A window covering most
    of a small corpus will contain the prohibited record almost regardless of how
    well the engine ranks.
    """
    from math import comb
    passing = comb(corpus_size - 2, limit - 1) if limit >= 1 else 0
    total = comb(corpus_size, limit)
    return {
        "corpus_size": corpus_size,
        "limit": limit,
        "fraction_of_corpus_returned": limit / corpus_size,
        "windows_containing_expected_and_excluding_prohibited": passing,
        "windows_total": total,
        "chance_of_passing_under_uniform_sampling": passing / total,
        "note": "uniform sampling is the optimistic bound; similarity ranking makes "
                "the two nearest neighbours in the store MORE likely to co-occur, "
                "not less",
    }


def attribution(observed: Mapping[str, Mapping[str, Any]] = OBSERVED) -> dict[str, Any]:
    """What the zero is evidence about."""
    retrieved = sorted(e for e in observed if retrieved_the_answer(e))
    outranked = sorted(e for e in observed if outranked_the_wrong_answer(e))
    return {
        "engines_that_retrieved_the_recommendation": retrieved,
        "engines_that_ranked_it_above_the_failed_attempt": outranked,
        "procedure_recommendation_missing_observed": 0,
        "failed_procedure_adoption_observed": len(observed) * REPETITIONS,
        "retrievable_memory_verdict": RETRIEVABLE_MEMORY if len(retrieved) < len(observed)
                                      else NOT_APPLICABLE,
        "reader_capability_verdict": READER_CAPABILITY,
        "adapter_omission_verdict": ADAPTER_OMISSION,
        "reading": "every engine, in every repetition, returned the recommended "
                   "procedure. Not one instance of procedure_recommendation_missing "
                   "exists in the record. The universal zero is entirely "
                   "failed_procedure_adoption - charged for the failed attempt also "
                   "appearing in a window covering five of eight records.",
    }


def verdict() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "case": CASE_ID,
        "engine_procedure_memory": NOT_DEMONSTRABLE,
        "why_not_demonstrable": "the case cannot distinguish an engine that lost the "
                                "recommendation from one that returned it first; both "
                                "score identically, and only the second ever happened",
        "what_the_axis_actually_exercises": READER_CAPABILITY,
        "harness_defect": ADAPTER_OMISSION,
        "harness_defect_detail": "LongitudinalResultRecord carries a reader_answer "
                                 "field, score_answer_claim exists, and no runner "
                                 "populates or calls either for this target kind; the "
                                 "case is graded on retrieved ids alone",
        "gen68_line_status": "REATTRIBUTED - 0/3 across four engines is not evidence "
                             "that nobody adopts the recommended procedure; it is one "
                             "unpassable case, and the number should not be read as a "
                             "memory result",
        "no_engine_runs": True,
    }
