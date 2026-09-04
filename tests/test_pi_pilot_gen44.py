"""Gen44 focused tests: arms, composition caps, tasks, churn, order, guards."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen44"


def _json(name: str) -> dict:
    path = OUT / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


# --- composition, frozen before any live run ---------------------------------


def test_interaction_units_are_defined_not_judged():
    messages = [
        {"role": "assistant", "content": "orphan before any user turn"},
        {"role": "user", "content": "one"},
        {"role": "assistant", "content": "a"},
        {"role": "toolResult", "content": "t"},
        {"role": "user", "content": "two"},
        {"role": "assistant", "content": "b"},
    ]
    units = P.interaction_units(messages)
    assert len(units) == 2
    assert units[0][0]["content"] == "one" and len(units[0]) == 3
    assert units[1][0]["content"] == "two"
    assert all(m["content"] != "orphan before any user turn" for unit in units for m in unit)


def test_window_keeps_only_the_last_two_units_in_order():
    messages = []
    for turn in range(5):
        messages += [{"role": "user", "content": f"u{turn}"},
                     {"role": "assistant", "content": f"a{turn}"}]
    kept, _ = P.recent_window(messages)
    assert [m["content"] for m in kept] == ["u3", "a3", "u4", "a4"]


def test_window_respects_the_byte_cap():
    messages = [{"role": "user", "content": "x" * 20000},
                {"role": "assistant", "content": "y" * 20000}]
    kept, used = P.recent_window(messages)
    assert used <= P.RECENT_WINDOW_BYTE_CAP
    assert len(kept) < len(messages)


def test_caps_are_frozen_values_not_derived_at_runtime():
    assert P.STATE_BYTE_CAP == 4096
    assert P.RECENT_WINDOW_UNITS == 2
    assert P.RECENT_WINDOW_BYTE_CAP == 8192
    assert P.LATEST_OBSERVATION_BYTE_CAP == 8192


def test_no_semantic_retrieval_is_offered_in_this_pilot():
    contract = P.pilot_contract()
    assert contract["composition"]["semantic_retrieval"] == "not available in this pilot"
    assert "retrieve_history" not in P.ARMS["pi_state_control_v1"]["state_control_tools"]


# --- arms --------------------------------------------------------------------


def test_arm_a_carries_no_treatment():
    a = P.ARMS["pi_default_v1"]
    assert a["context_hook_installed"] is False
    assert a["state_control_tools"] == []
    assert "enabled" in a["pi_compaction"]


def test_treatment_is_named_as_a_bundle_not_a_single_variable():
    assert len(P.TREATMENT_COMPONENTS) >= 4
    assert any("tools" in component for component in P.TREATMENT_COMPONENTS)


# --- churn definitions -------------------------------------------------------


def test_repeat_definitions_match_a_hand_checked_log():
    log = [
        {"tool": "read", "args": {"path": "a.py"}, "path": "a.py"},
        {"tool": "read", "args": {"path": "a.py"}, "path": "a.py"},
        {"tool": "edit", "args": {"path": "a.py"}, "path": "a.py", "mutates_repo": True},
        {"tool": "read", "args": {"path": "a.py"}, "path": "a.py"},
    ]
    churn = P.count_churn(log)
    assert churn["redundant_file_reads"] == 1
    assert churn["exact_repeated_tool_calls"] == 2
    assert churn["repo_mutations"] == 1


def test_a_verifier_rerun_after_a_change_is_not_redundant():
    log = [
        {"tool": "bash", "args": {"cmd": "v"}, "command": "v"},
        {"tool": "edit", "args": {"path": "a.py"}, "path": "a.py", "mutates_repo": True},
        {"tool": "bash", "args": {"cmd": "v"}, "command": "v"},
    ]
    assert P.count_churn(log)["redundant_verifier_invocations"] == 0


def test_churn_definitions_are_frozen_in_the_contract():
    definitions = P.pilot_contract()["churn_definitions"]
    assert set(definitions) == {
        "exact_repeated_tool_call", "redundant_file_read", "redundant_verifier_invocation"
    }


# --- order -------------------------------------------------------------------


def test_order_is_deterministic_balanced_and_counterbalanced():
    order = P.run_order()
    assert len(order) == 24
    assert order == P.run_order()
    arms = [row["arm"] for row in order]
    assert arms.count("pi_default_v1") == arms.count("pi_state_control_v1") == 12
    firsts = [row["arm"] for row in order if row["position_in_pair"] == 1]
    assert firsts.count("pi_default_v1") == firsts.count("pi_state_control_v1") == 6


def test_pairs_share_task_and_repetition():
    order = P.run_order()
    for index in range(0, len(order), 2):
        assert order[index]["task"] == order[index + 1]["task"]
        assert order[index]["repetition"] == order[index + 1]["repetition"]
        assert order[index]["arm"] != order[index + 1]["arm"]


# --- artifact-backed ---------------------------------------------------------


def test_every_task_fails_before_and_passes_after_a_reference_fix():
    manifest = _json("task_manifest.json")
    assert manifest["all_tasks_fail_before_and_pass_after"] is True
    assert set(manifest["tasks"]) == {"T1", "T2", "T3", "T4"}
    for task in manifest["tasks"].values():
        assert task["git_tree_digest"]
        assert task["verifier_sha256"]


def test_the_agent_never_sees_the_verifier():
    isolation = _json("preflight.json")["task_isolation"]
    assert isolation["verifier_never_inside_repo"] is True
    assert isolation["verifier_never_named_to_the_agent"] is True


def test_preflight_passed_with_both_arms_verified_in_real_pi():
    preflight = _json("preflight.json")
    assert preflight["passed"] is True
    assert all(preflight["pi_arms"].values())
    assert preflight["no_network"]["outbound_blocked"] is True
    assert preflight["model_candidate"]["generation_performed"] is False


def test_arm_a_did_not_touch_pi_context_and_arm_b_did():
    verification = _json("pi_arm_verification.json")
    assert verification["arm_a"]["returned_replacement"] is False
    assert verification["arm_a"]["pi_message_array_unmutated"] is True
    assert verification["arm_b"]["returned_replacement"] is True
    assert verification["arm_b"]["replacement_bytes"] < verification["arm_b"]["incoming_bytes"]
    assert verification["core_patched"] is False


def test_state_control_guarantees_still_hold_under_the_pilot_caps():
    state = _json("preflight.json")["state_control"]
    assert all(state.values())


def test_model_candidate_is_pinned_without_generating():
    identity = _json("model_candidate_identity.json")
    assert identity["status"] == "PINNED"
    assert identity["model"]["sha256"]
    assert identity["inference_server"]["version_line"]
    assert identity["runtime_flags"]["seed"] is None
    assert any("seed" in risk.lower() for risk in identity["open_risks_for_gen45"])


def test_committed_contract_matches_the_module():
    committed = _json("pilot_contract.json")
    assert committed["contract_sha256"] == P.contract_sha256()
    assert committed["run_plan"]["runs"] == 24
    assert committed["evidence_class"] == "architecture_pilot_design_no_score"
