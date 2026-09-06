"""`reader-interference-v1`: does a stale record alongside the current one change the answer?

Round 3 closed with one result that generalised: every engine co-returns the
superseded record beside the current one, 192 of 192. It never asked whether
that **changes an answer**. This contract asks exactly that, and is frozen
before any model is called.

**Parsing is not grading.** The two were entangled in Gen85 and it cost the
whole attempt: a `CITE:` pattern anchored to line start scored valid inline
citations as UNPARSED, and the scorer then charged them as substantive
failures. Here a parse failure is `UNPARSED` and nothing else - never a stale
answer, never an abstention, never a model failure. The deterministic grader,
not the reader, assigns the final decision from benchmark truth.

**Order is a variable, not an accident.** `CONFLICT_STALE_FIRST` and
`CONFLICT_CURRENT_FIRST` present the identical two records and differ in
nothing but sequence. `assert_conflict_pair_differs_only_in_order` raises if
anything else drifts.

Gen85 establishes nothing here. Its outputs are QUARANTINED and may not seed a
fixture, threshold, example or verdict rule.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

CONTRACT_VERSION = "reader-interference-v1"

# --- conditions ---------------------------------------------------------------
CLEAN_CURRENT = "CLEAN_CURRENT"
CONFLICT_STALE_FIRST = "CONFLICT_STALE_FIRST"
CONFLICT_CURRENT_FIRST = "CONFLICT_CURRENT_FIRST"
CLEAN_STALE_NEGATIVE_CONTROL = "CLEAN_STALE_NEGATIVE_CONTROL"
INSUFFICIENT_CONTROL = "INSUFFICIENT_CONTROL"
CONDITIONS = (CLEAN_CURRENT, CONFLICT_STALE_FIRST, CONFLICT_CURRENT_FIRST,
              CLEAN_STALE_NEGATIVE_CONTROL, INSUFFICIENT_CONTROL)
CONFLICT_PAIR = (CONFLICT_STALE_FIRST, CONFLICT_CURRENT_FIRST)

# --- response contract --------------------------------------------------------
DECISIONS = ("CURRENT", "STALE", "MIXED", "INSUFFICIENT", "UNPARSED")

# Deliberately NOT anchored with `^`. Gen85 attempt 1 used `^\s*CITE:` under
# MULTILINE, so a reply that put its citation inline parsed as UNPARSED and was
# then scored as a substantive failure. Placement is presentation; it may not
# change whether a semantically valid response parses.
ANSWER_PATTERN = re.compile(r"ANSWER:\s*(.+?)\s*$", re.MULTILINE)
CITE_PATTERN = re.compile(r"CITE:\s*(.+?)\s*$", re.MULTILINE)
RECORD_ID_PATTERN = re.compile(r"\bC[0-3]-(?:CUR|SUP)\b")
NO_CITATION = "NONE"

RESPONSE_INSTRUCTION = (
    "Answer the question using only the records provided.\n"
    "Write one line beginning ANSWER: with your answer.\n"
    "Write CITE: followed by the record ids you used, or CITE: NONE if the "
    "records do not answer the question.\n"
    "If the records do not contain the answer, say so and cite NONE."
)

# --- parse outcomes (NOT grades) ---------------------------------------------
PARSED = "PARSED"
UNPARSED_NO_ANSWER = "UNPARSED_NO_ANSWER_LINE"
UNPARSED_NO_CITE = "UNPARSED_NO_CITE_LINE"
UNPARSED_BAD_CITE = "UNPARSED_UNREADABLE_CITE"

# --- grades (assigned by the harness, never by the model) ---------------------
CORRECT_CURRENT = "correct_current_answer"
PROHIBITED_STALE = "prohibited_stale_answer"
MIXED_ANSWER = "mixed_contradictory_answer"
CORRECT_INSUFFICIENCY = "correct_insufficiency"
INCORRECT_ABSTENTION = "incorrect_abstention"
CITATION_MISMATCH = "citation_mismatch"
UNPARSED_OUTCOME = "unparsed_response"
GRADES = (CORRECT_CURRENT, PROHIBITED_STALE, MIXED_ANSWER, CORRECT_INSUFFICIENCY,
          INCORRECT_ABSTENTION, CITATION_MISMATCH, UNPARSED_OUTCOME)


def parse_response(text: str) -> dict[str, Any]:
    """Read the reply. Assign NO grade - that is the grader's job alone."""
    answers = ANSWER_PATTERN.findall(text or "")
    cites = CITE_PATTERN.findall(text or "")
    if not answers:
        return {"parse_status": UNPARSED_NO_ANSWER, "parsed": False,
                "answer_text": None, "cited_record_ids": ()}
    if not cites:
        return {"parse_status": UNPARSED_NO_CITE, "parsed": False,
                "answer_text": answers[-1], "cited_record_ids": ()}
    # An INLINE citation would otherwise leave "CITE: ..." inside answer_text,
    # where a record id could later be mistaken for an asserted value.
    answer_text = re.sub(r"\s*CITE:.*$", "", answers[-1]).strip()
    final = cites[-1]                      # the LAST citation anywhere in the reply
    ids = tuple(dict.fromkeys(RECORD_ID_PATTERN.findall(final)))
    if not ids and NO_CITATION not in final.upper():
        return {"parse_status": UNPARSED_BAD_CITE, "parsed": False,
                "answer_text": answer_text, "cited_record_ids": ()}
    return {"parse_status": PARSED, "parsed": True,
            "answer_text": answer_text, "cited_record_ids": ids}


