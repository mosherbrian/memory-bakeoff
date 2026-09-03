"""Gen36: the MemConflict contract must be exact about what a product may see,
where its history stops, and which numbers were never measured."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from memory_bakeoff import memconflict as M
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.round2_reporting import ReportingError, Status

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "results/memconflict_gen36_contract"
PILOT_DIR = ROOT / "results/memconflict_gen36_pilot"

pytestmark = pytest.mark.skipif(not CONTRACT_DIR.is_dir(), reason="Gen36 artifacts not present")


@pytest.fixture(scope="module")
def contract() -> dict:
    return json.loads((CONTRACT_DIR / "contract.json").read_text())


@pytest.fixture(scope="module")
def persona() -> dict:
    return M.load_personas()[0]


def test_upstream_pin_is_exact(contract):
    assert contract["upstream"]["commit"] == "ec51d5d36e87f7665d1337f3a88cbde95fc2a964"
    assert contract["upstream"]["dataset_path"] == "Data/Step4_4.jsonl"
    assert contract["upstream"]["dataset_sha256"] == M.DATASET_SHA256
    assert M.dataset_sha256() == M.DATASET_SHA256


def test_dataset_parses_completely_and_totals_reconcile(contract):
    stats = contract["dataset_statistics"]
    personas = M.load_personas()
    assert len(personas) == stats["personas"] == 30
    counted = sum(len(M.questions(p)) for p in personas)
    assert counted == stats["questions_total"] == 3750
    assert sum(stats["questions_by_conflict_type"].values()) == counted
    assert stats["persona_ids_unique"] is True


def test_malformed_messages_are_counted_not_dropped(contract):
    stats = contract["dataset_statistics"]
    assert stats["malformed_messages_excluded"] == len(stats["malformed_message_ids"])
    assert stats["malformed_messages_excluded"] > 0
    assert sum(stats["malformed_messages_by_anomaly"].values()) == stats["malformed_messages_excluded"]


def test_public_and_scorer_only_registries_are_disjoint_and_complete(contract):
    public = set(contract["field_registry"]["public_input_fields"])
    scorer = set(contract["field_registry"]["scorer_only_fields"])
    assert public & scorer == set()
    assert "Full_Session_Chain[].Session_Questions[].answer" in scorer
    assert "Full_Session_Chain[].Session_Questions[].conflict_type" in scorer
    assert "Full_Session_Chain[].Updated_Attributes" in scorer
    assert "Full_Session_Chain[].Session_Dialogue" in public


@pytest.mark.parametrize("payload", [
    {"content": "hi", "answer": "gold"},
    {"metadata": {"conflict_type": "static_conflict"}},
    {"units": [{"text": "hi", "Updated_Attributes": []}]},
    {"nested": {"deeper": {"Static_Conflict_Information": [{"Role": "Point_A"}]}}},
    {"Session_Questions": [{"question": "public", "answer": "gold"}]},
])
def test_every_scorer_only_field_is_rejected_in_a_payload(payload):
    with pytest.raises(ReportingError):
        M.assert_public_only(payload)


def test_public_question_text_is_allowed():
    M.assert_public_only({"question_id": "Q_001", "question": "Did the residence change?"})


def test_chronology_prefix_is_inclusive_and_future_is_rejected(persona):
    units = M.ingestion_units(persona)
    question = next(q for q in M.questions(persona) if q.session_index > 0)
    allowed = M.allowed_session_indices(question)
    assert allowed.stop == question.session_index + 1
    M.assert_within_boundary(question, [u for u in units if u.session_index in allowed])
    future = [u for u in units if u.session_index > question.session_index]
    assert future
    with pytest.raises(ReportingError):
        M.assert_within_boundary(question, future[:1])


def test_metric_legal_streams_are_enforced():
    M.legal_stream("exact_support_hit_at_k", M.Stream.RETRIEVAL)
    with pytest.raises(ReportingError):
        M.legal_stream("exact_support_hit_at_k", M.Stream.ANSWER_READER)
    with pytest.raises(ReportingError):
        M.legal_stream("dynamic_answer_accuracy", M.Stream.RETRIEVAL)
    with pytest.raises(ReportingError):
        M.legal_stream("no_such_metric", M.Stream.RETRIEVAL)


def test_unmappable_gold_is_unmeasured_not_zero(persona):
    unmeasured = None
    for p in M.load_personas():
        for question in M.questions(p):
            gold = M.gold_for(p, question)
            if gold.support_sessions is None:
                unmeasured = (p, question, gold)
                break
        if unmeasured:
            break
    assert unmeasured, "the corpus must contain at least one unmappable question"
    _, question, gold = unmeasured
    rank = M.first_support_rank([], gold)
    assert rank.status is Status.UNMEASURED
    assert M.hit_at_k(rank, 3).status is Status.UNMEASURED
    assert M.log_rank_at_k(rank, 3) is None
    with pytest.raises(ReportingError):
        rank.value_or_raise()


def test_measured_zero_is_distinct_from_unmeasured(persona):
    question = next(q for q in M.questions(persona))
    gold = M.gold_for(persona, question)
    assert gold.support_sessions is not None
    rank = M.first_support_rank([], gold)
    assert rank.status is Status.MEASURED_ZERO
    assert rank.value_or_raise() == 0
    assert M.hit_at_k(rank, 3).value_or_raise() == 0


def test_exact_whitebox_credits_session_identity_not_text(persona):
    """A unit with the right words but the wrong released session earns nothing."""
    units = M.ingestion_units(persona)
    question = next(q for q in M.questions(persona))
    gold = M.gold_for(persona, question)
    assert gold.support_sessions is not None
    supporting = next(u for u in units if u.session_id in gold.support_sessions)
    impostor = M.Unit(persona_id=supporting.persona_id, session_id=-1, session_index=0,
                      turn_index=1, message_index=1, role=supporting.role,
                      text=supporting.text, date=supporting.date)
    assert M.first_support_rank([impostor], gold).status is Status.MEASURED_ZERO
    assert M.first_support_rank([supporting], gold).value_or_raise() == 1


def test_oracle_reaches_the_maximum(persona):
    """Scorer-side only: proves the metric can be earned, never published as a contestant."""
    units = M.ingestion_units(persona)
    question = next(q for q in M.questions(persona))
    gold = M.gold_for(persona, question)
    oracle = [u for u in units if u.session_id in gold.support_sessions][:1]
    rank = M.first_support_rank(oracle, gold)
    assert rank.value_or_raise() == 1
    assert M.hit_at_k(rank, 3).value_or_raise() == 1
    assert M.log_rank_at_k(rank, 3) == 1.0


def test_upstream_scoring_audit_records_the_fail_open_paths(contract):
    audit = contract["scoring_audit"]
    assert audit["white_box_is_llm_judged"] is True
    assert audit["official_result_requires_llm_judge"] is True
    for name in ("missing_model_answer", "llm_judge_unavailable_or_raising",
                 "judge_omits_a_metric_key", "unparsable_support_rank"):
        assert audit["failure_semantics"][name]["is_measured_zero"] is False
        assert audit["failure_semantics"][name]["our_treatment"].startswith("UNMEASURED")
    assert audit["primary_top_k"] == 3


def test_reader_lane_is_not_silently_substituted():
    lanes = M.LANES
    assert lanes["upstream_llm_judge"]["requires_reader"] is True
    assert lanes["upstream_llm_judge"]["status_without_reader"] == "requires_reader_authorization"
    assert lanes["upstream_rule_fallback"]["white_box_is_measured"] is False
    assert lanes["exact_provenance_whitebox"]["requires_reader"] is False


def test_calibration_subset_is_label_blind_and_deterministic(contract):
    manifest = contract["calibration_manifest"]
    ids = [p["ID"] for p in M.load_personas()]
    assert M.calibration_personas(ids) == manifest["calibration_persona_ids"]
    for pid in manifest["calibration_persona_ids"]:
        assert int(hashlib.sha256(pid.encode()).hexdigest(), 16) % manifest["fraction"] == 0
    assert manifest["calibration_persona_count"] + manifest["held_out_persona_count"] == len(ids)


def test_contract_and_content_digests_are_deterministic(contract):
    assert contract["contract_sha256"] == M.contract_sha256()
    content = {k: v for k, v in contract.items()}
    digest = hashlib.sha256(canonical_json(content).encode()).hexdigest()
    assert (CONTRACT_DIR / "content-digest.txt").read_text().strip() == digest


def test_pilot_ran_no_product_and_caught_the_illegal_provider():
    if not PILOT_DIR.is_dir():
        pytest.skip("pilot artifacts not present")
    validation = json.loads((PILOT_DIR / "validation.json").read_text())
    assert validation["passed"] is True
    for name in ("future_session_rejected", "gold_answer_rejected", "conflict_label_rejected",
                 "null_is_measured_zero_where_gold_exists"):
        assert validation["checks"][name] is True
    pilot = json.loads((PILOT_DIR / "pilot.json").read_text())
    assert sorted(pilot["providers"]) == ["bm25_baseline", "null"]
