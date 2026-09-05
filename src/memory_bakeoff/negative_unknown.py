"""`negative-unknown-audit-v1`: two capabilities behind one universal zero.

Gen68 reported `negative_unknown` as 0/3 for all four engines. Gen83 showed the
other universal zero on that table was an unpassable case rather than a memory
result; this module gives the second one the same treatment, and finds a
different — and more specific — defect.

`LQ16` asks *"Nimbus on call"* at `CP04`, expects no evidence, and prohibits
nothing. The scorer charges `unsupported_evidence` for anything returned. The
only clean answer is the empty result set.

**The split this module enforces.** Answering a question that has no answer is
two separate abilities, and the benchmark collapses them:

- **retrieval abstention** — can the retrieval surface return nothing? That needs
  a relevance floor the caller can set, and a score the caller can see.
- **answer abstention** — can a reader say "unknown" while holding retrieved
  distractors? That is what `score_answer_claim` grades, and it is a property of
  the reader, not of the store.

Scoring top-k retrieval as hallucination charges the first for failing at the
second. A retriever asked for the best five of four records did exactly what it
was asked; refusing was never on the menu.

**Deliberately not done here.** No reader is added. Gen68's zero has to be
attributed before anything is built to fix it, and a reader is a new
configuration boundary that belongs to its own generation.
"""
from __future__ import annotations

from typing import Any, Mapping

CONTRACT_VERSION = "negative-unknown-audit-v1"

CASE_ID = "LQ16"
CHECKPOINT_ID = "CP04"

# Layer verdicts.
FLOOR_PRESENT = "caller_settable_relevance_floor"
NO_FLOOR = "NO_ABSTENTION_SURFACE"
NOT_DEMONSTRABLE = "not_demonstrable"
NOT_APPLICABLE = "not_applicable"

# Read from each frozen adapter's own argument list, not from documentation.
ABSTENTION_SURFACE = {
    "perseus": {
        "arguments": ("query", "workspace_hash", "limit", "mode"),
        "relevance_floor": None,
        "scores_returned": False,
        "status": NO_FLOOR,
        "note": "recall exposes no threshold, and the records carry no score at "
                "all, so neither the engine nor the harness could apply one",
    },
    "hindsight": {
        "arguments": ("bank_id", "query", "max_tokens"),
        "relevance_floor": None,
        "scores_returned": True,
        "status": NO_FLOOR,
        "note": "max_tokens is a size budget, not a relevance floor; scores come "
                "back but nothing consumes them",
    },
    "mem0": {
        "arguments": ("query", "filters", "limit", "threshold"),
        "relevance_floor": 0.1,
        "scores_returned": True,
        "status": FLOOR_PRESENT,
        "note": "the only engine of the four with a caller-settable floor; the "
                "frozen Gen32 adapter pins it at 0.1",
    },
    "agentmemory": {
        "arguments": ("agentId", "project", "query", "limit"),
        "relevance_floor": None,
        "scores_returned": True,
        "status": NO_FLOOR,
        "note": "smart-search exposes no threshold; it returned 2 of 4 records, so "
                "some internal cut exists, but it is not caller-settable",
    },
}

# Measured from results/<engine>/repetition-1.json. `top_score` is the score of
# the highest-ranked row for LQ16; `cases_scoring_lower` counts scored cases WITH
# expected evidence that peaked below it.
OBSERVED = {
    "perseus": {"returned": 4, "top_score": None, "cases_scoring_lower": None,
                "total_scored_cases": None},
    "hindsight": {"returned": 4, "top_score": 0.04097377804291001,
                  "cases_scoring_lower": 6, "total_scored_cases": 19},
    "mem0": {"returned": 4, "top_score": 0.4644287432525836,
             "cases_scoring_lower": 1, "total_scored_cases": 19},
    "agentmemory": {"returned": 2, "top_score": 1.05,
                    "cases_scoring_lower": 13, "total_scored_cases": 19},
}
CORPUS_AT_CHECKPOINT = 4
REQUESTED_LIMIT = 5
REPETITIONS = 3


def separable(engine: str) -> dict[str, Any]:
    """Could ANY threshold abstain on LQ16 without silencing a real question?

    A floor high enough to reject LQ16 also rejects every legitimate case that
    peaked below it. Where that count is non-zero, abstention by threshold costs
    real answers; where scores are absent, no threshold is expressible at all.
    """
    entry = OBSERVED[engine]
    if entry["top_score"] is None:
        return {"engine": engine, "separable": NOT_DEMONSTRABLE,
                "why": "no scores are returned, so no threshold is expressible"}
    cost = entry["cases_scoring_lower"]
    return {
        "engine": engine,
        "separable": cost == 0,
        "legitimate_cases_lost_at_that_floor": cost,
        "of_scored_cases": entry["total_scored_cases"],
        "why": "a floor above the unanswerable question's own score also rejects "
               f"{cost} question(s) that do have an answer",
    }


def controls(score_case, score_claim, fixture, case) -> dict[str, Any]:
    """Both layers, each proved to fire and to stay silent."""
    def retrieval(returned):
        return tuple(score_case(fixture, case, returned).failure_classes)
    return {
        "retrieval_abstention": {
            "silent_on_empty": {"returned": (), "classes": retrieval(())},
            "fires_on_one_record": {"returned": ("L001",), "classes": retrieval(("L001",))},
            "fires_on_the_whole_store": {
                "returned": ("L001", "L002", "L003", "L004"),
                "classes": retrieval(("L001", "L002", "L003", "L004"))},
        },
        "answer_abstention": {
            "silent_on_refusal": {"supported": True,
                                  "classes": tuple(score_claim(case, assertion_supported=True))},
            "fires_on_assertion": {"supported": False,
                                   "classes": tuple(score_claim(case, assertion_supported=False))},
        },
    }


def layers() -> dict[str, Any]:
    """What each layer can and cannot say, per engine."""
    out = {}
    for engine, surface in ABSTENTION_SURFACE.items():
        floor = surface["status"] == FLOOR_PRESENT
        out[engine] = {
            "retrieval_abstention_surface": surface["status"],
            "retrieval_abstention_exercised": floor,
            "retrieval_abstention_verdict": (
                "measured_and_failed" if floor else NOT_DEMONSTRABLE),
            "answer_abstention_verdict": NOT_DEMONSTRABLE,
            "answer_abstention_why": "score_answer_claim was never called in Round 2 "
                                     "and no reader answer exists to grade",
            "separability": separable(engine),
        }
    return out


def verdict() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "case": CASE_ID,
        "what_the_0_of_3_measured": "top-k retrieval, scored as if it were an "
                                    "abstention decision",
        "retrieval_abstention": "NOT_DEMONSTRABLE for perseus, hindsight and "
                                "agentmemory - no caller-settable relevance floor "
                                "exists on those surfaces; mem0 has one, pinned at "
                                "0.1, and no setting of it separates this case",
        "answer_abstention": NOT_DEMONSTRABLE,
        "answer_abstention_why": "no reader answer was ever produced or graded; "
                                 "the capability the case is named for was never "
                                 "exercised",
        "gen68_line_status": "RETRACTED - 'every engine returns evidence for a "
                             "question whose answer should be unknown' describes "
                             "the harness asking for top-k and charging the answer "
                             "to the engine, not a measured hallucination",
        "unknown_hallucination_status": "reachable since Gen69, still never fired "
                                        "in a scored Round-2 run",
        "no_reader_added": True,
        "no_engine_runs": True,
    }
