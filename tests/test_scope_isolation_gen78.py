"""The ablation must move exactly one variable, and its cleanliness must be real.

An empty answer also avoids scope_collapse, so these check that the expected
evidence actually came back - the Gen73 lesson applied to the scope axis.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/scope_isolation_gen78"
ENGINES = ("mem0", "hindsight", "agentmemory")
EXPECTED = {"LQ08": "L003", "LQ09": "L006"}


def load(engine: str) -> dict:
    return json.loads((RESULTS / f"{engine}.json").read_text())


@pytest.mark.parametrize("engine", ENGINES)
def test_no_scope_collapse_under_the_native_binding(engine):
    assert load(engine)["scope_collapse_total"] == 0


@pytest.mark.parametrize("engine", ENGINES)
def test_cleanliness_is_not_an_empty_answer(engine):
    """Each case must actually return the observation it was asked for."""
    for rep in load(engine)["repetitions"]:
        for record in rep["records"]:
            assert EXPECTED[record["case_id"]] in record["returned_ids"], record


@pytest.mark.parametrize("engine", ENGINES)
def test_the_other_scope_never_appears(engine):
    """Isolation, stated positively rather than as the absence of a flag."""
    foreign = {"LQ08": "L006", "LQ09": "L003"}
    for rep in load(engine)["repetitions"]:
        for record in rep["records"]:
            assert foreign[record["case_id"]] not in record["returned_ids"], record


@pytest.mark.parametrize("engine", ENGINES)
def test_only_genuinely_cross_scope_cases_were_run(engine):
    payload = load(engine)
    assert payload["cases"] == ["LQ08", "LQ09"]
    assert "LQ03" in payload["excluded"]


@pytest.mark.parametrize("engine", ENGINES)
def test_ingestion_was_limited_to_the_queried_checkpoint(engine):
    """The whole timeline would charge future_leakage as a runner artefact."""
    assert "prefix" in load(engine)["ingestion"]


@pytest.mark.parametrize("engine", ENGINES)
def test_three_repetitions_of_both_cases(engine):
    payload = load(engine)
    assert payload["case_runs"] == 6
    assert len(payload["repetitions"]) == 3


@pytest.mark.parametrize("engine", ENGINES)
def test_each_run_records_the_bound_identity_it_used(engine):
    for rep in load(engine)["repetitions"]:
        for record in rep["records"]:
            assert record["bound_identity"], record


def test_scopes_got_different_identities_within_a_run():
    """If both scopes shared an identity the clean result would prove nothing."""
    for engine in ENGINES:
        first = load(engine)["repetitions"][0]["records"]
        identities = {r["case_id"]: r["bound_identity"] for r in first}
        assert identities["LQ08"] != identities["LQ09"], engine


def test_perseus_was_not_rerun():
    assert not (RESULTS / "perseus.json").exists()