def grade(parsed: Mapping[str, Any], *, current_id: str | None,
          stale_id: str | None, current_answer: str | None,
          stale_answer: str | None, answerable: bool) -> dict[str, Any]:
    """Deterministic. Benchmark truth plus the parsed reply. No model self-report."""
    if not parsed["parsed"]:
        return {"grade": UNPARSED_OUTCOME, "decision": "UNPARSED",
                "why": parsed["parse_status"]}

    text = (parsed["answer_text"] or "").lower()
    cited = set(parsed["cited_record_ids"])
    says_current = bool(current_answer) and current_answer.lower() in text
    says_stale = bool(stale_answer) and stale_answer.lower() in text
    abstained = not cited and not says_current and not says_stale

    if says_current and says_stale:
        return {"grade": MIXED_ANSWER, "decision": "MIXED",
                "why": "the reply asserts both the current and the stale value"}
    if not answerable:
        return ({"grade": CORRECT_INSUFFICIENCY, "decision": "INSUFFICIENT",
                 "why": "no supported answer exists and the reader abstained"}
                if abstained else
                {"grade": PROHIBITED_STALE if says_stale else CITATION_MISMATCH,
                 "decision": "STALE" if says_stale else "CURRENT",
                 "why": "answered where nothing supports an answer"})
    if abstained:
        return {"grade": INCORRECT_ABSTENTION, "decision": "INSUFFICIENT",
                "why": "an answer was supported and the reader abstained"}
    if says_stale:
        return {"grade": PROHIBITED_STALE, "decision": "STALE",
                "why": "answered from the superseded record"}
    if says_current:
        if current_id and cited and current_id not in cited:
            return {"grade": CITATION_MISMATCH, "decision": "CURRENT",
                    "why": f"answer is current but cites {sorted(cited)}"}
        return {"grade": CORRECT_CURRENT, "decision": "CURRENT",
                "why": "answered from the current record"}
    return {"grade": CITATION_MISMATCH, "decision": "CURRENT",
            "why": "the answer matches neither the current nor the stale value"}


# --- pre-registered questions -------------------------------------------------
QUESTIONS: tuple[dict[str, Any], ...] = (
    {"id": "Q1",
     "question": "Does adding the stale record increase stale or mixed answers "
                 "relative to CLEAN_CURRENT?",
     "compares": [CLEAN_CURRENT, CONFLICT_STALE_FIRST, CONFLICT_CURRENT_FIRST],
     "rule": "per core: effect if (PROHIBITED_STALE + MIXED_ANSWER) in either "
             "conflict condition exceeds CLEAN_CURRENT; no effect if equal or lower"},
    {"id": "Q2",
     "question": "With identical records present, does swapping presentation "
                 "order change the decision?",
     "compares": list(CONFLICT_PAIR),
     "rule": "per core: order effect if the grade distributions of the two "
             "conflict conditions differ in any cell; otherwise none"},
    {"id": "Q3",
     "question": "Does the reader consistently prefer current truth when both "
                 "versions are available?",
     "compares": list(CONFLICT_PAIR),
     "rule": "per core: prefers-current only if every conflict cell grades "
             "CORRECT_CURRENT; any stale or mixed answer refutes it"},
    {"id": "Q4",
     "question": "Are observed effects replicated across all four cores, "
                 "fixture-specific, or partial?",
     "compares": ["all cores"],
     "rule": "REPLICATED_ACROSS_CORES if the Q1 effect holds in 4 of 4 cores; "
             "FIXTURE_SPECIFIC if in exactly 1; PARTIAL_REPLICATION if 2 or 3. "
             "Cores are never averaged"},
    {"id": "Q5",
     "question": "Does the parser accept every contract-valid formatting "
                 "variant without accepting malformed output?",
     "compares": ["parser regression fixtures"],
     "rule": "pass only if every valid variant parses AND every malformed "
             "variant is UNPARSED. Placement may never change the outcome"},
)

