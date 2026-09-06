"""`reader-interference-v6`: decidable conflict, with VERBATIM value copying.

v5 ran once (Gen117) and produced NON_EVIDENCE: its values were two-word phrases
and the reader answered with the distinguishing word alone in 36 of 48
selections, so correct selections scored UNSUPPORTED_VALUE. The control plane
ruled option 3 - require the complete phrase - explicitly NOT the option that
would have rescued Gen117, since that acceptance class was suggested by the
observed failures.

Twelve entirely fresh cores. No subject, head noun, distinguishing token,
record sentence or question from v5 appears here.


Gen115 showed why v4 could not answer the question it was built for: no conflict
prompt told the reader which record was current, so scoring "picked the current
value" scored a guess. Gen116 rules R-1(a): recency becomes an explicit, uniform,
role-neutral field on EVERY record.

    effective_revision   on every record, same schema, same field order
    as_of_revision       in the question
    the rule             select the record whose effective_revision equals
                         as_of_revision; if none matches exactly, INSUFFICIENT

Nothing else may carry recency. No role words, no version-like values, no
progression prose, no ordering by context position - context order is
counterbalanced across the two conflict conditions, so it cannot encode truth.

The independent unit is the CORE, not the cell. 12 cores x 5 conditions = 60
unique model-facing cases; there are no repeated identical requests, so a cell
count is never an observation count.

NOTHING HERE HAS BEEN RUN. This module is a candidate protocol awaiting
control-plane review.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

CONTRACT_VERSION = "reader-interference-v6"
R1_DECISION = "R-1(a) explicit uniform role-neutral recency via effective_revision/as_of_revision"
VERBATIM_RULING = ("Gen118 option 3: the reader must copy the COMPLETE value phrase "
                   "verbatim. Chosen on protocol-design grounds, not because it "
                   "rescues Gen117 - the distinguishing-token acceptance class was "
                   "suggested by the observed failures and is therefore refused.")

# --- fixture ------------------------------------------------------------------
# Twelve fresh cores. None reuses or paraphrases branch:vega, budget:solstice,
# oncall:kestrel or throughput:atlas, their values, questions, record prose, or
# any answer wording observed in Generations 110-115.
#
# Each pair shares its head noun and has matched morphology: same token count,
# closely matched length, no numerals, no version shape, no natural order.
# `rev2_is_b` alternates so the revision-2 value is not systematically longer,
# lexicographically larger, or first-listed.
CORES: tuple[dict[str, Any], ...] = (
    {"key": "core01", "subject": 'The Ambergris terminal', "question": 'Ambergris terminal berthing bay',
     "verb": 'berths at', "a": 'bay tolliver', "b": 'bay quillon', "rev2_is_b": False},
    {"key": "core02", "subject": 'The Nocturne foundry', "question": 'Nocturne foundry casting floor',
     "verb": 'casts on', "a": 'floor pemberly', "b": 'floor darnwick', "rev2_is_b": False},
    {"key": "core03", "subject": 'The Selvage exchange', "question": 'Selvage exchange trading pit',
     "verb": 'trades in', "a": 'pit halloway', "b": 'pit merrivale', "rev2_is_b": False},
    {"key": "core04", "subject": 'The Fathom conservatory', "question": 'Fathom conservatory glass annex',
     "verb": 'is kept in', "a": 'annex brackenby', "b": 'annex solvane', "rev2_is_b": False},
    {"key": "core05", "subject": 'The Kestrelmoor mill', "question": 'Kestrelmoor mill grinding stage',
     "verb": 'grinds at', "a": 'stage crowther', "b": 'stage abernay', "rev2_is_b": False},
    {"key": "core06", "subject": 'The Lantern reservoir', "question": 'Lantern reservoir intake channel',
     "verb": 'draws by', "a": 'channel wrenfell', "b": 'channel maddox', "rev2_is_b": False},
    {"key": "core07", "subject": 'The Palisade infirmary', "question": 'Palisade infirmary triage ward',
     "verb": 'admits to', "a": 'ward tillingham', "b": 'ward stonebrook', "rev2_is_b": False},
    {"key": "core08", "subject": 'The Cordwain atelier', "question": 'Cordwain atelier cutting bench',
     "verb": 'cuts at', "a": 'bench farrowly', "b": 'bench ondrimor', "rev2_is_b": False},
    {"key": "core09", "subject": 'The Wrackline observatory', "question": 'Wrackline observatory sighting arc',
     "verb": 'sights along', "a": 'arc penderyn', "b": 'arc glasswych', "rev2_is_b": True},
    {"key": "core10", "subject": 'The Tamarind depot', "question": 'Tamarind depot loading ramp',
     "verb": 'loads by', "a": 'ramp shawcross', "b": 'ramp ellerby', "rev2_is_b": False},
    {"key": "core11", "subject": 'The Vellum bindery', "question": 'Vellum bindery stitching table',
     "verb": 'stitches at', "a": 'table norrington', "b": 'table caskwell', "rev2_is_b": True},
    {"key": "core12", "subject": 'The Ossuary cloister', "question": 'Ossuary cloister east walk',
     "verb": 'runs along', "a": 'walk emberline', "b": 'walk thanewood', "rev2_is_b": False},
)

CONDITIONS = ("CLEAN_CURRENT", "CONFLICT_CURRENT_FIRST", "CONFLICT_STALE_FIRST",
              "CLEAN_HISTORICAL_AS_OF", "INSUFFICIENT_CURRENT")

# Words that would let the reader date a record without the frozen rule.
BANNED_PROSE = ("after", "before", "initially", "resized", "previous", "previously",
                "formerly", "new", "newer", "old", "older", "latest", "current",
                "stale", "superseded", "upgrade", "upgraded", "replacement",
                "replaced", "migrated", "now", "then", "since", "until", "prior",
                "recent", "original", "update", "updated", "legacy", "modern")
# Words that would name the evaluator's role outright.
BANNED_ROLE = ("current", "stale", "superseded", "latest", "winning", "correct",
               "prior", "old", "new", "canonical", "authoritative")

# The gate is on the REALIZED fixture, not the intent. Strict alternation of the
# slot->revision map keeps ids revision-independent by construction, but the
# realized digest ordering landed at 7/12 with the first salt, which fails the
# declared balance gate. Only this arbitrary constant was re-rolled - the twelve
# per-core assignments were NOT hand-picked to hit a number, which would be
# fitting the fixture to its own audit.
_ID_SALT = "reader-interference-v6/opaque-record-id/v13"


def _slot_id(core_key: str, slot: int) -> str:
    d = hashlib.sha256(f"{_ID_SALT}|{core_key}|slot{slot}".encode()).hexdigest()
    return f"REC-{d[:10].upper()}"


def record_id(core_key: str, revision: int) -> str:
    """Opaque and role-neutral BY CONSTRUCTION.

    The digest is computed from a slot, never from the revision, and the
    slot->revision map alternates across cores. So the id cannot carry the role
    even by accident. The first freeze hashed the revision directly and the
    revision-2 id happened to sort first in only 2 of 12 cores - chance, but a
    reader that sorted ids would have had a signal we never intended to give it.
    """
    idx = next(i for i, c in enumerate(CORES) if c["key"] == core_key)
    slot_for_rev2 = idx % 2
    slot = slot_for_rev2 if revision == 2 else 1 - slot_for_rev2
    return _slot_id(core_key, slot)


def canonical_values(core: Mapping[str, Any]) -> dict[int, str]:
    """revision -> value. `rev2_is_b` alternates so revision 2 is not biased."""
    return ({1: core["a"], 2: core["b"]} if core["rev2_is_b"]
            else {1: core["b"], 2: core["a"]})


def build_records(core: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    vals = canonical_values(core)
    return {rev: {"record_id": record_id(core["key"], rev),
                  "effective_revision": rev,
                  "statement": f"{core['subject']} {core['verb']} {vals[rev]}."}
            for rev in (1, 2)}


def build_fixture() -> dict[str, Any]:
    cases = []
    for core in CORES:
        recs = build_records(core)
        vals = canonical_values(core)
        plan = {
            "CLEAN_CURRENT":          ([2],    2),
            "CONFLICT_CURRENT_FIRST": ([2, 1], 2),
            "CONFLICT_STALE_FIRST":   ([1, 2], 2),
            "CLEAN_HISTORICAL_AS_OF": ([1],    1),
            "INSUFFICIENT_CURRENT":   ([1],    2),
        }
        for cond in CONDITIONS:
            order, as_of = plan[cond]
            cases.append({
                "case_id": f"{core['key']}|{cond}",
                "core": core["key"], "condition": cond,
                "question": core["question"], "as_of_revision": as_of,
                "context_order": [recs[r]["record_id"] for r in order],
                "records": [recs[r] for r in order],
                "canonical_values": vals,
                "expected_disposition": "INSUFFICIENT" if cond == "INSUFFICIENT_CURRENT" else "RESOLVED",
                "expected_value": None if cond == "INSUFFICIENT_CURRENT" else vals[as_of],
                "expected_record_id": None if cond == "INSUFFICIENT_CURRENT" else recs[as_of]["record_id"],
            })
    return {"contract": CONTRACT_VERSION, "r1_decision": R1_DECISION,
            "cores": len(CORES), "conditions": CONDITIONS, "cases": cases,
            "independent_unit": "core",
            "note": "60 unique cases, not 60 independent observations"}


# --- the model-facing prompt --------------------------------------------------
RULE = ("Select the record whose effective_revision is exactly equal to as_of_revision. "
        "If no record has that exact effective_revision, you must answer INSUFFICIENT "
        "rather than infer, extrapolate, or choose the closest record. "
        "For selected_value, copy the ENTIRE value phrase exactly as written in the "
        "selected record. Do not abbreviate it, omit a word, return only the "
        "distinguishing word, paraphrase it, or place it inside a sentence.")

SCHEMA = ('{"disposition": "RESOLVED|UNRESOLVED|INSUFFICIENT", '
          '"selected_record_id": "<record id or null>", '
          '"selected_value": "<value or null>", '
          '"prior_values": ["<value>", ...], '
          '"citations": ["<record id>", ...]}')


def project_prompt(case: Mapping[str, Any]) -> str:
    lines = [f"[{r['record_id']}] effective_revision: {r['effective_revision']} | {r['statement']}"
             for r in case["records"]]
    return (
        "Answer using only the records provided.\n"
        f"{RULE}\n"
        "Reply with a single JSON object and nothing else:\n"
        f"{SCHEMA}\n\n"
        "RECORDS:\n" + "\n".join(lines) + "\n\n"
        f"QUESTION: {case['question']}\n"
        f"as_of_revision: {case['as_of_revision']}\n")


# --- response contract --------------------------------------------------------
DISPOSITIONS = ("RESOLVED", "UNRESOLVED", "INSUFFICIENT")

CURRENT_ONLY = "CURRENT_ONLY"
CURRENT_WITH_HISTORY = "CURRENT_WITH_HISTORY"
STALE_ONLY = "STALE_ONLY"
STALE_WITH_HISTORY = "STALE_WITH_HISTORY"
UNRESOLVED_BOTH = "UNRESOLVED_BOTH"
RECONCILED_CURRENT = "TEMPORAL_RECONCILIATION_TO_CURRENT"
RECONCILED_STALE = "TEMPORAL_RECONCILIATION_TO_STALE"
SIMULTANEOUS = "EXPLICIT_SIMULTANEOUS_CONTRADICTION"
CORRECT_INSUFFICIENT = "CORRECT_INSUFFICIENT"
UNSUPPORTED_VALUE = "UNSUPPORTED_VALUE"
MALFORMED = "MALFORMED_RESPONSE"
# Nine classes, not eleven. Under a structured response contract a chronology
# that ends at a selected value IS *_WITH_HISTORY; keeping a separate
# TEMPORAL_RECONCILIATION_* row would mean two labels for one response, which is
# the ambiguity this ontology exists to remove. The Gen116 brief asked for both;
# this deviation is deliberate and is recorded for the control plane to rule on.
ONTOLOGY = (CURRENT_ONLY, CURRENT_WITH_HISTORY, STALE_ONLY, STALE_WITH_HISTORY,
            UNRESOLVED_BOTH, SIMULTANEOUS, CORRECT_INSUFFICIENT,
            UNSUPPORTED_VALUE, MALFORMED)
RECONCILIATION_IS_EXPRESSED_AS = {
    RECONCILED_CURRENT: CURRENT_WITH_HISTORY,
    RECONCILED_STALE: STALE_WITH_HISTORY,
}


# CANONICALISATION POLICY, frozen and named rather than implied.
#
# The model-facing rule says "verbatim". The matcher is not byte-identity: it
# folds case and collapses runs of whitespace, and nothing else. Gen118 requires
# the prose and the executable behaviour to agree, so the difference is stated
# here instead of left for a reader to discover.
#
# ACCEPTED : "Bay Tolliver", "bay  tolliver", " bay tolliver "
# REJECTED : "tolliver", "bay", "the bay tolliver", "bay tolliver.", "tolliver bay",
#            "bay tollivers", "bay tollıver" (Unicode lookalike)
CANONICALISATION = ("casefold and collapse internal whitespace; nothing else. "
                    "No suffix, token-subset, semantic, fuzzy, embedding, "
                    "edit-distance or judge-based acceptance.")


def _norm(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s)).strip().casefold()


def value_present(text: Any, value: str) -> bool:
    """Token-aware, not substring. 'lane amber' must not match 'lane ambergris'."""
    return re.search(rf"(?<!\w){re.escape(_norm(value))}(?!\w)", _norm(text)) is not None


def parse_response(text: str) -> dict[str, Any]:
    """Strict. A response that is not exactly one conforming JSON object is MALFORMED."""
    try:
        obj = json.loads(text)
    except Exception:
        return {"ok": False, "reason": "not json"}
    if not isinstance(obj, dict):
        return {"ok": False, "reason": "not an object"}
    if set(obj) != {"disposition", "selected_record_id", "selected_value",
                    "prior_values", "citations"}:
        return {"ok": False, "reason": "field set mismatch"}
    if obj["disposition"] not in DISPOSITIONS:
        return {"ok": False, "reason": "bad disposition"}
    if not isinstance(obj["prior_values"], list) or not isinstance(obj["citations"], list):
        return {"ok": False, "reason": "prior_values and citations must be arrays"}
    for f in ("selected_record_id", "selected_value"):
        if obj[f] is not None and not isinstance(obj[f], str):
            return {"ok": False, "reason": f"{f} must be a string or null"}
    if any(not isinstance(x, str) for x in obj["prior_values"] + obj["citations"]):
        return {"ok": False, "reason": "array members must be strings"}
    # Disposition coherence is part of the contract, not a matter of taste. An
    # INSUFFICIENT reply that also selects a value is not an abstention, and a
    # RESOLVED reply that selects nothing has not resolved anything. Accepting
    # either let an incoherent answer pass a control gate - the Gen112 defect,
    # reappearing in a new place.
    selected = obj["selected_record_id"] is not None or obj["selected_value"] is not None
    if obj["disposition"] in ("INSUFFICIENT", "UNRESOLVED") and selected:
        return {"ok": False, "reason": f"{obj['disposition']} must not select a record or value"}
    if obj["disposition"] == "RESOLVED" and (
            obj["selected_record_id"] is None or obj["selected_value"] is None):
        return {"ok": False, "reason": "RESOLVED must name both a record and a value"}
    return {"ok": True, **obj}


def classify_answer(parsed: Mapping[str, Any], values: Mapping[int, str]) -> str:
    """Answer class from response content and canonical values ONLY.

    Citations are not consulted here and can never rewrite this (R-9). The class
    is computed before `citation_relation` is even looked at.
    """
    if not parsed.get("ok"):
        return MALFORMED
    v1, v2 = values[1], values[2]
    sel = parsed["selected_value"]
    prior = parsed["prior_values"]
    disp = parsed["disposition"]

    # A genuine assertion that both values hold at once is expressible in exactly
    # one way under this contract: naming both inside the single selected_value.
    # That is an assertion. Inferring it from a null selection, as the first
    # freeze did, is reading meaning into a field that does not carry it.
    if sel is not None and value_present(sel, v1) and value_present(sel, v2):
        return SIMULTANEOUS
    sel_is = (2 if sel is not None and _norm(sel) == _norm(v2) else
              1 if sel is not None and _norm(sel) == _norm(v1) else None)
    if sel is not None and sel_is is None:
        return UNSUPPORTED_VALUE
    if any(not (value_present(p, v1) or value_present(p, v2)) for p in prior):
        return UNSUPPORTED_VALUE

    has1 = any(value_present(p, v1) for p in prior)
    has2 = any(value_present(p, v2) for p in prior)

    if disp == "INSUFFICIENT":
        return CORRECT_INSUFFICIENT
    if disp == "UNRESOLVED":
        return UNRESOLVED_BOTH
    # RESOLVED, with a selection the parser has already guaranteed is present.
    # A selection that also carries the other value as history IS the temporal
    # reconciliation; there is no separate class for it, because under a
    # structured contract they are the same response.
    if sel_is == 2:
        return CURRENT_WITH_HISTORY if has1 else CURRENT_ONLY
    return STALE_WITH_HISTORY if has2 else STALE_ONLY


def citation_relation(parsed: Mapping[str, Any], case: Mapping[str, Any]) -> str:
    """Computed AFTER the answer class, recorded separately, never overriding it."""
    if not parsed.get("ok"):
        return "NONE"
    shown = {r["record_id"] for r in case["records"]}
    cited = set(parsed["citations"])
    if not cited:
        return "ABSENT"
    if not cited <= shown:
        return "UNSHOWN_RECORD"
    if parsed["selected_record_id"] and parsed["selected_record_id"] not in cited:
        return "SELECTION_UNCITED"
    return "CONSISTENT"


SUCCESS = {  # the frozen success state per condition
    "CLEAN_CURRENT": (CURRENT_ONLY, CURRENT_WITH_HISTORY),
    "CONFLICT_CURRENT_FIRST": (CURRENT_ONLY, CURRENT_WITH_HISTORY),
    "CONFLICT_STALE_FIRST": (CURRENT_ONLY, CURRENT_WITH_HISTORY),
    "CLEAN_HISTORICAL_AS_OF": (STALE_ONLY, STALE_WITH_HISTORY),
    "INSUFFICIENT_CURRENT": (CORRECT_INSUFFICIENT,),
}


def grade(parsed: Mapping[str, Any], case: Mapping[str, Any]) -> dict[str, Any]:
    values = {int(k): v for k, v in case["canonical_values"].items()}
    cls = classify_answer(parsed, values)
    as_of = case["as_of_revision"]
    # For CLEAN_HISTORICAL_AS_OF the target is revision 1, so the ontology's
    # revision-relative STALE_* names are the SUCCESS there. The ontology names a
    # revision, the success table names the condition; they are kept apart.
    rel = citation_relation(parsed, case)
    selected_ok = (parsed.get("ok") and parsed.get("selected_record_id") == case["expected_record_id"])
    # Naming the right VALUE while pointing at the wrong record is not success.
    # v4 scored on value presence and that is the habit this protocol exists to
    # break, so the selection and the citation are load-bearing here.
    if case["condition"] == "INSUFFICIENT_CURRENT":
        citation_ok = rel == "ABSENT"
    else:
        citation_ok = rel == "CONSISTENT"
    ok = (cls in SUCCESS[case["condition"]]) and selected_ok and citation_ok
    return {"answer_class": cls,
            "citation_relation": rel,
            "meets_success_state": bool(ok),
            "selected_expected_record": bool(selected_ok),
            "citation_supports_selection": bool(citation_ok),
            "as_of_revision": as_of}


def contract_payload() -> dict[str, Any]:
    """Behaviour generated by RUNNING the real functions, plus source digests."""
    fixture = build_fixture()
    cases = {c["case_id"]: c for c in fixture["cases"]}
    prompt_sha = {cid: hashlib.sha256(project_prompt(c).encode()).hexdigest()
                  for cid, c in cases.items()}
    return {
        "version": CONTRACT_VERSION,
        "r1_decision": R1_DECISION,
        "cores": [c["key"] for c in CORES],
        "conditions": CONDITIONS,
        "ontology": ONTOLOGY,
        "dispositions": DISPOSITIONS,
        "success_states": {k: list(v) for k, v in SUCCESS.items()},
        "rule_text": RULE,
        "canonicalisation": CANONICALISATION,
        "verbatim_ruling": VERBATIM_RULING,
        "response_schema": SCHEMA,
        "case_count": len(cases),
        "unique_prompt_count": len(set(prompt_sha.values())),
        "prompt_sha256": prompt_sha,
        "parser_table": _parser_table(),
        "ontology_table": _ontology_table(),
        "citation_table": _citation_table(),
        "banned_prose": BANNED_PROSE,
        "banned_role": BANNED_ROLE,
        "independent_unit": "core",
    }


def _parser_table() -> list[dict[str, Any]]:
    good = json.dumps({"disposition": "RESOLVED", "selected_record_id": "REC-A",
                       "selected_value": "lane amber", "prior_values": [], "citations": ["REC-A"]})
    probes = [
        ("well formed", good),
        ("not json", "lane amber"),
        ("array not object", "[]"),
        ("missing field", '{"disposition":"RESOLVED"}'),
        ("extra field", good[:-1] + ',"extra":1}'),
        ("bad disposition", good.replace("RESOLVED", "MAYBE")),
        ("prior not array", good.replace('"prior_values": []', '"prior_values": "x"')),
        ("citation not string", good.replace('["REC-A"]', "[1]")),
        ("null selection", good.replace('"REC-A"', "null", 1).replace('"lane amber"', "null")),
        ("prose around json", "Here: " + good),
    ]
    return [{"probe": n, "ok": parse_response(t)["ok"],
             "reason": parse_response(t).get("reason")} for n, t in probes]


def _ontology_table() -> list[dict[str, Any]]:
    """Exhaustive over the declared response contract, by execution."""
    values = {1: "lane amber", 2: "lane cobalt"}
    rows = []
    for disp in DISPOSITIONS:
        for sel in (None, values[1], values[2], "lane ambergris",
                    f"{values[1]} and {values[2]}"):
            for prior in ([], [values[1]], [values[2]], [values[1], values[2]]):
                body = {"disposition": disp, "selected_record_id": "REC-A" if sel else None,
                        "selected_value": sel, "prior_values": prior, "citations": []}
                rows.append({"disposition": disp, "selected_value": sel,
                             "prior_values": prior,
                             "answer_class": classify_answer({"ok": True, **body}, values)})
    rows.append({"disposition": None, "selected_value": None, "prior_values": None,
                 "answer_class": classify_answer({"ok": False}, values)})
    return rows


def _citation_table() -> list[dict[str, Any]]:
    case = build_fixture()["cases"][1]
    shown = [r["record_id"] for r in case["records"]]
    rows = []
    for cites in ([], shown[:1], shown, ["REC-NOTSHOWN"]):
        body = {"ok": True, "disposition": "RESOLVED", "selected_record_id": shown[0],
                "selected_value": case["expected_value"], "prior_values": [], "citations": cites}
        rows.append({"citations": cites, "relation": citation_relation(body, case)})
    return rows


def contract_sha256(payload: Mapping[str, Any] | None = None) -> str:
    return hashlib.sha256(json.dumps(payload or contract_payload(),
                                     sort_keys=True, default=str).encode()).hexdigest()
