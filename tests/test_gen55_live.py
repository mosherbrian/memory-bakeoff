"""Gen55: the live controller must have obeyed its frozen contract exactly."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "pi_quiescent_completion_gen55"
ARM_C = "pi_harness_state_control_v1"
ARM_F = "pi_harness_state_control_quiescent_tracked_k3_v1"


@pytest.fixture(scope="module")
def preflight():
    path = RESULTS / "preflight.json"
    if not path.exists():
        pytest.skip("Gen55 preflight has not been generated")
    return json.loads(path.read_text())


def test_every_pre_live_gate_passed(preflight):
    assert preflight["passed"] is True
    assert all(preflight["gates"].values())


def test_arm_c_was_the_frozen_baseline(preflight):
    assert preflight["arms"][ARM_C] == \
        "205279d9c1db4659459ccd9e504421f21623c6d9a74c14142b322450bad848df"


def test_the_frozen_contracts_are_recorded(preflight):
    frozen = preflight["frozen_contracts"]
    assert frozen["quiescence"] == "quiescent-completion-toolcall-v2"
    assert frozen["tracked_digest"] == "tracked-tree-digest-v1"
    assert frozen["k"] == 3
    assert "deviation" in frozen["k_choice"]


@pytest.fixture(scope="module")
def aggregate():
    path = RESULTS / "aggregate.json"
    if not path.exists():
        pytest.skip("Gen55 aggregate has not been generated")
    return json.loads(path.read_text())


def test_all_twenty_four_runs_completed(aggregate):
    assert aggregate["runs"] == 24
    for arm in (ARM_C, ARM_F):
        assert aggregate["arms"][arm]["runs"] == 12
        assert aggregate["arms"][arm]["termination"]["crash_or_orchestration_failure"] == 0


def test_no_stop_violated_the_frozen_contract(aggregate):
    audit = aggregate["contract_audit"]
    assert audit["violations"] == []
    assert audit["all_triggers_satisfied_the_frozen_contract"] is True


def test_no_stop_landed_on_a_tree_equal_to_its_start(aggregate):
    """The hard-failure condition, and the defect that broke the first version."""
    assert aggregate["contract_audit"]["stops_on_a_tree_equal_to_start"] == 0
    assert aggregate["stop_policy"]["stopped_on_a_tree_identical_to_the_start"] == 0


def test_every_trigger_held_its_receipt_on_the_tree_it_stopped_on(aggregate):
    assert aggregate["stop_policy"]["tree_unchanged_between_receipt_and_stop_all_triggers"] is True


def test_no_running_tool_was_killed(aggregate):
    assert aggregate["stop_policy"]["total_same_batch_overshoot"] == 0


def test_the_arms_were_indistinguishable_to_the_model(aggregate):
    assert aggregate["h1_first_request_bytes_identical_across_arms"] is True


def test_the_treated_arm_had_no_timeouts_and_the_baseline_did(aggregate):
    assert aggregate["arms"][ARM_F]["termination"]["timeout"] == 0
    assert aggregate["arms"][ARM_C]["termination"]["timeout"] >= 1


def test_exposure_is_recorded_so_it_cannot_be_confused_with_efficacy(aggregate):
    """Most F runs never trigger; the report must be able to say so."""
    policy = aggregate["stop_policy"]
    assert policy["triggered_runs"] <= policy["eligible_runs"]
    assert policy["triggered_runs"] == aggregate["arms"][ARM_F]["termination"]["quiescent_stop"]


@pytest.fixture(scope="module")
def safety():
    path = RESULTS / "stop_and_safety_table.json"
    if not path.exists():
        pytest.skip("Gen55 safety table has not been generated")
    return json.loads(path.read_text())


def test_each_trigger_satisfied_every_condition_individually(safety):
    for row in safety:
        if not row["triggered"]:
            continue
        assert (row["mutations"] or 0) >= 1
        assert row["net_tree_changed"] is True
        assert row["valid_receipt_tree"] == row["current_tree_digest"]
        assert row["current_tree_digest"] != row["initial_tree_digest"]
        assert (row["idle_count"] or 0) >= 3
        assert row["effective_stop_tool_index"] >= row["trigger_tool_index"]


def test_untriggered_runs_are_visible_as_untreated(safety):
    untriggered = [r for r in safety if not r["triggered"]]
    assert untriggered, "with no untriggered runs the exposure caveat would be moot"
    for row in untriggered:
        assert row["trigger_tool_index"] is None


@pytest.fixture(scope="module")
def manifest():
    path = RESULTS / "raw_stream_manifest.json"
    if not path.exists():
        pytest.skip("Gen55 retention manifest has not been generated")
    return json.loads(path.read_text())


def test_every_raw_stream_survived_cleanup(manifest):
    assert len(manifest["streams"]) == 24
    assert manifest["retention_verified"] is True
    assert manifest["failures"] == []
    assert manifest["cleanup"]["kept_because_unverified"] == []
