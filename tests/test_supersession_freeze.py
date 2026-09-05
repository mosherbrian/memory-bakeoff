"""Gen101: the chronology repair and the four minimal bindings, frozen."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import interference as itf
from memory_bakeoff import interference_v2 as v2
from memory_bakeoff import interference_v3 as v3
from memory_bakeoff import supersession_binding as sb

ROOT = pathlib.Path(__file__).resolve().parents[1]
FREEZE = ROOT / "results" / "supersession_freeze_gen101" / "freeze.json"


@pytest.fixture(scope="module")
def fixture():
    return v3.build_fixture()


@pytest.fixture(scope="module")
def frozen():
    return json.loads(FREEZE.read_text())


# --- exactly one thing changed -------------------------------------------
def test_the_records_are_identical_to_v2(fixture):
    old, new = v2.build_fixture(), fixture
    assert [o.id for o in old.observations] == [o.id for o in new.observations]
    assert [c.id for c in old.cases] == [c.id for c in new.cases]
    assert [(o.text, o.scope, o.configuration) for o in old.observations] == \
        [(o.text, o.scope, o.configuration) for o in new.observations]


def test_only_the_ingest_order_changed(fixture):
    for case in fixture.cases:
        old = v2.visible_ids(fixture, case)
        new = v3.visible_ids(fixture, case)
        assert sorted(old) == sorted(new), case.id
        assert list(old) != list(new), case.id


def test_the_superseded_record_is_written_first(fixture):
    for case in fixture.cases:
        order = v3.visible_ids(fixture, case)
        assert order[0].endswith("-SUP"), case.id
        assert order[1].endswith("-CUR"), case.id


def test_v2_is_not_rewritten(fixture):
    """The defect stays on the record; the repair carries its own version."""
    for case in fixture.cases:
        assert v2.visible_ids(fixture, case)[0].endswith("-CUR")
    assert v3.SUPERSEDES == v2.FIXTURE_VERSION
    assert v3.SCORER_VERSION == itf.SCORER_VERSION
    assert "untouched" in v3.contract()["v2_not_rewritten"]
    assert "defect stays on the record" in v3.contract()["v2_not_rewritten"]


def test_the_scorer_cores_loads_and_bindings_are_untouched(fixture):
    assert v3.contract()["scorer_version"] == itf.SCORER_VERSION
    assert {c.core for c in fixture.cases} == {c["id"] for c in v2.CORES}
    assert sorted({c.load for c in fixture.cases}) == list(itf.LOAD_LEVELS)
    for case in fixture.cases:
        core = next(c for c in v2.CORES if c["id"] == case.core)
        assert case.scope == core["scope"] and case.configuration == core["configuration"]


# --- control 1: the repair is visible to the rule ------------------------
def test_the_corrected_order_is_visible_to_the_write_time_rule(frozen):
    control = frozen["control_order_visible_to_the_rule"]
    kestrel = control["oncall:kestrel"]
    assert kestrel["rule_can_fire"] is True
    assert kestrel["v2_would_retire"] == "current"
    assert kestrel["v3_would_retire"] == "superseded"
    assert kestrel["repair_visible_to_the_rule"] is True


def test_the_other_cores_are_below_the_threshold_either_way(frozen):
    control = frozen["control_order_visible_to_the_rule"]
    for core in ("throughput:atlas", "branch:vega", "budget:solstice"):
        assert control[core]["rule_can_fire"] is False
        assert control[core]["v3_would_retire"] == "nothing"


def test_every_core_shows_the_same_repair(frozen):
    for entry in frozen["control_order_visible_to_the_rule"].values():
        assert entry["same_records"] is True
        assert entry["superseded_now_first"] is True
        assert entry["current_now_second"] is True


# --- control 2: nothing deletes ------------------------------------------
def test_no_binding_deletes(frozen):
    for engine, binding in sb.BINDINGS.items():
        sb.assert_no_deletion(engine, binding)
        assert binding["old_record_retained"] is True, engine
    assert frozen["control_nothing_deletes"]["_guard_rejects_a_delete_binding"] is True


def test_the_guard_refuses_a_destructive_binding():
    for call in ("Memory.delete(id)", "erase --key x", "purge old records",
                 "documents.delete_document(...)"):
        with pytest.raises(ValueError, match="must not call"):
            sb.assert_no_deletion("x", {"call": call, "old_record_retained": True})
    with pytest.raises(ValueError, match="must remain in the store"):
        sb.assert_no_deletion("x", {"call": "update", "old_record_retained": False})


def test_mem0_declines_the_update_path_and_says_why():
    entry = sb.BINDINGS["mem0"]
    assert entry["kind"] == sb.PRODUCT_DECIDES
    assert entry["arguments"] == {"infer": True}
    assert "Memory.update exists and is NOT used" in entry["note"]


# --- the three kinds are kept apart --------------------------------------
def test_the_three_mechanism_kinds_are_named_not_blurred():
    assert sb.kinds() == {"perseus": sb.EXPLICIT_LINEAGE,
                          "hindsight": sb.STATE_TRANSITION,
                          "mem0": sb.PRODUCT_DECIDES,
                          "agentmemory": sb.PRODUCT_DECIDES}
    assert "three different things" in \
        sb.contract()["mechanism_kinds_are_not_equivalent"]
    assert "manufacture an equivalence" in \
        sb.contract()["mechanism_kinds_are_not_equivalent"]


def test_only_perseus_names_both_records_and_the_relationship():
    arguments = sb.BINDINGS["perseus"]["arguments"]
    assert {"from_key", "to_key", "relationship"} <= set(arguments)
    assert arguments["relationship"] == "supersedes"


def test_hindsight_changes_state_not_content():
    entry = sb.BINDINGS["hindsight"]
    assert entry["arguments"]["state"] == "invalidated"
    assert "text is NOT replaced" in entry["effect"]
    assert "valid" in entry["note"] and "invalidated" in entry["note"]


def test_agentmemory_binding_moves_nothing(frozen):
    entry = sb.BINDINGS["agentmemory"]
    assert entry["arguments"] == {}
    assert entry["one_variable"].startswith("NOTHING changes")
    assert "already exercised" in sb.contract()["agentmemory_binding_is_empty"]


def test_both_contracts_are_frozen_and_hashed(frozen):
    assert len(frozen["fixture_sha256"]) == 64
    assert frozen["fixture_contract_sha256"] == v3.contract_sha256()
    assert frozen["fixture_contract"]["frozen_before_any_engine_run"] is True
    assert frozen["binding_contract"]["frozen_before_any_engine_run"] is True
