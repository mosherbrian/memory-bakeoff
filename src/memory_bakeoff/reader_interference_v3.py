"""`reader-interference-v3`: semantic classification, freed from case composition.

v2 was frozen and never run, and control-plane review found a fifth defect in it
before any output existed. The bug is one line of my reasoning, repeated twice:

    said_current = case["current_opaque"] is not None and contains_value(...)
    said_stale   = case["stale_opaque"]   is not None and contains_value(...)

That conflates **"this role's record was not presented"** with **"this value is
not in the answer."** In `CLEAN_CURRENT` there is no stale record, so `said_stale`
was forced false and a reply saying *"41 t/s, previously 27 t/s"* graded
`correct_current_answer`. In `CLEAN_STALE_NEGATIVE_CONTROL` the mirror image
graded `correct_stale_control_answer`. **A self-contradicting answer could pass a
control gate**, which would have silently certified a core as interpretable.

v3 separates the two questions completely:

1. **What did the answer say?** Determined from the normalised text and the
   core's canonical values ALONE - never from `current_opaque`, `stale_opaque`,
   `records`, `context_order`, `condition` or `citations`.
2. **Is that correct here?** Determined afterwards, condition-relative.

`BOTH` therefore stays `BOTH` even when only one record was shown, and it always
resolves to `mixed_contradictory_answer`. No control can be passed by a
contradiction.

Everything else is carried forward from v2 unchanged: cores, record texts,
scopes, configurations, questions, conditions, opaque ids, prompt projection,
parser, canonical values, normalisation, response schema, control policy, and
the ban on deriving anything from Gen110 output. v2 is recorded
`SUPERSEDED_AS_RULER / NON_EVIDENCE` with every Gen111 byte intact.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from memory_bakeoff import reader_interference_v2 as V2

CONTRACT_VERSION = "reader-interference-v3"
SUPERSEDES = {"contract": "reader-interference-v2",
              "status": "SUPERSEDED_AS_RULER / NON_EVIDENCE",
              "artifacts_unchanged": True,
              "never_executed": True,
              "note": "v2 was frozen and never run, so no scientific result is "
                      "lost - only the ruler was wrong"}

# --- carried forward from v2, unchanged --------------------------------------
CONDITIONS = V2.CONDITIONS
CONFLICT_PAIR = V2.CONFLICT_PAIR
CONTROL_CONDITIONS = V2.CONTROL_CONDITIONS
CANONICAL = V2.CANONICAL
NORMALIZATION = V2.NORMALIZATION
INSTRUCTION = V2.INSTRUCTION
ACCEPT_JSON_FENCE = V2.ACCEPT_JSON_FENCE
INSUFFICIENT = V2.INSUFFICIENT
parse_response = V2.parse_response
project_prompt = V2.project_prompt
assert_prompt_is_blind = V2.assert_prompt_is_blind
assert_id_is_role_neutral = V2.assert_id_is_role_neutral
opaque_id = V2.opaque_id
normalise = V2.normalise
contains_value = V2.contains_value
build_fixture = V2.build_fixture
VALID_FIXTURES = V2.VALID_FIXTURES
INVALID_FIXTURES = V2.INVALID_FIXTURES
UNPARSED_STATES = V2.UNPARSED_STATES
CONTROL_RULE = V2.CONTROL_RULE
NOT_INTERPRETABLE = V2.NOT_INTERPRETABLE
ACROSS_CORE_VERDICTS = V2.ACROSS_CORE_VERDICTS
QUESTIONS = V2.QUESTIONS

OUTCOMES = V2.OUTCOMES
CORRECT_CURRENT = V2.CORRECT_CURRENT
PROHIBITED_STALE = V2.PROHIBITED_STALE
MIXED = V2.MIXED
CORRECT_STALE_CONTROL = V2.CORRECT_STALE_CONTROL
CORRECT_INSUFFICIENCY = V2.CORRECT_INSUFFICIENCY
INCORRECT_ABSTENTION = V2.INCORRECT_ABSTENTION
CITATION_MISMATCH = V2.CITATION_MISMATCH
UNSUPPORTED_VALUE = V2.UNSUPPORTED_VALUE
UNPARSED_OUTCOME = V2.UNPARSED_OUTCOME

CONTROL_PASSING = (CORRECT_CURRENT, CORRECT_STALE_CONTROL, CORRECT_INSUFFICIENCY)

# --- 1. semantic answer class: case composition is NOT consulted -------------
ANSWER_CLASSES = ("INSUFFICIENT", "BOTH", "CURRENT_ONLY", "STALE_ONLY", "NEITHER")


def classify_answer(answer: str, core: str) -> str:
    """What the answer SAID. Nothing about the case may influence this.

    Deliberately takes only the text and the core name - not the case - so the
    v2 defect is unrepresentable rather than merely unwritten.
    """
    values = CANONICAL[core]
    fold = values["casefold"]
    if normalise(answer, casefold=False) == INSUFFICIENT:
        return "INSUFFICIENT"
    said_current = contains_value(answer, values["current"], casefold=fold)
    said_stale = contains_value(answer, values["stale"], casefold=fold)
    if said_current and said_stale:
        return "BOTH"
    if said_current:
        return "CURRENT_ONLY"
    if said_stale:
        return "STALE_ONLY"
    return "NEITHER"


# --- 2. citation relation, computed only once the class is known -------------
CITATION_RELATIONS = ("EMPTY", "MATCHES_CURRENT", "MATCHES_STALE",
                      "UNKNOWN_ID", "OTHER")


def citation_relation(citations: Sequence[str], case: Mapping[str, Any]) -> str:
    cited = set(citations)
    known = {r["opaque_id"] for r in case["records"]}
    if not cited:
        return "EMPTY"
    if not cited <= known:
        return "UNKNOWN_ID"
    if case["current_opaque"] and cited == {case["current_opaque"]}:
        return "MATCHES_CURRENT"
    if case["stale_opaque"] and cited == {case["stale_opaque"]}:
        return "MATCHES_STALE"
    return "OTHER"


# --- 3. condition-relative grading, total and exclusive ----------------------
def grade(parsed: Mapping[str, Any], case: Mapping[str, Any]) -> dict[str, Any]:
    """Exactly one outcome. BOTH is never a control pass, in any condition."""
    if not parsed["parsed"]:
        return {"outcome": UNPARSED_OUTCOME, "answer_class": "UNPARSED",
                "citation_relation": "NONE", "why": parsed["parse_status"]}

    answer_class = classify_answer(parsed["answer"], case["core"])
    relation = citation_relation(parsed["citations"], case)
    condition = case["condition"]
    verdict = {"answer_class": answer_class, "citation_relation": relation}

    # Abstention is exclusive and legal only with an empty citation list.
    if answer_class == "INSUFFICIENT":
        if relation != "EMPTY":
            return {**verdict, "outcome": UNPARSED_OUTCOME,
                    "why": "INSUFFICIENT with a non-empty citation list"}
        return {**verdict,
                "outcome": CORRECT_INSUFFICIENCY if condition == "INSUFFICIENT_CONTROL"
                else INCORRECT_ABSTENTION,
                "why": "nothing supported an answer" if condition == "INSUFFICIENT_CONTROL"
                else "an answer was supported and the reader abstained"}

    # A substantive answer must carry a citation, and it must be a real one.
    if relation == "EMPTY":
        return {**verdict, "outcome": UNPARSED_OUTCOME,
                "why": "substantive answer with no citations"}
    if relation == "UNKNOWN_ID":
        return {**verdict, "outcome": UNPARSED_OUTCOME,
                "why": "cites an id that was not presented"}

    # BOTH is a contradiction wherever it appears. This is the v2 repair.
    if answer_class == "BOTH":
        return {**verdict, "outcome": MIXED,
                "why": "asserts both canonical values; a contradiction can "
                       "never pass a control"}
    if answer_class == "NEITHER":
        return {**verdict, "outcome": UNSUPPORTED_VALUE,
                "why": "answer matches no canonical value"}

    if condition == "CLEAN_STALE_NEGATIVE_CONTROL":
        if answer_class == "STALE_ONLY" and relation == "MATCHES_STALE":
            return {**verdict, "outcome": CORRECT_STALE_CONTROL,
                    "why": "the stale record is the only evidence; control works"}
        return {**verdict, "outcome": CITATION_MISMATCH,
                "why": "the only passing form here is STALE_ONLY with the "
                       "matching stale citation"}

    if answer_class == "STALE_ONLY":
        return {**verdict, "outcome": PROHIBITED_STALE,
                "why": "current truth was expected and stale was selected"}
    if relation != "MATCHES_CURRENT":
        return {**verdict, "outcome": CITATION_MISMATCH,
                "why": "current value with a non-matching citation"}
    return {**verdict, "outcome": CORRECT_CURRENT,
            "why": "current value with the matching current citation"}


# --- the exhaustive matrix ---------------------------------------------------
def truth_matrix() -> list[dict[str, Any]]:
    """Every condition x answer class x reachable citation relation."""
    rows: list[dict[str, Any]] = []
    for case in build_fixture()["cases"]:
        values = CANONICAL[case["core"]]
        texts = {
            "INSUFFICIENT": INSUFFICIENT,
            "BOTH": f"{values['current']} and {values['stale']}",
            "CURRENT_ONLY": values["current"],
            "STALE_ONLY": values["stale"],
            "NEITHER": "something else entirely",
        }
        citation_sets = {"EMPTY": []}
        if case["current_opaque"]:
            citation_sets["MATCHES_CURRENT"] = [case["current_opaque"]]
        if case["stale_opaque"]:
            citation_sets["MATCHES_STALE"] = [case["stale_opaque"]]
        if case["current_opaque"] and case["stale_opaque"]:
            citation_sets["OTHER"] = [case["current_opaque"], case["stale_opaque"]]
        citation_sets["UNKNOWN_ID"] = ["REC-0000000000"]

        for klass, text in texts.items():
            for relation, citations in citation_sets.items():
                reply = json.dumps({"answer": text, "citations": citations})
                result = grade(parse_response(reply), case)
                rows.append({
                    "condition": case["condition"], "core": case["core"],
                    "answer_class": klass, "citation_relation_requested": relation,
                    "observed_answer_class": result["answer_class"],
                    "observed_citation_relation": result["citation_relation"],
                    "outcome": result["outcome"]})
    return rows


def assert_no_control_pass_from_a_bad_answer(rows: Sequence[Mapping[str, Any]]) -> None:
    """No control-passing outcome may come from BOTH, NEITHER or a bad citation."""
    for row in rows:
        if row["outcome"] not in CONTROL_PASSING:
            continue
        if row["observed_answer_class"] in ("BOTH", "NEITHER"):
            raise ValueError(
                f"{row['condition']}/{row['core']}: {row['outcome']} reachable "
                f"from answer class {row['observed_answer_class']}")
        if row["observed_citation_relation"] in ("UNKNOWN_ID", "OTHER"):
            raise ValueError(
                f"{row['condition']}/{row['core']}: {row['outcome']} reachable "
                f"from citation relation {row['observed_citation_relation']}")


def control_passing_forms() -> dict[str, dict[str, str]]:
    """Exactly one (answer class, citation relation) passes each control."""
    forms: dict[str, set[tuple[str, str]]] = {c: set() for c in CONTROL_CONDITIONS}
    for row in truth_matrix():
        if row["condition"] in forms and row["outcome"] in CONTROL_PASSING:
            forms[row["condition"]].add(
                (row["observed_answer_class"], row["observed_citation_relation"]))
    for condition, seen in forms.items():
        if len(seen) != 1:
            raise ValueError(f"{condition} has {len(seen)} passing forms: {sorted(seen)}")
    return {c: {"answer_class": next(iter(s))[0],
                "citation_relation": next(iter(s))[1]} for c, s in forms.items()}


def core_is_interpretable(core_cells: Sequence[Mapping[str, Any]]) -> bool:
    return V2.core_is_interpretable(core_cells)


CHANGE_LEDGER = (
    {"field": "semantic answer classification", "change": "REPLACED",
     "defect": "detection was gated by case.current_opaque / case.stale_opaque, "
               "so an absent record-role pointer was read as absence of that "
               "value in the answer",
     "reason": "a reply containing BOTH canonical values graded "
               "correct_current_answer in CLEAN_CURRENT and "
               "correct_stale_control_answer in CLEAN_STALE_NEGATIVE_CONTROL - "
               "a contradiction could pass a control gate",
     "expected_effect": "BOTH is detected regardless of which records were "
                        "presented and always resolves to "
                        "mixed_contradictory_answer",
     "found_by": "control plane, reviewing the frozen v2 truth table and grader"},
    {"field": "citation relation", "change": "EXTRACTED",
     "defect": None,
     "reason": "computed only AFTER the answer class, so citation validity can "
               "never erase the fact that an answer is BOTH",
     "expected_effect": "the two judgements stay separable and serialized apart",
     "found_by": "executor, implementing the repair"},
    {"field": "cores, record texts, scopes, configurations, questions, five "
              "conditions, opaque ids, prompt projection, parser, canonical "
              "values, normalisation, response schema, control policy",
     "change": "UNCHANGED",
     "defect": None, "reason": "v3 repairs grading only",
     "expected_effect": "prompts are byte-identical to v2",
     "found_by": None},
)


def contract_hash() -> str:
    body = json.dumps({
        "version": CONTRACT_VERSION, "conditions": CONDITIONS,
        "outcomes": OUTCOMES, "answer_classes": ANSWER_CLASSES,
        "citation_relations": CITATION_RELATIONS, "questions": QUESTIONS,
        "canonical": CANONICAL, "normalization": NORMALIZATION,
        "instruction": INSTRUCTION, "accept_fence": ACCEPT_JSON_FENCE,
        "control_rule": CONTROL_RULE, "verdicts": ACROSS_CORE_VERDICTS,
        "ledger": CHANGE_LEDGER,
    }, sort_keys=True, default=str)
    return hashlib.sha256(body.encode()).hexdigest()
