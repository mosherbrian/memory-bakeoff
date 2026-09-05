"""The closure must rest on the actual whitelists, and must not close too fast.

Two failure modes guarded: declaring no surface exists when a symmetric one does,
and accepting a one-sided field as if it could isolate.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff.providers import agentmemory_surface as S

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "results/agentmemory_surface_gen82/surface.json"


def payload() -> dict:
    return json.loads(REPORT.read_text())


def test_only_two_fields_are_symmetric_at_all():
    assert S.symmetric_fields() == {"agentId", "project"}


def test_session_id_is_search_only_and_therefore_unusable():
    assert "sessionId" in S.SEARCH_ACCEPTS
    assert "sessionId" not in S.WRITE_ACCEPTS
    assert "sessionId" not in S.MCP_WRITE_ACCEPTS
    assert S.CANDIDATES["sessionId"]["symmetric"] is False


def test_write_only_fields_are_not_treated_as_filters():
    for field in ("type", "concepts", "files", "ttlDays"):
        assert field in S.WRITE_ACCEPTS
        assert field not in S.SEARCH_ACCEPTS
        assert S.CANDIDATES[field]["usable_as_second_identity"] is False


def test_agent_id_is_excluded_because_it_already_carries_scope():
    entry = S.CANDIDATES["agentId"]
    assert entry["symmetric"] is True
    assert entry["usable_as_second_identity"] is False
    assert "already carries scope" in entry["why"]


def test_project_is_excluded_on_measured_behaviour_not_on_absence():
    entry = S.CANDIDATES["project"]
    assert entry["symmetric"] is True
    assert "Gen81 measured" in entry["why"]


def test_the_verdict_is_no_usable_second_surface():
    data = payload()
    assert data["verdict"] == S.NO_SECOND_SURFACE
    assert data["usable_second_identity"] == []


def test_all_three_surfaces_were_examined():
    surfaces = payload()["surfaces_examined"]
    assert any("remember" in s for s in surfaces)
    assert any("smart-search" in s for s in surfaces)
    assert any("MCP" in s for s in surfaces)


def test_the_scope_axis_is_explicitly_left_intact():
    assert "Gen78 stands" in payload()["scope_axis_unaffected"]


def test_the_claim_is_bounded_to_the_pinned_build():
    assert "not a claim about the product in general" in payload()["bounded_to"]
    assert payload()["no_engine_run"] is True
