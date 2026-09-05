"""Scope classes must be provably reachable, and unexercised scope must not read as failure.

This is the Gen73 error in a new axis: reading an adapter decision as an engine
property. These tests exist to make that error fail loudly.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff import scope_audit as S

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "results/scope_audit_gen76/scope_audit.json"


def payload() -> dict:
    return json.loads(REPORT.read_text())


def test_scope_collapse_fires_and_its_control_stays_clean():
    proof = payload()["scope_collapse_proof"]
    assert proof["fires"] is True
    assert proof["control_clean"] is True


def test_configuration_collapse_fires_and_its_control_stays_clean():
    proof = payload()["configuration_collapse_proof"]
    assert proof["fires"] is True
    assert proof["control_clean"] is True


def test_the_fixture_contains_both_kinds_of_violation():
    reach = payload()["reachability_in_fixture"]
    assert reach["scope_collapse"]["reachable"] is True
    assert reach["configuration_collapse"]["reachable"] is True


def test_an_adapter_passing_scope_on_both_paths_is_measured():
    verdict = S.capability_verdict(
        {"passed_on_write": True, "passed_on_query": True})
    assert verdict["scope_exercised"] == S.ISOLATED
    assert verdict["engine_scope_capability"] == S.MEASURED


def test_an_adapter_passing_no_scope_yields_not_demonstrable():
    verdict = S.capability_verdict(
        {"passed_on_write": False, "passed_on_query": False})
    assert verdict["engine_scope_capability"] == S.NOT_DEMONSTRABLE
    assert "not evidence about the product" in verdict["why"]


def test_write_only_scope_is_not_enough_to_call_it_measured():
    """Filtering must happen on the read path too, or nothing is being tested."""
    verdict = S.capability_verdict(
        {"passed_on_write": True, "passed_on_query": False})
    assert verdict["engine_scope_capability"] == S.NOT_DEMONSTRABLE


def test_only_perseus_actually_exercises_scope():
    adapters = payload()["adapters"]
    assert adapters["perseus"]["engine_scope_capability"] == S.MEASURED
    for name in ("mem0", "hindsight", "agentmemory"):
        assert adapters[name]["engine_scope_capability"] == S.NOT_DEMONSTRABLE


def test_the_configuration_behaviour_is_still_reported_for_unexercised_adapters():
    """Two true statements: the configuration collapses; the engine is untested."""
    for name in ("mem0", "hindsight", "agentmemory"):
        entry = payload()["adapters"][name]
        assert "collapses scopes" in entry["configuration_behaviour"]


def test_each_adapter_claim_carries_its_evidence():
    for entry in payload()["adapters"].values():
        assert entry["evidence"].strip()
        assert entry["mechanism"].strip()


def test_no_engine_was_run():
    assert payload()["engines_run"] == 0
