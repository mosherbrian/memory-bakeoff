"""The boundary probe must localise the loss, and must admit when it cannot see.

The first pass read the wrong response field and reported NO_CROSSING_OBSERVED -
a boundary result it could not actually observe. These tests pin both the
corrected finding and the opacity guard that now prevents that.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "results/project_boundary_gen81/boundary.json"


def payload() -> dict:
    return json.loads(REPORT.read_text())


def test_the_probe_used_one_agent_and_two_projects():
    data = payload()
    assert "ONE fixed agentId" in data["design"]
    assert data["no_alternative_schemes_tried"] is True


def test_project_survives_ingestion():
    """Write-time is not where the boundary is lost."""
    data = payload()
    assert data["project_survives_write"] is True
    assert data["stored_project_values"] == ["gen81-project-a", "gen81-project-b"]


def test_every_stored_record_carries_a_project_field():
    for record in payload()["stored"]:
        assert record["project_field"] != "<absent>"
        assert "project" in record["keys_present"]


def test_search_returns_the_other_projects_marker():
    """The crossing, established from marker text rather than an absent flag."""
    data = payload()
    assert data["cross_project_results_returned"] is True
    for query in data["queries"]:
        contents = " ".join(hit["content"] for hit in query["returned"])
        assert "Alpha marker" in contents and "Beta marker" in contents


def test_the_verdict_is_search_time_ignoring():
    data = payload()
    assert data["verdict"] == "SEARCH_TIME_IGNORING"
    assert "stored record carries the right project" in data["why"]


def test_attribution_was_actually_possible():
    """Guards against the first pass's failure: a verdict read from blank hits."""
    assert payload()["attribution_possible"] is True


def test_search_hits_carry_no_project_field_at_all():
    """Supporting detail: the response is opaque to project, not merely unfiltered."""
    for query in payload()["queries"]:
        for hit in query["returned"]:
            assert hit["project_field"] == "<absent>"


def test_the_exact_requests_are_recorded():
    requests = payload()["requests"]
    assert len(requests) == 4
    for request in requests:
        assert request["body"]["agentId"] == "gen81-single-agent"
        assert request["body"]["project"].startswith("gen81-project-")
