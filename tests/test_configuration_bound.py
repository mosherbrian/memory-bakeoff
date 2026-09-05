"""Two configurations must separate without the scope key moving at all.

The failure this guards is subtle: repurposing the scope primitive would make two
configurations look like two scopes, and the resulting isolation would be an
artefact of relabelling rather than a capability.
"""
from __future__ import annotations

import pytest

from memory_bakeoff.providers import configuration_bound as C
from memory_bakeoff.providers import scope_bound as S

ENGINES = ("perseus", "mem0", "hindsight", "agentmemory")
CONF_A, CONF_B = "C1", "C2"


@pytest.mark.parametrize("engine", ENGINES)
def test_two_configurations_produce_distinct_write_and_query_coordinates(engine):
    proof = C.distinct_coordinates(engine, CONF_A, CONF_B)
    assert proof["writes_differ"] is True
    assert proof["queries_differ"] is True


@pytest.mark.parametrize("engine", ENGINES)
def test_the_configuration_binding_never_touches_the_scope_primitive(engine):
    """The hard constraint: no relabelling of scope as configuration."""
    assert C.distinct_coordinates(engine, CONF_A, CONF_B)["touches_scope_primitive"] is False


@pytest.mark.parametrize("engine", ENGINES)
def test_the_same_configuration_is_stable_across_calls(engine):
    first = C.distinct_coordinates(engine, CONF_A, CONF_B)
    second = C.distinct_coordinates(engine, CONF_A, CONF_B)
    assert first["write_a"] == second["write_a"]
    assert first["query_a"] == second["query_a"]


@pytest.mark.parametrize("engine", ENGINES)
def test_write_and_query_carry_the_same_configuration_token(engine):
    token = C.configuration_token(CONF_A)
    proof = C.distinct_coordinates(engine, CONF_A, CONF_B)
    assert token in str(proof["write_a"])
    assert token in str(proof["query_a"])


@pytest.mark.parametrize("engine", ENGINES)
def test_every_binding_names_a_real_call_on_each_path(engine):
    binding = C.BINDINGS[engine]
    assert binding["write_call"] and binding["query_call"]
    assert binding["status"] == C.SUPPORTED


def test_the_three_shared_engines_use_a_different_primitive_than_their_scope_key():
    """Independence, checked against the Gen78 bindings rather than asserted."""
    for engine in ("mem0", "hindsight", "agentmemory"):
        assert C.BINDINGS[engine]["primitive"] != S.BINDINGS[engine]["primitive"]
        assert C.BINDINGS[engine]["scope_primitive"] == S.BINDINGS[engine]["primitive"]


def test_a_configuration_token_is_not_a_scope_token():
    """Different namespaces, so a configuration can never collide with a scope."""
    assert C.configuration_token("C1") != S.scope_token("C1")


def test_the_configuration_token_carries_no_fixture_wording():
    token = C.configuration_token("C1")
    assert "C1" not in token and "config" not in token


def test_the_agentmemory_caveat_is_recorded_prominently():
    note = C.BINDINGS["agentmemory"]["note"]
    assert "CAVEAT" in note
    assert "not a prediction" in note


def test_the_contract_states_the_hard_constraint_and_leaves_gen78_alone():
    contract = C.contract()
    assert "must not appear" in contract["hard_constraint"]
    assert contract["gen78_scope_bindings_untouched"] is True
    assert contract["frozen_before_any_run"] is True
