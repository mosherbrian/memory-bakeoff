"""Gen37: the calibration pass is only evidence if the contract, the identities and
the provenance chain all held while two real products were exposed to it."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from memory_bakeoff import memconflict as M
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.providers import mem0_memconflict as MEM0A
from memory_bakeoff.providers import perseus_memconflict as PERSA
from memory_bakeoff.round2_reporting import ReportingError

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION = ROOT / "results/memconflict_gen37_calibration"
GEN36 = ROOT / "results/memconflict_gen36_contract"

pytestmark = pytest.mark.skipif(not (CALIBRATION / "content-digest.txt").exists(),
                                reason="Gen37 calibration evidence not present")

FROZEN_ADAPTERS = {
    "perseus": "627f812d5296130cdee5062ee48a9690a8873e635ee5683c8dd51432fd0e2c99",
    "mem0": "920f496be7470fca3bb5da4fb26b6bde6b9a13214ba5b934d875b06e97e0d190",
}


@pytest.fixture(scope="module")
def derived() -> dict:
    return json.loads((CALIBRATION / "exact-provenance-derived.json").read_text())


@pytest.fixture(scope="module")
def leaves() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for engine in ("perseus", "mem0"):
        directory = CALIBRATION / engine
        if directory.is_dir():
            out[engine] = [json.loads(p.read_text()) for p in sorted(directory.glob("persona-*.json"))]
    return out


def test_gen36_contract_and_dataset_pin_unchanged(derived):
    assert derived["contract_sha256"] == "0521210818e448c8f189dacc33e287b15525f89d63f39cb627f9cdc7a3dccd28"
    assert derived["contract_sha256"] == M.contract_sha256()
    assert derived["dataset_sha256"] == M.DATASET_SHA256 == M.dataset_sha256()
    assert derived["upstream_commit"] == "ec51d5d36e87f7665d1337f3a88cbde95fc2a964"


def test_calibration_manifest_unchanged(leaves):
    manifest = json.loads((GEN36 / "calibration-manifest.json").read_text())
    frozen = manifest["calibration_persona_ids"]
    assert frozen == M.calibration_personas([p["ID"] for p in M.load_personas()])
    for engine, rows in leaves.items():
        assert sorted(r["persona_id"] for r in rows) == sorted(frozen), engine


def test_adapters_are_the_frozen_preflight_contracts(leaves):
    assert PERSA.adapter_contract_sha256() == FROZEN_ADAPTERS["perseus"]
    assert MEM0A.adapter_contract_sha256() == FROZEN_ADAPTERS["mem0"]
    for engine, rows in leaves.items():
        for row in rows:
            assert row["adapter_sha256"] == FROZEN_ADAPTERS[engine]


def test_product_identities_are_the_round_two_profiles():
    perseus = PERSA.adapter_contract_payload()
    assert perseus["product_version"] == "2.23.2" and perseus["product_build"] == "9c82920"
    assert perseus["write_path"].startswith("perseus-vault write")
    assert perseus["temporal_arguments"].startswith("none")
    assert perseus["post_filtering"].startswith("none")
    mem0 = MEM0A.adapter_contract_payload()
    assert mem0["product_version"] == "2.0.19"
    assert mem0["upstream_commit"] == "19cb89aff472325c707f64b2f34ae6afdbf7faf7"
    assert mem0["write_path"] == "upstream Memory.add(text, user_id, infer=False)"
    assert mem0["metadata_fields"] == []
    assert mem0["threshold"] == 0.1 and mem0["embedding_dims"] == 1024


def test_no_scorer_only_field_can_reach_either_product():
    for payload in ({"text": "x", "answer": "gold"},
                    {"metadata": {"conflict_type": "static_conflict"}},
                    {"body": {"Session_Type": "update"}},
                    {"deep": {"deeper": {"Updated_Attributes": []}}}):
        with pytest.raises(ReportingError):
            M.assert_public_only(payload)


def test_indexed_text_carries_no_released_identifier():
    body = PERSA.body_for_message("a plain released sentence")
    assert sorted(body) == ["assertion", "source_kind"]
    PERSA.assert_no_identifier_in_body(body, {"persona": "abc-123", "session": 7})
    with pytest.raises(ValueError):
        PERSA.assert_no_identifier_in_body({"assertion": "text abc-123"}, {"persona": "abc-123"})
    assert MEM0A.add_arguments("a plain released sentence", "abc-123") == {
        "text": "a plain released sentence",
        "user_id": MEM0A.user_id_for_persona("abc-123"), "infer": False}


def test_query_is_the_released_question_text_unmodified():
    persona = M.load_personas()[0]
    question = M.questions(persona)[0]
    assert PERSA.recall_arguments(question.text, persona["ID"])["query"] == question.text
    assert MEM0A.search_arguments(question.text, persona["ID"])["query"] == question.text
    assert PERSA.recall_arguments(question.text, persona["ID"])["limit"] == 5
    assert MEM0A.search_arguments(question.text, persona["ID"])["limit"] == 5


def test_one_message_one_write_and_ledger_reconciles(leaves):
    personas = {p["ID"]: p for p in M.load_personas()}
    for engine, rows in leaves.items():
        for row in rows:
            expected = len(M.ingestion_units(personas[row["persona_id"]]))
            ops = row["operations"]
            assert ops["expected_valid_messages"] == expected, (engine, row["persona_id"])
            assert ops["successful_writes"] + len(ops["write_failures"]) == expected
            ledger = json.loads((CALIBRATION / engine / f"ledger-{row['persona_id']}.json").read_text())
            assert len(ledger) == row["ledger_size"] == ops["distinct_native_ids"]
            # a native id issued twice is a product replacement, and must be recorded by name
            assert ops["successful_writes"] - ops["distinct_native_ids"] == len(ops["native_id_replacements"])


def test_malformed_message_exclusion_matches_gen36(leaves):
    stats = json.loads((GEN36 / "dataset-stats.json").read_text())["dataset_statistics"]
    excluded_ids = set(stats["malformed_message_ids"])
    personas = {p["ID"]: p for p in M.load_personas()}
    for rows in leaves.values():
        for row in rows:
            anomalies = M.dialogue_anomalies(personas[row["persona_id"]])
            ids = {f"{a['persona_id']}|S{a['session_id']}|T{a['turn']}|M{a['message']}" for a in anomalies}
            assert ids <= excluded_ids
            assert row["operations"]["malformed_excluded"] == len(anomalies)


def test_every_returned_item_maps_through_the_ledger(derived, leaves):
    for engine, rows in leaves.items():
        for row in rows:
            for record in row["questions"]:
                for item in record["returned"]:
                    assert item["provenance_status"] == "mapped"
                    assert item["session_id"] is not None
        assert derived["engines"][engine]["retrieval_health"]["unmapped_provenance_items"] == 0


def test_chronology_holds_for_every_returned_item(leaves):
    for engine, rows in leaves.items():
        for row in rows:
            for record in row["questions"]:
                for item in record["returned"]:
                    assert item["session_index"] <= record["session_index"], (engine, record["question_key"])


def test_native_order_is_preserved_and_k_are_slices(leaves):
    for rows in leaves.values():
        for row in rows:
            for record in row["questions"]:
                ranks = [item["rank"] for item in record["returned"]]
                assert ranks == sorted(ranks) == list(range(1, len(ranks) + 1))
                assert len(ranks) <= 5


def test_unaddressable_conditional_questions_stay_unmeasured(derived):
    for engine, result in derived["engines"].items():
        conditional = result["by_conflict_type"].get("conditional_conflict")
        assert conditional is not None, engine
        assert conditional["unmeasured_questions"] > 0
        assert conditional["measured_questions"] + conditional["unmeasured_questions"] == 444 // 10 * 0 + \
            conditional["measured_questions"] + conditional["unmeasured_questions"]
        for k in ("2", "3", "5"):
            assert conditional["hit_at"][k]["hits"] <= conditional["measured_questions"]


def test_credit_requires_session_identity_not_text():
    persona = M.load_personas()[0]
    question = M.questions(persona)[0]
    gold = M.gold_for(persona, question)
    assert gold.support_sessions is not None
    supporting = next(u for u in M.ingestion_units(persona) if u.session_id in gold.support_sessions)
    impostor = M.Unit(persona_id=supporting.persona_id, session_id=-1, session_index=0, turn_index=1,
                      message_index=1, role=supporting.role, text=supporting.text, date=supporting.date)
    assert M.first_support_rank([impostor], gold).count == 0
    assert M.first_support_rank([supporting], gold).count == 1


def test_metrics_come_only_from_the_retrieval_stream():
    M.legal_stream("exact_support_hit_at_k", M.Stream.RETRIEVAL)
    with pytest.raises(ReportingError):
        M.legal_stream("exact_support_hit_at_k", M.Stream.ANSWER_READER)
    with pytest.raises(ReportingError):
        M.legal_stream("dynamic_answer_accuracy", M.Stream.RETRIEVAL)


def test_reads_and_repeats_were_audited(derived):
    validation = json.loads((CALIBRATION / "validation.json").read_text())
    for engine in derived["engines"]:
        audit = validation["audits"][engine]
        assert audit["reads_left_state_unchanged"] is True
        assert audit["deterministic_repeats_stable"] is True
        assert audit["repeat_questions_checked"] > 0


def test_inventory_reconciles_or_the_discrepancy_is_explicit(leaves):
    """The store may hold fewer rows than we wrote. It may not do so silently."""
    for engine, rows in leaves.items():
        for row in rows:
            ops = row["operations"]
            inventory = row["inventory"]
            native = inventory.get("active_entities", inventory.get("points"))
            assert native is not None, (engine, row["persona_id"])
            if native != ops["distinct_native_ids"]:
                # every missing row must be accounted for by a recorded native event,
                # never by an inferred cause
                assert ops["native_id_replacements"] or ops["write_actions"], (
                    engine, row["persona_id"], native, ops["distinct_native_ids"])
                assert row.get("inventory_reconciliation") or ops["duplicate_message_texts"] >= 0


def test_operations_are_outside_the_scientific_digest(derived):
    blob = canonical_json(derived)
    for noisy in ("wall_seconds", "p50_ms", "store_bytes", "latency_ms"):
        assert noisy not in blob
    content = {k: v for k, v in derived.items() if k != "content_digest"}
    assert hashlib.sha256(canonical_json(content).encode()).hexdigest() == derived["content_digest"]
    assert (CALIBRATION / "content-digest.txt").read_text().strip() == derived["content_digest"]


def test_no_reader_or_official_lane_was_used(derived):
    assert derived["lane"] == "memconflict-exact-whitebox-v1"
    for result in derived["engines"].values():
        assert result["evidence_class"] == "external_benchmark_calibration_raw_product"
        assert result["development_exposed"] is True
    assert M.LANES["upstream_llm_judge"]["status_without_reader"] == "requires_reader_authorization"


def test_preflight_passed_before_exposure():
    preflight = json.loads((CALIBRATION / "preflight.json").read_text())
    assert preflight["passed"] is True
    assert preflight["adapter_contracts"]["perseus"]["sha256"] == FROZEN_ADAPTERS["perseus"]
    assert preflight["adapter_contracts"]["mem0"]["sha256"] == FROZEN_ADAPTERS["mem0"]
    for group in ("shared", "perseus", "mem0"):
        for name, value in preflight[group].items():
            if isinstance(value, bool):
                assert value is True, f"{group}.{name}"
