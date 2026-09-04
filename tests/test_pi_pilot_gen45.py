"""Gen45 focused tests: 24 leaves, arm separation, frozen order, honest reporting."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen45"
GEN44 = ROOT / "results" / "pi_state_control_gen44"


def _json(name: str) -> dict:
    path = OUT / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


def test_all_twenty_four_slots_ran_in_the_frozen_order():
    agg, order = _json("aggregate.json"), json.loads((GEN44 / "order_manifest.json").read_text())["order"]
    assert agg["runs"] == 24
    ran = [(leaf["index"], leaf["task"], leaf["repetition"], leaf["arm"]) for leaf in agg["leaves"]]
    frozen = [(row["index"], row["task"], row["repetition"], row["arm"]) for row in order]
    assert sorted(ran) == sorted(frozen)


def test_every_run_started_from_the_frozen_tree():
    manifest = json.loads((GEN44 / "task_manifest.json").read_text())["tasks"]
    for leaf in _json("aggregate.json")["leaves"]:
        expected = manifest[leaf["task"]]["git_tree_digest"]
        assert leaf["start_tree"] == expected, leaf["index"]


def test_no_failure_was_averaged_away():
    agg = _json("aggregate.json")
    assert len(agg["leaves"]) == 24
    assert agg["by_arm"]["pi_state_control_v1"]["timeouts"] == 3
    statuses = {leaf["status"] for leaf in agg["leaves"]}
    assert "timeout" in statuses


def test_seed_policy_resolved_to_samples_and_no_patch_was_applied():
    seed = _json("seed_policy.json")
    assert seed["decision"] == "NO_SEED"
    assert seed["no_patch_applied"] is True
    assert seed["resolved_before_any_frozen_task"] is True


def test_smoke_passed_and_its_failed_attempts_are_recorded():
    smoke = _json("compatibility_smoke.json")
    assert smoke["passed"] is True
    assert smoke["attempts"] == 3
    assert len(smoke["attempt_history"]) == 3
    assert all(smoke["requirements"].values())
    # the two failures are recorded as harness faults, not model behaviour
    assert "harness" in smoke["attempt_history"][0]["class"]
    assert smoke["cap_declared_before_attempt_3"]


def test_arm_b_control_layer_was_never_exercised():
    """The result that changes how everything else reads."""
    control = _json("aggregate.json")["arm_b_control_totals"]
    assert control["transitions_accepted"] == 0
    assert control["blocked_completions"] == 0
    assert control["artifact_revalidations"] == 0
    phases = _json("aggregate.json")["arm_b_final_phases"]
    assert set(phases) == {"inspect"}


def test_per_request_growth_is_bounded_in_arm_b():
    """H2, which holds even though H1 does not."""
    runs = sorted((OUT / "runs").glob("*/leaf.json"))
    if not runs:
        pytest.skip("no run leaves")
    for path in runs:
        leaf = json.loads(path.read_text())
        series = leaf["measured"]["request_bytes_by_turn"]
        if leaf["slot"]["arm"] != "pi_state_control_v1" or len(series) < 5:
            continue
        assert max(series) / series[0] < 20, leaf["slot"]


def test_arm_a_outperformed_arm_b_on_this_task_set():
    agg = _json("aggregate.json")
    assert agg["by_arm"]["pi_default_v1"]["verifier_passes"] == 12
    assert agg["by_arm"]["pi_state_control_v1"]["verifier_passes"] == 7
    assert (agg["by_arm"]["pi_state_control_v1"]["request_bytes_median"]
            > agg["by_arm"]["pi_default_v1"]["request_bytes_median"])


def test_raw_streams_are_hashed_even_though_they_are_not_committed():
    manifest = _json("raw_stream_manifest.json")
    assert len(manifest["streams"]) == 24
    assert all(entry["sha256"] and entry["bytes"] for entry in manifest["streams"].values())


def test_execution_identity_matches_the_gen44_pins():
    ident = _json("execution_identity.json")
    pin = json.loads((GEN44 / "model_candidate_identity.json").read_text())
    assert ident["model"]["sha256"] == pin["model"]["sha256"]
    assert ident["server"]["version_line"] == pin["inference_server"]["version_line"]
    assert ident["sampling"] == pin["runtime_flags"]["sampling"]
    assert ident["pi"]["version"] == "0.73.0"
    assert "pi-lcm" in ident["pi"]["why_isolated"]


def test_pairs_keep_the_pairing():
    pairs = _json("pairs.json")
    assert len(pairs) == 12
    for pair in pairs:
        assert set(pair) >= {"task", "repetition", "A", "B", "bytes_delta_b_minus_a"}
