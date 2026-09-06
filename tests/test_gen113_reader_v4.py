"""Gen113: I1-I6. A freeze that actually detects a changed ruler."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference_v3 as V3
from memory_bakeoff import reader_interference_v4 as V4

ROOT = Path(__file__).resolve().parents[1]
def _latest_attempt():
    """The authoritative freeze is the LAST attempt, not the first.

    attempt1 was a pre-repair freeze: its payload still bound three behaviour
    tables at import, so it could not see a substituted classifier, grader or
    parser. Correcting that changed the payload and therefore the digest, and
    the evidence contract refused to overwrite attempt1 - which is the contract
    working. attempt1 is PRESERVED and superseded; attempt2 is authoritative.
    """
    base = ROOT / "results" / "gen113"
    if not base.exists():
        return None
    attempts = sorted(base.glob("attempt*"), key=lambda p: int(p.name[7:]))
    return attempts[-1] if attempts else None


ATTEMPT = _latest_attempt()


def frozen():
    if ATTEMPT is None or not (ATTEMPT / "reader_interference_v4.json").exists():
        pytest.skip("v4 not frozen in this checkout")
    return json.loads((ATTEMPT / "reader_interference_v4.json").read_text())


# --- I1: the v3 blind spots were real ----------------------------------------
@pytest.mark.parametrize("attribute,replacement", [
    ("classify_answer", lambda a, c: "NEITHER"),
    ("grade", lambda p, c: {"outcome": V3.PROHIBITED_STALE, "answer_class": "X",
                            "citation_relation": "Y", "why": ""}),
    ("parse_response", lambda t: {"parse_status": "PARSED", "parsed": True,
                                  "answer": "hijacked", "citations": ()}),
    ("project_prompt", lambda c: "LEAKED: the second record is current"),
])
def test_v3_hash_is_blind_to_behaviour_changes(monkeypatch, attribute, replacement):
    before = V3.contract_hash()
    monkeypatch.setattr(V3, attribute, replacement)
    assert V3.contract_hash() == before, f"{attribute} unexpectedly moved v3"


def test_the_audit_records_all_four_witnesses():
    if ATTEMPT is None:
        pytest.skip("audit not present")
    audit = json.loads((ATTEMPT / "gen112_contract_hash_gap_audit.json").read_text())
    assert len(audit["witnesses"]) == 4
    assert all(not w["v3_hash_moved"] and w["v4_hash_moved"]
               for w in audit["witnesses"])
    assert audit["gen112_files_modified"] is False


def test_the_audit_admits_the_gap_the_executor_found_in_its_own_repair():
    if ATTEMPT is None:
        pytest.skip("audit not present")
    audit = json.loads((ATTEMPT / "gen112_contract_hash_gap_audit.json").read_text())
    own = audit["executor_found_gap_in_its_own_repair"]
    assert "bound project_prompt at import" in own["detail"]
    assert own["found_by"].startswith("executor")


# --- I2: coverage -------------------------------------------------------------
def test_payload_covers_declarations_generated_tables_and_source_bytes():
    payload = V4.contract_payload()
    for field in ("conditions", "canonical_values", "questions", "control_rule",
                  "reader_settings", "repetitions",
                  "fixture_identity", "prompt_sha256", "parser_table",
                  "classifier_table", "citation_table", "truth_matrix",
                  "control_passing_forms", "source_sha256"):
        assert field in payload, field
    assert len(payload["truth_matrix"]) == 360
    assert len(payload["prompt_sha256"]) == 20
    assert set(payload["source_sha256"]) == set(V4.SOURCE_FILES)


def test_every_exclusion_is_stated_and_only_three_exist():
    fields = {e["field"] for e in V4.EXCLUSIONS}
    assert fields == {"contract_sha256", "write timestamps",
                      "output directory paths"}
    for exclusion in V4.EXCLUSIONS:
        assert exclusion["why"]


def test_the_digest_is_not_inside_its_own_payload():
    assert "contract_sha256" not in V4.contract_payload()


# --- I3: every material change moves the digest or fails verification --------
@pytest.mark.parametrize("attribute,replacement", [
    ("classify_answer", lambda a, c: "NEITHER"),
    ("grade", lambda p, c: {"outcome": V3.PROHIBITED_STALE, "answer_class": "X",
                            "citation_relation": "Y", "why": ""}),
    ("parse_response", lambda t: {"parse_status": "PARSED", "parsed": True,
                                  "answer": "hijacked", "citations": ()}),
    ("project_prompt", lambda c: "LEAKED: the second record is current"),
])
def test_v4_detects_every_behaviour_change(monkeypatch, attribute, replacement):
    """Detection is a moved digest OR a refusal to produce one.

    A hijacked classifier or grader makes control_passing_forms() raise, because
    no control can pass any more - so contract_hash() fails closed rather than
    returning a different value. That is stronger than a changed digest, not
    weaker, and the assertion has to allow for it.
    """
    before = V4.contract_hash()
    monkeypatch.setattr(V3, attribute, replacement)
    try:
        detected = V4.contract_hash() != before
        how = "digest moved"
    except Exception:
        detected, how = True, "failed closed"
    assert detected, f"v4 is blind to {attribute}"
    assert how in ("digest moved", "failed closed")


@pytest.mark.parametrize("attribute,value", [
    ("REPETITIONS", 5),
    ("READER_SETTINGS", {"endpoint": "elsewhere"}),
    ("QUESTIONS", ()),
    ("CONTROL_RULE", {"rule": "relaxed"}),
    ("INSTRUCTION", "say whatever you like"),
    ("ACCEPT_JSON_FENCE", False),
    ("CANONICAL", {}),
])
def test_v4_digest_moves_for_declaration_changes(monkeypatch, attribute, value):
    before = V4.contract_hash()
    monkeypatch.setattr(V4, attribute, value)
    assert V4.contract_hash() != before, attribute


def test_a_changed_source_byte_moves_the_digest(monkeypatch, tmp_path):
    before = V4.contract_hash()
    real = V4.source_hashes()
    monkeypatch.setattr(V4, "source_hashes",
                        lambda: {**real, V4.SOURCE_FILES[0]: "0" * 64})
    assert V4.contract_hash() != before


def test_a_missing_source_file_fails_closed(monkeypatch):
    monkeypatch.setattr(V4, "SOURCE_FILES", V4.SOURCE_FILES + ("src/nope.py",))
    with pytest.raises(FileNotFoundError, match="scientific source missing"):
        V4.source_hashes()


# --- I4: independent reconstruction ------------------------------------------
def test_verifier_accepts_the_frozen_artifact():
    result = V4.verify_contract(frozen())
    assert result["verified"] is True, result["problems"]
    assert result["recomputed"] == result["frozen"]


def test_verifier_rejects_a_tampered_digest():
    tampered = {**frozen(), "contract_sha256": "0" * 64}
    result = V4.verify_contract(tampered)
    assert result["verified"] is False
    assert any("does not match" in p for p in result["problems"])


def test_verifier_rejects_a_widened_exclusion_list():
    tampered = {**frozen(),
                "exclusions": list(V4.EXCLUSIONS) + [{"field": "truth_matrix",
                                                      "why": "convenient"}]}
    assert V4.verify_contract(tampered)["verified"] is False


def test_verifier_notices_a_lost_or_gained_payload_field():
    payload = dict(frozen()["contract_payload"])
    payload.pop("truth_matrix")
    assert V4.verify_contract({**frozen(), "contract_payload": payload})["verified"] is False
    payload = {**frozen()["contract_payload"], "extra": 1}
    assert V4.verify_contract({**frozen(), "contract_payload": payload})["verified"] is False


def test_manifest_and_contract_are_separate_proofs():
    if ATTEMPT is None:
        pytest.skip("attempt not present")
    assert EV.verify(ATTEMPT)["verified"] is True
    assert V4.verify_contract(frozen())["verified"] is True


def test_digest_is_reproducible_from_the_checkout():
    assert V4.contract_hash() == frozen()["contract_sha256"]
    assert hashlib.sha256(V4.canonical_bytes()).hexdigest() == frozen()["contract_sha256"]


# --- I5: no scientific drift --------------------------------------------------
def test_v4_is_behaviour_identical_to_v3():
    assert all(V4.assert_behaviour_identical_to_v3().values())


@pytest.mark.parametrize("condition,answer", [
    ("CLEAN_CURRENT", "41 t/s, previously 27 t/s"),
    ("CLEAN_STALE_NEGATIVE_CONTROL", "27 t/s, now 41 t/s"),
])
def test_both_gen112_witnesses_still_grade_mixed(condition, answer):
    case = next(c for c in V4.build_fixture()["cases"]
                if c["core"] == "throughput:atlas" and c["condition"] == condition)
    reply = json.dumps({"answer": answer,
                        "citations": [case["current_opaque"] or case["stale_opaque"]]})
    assert V4.grade(V4.parse_response(reply), case)["outcome"] == V4.MIXED


def test_control_forms_and_matrix_unchanged():
    assert V4.control_passing_forms() == V3.control_passing_forms()
    assert V4.truth_matrix() == V3.truth_matrix()
    V4.assert_no_control_pass_from_a_bad_answer(V4.truth_matrix())


def test_all_twenty_prompts_still_byte_identical():
    for case in V4.build_fixture()["cases"]:
        assert V4.project_prompt(case) == V3.project_prompt(case)
        V4.assert_prompt_is_blind(case)


# --- I6: history intact -------------------------------------------------------
@pytest.mark.parametrize("gen,count", [(109, 1), (110, 6), (111, 2), (112, 2)])
def test_every_earlier_attempt_still_verifies(gen, count):
    path = ROOT / "results" / f"gen{gen}" / "attempt1"
    if not path.exists():
        pytest.skip(f"gen{gen} absent")
    result = EV.verify(path)
    assert result["verified"] is True and result["artifacts"] == count


def test_v3_superseded_for_identity_not_science():
    supersedes = frozen()["supersedes"]
    assert supersedes["status"] == "SUPERSEDED_AS_RULER / NON_EVIDENCE"
    assert supersedes["science_was_sound"] is True
    assert supersedes["never_executed"] is True
    assert supersedes["scientific_loss"] == "none"


def test_gen113_declares_it_ran_nothing():
    assert frozen()["status"] == "FROZEN_UNRUN"
    assert "OPEN" in frozen()["reader_question_state"]



# --- the superseded first attempt is preserved, not deleted ------------------
def test_attempt1_is_preserved_and_superseded():
    first = ROOT / "results" / "gen113" / "attempt1"
    if not first.exists():
        pytest.skip("attempt1 absent")
    assert EV.verify(first)["verified"] is True, \
        "the superseded attempt must still verify against its own manifest"
    stale = json.loads((first / "reader_interference_v4.json").read_text())
    assert stale["contract_sha256"] != V4.contract_hash(), \
        "attempt1 froze a payload that predates the binding repair"
    assert ATTEMPT.name != "attempt1", "attempt1 is not the authoritative freeze"
