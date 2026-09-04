"""Gen47 focused tests: 24 leaves, mechanism integrity, pre-exposure corrections."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results" / "pi_state_control_gen47"
GEN46 = ROOT / "results" / "pi_state_control_gen46"
GEN44 = ROOT / "results" / "pi_state_control_gen44"


def _json(name: str, base: Path = OUT) -> dict:
    path = base / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


def test_all_twenty_four_slots_ran_in_the_frozen_gen47_order():
    agg = _json("aggregate.json")
    order = _json("gen47_order_manifest.json", GEN46)["order"]
    assert agg["runs"] == 24
    ran = sorted((l["index"], l["task"], l["repetition"], l["arm"]) for l in agg["leaves"])
    frozen = sorted((r["index"], r["task"], r["repetition"], r["arm"]) for r in order)
    assert ran == frozen


def test_the_harness_arm_exercised_its_loop_on_every_run():
    """H1: the mechanism Gen45 could not test."""
    totals = _json("aggregate.json")["arm_c_harness_totals"]
    assert totals["runs_with_any_transition"] == 12
    assert totals["transitions_accepted"] > 0
    assert totals["transitions_rejected"] == 0
    assert totals["runs_with_valid_receipt_at_end"] == 12


def test_the_model_still_never_requested_a_transition():
    """The Gen45 non-adoption reproduced, which is what makes the contrast fair."""
    adoption = _json("aggregate.json")["arm_b_tool_adoption"]
    assert adoption["request_transition"]["total_calls"] == 0
    assert _json("aggregate.json")["by_arm"]["pi_state_control_v1"]["reached_done"] == 0


def test_the_harness_arm_passed_more_and_timed_out_less():
    arms = _json("aggregate.json")["by_arm"]
    b, c = arms["pi_state_control_v1"], arms["pi_harness_state_control_v1"]
    assert c["verifier_passes"] > b["verifier_passes"]
    assert c["timeouts"] == 0 and b["timeouts"] > 0
    assert c["payload_bytes_median"] < b["payload_bytes_median"]


def test_no_failure_or_timeout_was_dropped():
    agg = _json("aggregate.json")
    assert len(agg["leaves"]) == 24
    assert any(l["status"] == "timeout" for l in agg["leaves"])
    assert any(l["verifier_passed"] is False for l in agg["leaves"])


def test_every_run_started_from_the_frozen_tree():
    manifest = _json("task_manifest.json", GEN44)["tasks"]
    for path in sorted((OUT / "runs").glob("*/leaf.json")):
        leaf = json.loads(path.read_text())
        assert leaf["task"]["start_tree"] == manifest[leaf["slot"]["task"]]["git_tree_digest"]


# --- pre-exposure corrections ------------------------------------------------


def test_the_tree_digest_no_longer_mutates_the_repository():
    fix = _json("preflight_bindings.json")["tree_digest_correction"]
    assert fix["all_states_match"] is True
    assert fix["git_status_unchanged_over_100_calls"] is True
    assert fix["real_index_unchanged_over_100_calls"] is True
    assert fix["old_method_visibly_mutated_status"] is True
    assert fix["gate_45_seconds_passed"] is True


def test_exit_status_was_bound_before_exposure():
    binding = _json("preflight_bindings.json")["exit_status_binding"]
    assert binding["known_failure_classified"] is True
    assert binding["known_success_classified"] is True
    assert binding["pi_surfaces_an_exit_code_field"] is False


def test_the_payload_observer_is_observation_only():
    observer = _json("preflight_bindings.json")["provider_payload_observer"]
    assert observer["returns"] == "nothing"
    assert observer["added_to_both_arms"] is True


def test_the_pre_exposure_commit_is_recorded():
    assert _json("preflight_bindings.json").get("pre_exposure_commit")


def test_raw_streams_are_hashed_even_though_they_are_not_committed():
    manifest = _json("raw_stream_manifest.json")
    assert len(manifest["streams"]) == 24
