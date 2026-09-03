import json
from pathlib import Path

import pytest

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import perseus_longitudinal as A

GEN30 = Path("results/perseus_vault_gen30_mcp_valid_time/summary.json")
GEN29 = Path("results/perseus_vault_gen29_longitudinal/summary.json")
FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
SCORER_SHA = "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"
ADAPTER_SHA = "09f2414e1e02784176016cdbe2ffda799cf24c2812a9a0c9a3c5342ecea9a4e2"


def test_gen30_leaves_the_frozen_ruler_and_gen29_query_adapter_untouched():
    assert L.fixture_sha256() == FIXTURE_SHA
    assert L.scorer_contract_sha256() == SCORER_SHA
    assert A.adapter_contract_sha256() == ADAPTER_SHA


@pytest.mark.skipif(not GEN29.exists(), reason="Gen29 results are produced by its runner")
def test_gen29_result_is_preserved_unchanged_by_gen30():
    summary = json.loads(GEN29.read_text())
    assert len(summary["repetitions"]) == 3
    assert summary["failure_totals_all_repetitions"].get("future_leakage", 0) == 0
    assert summary["system_identity"]["write_path"] == "documented operator CLI write"


@pytest.mark.skipif(not GEN30.exists(), reason="Gen30 probe output is produced by its script")
def test_gen30_publishes_a_blocker_and_no_invented_longitudinal_score():
    findings = json.loads(GEN30.read_text())
    assert findings["status"] == "blocked_valid_time_reset_by_admission_approval"
    assert findings["scored_longitudinal_result_published"] is False
    assert findings["post_hoc_ablation"] is True
    assert findings["model_or_product_llm_calls"] is False
    assert findings["inference_server_used"] is False
    assert "repetitions" not in findings and "failure_totals" not in findings


@pytest.mark.skipif(not GEN30.exists(), reason="Gen30 probe output is produced by its script")
def test_serveable_and_retroactive_states_are_mutually_exclusive():
    measured = json.loads(GEN30.read_text())["measured"]
    assert measured["valid_from_preserved_by_remember"] is True
    assert measured["valid_from_preserved_by_approval"] is False
    assert measured["recallable_after_approval"] is True
    assert measured["recallable_after_second_remember"] is False
    assert measured["approval_reset_delta_ms"] > 0
    assert measured["after_remember"]["status"] == "proposed"
    assert measured["after_approval"]["status"] == "active"


@pytest.mark.skipif(not GEN30.exists(), reason="Gen30 probe output is produced by its script")
def test_admission_chain_is_recorded_as_a_uniform_documented_policy():
    findings = json.loads(GEN30.read_text())
    steps = [step["step"] for step in findings["documented_admission_chain"]]
    assert steps[:5] == ["agent_register", "authority_set", "server_env", "remember", "admission_decide_approve"]
    identity = findings["system_identity"]
    assert identity["product_version"] == "2.23.2"
    assert identity["release_tarball_sha256"] == "e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb"
    assert "remember" in identity["ingest_path"] and "admission_decide" in identity["ingest_path"]
    assert identity["trust_class"] != "documented operator CLI write"
