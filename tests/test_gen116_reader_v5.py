"""Gen116: prove the v5 freeze, including every rule that bit an earlier ruler."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference_v5 as V5

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = V5.build_fixture()
CASES = {c["case_id"]: c for c in FIXTURE["cases"]}
PROMPTS = {cid: V5.project_prompt(c) for cid, c in CASES.items()}
MODEL_FACING = " ".join(PROMPTS.values()).casefold()


# --- F1 fixture freshness and leakage ----------------------------------------
def test_twelve_cores_sixty_unique_cases():
    assert len(V5.CORES) == 12
    assert len(CASES) == 60
    assert len({c["core"] for c in FIXTURE["cases"]}) == 12


def test_every_prompt_is_byte_distinct():
    assert len(set(PROMPTS.values())) == 60, "nominal repetitions are forbidden"


def test_no_exposed_core_material_is_reused():
    for term in ("vega", "solstice", "kestrel", "atlas", "rota", "gib", "t/s"):
        assert not re.search(rf"(?<!\w){term}(?!\w)", MODEL_FACING), f"{term} is exposed"


def test_no_progression_language_in_model_facing_text():
    leaked = [w for w in V5.BANNED_PROSE if re.search(rf"(?<!\w){w}(?!\w)", MODEL_FACING)]
    assert leaked == []


def test_no_role_words_in_records_or_ids():
    rec = " ".join(f"{r['record_id']} {r['statement']}"
                   for c in FIXTURE["cases"] for r in c["records"]).casefold()
    assert [w for w in V5.BANNED_ROLE if re.search(rf"(?<!\w){w}(?!\w)", rec)] == []


def test_record_ids_are_generated_independently_of_revision():
    """The digest must come from a slot, never from the role."""
    for core in V5.CORES:
        ids = {V5.record_id(core["key"], 1), V5.record_id(core["key"], 2)}
        slots = {V5._slot_id(core["key"], 0), V5._slot_id(core["key"], 1)}
        assert ids == slots
    # and the slot->revision map alternates, so ordering cannot track the role
    first = sum(1 for c in V5.CORES if V5.record_id(c["key"], 2) == V5._slot_id(c["key"], 0))
    assert first == 6, "slot assignment must be balanced across cores"


def test_values_are_symmetric_and_unbiased():
    longer = larger = digits = 0
    for core in V5.CORES:
        v = V5.canonical_values(core)
        assert len(v[1].split()) == len(v[2].split())
        assert v[1].split()[0] == v[2].split()[0]
        assert abs(len(v[1]) - len(v[2])) <= 2
        longer += len(v[2]) > len(v[1])
        larger += v[2] > v[1]
        digits += any(ch.isdigit() for ch in v[1] + v[2])
    assert digits == 0, "version-like numeric values are banned"
    assert longer == 6, f"revision 2 longer in {longer}/12 - must not be systematic"
    assert larger == 6, f"revision 2 lexicographically larger in {larger}/12"


# --- F2/F3 structure and decidability ----------------------------------------
def test_conflict_order_is_counterbalanced():
    cf = [c for c in FIXTURE["cases"] if c["condition"] == "CONFLICT_CURRENT_FIRST"]
    sf = [c for c in FIXTURE["cases"] if c["condition"] == "CONFLICT_STALE_FIRST"]
    assert len(cf) == len(sf) == 12
    assert all(c["records"][0]["effective_revision"] == 2 for c in cf)
    assert all(c["records"][0]["effective_revision"] == 1 for c in sf)


def test_recency_is_derivable_only_from_the_frozen_fields():
    for cid, p in PROMPTS.items():
        assert "effective_revision" in p and "as_of_revision" in p
        assert "INSUFFICIENT" in p, "the abstention rule must be stated in every prompt"


def test_both_records_share_schema_and_field_order():
    for c in FIXTURE["cases"]:
        rendered = [l for l in V5.project_prompt(c).splitlines() if l.startswith("[REC-")]
        for line in rendered:
            assert re.match(r"^\[REC-[0-9A-F]{10}\] effective_revision: [12] \| ", line)


# --- F4/F5 ontology and matching ---------------------------------------------
def test_ontology_is_exhaustive_over_the_declared_contract():
    reached = {r["answer_class"] for r in V5._ontology_table()}
    assert set(V5.ONTOLOGY) - reached == set()


def test_classifier_returns_exactly_one_label():
    vals = {1: "lane amber", 2: "lane cobalt"}
    body = {"ok": True, "disposition": "RESOLVED", "selected_record_id": "R",
            "selected_value": "lane cobalt", "prior_values": [], "citations": []}
    assert V5.classify_answer(body, vals) in V5.ONTOLOGY


def test_contradiction_requires_assertion_not_substring():
    vals = {1: "lane amber", 2: "lane cobalt"}
    both = {"ok": True, "disposition": "UNRESOLVED", "selected_record_id": None,
            "selected_value": None, "prior_values": ["lane amber", "lane cobalt"],
            "citations": []}
    assert V5.classify_answer(both, vals) == V5.UNRESOLVED_BOTH
    hist = {**both, "disposition": "RESOLVED", "selected_record_id": "R",
            "selected_value": "lane cobalt", "prior_values": ["lane amber"]}
    assert V5.classify_answer(hist, vals) == V5.CURRENT_WITH_HISTORY
    # Simultaneity must be ASSERTED - both values named as the selection. A null
    # selection is not an assertion of anything.
    asserted = {**both, "disposition": "RESOLVED", "selected_record_id": "R",
                "selected_value": "lane amber and lane cobalt"}
    assert V5.classify_answer(asserted, vals) == V5.SIMULTANEOUS


def test_parser_rejects_incoherent_dispositions():
    """An abstention that still picks a value is not an abstention."""
    bad = ('{"disposition":"INSUFFICIENT","selected_record_id":"R",'
           '"selected_value":"lane amber","prior_values":[],"citations":[]}')
    assert V5.parse_response(bad)["ok"] is False
    bad2 = ('{"disposition":"RESOLVED","selected_record_id":null,'
            '"selected_value":null,"prior_values":[],"citations":[]}')
    assert V5.parse_response(bad2)["ok"] is False


def test_success_requires_the_selection_and_the_citation():
    """Naming the right value while pointing at the wrong record is not success."""
    case = CASES["core01|CONFLICT_CURRENT_FIRST"]
    right, wrong = case["expected_record_id"], case["records"][1]["record_id"]
    def body(**kw):
        return {"ok": True, "disposition": "RESOLVED", "selected_record_id": right,
                "selected_value": case["expected_value"], "prior_values": [],
                "citations": [right], **kw}
    assert V5.grade(body(), case)["meets_success_state"] is True
    assert V5.grade(body(selected_record_id=wrong), case)["meets_success_state"] is False
    assert V5.grade(body(citations=[]), case)["meets_success_state"] is False
    assert V5.grade(body(citations=["REC-NOTSHOWN"]), case)["meets_success_state"] is False


@pytest.mark.parametrize("text,value,expected", [
    ("lane amber", "lane amber", True),
    ("lane ambergris", "lane amber", False),          # containment collision
    ("LANE AMBER", "lane amber", True),               # case
    ("the answer is lane amber.", "lane amber", True),  # punctuation
    ("not lane amber", "lane amber", True),           # negation is not matching's job
    ('"lane amber"', "lane amber", True),             # quotation
    ("lane  amber", "lane amber", True),              # collapsed whitespace
    ("xlane ambery", "lane amber", False),            # adversarial collision
    ("lane ämber", "lane amber", False),              # unicode
])
def test_token_aware_matching(text, value, expected):
    assert V5.value_present(text, value) is expected


def test_unsupported_value_is_detected():
    vals = {1: "lane amber", 2: "lane cobalt"}
    body = {"ok": True, "disposition": "RESOLVED", "selected_record_id": "R",
            "selected_value": "lane viridian", "prior_values": [], "citations": []}
    assert V5.classify_answer(body, vals) == V5.UNSUPPORTED_VALUE


@pytest.mark.parametrize("bad", [
    "not json", "[]", '{"disposition":"RESOLVED"}',
    '{"disposition":"MAYBE","selected_record_id":null,"selected_value":null,'
    '"prior_values":[],"citations":[]}',
])
def test_parser_is_strict(bad):
    assert V5.parse_response(bad)["ok"] is False
    assert V5.classify_answer(V5.parse_response(bad), {1: "a b", 2: "c d"}) == V5.MALFORMED


# --- R-9 citation independence -----------------------------------------------
def test_citations_can_never_rewrite_answer_class():
    case = CASES["core01|CONFLICT_CURRENT_FIRST"]
    vals = {int(k): v for k, v in case["canonical_values"].items()}
    base = {"ok": True, "disposition": "RESOLVED",
            "selected_record_id": case["expected_record_id"],
            "selected_value": case["expected_value"], "prior_values": []}
    classes = {V5.classify_answer({**base, "citations": c}, vals)
               for c in ([], ["REC-NOTSHOWN"], case["context_order"], case["context_order"][:1])}
    assert len(classes) == 1, "answer class must not depend on citations"


def test_citation_relation_is_recorded_separately():
    case = CASES["core01|CONFLICT_CURRENT_FIRST"]
    body = {"ok": True, "disposition": "RESOLVED",
            "selected_record_id": case["expected_record_id"],
            "selected_value": case["expected_value"], "prior_values": [],
            "citations": ["REC-NOTSHOWN"]}
    assert V5.citation_relation(body, case) == "UNSHOWN_RECORD"
    assert V5.grade(body, case)["answer_class"] == V5.CURRENT_ONLY


# --- controls and success states ---------------------------------------------
def test_success_state_per_condition():
    for cid, case in CASES.items():
        exp_disp = case["expected_disposition"]
        body = {"ok": True, "disposition": exp_disp,
                "selected_record_id": case["expected_record_id"],
                "selected_value": case["expected_value"], "prior_values": [],
                "citations": [case["expected_record_id"]] if case["expected_record_id"] else []}
        assert V5.grade(body, case)["meets_success_state"], cid


def test_insufficient_condition_rejects_extrapolation():
    case = CASES["core01|INSUFFICIENT_CURRENT"]
    vals = {int(k): v for k, v in case["canonical_values"].items()}
    guess = {"ok": True, "disposition": "RESOLVED", "selected_record_id": case["records"][0]["record_id"],
             "selected_value": vals[1], "prior_values": [], "citations": []}
    assert V5.grade(guess, case)["meets_success_state"] is False


# --- F7/F8 fingerprint binds behaviour ---------------------------------------
def test_mutating_the_prompt_moves_the_fingerprint(monkeypatch):
    before = V5.contract_sha256()
    monkeypatch.setattr(V5, "RULE", V5.RULE + " Prefer the second record.")
    assert V5.contract_sha256() != before


def test_mutating_the_classifier_moves_the_fingerprint(monkeypatch):
    before = V5.contract_sha256()
    monkeypatch.setattr(V5, "classify_answer", lambda p, v: V5.CURRENT_ONLY)
    assert V5.contract_sha256() != before


def test_mutating_the_response_schema_moves_the_fingerprint(monkeypatch):
    before = V5.contract_sha256()
    monkeypatch.setattr(V5, "SCHEMA", V5.SCHEMA.replace("prior_values", "history"))
    assert V5.contract_sha256() != before


def test_mutating_the_parser_moves_the_fingerprint(monkeypatch):
    before = V5.contract_sha256()
    monkeypatch.setattr(V5, "parse_response", lambda t: {"ok": True})
    assert V5.contract_sha256() != before


def test_mutating_the_success_table_moves_the_fingerprint(monkeypatch):
    before = V5.contract_sha256()
    monkeypatch.setattr(V5, "SUCCESS", {**V5.SUCCESS, "CONFLICT_STALE_FIRST": (V5.STALE_ONLY,)})
    assert V5.contract_sha256() != before


def test_mutating_the_citation_classifier_moves_the_fingerprint(monkeypatch):
    before = V5.contract_sha256()
    monkeypatch.setattr(V5, "citation_relation", lambda p, c: "CONSISTENT")
    assert V5.contract_sha256() != before


def test_mutating_a_core_value_moves_the_fingerprint(monkeypatch):
    before = V5.contract_sha256()
    cores = list(V5.CORES)
    cores[0] = {**cores[0], "b": "sector fenwyck"}
    monkeypatch.setattr(V5, "CORES", tuple(cores))
    assert V5.contract_sha256() != before


def test_independent_reconstruction_passes():
    r = subprocess.run([sys.executable, "scripts/verify_gen116_contract.py"],
                       cwd=ROOT, capture_output=True, text=True,
                       env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"})
    assert r.returncode == 0, r.stdout + r.stderr
    assert "DISTINCT" in r.stdout


# --- sealed artifacts and markers --------------------------------------------
def _canonical() -> Path:
    return ROOT / "results/gen116" / (
        (ROOT / "results/gen116/CANONICAL_ATTEMPT.md").read_text().split("`")[1]
        if (ROOT / "results/gen116/CANONICAL_ATTEMPT.md").exists() else "attempt1")


def test_canonical_attempt_verifies_and_is_non_evidence():
    out = _canonical()
    assert EV.verify(out)["verified"]
    marker = json.loads((out / "NON_EVIDENCE.json").read_text())
    assert marker["marker"] == "NON_EVIDENCE"
    assert marker["reader_calls"] == 0 and marker["model_calls"] == 0
    assert marker["may_not_be_upgraded_retrospectively"] is True


def test_no_reader_result_exists_anywhere_in_gen116():
    """No vacuous exemptions: NON_EVIDENCE.json never contains RUN_EVIDENCE, so
    exempting it made the check unable to fail on that file."""
    for p in (ROOT / "results/gen116").rglob("*.json"):
        blob = p.read_text()
        assert "RUN_EVIDENCE" not in blob, p
        assert "reader_responses" not in blob, p


def test_legacy_projection_is_marked_non_confirmatory():
    d = json.loads((_canonical() / "reader_interference_v5_legacy_development_projection.json").read_text())
    assert d["status"] == "NON_CONFIRMATORY"
    assert d["restores_retracted_v4_reading"] is False


def test_historical_evidence_is_unchanged():
    for p in ("results/gen114/attempt1", "results/gen115/attempt4", "results/gen113/attempt2"):
        assert EV.verify(ROOT / p)["verified"], p


def test_contract_names_tracked_runner_grader_and_verifier():
    c = json.loads((_canonical() / "reader_interference_v5_contract.json").read_text())
    for key in ("runner", "grader", "verifier"):
        path = ROOT / c[key]
        assert path.exists(), f"{key} {c[key]} must exist at the pinned commit"
        assert c["source_sha256"][c[key]] == hashlib.sha256(path.read_bytes()).hexdigest()
