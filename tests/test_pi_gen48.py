"""Gen48 focused tests: the human-direction floor and the intent-persistence ruler."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results" / "pi_state_control_gen48"
GEN47 = ROOT / "results" / "pi_state_control_gen47"
EXT = ROOT / "extensions" / "pi_state_control"


def _json(name: str, base: Path = OUT) -> dict:
    path = base / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


# --- the floor ---------------------------------------------------------------


def test_arms_are_identical_until_the_floor_activates():
    """The primary integrity property: D must not be C-plus-noise early on."""
    pre = _json("preflight.json")["arm_equality_before_activation"]
    assert pre["requests_checked"] >= 2
    assert pre["all_identical"] is True
    assert pre["no_early_floor"] is True


def test_the_floor_activates_exactly_when_the_window_drops_the_task():
    floor = _json("preflight.json")["floor_activation"]
    assert floor["activates_exactly_when_the_window_drops_the_task"] is True
    assert floor["never_deactivates"] is True
    assert floor["c_never_carries_it_after"] is True


def test_the_floor_carries_the_prompt_verbatim_over_a_long_run():
    floor = _json("preflight.json")["floor_activation"]
    assert floor["verbatim_after_activation"] is True
    assert floor["checked_up_to_turns"] >= 100


def test_the_two_arms_offer_the_same_tools():
    surface = _json("preflight.json")["same_tool_surface"]
    assert surface["identical"] is True
    assert surface["neither_offers_state_control_tools"] is True


def test_arm_d_is_generated_from_arm_c_so_they_cannot_drift():
    source = (EXT / "pi_pilot_task_floor.ts").read_text()
    assert "Generated from" in source
    assert "harness-state-v1" in source
    assert _json("preflight.json")["derivation_unchanged"]["d_generated_from_c"] is True


def test_arm_c_is_untouched_since_gen47():
    check = _json("preflight.json")["arm_c_unchanged_from_gen47"]
    assert check["identical"] is True
    assert check["current"] == hashlib.sha256((EXT / "pi_pilot_harness_state.ts").read_bytes()).hexdigest()


# --- the ruler ---------------------------------------------------------------


def test_every_task_fails_before_and_passes_after_its_reference_fix():
    manifest = _json("task_manifest.json")
    assert manifest["all_tasks_fail_before_and_pass_after"] is True
    assert len(manifest["tasks"]) == 4
    for task in manifest["tasks"].values():
        assert task["git_tree_digest"] and task["verifier_sha256"] and task["prompt_sha256"]


def test_each_task_has_two_public_requirements_so_failures_can_be_named():
    manifest = _json("task_manifest.json")
    for task in manifest["tasks"].values():
        assert set(task["requirements"]) == {"A", "B"}


def test_prompts_fit_the_floor_cap():
    manifest = _json("task_manifest.json")
    for task in manifest["tasks"].values():
        assert task["prompt_bytes"] <= 4096


def test_the_incomplete_visible_check_diagnostic_is_real():
    """A partial fix must pass the project's own check and fail the hidden verifier."""
    probe = _json("task_manifest.json")["tasks"]["IP4"]["incomplete_visible_check_probe"]
    assert probe["visible_check_passes"] is True
    assert probe["hidden_verifier_passes"] is False
    assert probe["demonstrates_false_assurance"] is True


def test_ip1_stale_visible_test_is_recorded_not_hidden():
    """A correct IP1 fix makes the shipped test fail until the agent updates it."""
    tasks = _json("preflight.json")["tasks"]
    assert tasks["ip1_visible_check_contradicts_the_new_instruction"] is True
    assert "control-valid done" in tasks["note"]


def test_the_agent_cannot_see_the_verifier():
    isolation = _json("preflight.json")["task_isolation"]
    assert all(isolation.values())


# --- plan --------------------------------------------------------------------


def test_gen49_order_is_new_balanced_and_counterbalanced():
    order = _json("gen49_order_manifest.json")
    assert order["seed"] == 20260907
    assert order["runs"] == 24
    arms = [row["arm"] for row in order["order"]]
    assert set(arms) == {"pi_harness_state_control_v1", "pi_harness_state_control_task_floor_v1"}
    assert arms.count("pi_harness_state_control_v1") == 12
    firsts = [row["arm"] for row in order["order"] if row["position_in_pair"] == 1]
    assert firsts.count("pi_harness_state_control_v1") == 6


def test_preflight_passed_with_no_network():
    pre = _json("preflight.json")
    assert pre["passed"] is True
    assert pre["no_network"]["outbound_blocked"] is True


def test_gen47_clarification_was_appended_without_changing_numbers():
    report = (ROOT / "research" / "PI_STATE_CONTROL_GEN47_HARNESS_STATE_LIVE.md").read_text()
    assert "Post-Gen47 interpretation clarification" in report
    assert "12/12" in report and "9/12" in report
    assert "does **not** license" in report
