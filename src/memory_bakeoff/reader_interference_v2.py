"""`reader-interference-v2`: the repaired ruler. Frozen, and deliberately unrun.

v1 executed cleanly at Gen110 and produced no science, because the ruler was
wrong in four ways. Two I found in my own output; two the control plane found by
reading the actual requests I had sent. All four are repaired here, and v1 is
recorded `SUPERSEDED_AS_RULER / NON_EVIDENCE` without a byte of it being changed.

**Defect 1 - graded record prose, not an answer value.** v1 asked whether the
record's whole sentence appeared in the reply, so `ANSWER: 41 t/s` against
*"Atlas measured 41 t/s after the cache fix."* graded `citation_mismatch`.
v2 carries an evaluator-only canonical value per record and compares against
that, under a normalisation that is written down rather than assumed.

**Defect 2 - abstention was impossible to express.** v1 demanded an `ANSWER:`
line; a model correctly declining writes prose. v2 freezes a strict two-field
JSON object with an explicit `INSUFFICIENT` sentinel.

**Defect 3 - the experiment was not blinded.** This one is mine and it is the
worst: v1 showed the model ids `C1-CUR` and `C1-SUP`, which spell out which
record is current in every conflict prompt. The measurement could not have meant
anything. v2 uses opaque role-neutral ids and audits the projected prompt.

**Defect 4 - the negative control was graded as a failure.** Answering with the
stale value in `CLEAN_STALE_NEGATIVE_CONTROL` is what makes that control
succeed; v1 charged it `prohibited_stale_answer`. The Gen110 report said so in
prose while the grader did the opposite. v2 grades **condition-relative**.

Gen110's 60 responses are cited as the reason the contract changed. They supply
no alias, tolerance rule or fixture.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any, Mapping, Sequence

CONTRACT_VERSION = "reader-interference-v2"
SUPERSEDES = {"contract": "reader-interference-v1",
              "status": "SUPERSEDED_AS_RULER / NON_EVIDENCE",
              "artifacts_unchanged": True,
              "gen110_attempt": "NON_EVIDENCE, preserved byte-for-byte"}

CONDITIONS = ("CLEAN_CURRENT", "CONFLICT_STALE_FIRST", "CONFLICT_CURRENT_FIRST",
              "CLEAN_STALE_NEGATIVE_CONTROL", "INSUFFICIENT_CONTROL")
CONFLICT_PAIR = ("CONFLICT_STALE_FIRST", "CONFLICT_CURRENT_FIRST")
CONTROL_CONDITIONS = ("CLEAN_CURRENT", "CLEAN_STALE_NEGATIVE_CONTROL",
                      "INSUFFICIENT_CONTROL")

INSUFFICIENT = "INSUFFICIENT"
ACCEPT_JSON_FENCE = True   # decided explicitly, and tested; never implicit

# --- evaluator-only canonical values -----------------------------------------
# The record TEXT stays exactly as Round 3 froze it. These are the atomic values
# the grader compares against, and they live only in evaluator truth.
CANONICAL: dict[str, dict[str, Any]] = {
    "throughput:atlas": {"current": "41 t/s", "stale": "27 t/s",
                         "casefold": False},
    "branch:vega": {"current": "release/vega-4.x", "stale": "release/vega-3.x",
                    "casefold": True},
    "oncall:kestrel": {"current": "platform rota", "stale": "network rota",
                       "casefold": True},
    "budget:solstice": {"current": "512 GiB", "stale": "256 GiB",
                        "casefold": False},
}

NORMALIZATION = {
    "steps": ["unicode NFKC", "strip leading and trailing whitespace",
              "collapse internal whitespace runs to one space",
              "case-fold ONLY where the value definition permits it"],
    "forbidden": ["LLM", "embedding", "fuzzy match", "semantic similarity",
                  "substring of the full record sentence",
                  "alias list learned from Gen110 responses"],
}


def normalise(value: str, *, casefold: bool) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.casefold() if casefold else text


def contains_value(answer: str, value: str, *, casefold: bool) -> bool:
    return normalise(value, casefold=casefold) in normalise(answer, casefold=casefold)


# --- opaque, role-neutral identifiers ----------------------------------------
ROLE_BEARING_MARKERS = ("cur", "sup", "current", "stale", "superseded", "old",
                        "new", "valid", "invalid", "v1", "v2", "prev", "latest",
                        "first", "second")


def opaque_id(core: str, record_id: str) -> str:
    """Deterministic, stable across the paired conditions, and role-free."""
    digest = hashlib.sha256(f"{CONTRACT_VERSION}|{core}|{record_id}".encode())
    return "REC-" + digest.hexdigest()[:10].upper()


def assert_id_is_role_neutral(identifier: str) -> None:
    body = identifier.lower().replace("rec-", "")
    for marker in ROLE_BEARING_MARKERS:
        if marker in body:
            raise ValueError(f"{identifier!r} leaks role via {marker!r}")


# --- the frozen prompt --------------------------------------------------------
INSTRUCTION = (
    "Answer the question using only the records provided.\n"
    'Reply with a single JSON object and nothing else: '
    '{"answer": "<your answer>", "citations": ["<record id>", ...]}\n'
    f'If the records do not answer the question, reply exactly '
    f'{{"answer": "{INSUFFICIENT}", "citations": []}}.'
)

MODEL_FACING_FIELDS = ("instruction", "records", "question")
FORBIDDEN_IN_PROMPT = ("role", "condition", "core", "current_answer",
                       "stale_answer", "truth", "canonical", "mapping",
                       "C0-CUR", "C0-SUP", "C1-CUR", "C1-SUP",
                       "C2-CUR", "C2-SUP", "C3-CUR", "C3-SUP")


def project_prompt(case: Mapping[str, Any]) -> str:
    """Exactly what the model sees. Nothing evaluator-owned may enter here."""
    lines = [INSTRUCTION, "", "RECORDS:"]
    shown = {r["opaque_id"]: r["text"] for r in case["records"]}
    for oid in case["context_order"]:
        lines.append(f"[{oid}] {shown[oid]}")
    if not case["context_order"]:
        lines.append("(no records)")
    lines.extend(["", f"QUESTION: {case['question']}"])
    return "\n".join(lines)


def assert_prompt_is_blind(case: Mapping[str, Any]) -> None:
    """The Gen110 defect, as an enforced audit."""
    prompt = project_prompt(case)
    for marker in FORBIDDEN_IN_PROMPT:
        if marker.lower() in prompt.lower():
            raise ValueError(f"prompt leaks {marker!r}")
    for record in case["records"]:
        assert_id_is_role_neutral(record["opaque_id"])
        if record["id"] in prompt:
            raise ValueError(f"prompt leaks benchmark id {record['id']!r}")


# --- parser: SYNTAX ONLY ------------------------------------------------------
PARSED = "PARSED"
UNPARSED_NOT_JSON = "UNPARSED_NOT_JSON"
UNPARSED_NOT_OBJECT = "UNPARSED_NOT_A_SINGLE_OBJECT"
UNPARSED_FIELDS = "UNPARSED_FIELD_SET"
UNPARSED_TYPES = "UNPARSED_FIELD_TYPES"
UNPARSED_STATES = (UNPARSED_NOT_JSON, UNPARSED_NOT_OBJECT, UNPARSED_FIELDS,
                   UNPARSED_TYPES)

FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


def parse_response(text: str) -> dict[str, Any]:
    """Returns PARSED or a specific UNPARSED reason. Decides NO semantics."""
    body = (text or "").strip()
    if ACCEPT_JSON_FENCE:
        fenced = FENCE.match(body)
        if fenced:
            body = fenced.group(1).strip()
    try:
        loaded = json.loads(body)
    except Exception:
        return {"parse_status": UNPARSED_NOT_JSON, "parsed": False,
                "answer": None, "citations": ()}
    if not isinstance(loaded, dict):
        return {"parse_status": UNPARSED_NOT_OBJECT, "parsed": False,
                "answer": None, "citations": ()}
    if set(loaded) != {"answer", "citations"}:
        return {"parse_status": UNPARSED_FIELDS, "parsed": False,
                "answer": None, "citations": ()}
    if not isinstance(loaded["answer"], str) or \
            not isinstance(loaded["citations"], list) or \
            not all(isinstance(c, str) for c in loaded["citations"]):
        return {"parse_status": UNPARSED_TYPES, "parsed": False,
                "answer": None, "citations": ()}
    return {"parse_status": PARSED, "parsed": True,
            "answer": loaded["answer"], "citations": tuple(loaded["citations"])}


# --- condition-relative grades ------------------------------------------------
CORRECT_CURRENT = "correct_current_answer"
PROHIBITED_STALE = "prohibited_stale_answer"
MIXED = "mixed_contradictory_answer"
CORRECT_STALE_CONTROL = "correct_stale_control_answer"
CORRECT_INSUFFICIENCY = "correct_insufficiency"
INCORRECT_ABSTENTION = "incorrect_abstention"
CITATION_MISMATCH = "citation_mismatch"
UNSUPPORTED_VALUE = "unsupported_answer_value"
UNPARSED_OUTCOME = "unparsed_response"
OUTCOMES = (CORRECT_CURRENT, PROHIBITED_STALE, MIXED, CORRECT_STALE_CONTROL,
            CORRECT_INSUFFICIENCY, INCORRECT_ABSTENTION, CITATION_MISMATCH,
            UNSUPPORTED_VALUE, UNPARSED_OUTCOME)


def grade(parsed: Mapping[str, Any], case: Mapping[str, Any]) -> dict[str, Any]:
    """Deterministic and CONDITION-RELATIVE. Exactly one outcome per response."""
    if not parsed["parsed"]:
        return {"outcome": UNPARSED_OUTCOME, "answer_class": "UNPARSED",
                "citation_relation": "NONE", "why": parsed["parse_status"]}

    core = CANONICAL[case["core"]]
    fold = core["casefold"]
    answer = parsed["answer"]
    cited = set(parsed["citations"])
    known = {r["opaque_id"] for r in case["records"]}
    condition = case["condition"]

    said_current = case["current_opaque"] is not None and \
        contains_value(answer, core["current"], casefold=fold)
    said_stale = case["stale_opaque"] is not None and \
        contains_value(answer, core["stale"], casefold=fold)
    abstained = normalise(answer, casefold=False) == INSUFFICIENT

    # 1. abstention is exclusive and must carry no citations
    if abstained:
        if cited:
            return {"outcome": UNPARSED_OUTCOME, "answer_class": "INSUFFICIENT",
                    "citation_relation": "ILLEGAL",
                    "why": "INSUFFICIENT with a non-empty citation list"}
        return ({"outcome": CORRECT_INSUFFICIENCY, "answer_class": "INSUFFICIENT",
                 "citation_relation": "EMPTY", "why": "nothing supports an answer"}
                if condition == "INSUFFICIENT_CONTROL" else
                {"outcome": INCORRECT_ABSTENTION, "answer_class": "INSUFFICIENT",
                 "citation_relation": "EMPTY",
                 "why": "an answer was supported and the reader abstained"})
    # 2. a substantive answer must cite, and cite something real
    if not cited:
        return {"outcome": UNPARSED_OUTCOME, "answer_class": "SUBSTANTIVE",
                "citation_relation": "EMPTY",
                "why": "substantive answer with no citations"}
    if not cited <= known:
        return {"outcome": UNPARSED_OUTCOME, "answer_class": "SUBSTANTIVE",
                "citation_relation": "UNKNOWN_ID",
                "why": f"cites unknown ids {sorted(cited - known)}"}
    # 3. both values asserted
    if said_current and said_stale:
        return {"outcome": MIXED, "answer_class": "BOTH",
                "citation_relation": "ANY", "why": "asserts both values"}
    # 4. neither value asserted
    if not said_current and not said_stale:
        return {"outcome": UNSUPPORTED_VALUE, "answer_class": "NEITHER",
                "citation_relation": "ANY",
                "why": "answer matches no canonical value"}
    # 5. exactly one value, graded against what THIS condition expects
    if said_stale:
        if condition == "CLEAN_STALE_NEGATIVE_CONTROL":
            return ({"outcome": CORRECT_STALE_CONTROL, "answer_class": "STALE",
                     "citation_relation": "MATCHES",
                     "why": "the stale record is the only evidence; the control works"}
                    if cited == {case["stale_opaque"]} else
                    {"outcome": CITATION_MISMATCH, "answer_class": "STALE",
                     "citation_relation": "MISMATCH",
                     "why": "stale value with a non-matching citation"})
        return {"outcome": PROHIBITED_STALE, "answer_class": "STALE",
                "citation_relation": "ANY",
                "why": "current truth was expected and stale was selected"}
    if cited != {case["current_opaque"]}:
        return {"outcome": CITATION_MISMATCH, "answer_class": "CURRENT",
                "citation_relation": "MISMATCH",
                "why": "current value with a non-matching citation"}
    return {"outcome": CORRECT_CURRENT, "answer_class": "CURRENT",
            "citation_relation": "MATCHES", "why": "current value, current citation"}


# --- control gates ------------------------------------------------------------
CONTROL_RULE = {
    "rule": "conservative: EVERY planned repetition of all three controls must "
            "receive its corresponding correct outcome for that core",
    "expected": {"CLEAN_CURRENT": CORRECT_CURRENT,
                 "CLEAN_STALE_NEGATIVE_CONTROL": CORRECT_STALE_CONTROL,
                 "INSUFFICIENT_CONTROL": CORRECT_INSUFFICIENCY},
    "on_failure": "Q1-Q3 for that core report NOT_INTERPRETABLE_CONTROL_FAILURE; "
                  "Q4 issues no across-core label unless all four cores pass",
    "never": "control failure is never excluded, averaged away, or used to "
             "change the rule",
}
NOT_INTERPRETABLE = "NOT_INTERPRETABLE_CONTROL_FAILURE"
ACROSS_CORE_VERDICTS = ("REPLICATED_ACROSS_CORES", "PARTIAL_REPLICATION",
                        "FIXTURE_SPECIFIC", "NO_EFFECT", NOT_INTERPRETABLE)


def core_is_interpretable(core_cells: Sequence[Mapping[str, Any]]) -> bool:
    for condition, expected in CONTROL_RULE["expected"].items():
        cells = [c for c in core_cells if c["condition"] == condition]
        if not cells or any(c["outcome"] != expected for c in cells):
            return False
    return True


# --- fixture: same cores, same texts, blinded ids -----------------------------
def build_fixture() -> dict[str, Any]:
    """Identical semantics to v1. Only the four repairs change anything."""
    from memory_bakeoff import interference_v3 as V3

    source = V3.build_fixture()
    cases: list[dict[str, Any]] = []
    for core in sorted({o.core for o in source.observations}):
        mine = [o for o in source.observations if o.core == core]
        current = next(o for o in mine if o.role == "current")
        stale = next(o for o in mine if o.role == "superseded")
        question = next((c.query for c in source.cases if c.core == core), None)
        cur_oid, sup_oid = opaque_id(core, current.id), opaque_id(core, stale.id)

        def record(obs, oid):
            return {"opaque_id": oid, "text": obs.text,          # model-facing
                    "id": obs.id, "role": obs.role,              # evaluator-only
                    "scope": obs.scope, "configuration": obs.configuration,
                    "core": obs.core}

        cur, sup = record(current, cur_oid), record(stale, sup_oid)
        base = {"core": core, "question": question,
                "current_opaque": cur_oid, "stale_opaque": sup_oid}
        cases.extend([
            {**base, "id": f"{core}|CLEAN_CURRENT", "condition": "CLEAN_CURRENT",
             "records": [cur], "context_order": [cur_oid], "stale_opaque": None},
            {**base, "id": f"{core}|CONFLICT_STALE_FIRST",
             "condition": "CONFLICT_STALE_FIRST", "records": [sup, cur],
             "context_order": [sup_oid, cur_oid]},
            {**base, "id": f"{core}|CONFLICT_CURRENT_FIRST",
             "condition": "CONFLICT_CURRENT_FIRST", "records": [sup, cur],
             "context_order": [cur_oid, sup_oid]},
            {**base, "id": f"{core}|CLEAN_STALE_NEGATIVE_CONTROL",
             "condition": "CLEAN_STALE_NEGATIVE_CONTROL", "records": [sup],
             "context_order": [sup_oid], "current_opaque": None},
            {**base, "id": f"{core}|INSUFFICIENT_CONTROL",
             "condition": "INSUFFICIENT_CONTROL", "records": [],
             "context_order": [], "current_opaque": None, "stale_opaque": None},
        ])
    for case in cases:
        assert_prompt_is_blind(case)
    return {"contract_version": CONTRACT_VERSION,
            "source_fixture": V3.FIXTURE_VERSION,
            "cores": sorted({c["core"] for c in cases}), "cases": cases}


# --- questions, re-frozen -----------------------------------------------------
QUESTIONS = (
    {"id": "Q1", "scope": "per interpretable core",
     "question": "Does adding the stale record increase prohibited-stale or "
                 "mixed answers in either conflict condition relative to "
                 "CLEAN_CURRENT?",
     "rule": "effect if (prohibited_stale_answer + mixed_contradictory_answer) "
             "in either conflict condition exceeds CLEAN_CURRENT; else no effect"},
    {"id": "Q2", "scope": "per interpretable core",
     "question": "With identical blinded records, does swapping only "
                 "presentation order change the outcome distribution?",
     "rule": "order effect if the two conflict outcome distributions differ in "
             "any cell; else none"},
    {"id": "Q3", "scope": "per interpretable core",
     "question": "Does every conflict cell select current truth with a matching "
                 "current citation?",
     "rule": "prefers-current only if every conflict cell is "
             "correct_current_answer; any other outcome refutes it"},
    {"id": "Q4", "scope": "all four cores interpretable, else NOT_INTERPRETABLE",
     "question": "Is the Q1 effect replicated across cores?",
     "rule": "REPLICATED_ACROSS_CORES if the Q1 effect holds in 4 of 4; "
             "PARTIAL_REPLICATION in 2 or 3; FIXTURE_SPECIFIC in exactly 1; "
             "NO_EFFECT in 0. If any core fails its control gate, report "
             "NOT_INTERPRETABLE_CONTROL_FAILURE and name the failed cores. "
             "Cores are never averaged"},
    {"id": "Q5", "scope": "parser",
     "question": "Does the strict parser accept every contract-valid synthetic "
                 "form and reject every malformed one?",
     "rule": "pass only if all valid fixtures PARSE and all invalid fixtures "
             "return an UNPARSED reason"},
    {"id": "Q6", "scope": "prompt projection",
     "question": "Do model-facing prompts leak no truth label, and do paired "
                 "conflict prompts differ only in record order?",
     "rule": "pass only if the projection audit finds no forbidden marker and "
             "the two conflict prompts are identical up to record order"},
)

# --- synthetic parser fixtures, created HERE, never from Gen110 wording -------
VALID_FIXTURES = (
    {"name": "current value, short",
     "text": '{"answer": "41 t/s", "citations": ["REC-AAAAAAAAAA"]}'},
    {"name": "current value in a full sentence",
     "text": '{"answer": "The throughput is 41 t/s.", "citations": ["REC-AAAAAAAAAA"]}'},
    {"name": "stale value, short",
     "text": '{"answer": "27 t/s", "citations": ["REC-BBBBBBBBBB"]}'},
    {"name": "both values",
     "text": '{"answer": "41 t/s, previously 27 t/s", "citations": ["REC-AAAAAAAAAA"]}'},
    {"name": "insufficient",
     "text": '{"answer": "INSUFFICIENT", "citations": []}'},
    {"name": "accepted json fence",
     "text": '```json\n{"answer": "41 t/s", "citations": ["REC-AAAAAAAAAA"]}\n```'},
)
INVALID_FIXTURES = (
    {"name": "malformed json", "text": '{"answer": "41 t/s", '},
    {"name": "missing field", "text": '{"answer": "41 t/s"}'},
    {"name": "extra field",
     "text": '{"answer": "41 t/s", "citations": [], "decision": "CURRENT"}'},
    {"name": "wrong type",
     "text": '{"answer": 41, "citations": ["REC-AAAAAAAAAA"]}'},
    {"name": "citations not a list",
     "text": '{"answer": "41 t/s", "citations": "REC-AAAAAAAAAA"}'},
    {"name": "multiple objects",
     "text": '{"answer": "41 t/s", "citations": []} {"answer": "27 t/s", "citations": []}'},
    {"name": "not an object", "text": '["41 t/s"]'},
)

# --- v1 -> v2 change ledger ---------------------------------------------------
CHANGE_LEDGER = (
    {"field": "canonical answer values", "change": "ADDED",
     "defect": "graded record prose instead of an answer value",
     "reason": "a short correct answer can never contain the full record "
               "sentence, so correct answers fell through to citation_mismatch",
     "expected_effect": "correct short and full-sentence answers now classify "
                        "identically when citations match",
     "found_by": "executor, from its own Gen110 output"},
    {"field": "response schema", "change": "REPLACED",
     "defect": "abstention was not expressible",
     "reason": "the contract demanded an ANSWER: line; a correct refusal is prose",
     "expected_effect": "INSUFFICIENT is now contract-legal and unambiguous",
     "found_by": "executor, from its own Gen110 output"},
    {"field": "model-facing record ids", "change": "REPLACED",
     "defect": "role leakage - ids C1-CUR and C1-SUP disclosed which record was "
               "current in every conflict prompt",
     "reason": "the experiment was not blinded, so no conflict measurement "
               "could have meant anything",
     "expected_effect": "the reader can no longer read the answer off an id",
     "found_by": "control plane, by reading the actual Gen110 requests"},
    {"field": "grading", "change": "MADE CONDITION-RELATIVE",
     "defect": "the stale-only negative control was graded as a failure",
     "reason": "answering with the stale value there is what makes the control "
               "succeed; v1 charged prohibited_stale_answer",
     "expected_effect": "correct_stale_control_answer exists and the control "
                        "can now pass",
     "found_by": "control plane"},
    {"field": "semantic cores, record texts, scopes, configurations, questions, "
              "five conditions", "change": "UNCHANGED",
     "defect": None, "reason": "v2 repairs the ruler, not the subject",
     "expected_effect": "results remain comparable in kind to the v1 design",
     "found_by": None},
)


def truth_table() -> list[dict[str, Any]]:
    """Every reachable (condition, answer class, citation relation) -> ONE outcome."""
    rows: list[dict[str, Any]] = []
    fixture = build_fixture()
    for case in fixture["cases"]:
        core = CANONICAL[case["core"]]
        cur, sup = case["current_opaque"], case["stale_opaque"]
        probes = [
            ("CURRENT/matching", core["current"], [cur] if cur else []),
            ("CURRENT/mismatched", core["current"], [sup] if sup else []),
            ("STALE/matching", core["stale"], [sup] if sup else []),
            ("STALE/mismatched", core["stale"], [cur] if cur else []),
            ("BOTH", f"{core['current']} and {core['stale']}", [cur or sup]),
            ("NEITHER", "something else entirely", [cur or sup]),
            ("INSUFFICIENT/empty", INSUFFICIENT, []),
            ("INSUFFICIENT/cited", INSUFFICIENT, [cur or sup]),
        ]
        for label, answer, citations in probes:
            if any(c is None for c in citations):
                continue
            reply = json.dumps({"answer": answer,
                                "citations": [c for c in citations if c]})
            outcome = grade(parse_response(reply), case)
            rows.append({"condition": case["condition"], "core": case["core"],
                         "probe": label, "outcome": outcome["outcome"]})
    return rows


def contract_hash() -> str:
    body = json.dumps({
        "version": CONTRACT_VERSION, "conditions": CONDITIONS,
        "outcomes": OUTCOMES, "questions": QUESTIONS,
        "canonical": CANONICAL, "normalization": NORMALIZATION,
        "instruction": INSTRUCTION, "accept_fence": ACCEPT_JSON_FENCE,
        "control_rule": CONTROL_RULE, "verdicts": ACROSS_CORE_VERDICTS,
        "ledger": CHANGE_LEDGER,
    }, sort_keys=True, default=str)
    return hashlib.sha256(body.encode()).hexdigest()
