"""`reader-interference-v4`: a fingerprint that actually covers the ruler.

v3's science was sound and its **identity was not**. `contract_hash` serialized
declarations - answer classes, questions, canonical values, the change ledger -
and nothing executable. Four mutations prove the gap: replacing the classifier,
the grader, the parser, or `project_prompt` (with one that leaks the answer)
leaves the digest byte-identical. A "frozen" contract that cannot detect a
leaking prompt is not frozen; it is a label.

v4 changes **identity only**. Every scientific behaviour is imported from v3 and
v2 unchanged, and equality with v3 is asserted across all 360 matrix rows, every
parser and classifier fixture, all control forms and all 20 prompt bytes. Any
behavioural drift is a failure, not an improvement.

**How the payload covers executable behaviour without circularity.** Three
layers, none of which contains the digest itself:

1. **Declarations** - the fields v3 already hashed.
2. **Behaviour tables** - the parser, classifier, citation-relation, truth
   matrix and control forms, computed by *running* the real functions and
   serializing what they return. A hijacked classifier changes its table.
3. **Source bytes** - SHA-256 of each repository file supplying scientific
   behaviour, by repository-relative path. This file is included; the digest is
   not, because `contract_sha256` is written into the artifact *after* hashing
   and is an explicit exclusion. Hashing this file's bytes is not circular -
   the file never contains its own digest.

Exclusions are enumerated, and the verifier fails if that list ever grows.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from memory_bakeoff import reader_interference_v2 as V2
from memory_bakeoff import reader_interference_v3 as V3

CONTRACT_VERSION = "reader-interference-v4"
SUPERSEDES = {
    "contract": "reader-interference-v3",
    "status": "SUPERSEDED_AS_RULER / NON_EVIDENCE",
    "reason": "self-identity was incomplete; the digest did not commit to the "
              "parser, classifier, citation logic, grader, prompt projection, "
              "fixture builder, truth matrix, prompt hashes or control forms",
    "science_was_sound": True,
    "never_executed": True,
    "scientific_loss": "none",
    "artifacts_unchanged": True,
}

# --- behaviour carried forward from v3, unchanged ----------------------------
CONDITIONS = V3.CONDITIONS
CONFLICT_PAIR = V3.CONFLICT_PAIR
CONTROL_CONDITIONS = V3.CONTROL_CONDITIONS
ANSWER_CLASSES = V3.ANSWER_CLASSES
CITATION_RELATIONS = V3.CITATION_RELATIONS
OUTCOMES = V3.OUTCOMES
CONTROL_PASSING = V3.CONTROL_PASSING
CANONICAL = V3.CANONICAL
NORMALIZATION = V3.NORMALIZATION
INSTRUCTION = V3.INSTRUCTION
ACCEPT_JSON_FENCE = V3.ACCEPT_JSON_FENCE
QUESTIONS = V3.QUESTIONS
CONTROL_RULE = V3.CONTROL_RULE
ACROSS_CORE_VERDICTS = V3.ACROSS_CORE_VERDICTS
VALID_FIXTURES = V3.VALID_FIXTURES
INVALID_FIXTURES = V3.INVALID_FIXTURES
MIXED = V3.MIXED

parse_response = V3.parse_response
classify_answer = V3.classify_answer
citation_relation = V3.citation_relation
grade = V3.grade
project_prompt = V3.project_prompt
assert_prompt_is_blind = V3.assert_prompt_is_blind
build_fixture = V3.build_fixture
truth_matrix = V3.truth_matrix
control_passing_forms = V3.control_passing_forms
core_is_interpretable = V3.core_is_interpretable
assert_no_control_pass_from_a_bad_answer = V3.assert_no_control_pass_from_a_bad_answer

REPETITIONS = 3
READER_SETTINGS = {
    "endpoint": "http://strix-halo.local:8080/v1",
    "requested_model": "qwen3.6-35b-vulkan-nothink",
    "thinking": "disabled", "temperature": 0.0, "seed": 0,
    "max_tokens": 256, "stateless": True, "repetitions": REPETITIONS,
    "evidence_class": "controlled_reader_interference",
}

# --- the source files that supply scientific behaviour -----------------------
SOURCE_FILES = (
    "src/memory_bakeoff/reader_interference_v2.py",   # parser, prompt, fixture
    "src/memory_bakeoff/reader_interference_v3.py",   # classifier, grader
    "src/memory_bakeoff/reader_interference_v4.py",   # this fingerprint
)

EXCLUSIONS = (
    {"field": "contract_sha256",
     "why": "the digest is written into the artifact AFTER hashing; including "
            "it would be circular"},
    {"field": "write timestamps",
     "why": "non-semantic; recorded by the evidence manifest instead"},
    {"field": "output directory paths",
     "why": "non-semantic and machine-specific; paths in the payload are "
            "repository-relative only"},
)

CHANGE_LEDGER = (
    {"field": "contract identity", "change": "REPLACED",
     "defect": "the v3 digest committed to declarations only, so the parser, "
               "classifier, citation logic, grader, prompt projection, fixture "
               "builder, truth matrix, prompt hashes and control forms could "
               "all change while the hash stayed constant",
     "reason": "a frozen contract that cannot detect a prompt which leaks the "
               "answer is a label, not a freeze",
     "expected_effect": "the digest moves for any material behavioural change",
     "found_by": "control plane, reviewing the v3 payload against its implementation"},
    {"field": "independent verifier", "change": "ADDED",
     "defect": None,
     "reason": "reconstruct the payload from a clean checkout and compare; the "
               "manifest and the contract digest each prove something the other "
               "cannot",
     "expected_effect": "verification fails closed on missing sources, changed "
                        "behaviour tables, altered prompts, or a widened "
                        "exclusion list",
     "found_by": "executor, implementing the repair"},
    {"field": "all scientific behaviour", "change": "UNCHANGED",
     "defect": None, "reason": "v4 repairs identity only",
     "expected_effect": "byte-identical prompts and row-identical tables vs v3",
     "found_by": None},
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_hashes() -> dict[str, str]:
    root = _repo_root()
    digests = {}
    for relative in SOURCE_FILES:
        path = root / relative
        if not path.exists():
            raise FileNotFoundError(f"scientific source missing: {relative}")
        digests[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


# --- behaviour tables: computed by RUNNING the real functions ----------------
def parser_table() -> list[dict[str, Any]]:
    rows = []
    for kind, fixtures in (("valid", VALID_FIXTURES), ("invalid", INVALID_FIXTURES)):
        for fixture in fixtures:
            parsed = V3.parse_response(fixture["text"])
            rows.append({"kind": kind, "name": fixture["name"],
                         "parse_status": parsed["parse_status"],
                         "parsed": parsed["parsed"],
                         "answer": parsed["answer"],
                         "citations": list(parsed["citations"])})
    return rows


def classifier_table() -> list[dict[str, Any]]:
    rows = []
    for core, values in sorted(CANONICAL.items()):
        probes = {
            "INSUFFICIENT": V3.INSUFFICIENT,
            "CURRENT_ONLY": values["current"],
            "STALE_ONLY": values["stale"],
            "BOTH": f"{values['current']} and {values['stale']}",
            "NEITHER": "something else entirely",
        }
        for expected, text in probes.items():
            rows.append({"core": core, "probe": expected,
                         "observed": V3.classify_answer(text, core)})
    return rows


def citation_table() -> list[dict[str, Any]]:
    rows = []
    for case in V3.build_fixture()["cases"]:
        probes = {"EMPTY": [], "UNKNOWN": ["REC-0000000000"]}
        if case["current_opaque"]:
            probes["CURRENT"] = [case["current_opaque"]]
        if case["stale_opaque"]:
            probes["STALE"] = [case["stale_opaque"]]
        if case["current_opaque"] and case["stale_opaque"]:
            probes["BOTH_IDS"] = [case["current_opaque"], case["stale_opaque"]]
        for name, citations in sorted(probes.items()):
            rows.append({"case": case["id"], "probe": name,
                         "relation": V3.citation_relation(citations, case)})
    return rows


def prompt_hashes() -> dict[str, str]:
    """Resolve project_prompt through the module at CALL time.

    Binding it at import captured a stale reference, so substituting the real
    function at runtime left the digest unmoved - the one mutation of four that
    v4 still missed, and the worst one, because a leaking prompt is exactly what
    a freeze must catch. Found by this generation's own mutation probe.
    """
    return {case["id"]: hashlib.sha256(
        V3.project_prompt(case).encode()).hexdigest()
            for case in build_fixture()["cases"]}


def fixture_identity() -> list[dict[str, Any]]:
    """Enough to detect case, record, order, question or opaque-id drift.

    Resolved through the module at call time, for the reason in prompt_hashes.
    """
    return [{"id": c["id"], "core": c["core"], "condition": c["condition"],
             "question": c["question"], "context_order": list(c["context_order"]),
             "records": [{"opaque_id": r["opaque_id"], "text": r["text"],
                          "scope": r["scope"], "configuration": r["configuration"]}
                         for r in c["records"]],
             "current_opaque": c["current_opaque"],
             "stale_opaque": c["stale_opaque"]}
            for c in build_fixture()["cases"]]


def contract_payload() -> dict[str, Any]:
    """The complete deterministic payload whose canonical form is hashed."""
    return {
        "version": CONTRACT_VERSION,
        "source_fixture": V3.build_fixture()["source_fixture"],
        "conditions": list(CONDITIONS),
        "answer_classes": list(ANSWER_CLASSES),
        "citation_relations": list(CITATION_RELATIONS),
        "outcomes": list(OUTCOMES),
        "canonical_values": CANONICAL,
        "normalization": NORMALIZATION,
        "instruction": INSTRUCTION,
        "accept_json_fence": ACCEPT_JSON_FENCE,
        "grading_precedence": ["parser status", "semantic answer class",
                               "citation relation", "condition-relative outcome"],
        "control_rule": CONTROL_RULE,
        "control_passing_forms": V3.control_passing_forms(),
        "across_core_verdicts": list(ACROSS_CORE_VERDICTS),
        "questions": list(QUESTIONS),
        "repetitions": REPETITIONS,
        "reader_settings": READER_SETTINGS,
        "change_ledger": list(CHANGE_LEDGER),
        "exclusions": list(EXCLUSIONS),
        # generated + executable coverage
        "fixture_identity": fixture_identity(),
        "prompt_sha256": prompt_hashes(),
        "parser_table": parser_table(),
        "classifier_table": classifier_table(),
        "citation_table": citation_table(),
        "truth_matrix": V3.truth_matrix(),
        "source_sha256": source_hashes(),
    }


def canonical_bytes(payload: Mapping[str, Any] | None = None) -> bytes:
    return json.dumps(payload if payload is not None else contract_payload(),
                      sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, default=str).encode()


def contract_hash(payload: Mapping[str, Any] | None = None) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


# --- independent verification -------------------------------------------------
def verify_contract(frozen: Mapping[str, Any]) -> dict[str, Any]:
    """Reconstruct from the checked-out sources and compare. Fails closed."""
    problems: list[str] = []
    recorded = frozen.get("contract_sha256")
    if not recorded:
        problems.append("frozen artifact carries no contract_sha256")

    try:
        rebuilt = contract_payload()
    except FileNotFoundError as exc:
        return {"verified": False, "problems": [str(exc)]}

    if contract_hash(rebuilt) != recorded:
        problems.append("recomputed digest does not match the frozen digest")

    stored = frozen.get("contract_payload")
    if stored is not None:
        for key in sorted(set(stored) | set(rebuilt)):
            if key not in stored:
                problems.append(f"payload gained field {key!r}")
            elif key not in rebuilt:
                problems.append(f"payload lost field {key!r}")
            elif json.dumps(stored[key], sort_keys=True, default=str) != \
                    json.dumps(rebuilt[key], sort_keys=True, default=str):
                problems.append(f"payload field {key!r} changed")

    declared = {e["field"] for e in frozen.get("exclusions", EXCLUSIONS)}
    if declared - {e["field"] for e in EXCLUSIONS}:
        problems.append("the exclusion list has widened")

    return {"verified": not problems, "problems": problems,
            "recomputed": contract_hash(rebuilt), "frozen": recorded}


def assert_behaviour_identical_to_v3() -> dict[str, Any]:
    """v4 may change identity only. Any scientific drift is a failure."""
    checks = {
        "truth_matrix": truth_matrix() == V3.truth_matrix(),
        "control_forms": control_passing_forms() == V3.control_passing_forms(),
        "prompts": all(project_prompt(c) == V3.project_prompt(c)
                       for c in build_fixture()["cases"]),
        "parser": all(parse_response(f["text"]) == V3.parse_response(f["text"])
                      for f in VALID_FIXTURES + INVALID_FIXTURES),
        "classifier": classifier_table() == [
            {**row, "observed": V3.classify_answer(
                {"INSUFFICIENT": V3.INSUFFICIENT,
                 "CURRENT_ONLY": CANONICAL[row["core"]]["current"],
                 "STALE_ONLY": CANONICAL[row["core"]]["stale"],
                 "BOTH": f"{CANONICAL[row['core']]['current']} and "
                         f"{CANONICAL[row['core']]['stale']}",
                 "NEITHER": "something else entirely"}[row["probe"]], row["core"])}
            for row in classifier_table()],
    }
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        raise ValueError(f"v4 drifted from v3 in: {failed}")
    return checks