ACROSS_CORE_VERDICTS = ("REPLICATED_ACROSS_CORES", "PARTIAL_REPLICATION",
                        "FIXTURE_SPECIFIC")

EXECUTION_BOUNDARY = {
    "gen109_runs_nothing": True,
    "future_run_must": [
        "consume this fixture and contract unmodified",
        "record model/backend, exact model id, prompt hash, temperature, seed "
        "when supported, request and response fingerprints, repetition number",
        "use predeclared repetitions and REPORT variation when the backend "
        "cannot guarantee deterministic sampling, never silently pick one",
        "write only under immutable-evidence-v1 attempt paths",
    ],
    "future_run_must_not": [
        "manufacture a product-linked mapping from missing historical cells",
        "use any fixed mutable result path or overwrite flag",
    ],
}

GEN85_STATUS = {
    "verdict": "QUARANTINED / NOT EVIDENCE",
    "on_main": False,
    "location": "branch reader-layer-gen85 only; never merged",
    "defect": r"attempt 1 anchored the citation as ^\s*CITE: under MULTILINE, so "
              "a reply citing inline parsed as UNPARSED and was then scored as a "
              "substantive failure",
    "may_not": ["seed a fixture", "set a threshold", "serve as a baseline",
                "provide hand-tuning examples", "influence a verdict rule"],
}


# --- guards -------------------------------------------------------------------
def assert_parse_and_grade_are_separate(record: Mapping[str, Any]) -> None:
    if record.get("parse_status") in (PARSED, None):
        return
    if record.get("grade") not in (UNPARSED_OUTCOME, None):
        raise ValueError(
            f"unparsed reply graded {record.get('grade')!r}: a parse failure is "
            "not a stale answer, an abstention or a model failure")


def assert_no_outcome_pooling(payload: Any) -> None:
    """stale, mixed, insufficient and unparsed are four outcomes, not one."""
    def walk(node: Any, path: str = "") -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                where = f"{path}.{key}" if path else str(key)
                low = str(key).lower()
                if any(w in low for w in ("total_failures", "failure_rate",
                                          "error_rate", "reader_score",
                                          "combined_outcome", "pooled")):
                    raise ValueError(f"{where}: pools distinct reader outcomes")
                walk(value, where)
        elif isinstance(node, (list, tuple)):
            for i, item in enumerate(node):
                walk(item, f"{path}[{i}]")
    walk(payload)


def assert_conflict_pair_differs_only_in_order(a: Mapping[str, Any],
                                               b: Mapping[str, Any]) -> None:
    """The two conflict conditions may differ in sequence and nothing else."""
    ignore = {"condition", "context_order", "id"}
    for key in set(a) | set(b):
        if key in ignore:
            continue
        if a.get(key) != b.get(key):
            raise ValueError(
                f"conflict conditions differ in {key!r}: {a.get(key)!r} vs "
                f"{b.get(key)!r}; order must be the only difference")
    if list(a.get("context_order", ())) == list(b.get("context_order", ())):
        raise ValueError("conflict conditions must differ in context_order")
    if sorted(a.get("context_order", ())) != sorted(b.get("context_order", ())):
        raise ValueError("conflict conditions must present the SAME records")


def assert_no_gen85_influence(payload: Any) -> None:
    text = json.dumps(payload, default=str, sort_keys=True).lower()
    for marker in ("gen85", "reader_layer_gen85", "order_ablation"):
        if marker in text and "quarantin" not in text:
            raise ValueError(f"Gen85 material ({marker}) used as evidence")


def assert_within_core(case: Mapping[str, Any]) -> None:
    for field in ("core", "scope", "configuration"):
        values = {r.get(field) for r in case.get("records", ())}
        if len(values) > 1:
            raise ValueError(f"case {case.get('id')} crosses {field}: {values}")


