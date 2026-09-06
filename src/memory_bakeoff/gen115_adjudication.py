"""`gen115-adjudication-v1`: how a Gen114 claim may be spoken about.

Frozen BEFORE any conclusion is recorded, because the outputs under review have
already been seen. Anything derived from looking at them is exploratory by
construction - the alternative is designing to observed outputs and then calling
those same outputs confirmatory.

Six fields are kept apart, and conflating them is how Gen114 went wrong:

  SOURCE ARTIFACT      which committed bytes the statement rests on
  BYTE OBSERVATION     what is literally in those bytes
  MACHINE LABEL        what frozen v4 code outputs, reproducibly
  SEMANTIC REVIEW      what a human/reviewer thinks the text MEANS - exploratory,
                       always, without exception
  PROTOCOL COMPLIANCE  whether the run followed its own declared procedure
  ALLOWED CLAIM        what may now be said in a report

Gen114's error was letting a MACHINE LABEL ("mixed_contradictory_answer") be
reported as a SEMANTIC FINDING ("the reader contradicts itself"). The label is
reproducible and stands; the finding does not follow from it.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

CONTRACT_VERSION = "gen115-adjudication-v1"

# --- claim statuses -----------------------------------------------------------
PRESERVED_RAW = "PRESERVED_RAW_OBSERVATION"
PRESERVED_LIMITED = "PRESERVED_WITH_PROVENANCE_LIMITATION"
RETRACTED = "RETRACTED_UNSUPPORTED"
OPEN_EXPLORATORY = "OPEN_EXPLORATORY"
CLAIM_STATUSES = (PRESERVED_RAW, PRESERVED_LIMITED, RETRACTED, OPEN_EXPLORATORY)

# --- exploratory semantic categories -----------------------------------------
# Deliberately finer than v4's outcome vocabulary. v4 had ONE bucket
# (mixed_contradictory_answer) for at least three distinct response forms.
CURRENT_ONLY = "CURRENT_ONLY"
STALE_ONLY = "STALE_ONLY"
UNRESOLVED_BOTH = "UNRESOLVED_BOTH"
RECONCILED_TO_CURRENT = "TEMPORAL_RECONCILIATION_TO_CURRENT"
RECONCILED_TO_STALE = "TEMPORAL_RECONCILIATION_TO_STALE"
EXPLICIT_CONTRADICTION = "EXPLICIT_CONTRADICTION"
AMBIGUOUS = "AMBIGUOUS"
UNPARSABLE = "UNPARSABLE"
SEMANTIC_CATEGORIES = (CURRENT_ONLY, STALE_ONLY, UNRESOLVED_BOTH,
                       RECONCILED_TO_CURRENT, RECONCILED_TO_STALE,
                       EXPLICIT_CONTRADICTION, AMBIGUOUS, UNPARSABLE)

EVIDENCE_CLASSIFICATION = {
    "gen114": "RESULT_PRESENT / PROTOCOL_INCOMPLETE / NOT_CONFIRMATORY",
    "why": "60 linked responses exist and the v4 machine grading reproduces "
           "exactly; the protocol was incomplete (no RUN_EVIDENCE marker, no "
           "focused tests, runner and grader absent from the pinned commit) and "
           "the semantic interpretation does not follow from the machine label",
    "raw_corpus": "PRESERVED - useful development evidence",
    "development_exposed": "the four cores and all observed wording are now "
                           "development-exposed and can NEVER serve as an "
                           "independent confirmatory set for a repaired ruler",
}

# --- decision rules, frozen before the audit ---------------------------------
DECISION_RULES = (
    {"id": "R1", "rule": "A machine label is never by itself a semantic finding. "
                         "v4 outputs a class; what the text MEANS is a separate "
                         "question with a separate answer."},
    {"id": "R2", "rule": "All post-run semantic review is EXPLORATORY, without "
                         "exception, because the outputs were already observed "
                         "before the categories were written."},
    {"id": "R3", "rule": "Presence of a canonical substring never determines "
                         "semantic category on its own. Every category carries a "
                         "written rationale referring to the actual sentence."},
    {"id": "R4", "rule": "A response naming both values in an explicit temporal "
                         "order that ENDS at the current value is a coherent "
                         "reconciliation, not a contradiction. It answers the "
                         "question and adds history."},
    {"id": "R5", "rule": "A response naming both values with no ordering, no "
                         "resolution and no selection is UNRESOLVED_BOTH - a "
                         "failure to select, which is NOT automatically a "
                         "logical contradiction."},
    {"id": "R6", "rule": "EXPLICIT_CONTRADICTION requires the text to assert two "
                         "incompatible states as simultaneously current. Nothing "
                         "weaker earns that label."},
    {"id": "R7", "rule": "Gen114 bytes are immutable. No rescoring, no backfilled "
                         "markers, no edits to results/gen114/attempt1."},
)


def assert_not_confirmatory(record: Mapping[str, Any]) -> None:
    """Semantic review may never be recorded as confirmatory."""
    if record.get("semantic_category") and record.get("confirmatory"):
        raise ValueError(
            f"{record.get('call_index')}: semantic review marked confirmatory; "
            "the outputs were observed before the categories existed (R2)")


def assert_rationale_present(rows: Sequence[Mapping[str, Any]]) -> None:
    """R3: no category without a written reason referring to the sentence."""
    missing = [r["call_index"] for r in rows
               if r.get("semantic_category") and not str(r.get("rationale", "")).strip()]
    if missing:
        raise ValueError(f"semantic category without rationale at {missing} (R3)")


def assert_machine_label_not_reused_as_finding(text: str) -> None:
    """R1: the phrase that caused this generation."""
    lowered = " ".join(str(text).split()).lower()
    for bad in ("the reader contradicts itself in 21",
                "21 of 24 contradictions",
                "21 of 24 conflict cells contradict"):
        if bad in lowered:
            raise ValueError(f"machine label restated as a semantic finding: {bad!r} (R1)")


def contract_hash() -> str:
    body = json.dumps({"version": CONTRACT_VERSION,
                       "claim_statuses": CLAIM_STATUSES,
                       "semantic_categories": SEMANTIC_CATEGORIES,
                       "decision_rules": DECISION_RULES,
                       "evidence_classification": EVIDENCE_CLASSIFICATION},
                      sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()
