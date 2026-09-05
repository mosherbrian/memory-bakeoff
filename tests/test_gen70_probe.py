"""The Gen70 probe records must show over-ingestion and separate the two clocks.

These read the committed engine results, so a later change that quietly reverts
to prefix-only ingestion, or that scores hallucination as a clean zero, fails
here.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/temporal_blind_spot_gen70"
ENGINES = ("perseus", "mem0", "hindsight", "agentmemory")


def load(engine: str) -> dict:
    return json.loads((RESULTS / f"{engine}.json").read_text())


@pytest.mark.parametrize("engine", ENGINES)
def test_every_engine_ran_three_repetitions_of_the_probe(engine):
    payload = load(engine)
    assert len(payload["repetitions"]) == 3
    assert payload["probe_cases_total"] == 39
    assert payload["suite_rerun"] is False


@pytest.mark.parametrize("engine", ENGINES)
def test_the_whole_timeline_was_ingested_before_any_question(engine):
    payload = load(engine)
    for rep in payload["repetitions"]:
        assert rep["observations_ingested"] == 16
        for record in rep["records"]:
            assert record["ingested_through"] == "CP16"
            assert record["queried_as_of"] != "CP16"


@pytest.mark.parametrize("engine", ENGINES)
def test_leakage_is_reported_separately_from_retrieval_failures(engine):
    for rep in load(engine)["repetitions"]:
        for record in rep["records"]:
            assert "future_leakage" in record
            assert "future_leakage" not in record["retrieval_failure_classes"]
            if record["future_leakage"]:
                assert record["leaked_observations"], record["case_id"]


@pytest.mark.parametrize("engine", ENGINES)
def test_hallucination_is_not_applicable_rather_than_a_clean_zero(engine):
    for rep in load(engine)["repetitions"]:
        probe = rep["unknown_hallucination"]
        assert probe["status"] == "NOT_APPLICABLE"
        assert probe["not_a_clean_zero"] is True
        assert probe["reader_answers_seen"] == 0


def test_perseus_temporal_operations_did_not_leak():
    """The headline: a temporal operation that actually holds."""
    leaked = [r for rep in load("perseus")["repetitions"] for r in rep["records"]
              if r["future_leakage"]]
    assert leaked, "expected perseus to leak on its non-temporal operation"
    assert all(r["native_temporal_operation"] == "recall_hybrid" for r in leaked)


def test_hindsight_timestamp_operation_leaked_every_time():
    """The counterpart: a temporal filter that is accepted and ignored."""
    timestamped = [r for rep in load("hindsight")["repetitions"] for r in rep["records"]
                   if r["native_temporal_operation"] == "recall_query_timestamp"]
    assert timestamped
    assert all(r["future_leakage"] for r in timestamped)


def test_the_frozen_fixture_hash_is_recorded_on_every_engine():
    frozen = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
    for engine in ENGINES:
        assert load(engine)["fixture_sha256"] == frozen


def test_hindsight_records_its_restored_pinned_model():
    note = load("hindsight")["pinned_model_note"]
    assert "614241f622f53c4eeff9890bdc4f31cfecc418b3" in note
    assert "same revision" in note