def contract_hash() -> str:
    """Changing the frozen contract must change this."""
    body = json.dumps({
        "version": CONTRACT_VERSION, "conditions": CONDITIONS,
        "decisions": DECISIONS, "grades": GRADES,
        "questions": QUESTIONS, "verdicts": ACROSS_CORE_VERDICTS,
        "instruction": RESPONSE_INSTRUCTION,
        "answer_pattern": ANSWER_PATTERN.pattern,
        "cite_pattern": CITE_PATTERN.pattern,
        "id_pattern": RECORD_ID_PATTERN.pattern,
    }, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


# --- fixtures, derived from the four frozen Round 3 cores ----------------------
def build_fixture() -> dict[str, Any]:
    """Reuse the Round 3 cores verbatim. No new semantic neighbourhoods.

    Each core already carries a current/superseded pair with its own scope and
    configuration identity. Those are preserved exactly; this generation adds
    only the reader question and the presentation conditions.
    """
    from memory_bakeoff import interference_v3 as V3

    source = V3.build_fixture()
    cases: list[dict[str, Any]] = []
    for core in sorted({o.core for o in source.observations}):
        mine = [o for o in source.observations if o.core == core]
        current = next(o for o in mine if o.role == "current")
        stale = next(o for o in mine if o.role == "superseded")
        question = next((c.query for c in source.cases if c.core == core), None)

        def record(observation) -> dict[str, Any]:
            return {"id": observation.id, "text": observation.text,
                    "core": observation.core, "scope": observation.scope,
                    "configuration": observation.configuration,
                    "role": observation.role}

        cur, sup = record(current), record(stale)
        common = {"core": core, "question": question,
                  "current_id": cur["id"], "stale_id": sup["id"],
                  "current_answer": cur["text"], "stale_answer": sup["text"],
                  "records": [cur, sup], "answerable": True,
                  "instruction": RESPONSE_INSTRUCTION}
        cases.extend([
            {**common, "id": f"{core}|{CLEAN_CURRENT}",
             "condition": CLEAN_CURRENT, "records": [cur],
             "context_order": [cur["id"]], "stale_id": None,
             "stale_answer": None},
            {**common, "id": f"{core}|{CONFLICT_STALE_FIRST}",
             "condition": CONFLICT_STALE_FIRST,
             "context_order": [sup["id"], cur["id"]]},
            {**common, "id": f"{core}|{CONFLICT_CURRENT_FIRST}",
             "condition": CONFLICT_CURRENT_FIRST,
             "context_order": [cur["id"], sup["id"]]},
            {**common, "id": f"{core}|{CLEAN_STALE_NEGATIVE_CONTROL}",
             "condition": CLEAN_STALE_NEGATIVE_CONTROL, "records": [sup],
             "context_order": [sup["id"]], "current_id": None,
             "current_answer": None},
            {**common, "id": f"{core}|{INSUFFICIENT_CONTROL}",
             "condition": INSUFFICIENT_CONTROL, "records": [],
             "context_order": [], "answerable": False,
             "current_id": None, "stale_id": None,
             "current_answer": None, "stale_answer": None},
        ])
    for case in cases:
        assert_within_core(case)
    return {"contract_version": CONTRACT_VERSION,
            "contract_sha256": contract_hash(),
            "source_fixture": V3.FIXTURE_VERSION,
            "cores": sorted({c["core"] for c in cases}),
            "cases": cases}


# --- parser regression fixtures the brief requires ----------------------------
PARSER_FIXTURES: tuple[dict[str, Any], ...] = (
    {"name": "citation on its own line", "text": "ANSWER: 240\nCITE: C2-CUR",
     "expect_parsed": True, "expect_ids": ("C2-CUR",)},
    {"name": "valid inline citation", "text": "ANSWER: 240 CITE: C2-CUR",
     "expect_parsed": True, "expect_ids": ("C2-CUR",)},
    {"name": "multiple cited record ids",
     "text": "ANSWER: 240\nCITE: C2-CUR, C2-SUP",
     "expect_parsed": True, "expect_ids": ("C2-CUR", "C2-SUP")},
    {"name": "malformed citation", "text": "ANSWER: 240\nCITE: ???",
     "expect_parsed": False, "expect_ids": ()},
    {"name": "missing citation", "text": "ANSWER: 240",
     "expect_parsed": False, "expect_ids": ()},
    {"name": "contradictory answer and citation",
     "text": "ANSWER: 240\nCITE: NONE", "expect_parsed": True, "expect_ids": ()},
    {"name": "extra prose around a valid response",
     "text": "Let me think about this.\nANSWER: 240\nCITE: C2-CUR\nHope that helps.",
     "expect_parsed": True, "expect_ids": ("C2-CUR",)},
)
