"""Gen103: agentmemory's supersession, localised to write-time mutation."""
from __future__ import annotations

import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOC = ROOT / "results" / "agentmemory_localization_gen103" / "localization.json"


@pytest.fixture(scope="module")
def report():
    return json.loads(LOC.read_text())


def live(stage):
    return [r for r in stage["rows"] if r.get("isLatest") is True]


def retired(stage):
    return [r for r in stage["rows"] if r.get("isLatest") is False]


def test_the_probe_used_two_records_and_unchanged_content(report):
    assert "two records only" in report["probe"]
    assert "semantic content unchanged" in report["probe"]
    for entry in report["probes"].values():
        assert entry["stages"][0]["rows"] == []


def test_both_orders_were_run_as_controls(report):
    orders = {e["order"] for e in report["probes"].values()}
    assert any(o.startswith("v2") for o in orders)
    assert any(o.startswith("v3") for o in orders)


def test_v2_retires_the_current_record(report):
    final = report["probes"]["v2_current_first"]["stages"][-1]
    assert [r["sourceObservationIds"] for r in retired(final)] == [["C2-CUR"]]
    assert [r["sourceObservationIds"] for r in live(final)] == [["C2-SUP"]]


def test_v3_retires_the_superseded_record(report):
    final = report["probes"]["v3_superseded_first"]["stages"][-1]
    assert [r["sourceObservationIds"] for r in retired(final)] == [["C2-SUP"]]
    assert [r["sourceObservationIds"] for r in live(final)] == [["C2-CUR"]]


def test_the_repair_works_and_gen102_is_contradicted(report):
    """Gen102 reported the current record absent under v3. It is present."""
    final = report["probes"]["v3_superseded_first"]["stages"][-1]
    assert live(final)[0]["sourceObservationIds"] == ["C2-CUR"]
    assert len(final["search_hits"]) == 1


def test_search_returns_exactly_the_live_row(report):
    for entry in report["probes"].values():
        final = entry["stages"][-1]
        assert len(final["search_hits"]) == 1
        assert final["search_hits"][0]["obsId"] == live(final)[0]["id"]


def test_the_retired_row_survives_in_the_store(report):
    """It leaves the index; it is not deleted."""
    for entry in report["probes"].values():
        final = entry["stages"][-1]
        assert retired(final), entry["order"]
        assert len(final["rows"]) == 2


def test_the_foreign_record_does_not_disturb_supersession(report):
    """The one targeted test the source justified: the project guard."""
    entry = report["probes"]["v3_with_foreign"]
    final = entry["stages"][-1]
    assert final["stage"].startswith("after write 3: foreign")
    assert [r["sourceObservationIds"] for r in live(final)] == [["C2-CUR"]]
    assert len(final["rows"]) == 2, "the foreign record is not agent-scoped here"
    assert len(final["search_hits"]) == 1


def test_the_write_time_rule_is_recorded_from_source(report):
    rule = report["write_time_rule_from_source"]
    assert rule["file"] == "src/functions/remember.ts"
    assert "INCOMING record" in rule["rule"]
    assert "STAYS in KV" in rule["effect_on_superseded"]
    assert "REMOVED from both search indexes" in rule["effect_on_superseded"]
    assert "auto-forget" in rule["note"] and "0.9" in rule["note"]


def test_the_two_rules_are_kept_apart(report):
    """Write-time supersession at 0.7 is not the maintenance pass at 0.9."""
    rule = report["write_time_rule_from_source"]
    assert "0.7" in rule["rule"]
    assert "not the write path" in rule["note"]
