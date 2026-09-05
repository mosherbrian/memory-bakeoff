"""Gen96: Round-3 adapters, reused bindings, and an honest retrieval-budget audit."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import round3_adapters as r3
from memory_bakeoff.providers.configuration_bound import BINDINGS as CONFIGURATION_BINDINGS
from memory_bakeoff.providers.scope_bound import BINDINGS as SCOPE_BINDINGS

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "round3_adapters_gen96" / "feasibility.json"


@pytest.fixture(scope="module")
def report():
    return json.loads(RESULTS.read_text())


# --- bindings are reused, not reinvented ---------------------------------
def test_the_bindings_come_from_gen77_and_gen79(report):
    for engine in ("mem0", "hindsight", "agentmemory"):
        entry = r3.bindings(engine, "server:atlas", "A1")
        assert entry["scope_primitive"] == SCOPE_BINDINGS[engine]["primitive"]
        assert entry["configuration_primitive"] == \
            CONFIGURATION_BINDINGS[engine]["primitive"]
        assert "Gen77/78" in entry["provenance"] and "Gen79/80" in entry["provenance"]


def test_scope_and_configuration_are_separate_primitives():
    for engine in r3.BUDGET_SURFACE:
        entry = r3.bindings(engine, "server:atlas", "A1")
        assert entry["scope_primitive"] != entry["configuration_primitive"], engine


def test_both_identities_are_bound_on_write_and_query():
    """Payload shapes differ; the identities must not."""
    for engine in r3.BUDGET_SURFACE:
        r3.assert_symmetric_identities(engine, r3.bindings(engine, "server:atlas", "A1"))


def test_a_one_sided_identity_is_rejected():
    with pytest.raises(ValueError, match="cannot isolate"):
        r3.assert_symmetric_identities(
            "mem0", {"write": {"user_id": "a", "agent_id": "b"},
                     "query": {"filters": {"user_id": "a"}}})


def test_a_query_only_modifier_is_not_treated_as_an_identity():
    """hindsight's tags_match is a matching mode, not an identity."""
    assert r3.identity_keys({"tags": ["x"], "tags_match": "all"}) == {"tags"}
    assert r3.identity_keys({"filters": {"user_id": "a"}}) == {"user_id"}


def test_every_engine_binds_both_axes_on_write_and_query():
    for engine in r3.BUDGET_SURFACE:
        entry = r3.bindings(engine, "server:atlas", "A1")
        assert entry["write"] and entry["query"]


# --- the budget audit, which is the point --------------------------------
def test_three_engines_express_a_result_count_and_one_does_not():
    counts = [e for e, s in r3.BUDGET_SURFACE.items()
              if s["kind"] == r3.NATIVE_RESULT_COUNT]
    tokens = [e for e, s in r3.BUDGET_SURFACE.items() if s["kind"] == r3.TOKEN_BUDGET]
    assert sorted(counts) == ["agentmemory", "mem0", "perseus"]
    assert tokens == ["hindsight"]
    assert r3.BUDGET_SURFACE["hindsight"]["window_expressible"] is False


def test_the_hindsight_contract_defect_is_recorded():
    surface = r3.BUDGET_SURFACE["hindsight"]
    assert "NEVER PASSES IT" in surface["evidence"]
    assert "truncated" in surface["evidence"]
    assert "inaccurate here" in surface["contract_defect"]


def test_the_defect_is_real_in_the_frozen_adapter():
    """Read the frozen adapter, not the claim about it."""
    from memory_bakeoff.providers import hindsight_longitudinal as H
    from memory_bakeoff.longitudinal import build_longitudinal_fixture
    case = next(c for c in build_longitudinal_fixture().cases if c.id == "LQ01")
    arguments = H.recall_arguments(case, "bank", 5)
    assert "limit" not in arguments, "the adapter accepts limit and drops it"
    assert arguments["max_tokens"] == 4096
    assert "native limit are preserved" in \
        H.adapter_contract_payload()["post_filtering"]


def test_saturation_is_meaningful_for_three_engines_and_not_the_fourth(report):
    saturation = report["preflight"]["saturation"]
    for engine in ("perseus", "mem0", "agentmemory"):
        assert saturation[engine]["saturated_is"] == "meaningful"
    assert saturation["hindsight"]["saturated_is"] == r3.NOT_DEMONSTRABLE
    assert "cannot be separated" in saturation["hindsight"]["consequence"]


def test_comparable_windows_are_recorded_as_not_expressible(report):
    preflight = report["preflight"]
    assert preflight["comparable_windows_expressible"] is False
    assert "different quantities" in preflight["why_not"]
    assert preflight["run_design"].startswith("within-engine scale curves")


# --- no manufactured equality --------------------------------------------
def test_a_mode_substitution_is_refused():
    r3.assert_no_mode_substitution("perseus",
                                   "perseus_vault_recall(mode=hybrid, limit=N)")
    with pytest.raises(ValueError, match="keep its own retrieval strategy"):
        r3.assert_no_mode_substitution("perseus", "perseus_vault_semantic_search")
    with pytest.raises(ValueError, match="manufactures an equality"):
        r3.assert_no_mode_substitution("hindsight", "recall(bank_id, query, limit=N)")


def test_a_cross_engine_pooled_count_is_refused():
    r3.assert_within_engine_only({"perseus_curve": [0, 1, 2], "mem0_curve": [0, 1]})
    for bad in ({"pooled_accuracy": 0.6}, {"cross_engine_total": 12}):
        with pytest.raises(ValueError, match="within-engine scale curves"):
            r3.assert_within_engine_only(bad)


# --- preflight assertions -------------------------------------------------
def test_scale_is_the_only_fixture_variable(report):
    check = report["fixture_check"]
    assert len(check["one_semantic_core"]) == 1
    assert len(check["one_query"]) == 1
    assert len(check["one_scope"]) == 1
    assert len(check["one_configuration"]) == 1
    assert check["levels"] == [0, 4, 16, 64]


def test_every_level_holds_the_core_plus_exactly_its_distractors(report):
    sizes = report["fixture_check"]["visible_per_level"]
    for case_id, size in sizes.items():
        load = int(case_id.replace("IQ", ""))
        assert size == load + 3


def test_the_preflight_is_frozen_and_no_engine_ran(report):
    assert len(report["preflight_sha256"]) == 64
    assert report["preflight"]["no_engine_runs"] is True
    assert report["preflight"]["strategies_unchanged"] is True
    assert report["mode_substitution_checked"] is True
