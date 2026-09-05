"""Every proposed binding must give two scopes distinct coordinates on BOTH paths.

Sol's condition for Gen77 was deterministic adapter tests proving that before any
isolation run. A primitive that separates writes but not queries, or the reverse,
isolates nothing.
"""
from __future__ import annotations

import pytest

from memory_bakeoff.providers import scope_bound as S

ENGINES = ("mem0", "hindsight", "agentmemory")
SCOPE_A, SCOPE_B = "server:forge", "server:anvil"


@pytest.mark.parametrize("engine", ENGINES)
def test_two_scopes_produce_distinct_write_and_query_coordinates(engine):
    proof = S.distinct_coordinates(engine, SCOPE_A, SCOPE_B)
    assert proof["writes_differ"] is True
    assert proof["queries_differ"] is True


@pytest.mark.parametrize("engine", ENGINES)
def test_the_same_scope_is_stable_across_calls(engine):
    """An isolation key that drifts between write and query isolates nothing."""
    first = S.distinct_coordinates(engine, SCOPE_A, SCOPE_B)
    second = S.distinct_coordinates(engine, SCOPE_A, SCOPE_B)
    assert first["write_a"] == second["write_a"]
    assert first["query_a"] == second["query_a"]


@pytest.mark.parametrize("engine", ENGINES)
def test_write_and_query_carry_the_same_scope_token(engine):
    """Symmetry, stated as an assertion rather than a claim in prose."""
    token = S.scope_token(SCOPE_A)
    proof = S.distinct_coordinates(engine, SCOPE_A, SCOPE_B)
    assert token in json_values(proof["write_a"])
    assert token in json_values(proof["query_a"])


def json_values(payload) -> str:
    if isinstance(payload, dict):
        return " ".join(json_values(v) for v in payload.values())
    return str(payload)


@pytest.mark.parametrize("engine", ENGINES)
def test_every_binding_names_a_real_call_on_each_path(engine):
    binding = S.BINDINGS[engine]
    assert binding["write_call"] and binding["query_call"]
    assert binding["status"] == S.SUPPORTED


def test_hindsight_and_agentmemory_bindings_are_run_scoped():
    """Repetitions must not share a bank or agent, or scopes leak across runs."""
    first = S.hindsight_write(SCOPE_A, run="r1")
    second = S.hindsight_write(SCOPE_A, run="r2")
    assert first != second
    assert S.agentmemory_write(SCOPE_A, run="r1") != S.agentmemory_write(SCOPE_A, run="r2")


def test_the_scope_token_carries_no_fixture_wording():
    token = S.scope_token("server:forge")
    assert "forge" not in token and "server" not in token


def test_the_contract_refuses_to_approximate_a_missing_surface():
    contract = S.contract()
    assert "will not be approximated" in contract["requirement"]
    assert contract["frozen_before_any_isolation_run"] is True
    assert "feasibility only" in contract["not_yet_measured"]


def test_agentmemory_binding_carries_the_gen13_caveat():
    note = S.BINDINGS["agentmemory"]["note"]
    assert "PROJECT alone did not isolate" in note
