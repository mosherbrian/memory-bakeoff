"""Configuration isolation must be measured, and one engine must be allowed to fail.

Gen78 made every engine look identical. This axis does not, and the tests protect
the difference: a real failure must stay visible, and a pass must be clean
retrieval rather than an empty answer.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/configuration_isolation_gen80"
ISOLATING = ("perseus", "mem0", "hindsight")
ALL_ENGINES = ISOLATING + ("agentmemory",)


def load(engine: str) -> dict:
    return json.loads((RESULTS / f"{engine}.json").read_text())


@pytest.mark.parametrize("engine", ALL_ENGINES)
def test_three_repetitions_of_the_single_qualifying_case(engine):
    payload = load(engine)
    assert payload["case"] == "LQ03"
    assert payload["case_runs"] == 3


@pytest.mark.parametrize("engine", ISOLATING)
def test_isolating_engines_do_not_collapse(engine):
    assert load(engine)["configuration_collapse_total"] == 0


@pytest.mark.parametrize("engine", ISOLATING)
def test_a_pass_is_clean_retrieval_not_an_empty_answer(engine):
    payload = load(engine)
    assert payload["clean_retrieval_total"] == payload["case_runs"]
    for rep in payload["repetitions"]:
        for record in rep["records"]:
            assert record["returned_expected"] is True
            assert record["returned_prohibited"] is False


def test_agentmemory_collapses_and_that_is_recorded_not_smoothed():
    """Gen13's prior evidence confirmed, not overturned."""
    payload = load("agentmemory")
    assert payload["configuration_collapse_total"] == 3
    assert payload["clean_retrieval_total"] == 0
    for rep in payload["repetitions"]:
        for record in rep["records"]:
            assert record["returned_prohibited"] is True


@pytest.mark.parametrize("engine", ALL_ENGINES)
def test_both_axes_were_bound_and_recorded(engine):
    payload = load(engine)
    assert payload["configuration_binding"]["primitive"]
    for rep in payload["repetitions"]:
        for record in rep["records"]:
            assert record["bound_scope"]
            assert record["bound_configuration"]
            assert record["bound_scope"] != record["bound_configuration"]


@pytest.mark.parametrize("engine", ALL_ENGINES)
def test_ingestion_was_prefix_limited(engine):
    assert "prefix" in load(engine)["ingestion"]


@pytest.mark.parametrize("engine", ALL_ENGINES)
def test_the_scope_axis_was_not_the_thing_that_moved(engine):
    """One variable: the configuration binding layered on an unchanged scope one."""
    ablation = load(engine)["ablation"]
    assert "Gen78 scope binding" in ablation
