"""Gen52: arm E must be arm C plus one dormant stop policy, and nothing else."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "extensions" / "pi_state_control"
ARM_C = EXT / "pi_pilot_harness_state.ts"
ARM_E = EXT / "pi_pilot_quiescent.ts"
RESULTS = ROOT / "results" / "pi_quiescent_completion_gen52"

# The arm C hash frozen at Gen48 and used unchanged for Gen49 and Gen52.
FROZEN_ARM_C = "205279d9c1db4659459ccd9e504421f21623c6d9a74c14142b322450bad848df"


def sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_arm_c_is_untouched():
    assert sha256(ARM_C) == FROZEN_ARM_C


def test_arm_e_is_generated_and_reproducible():
    before = ARM_E.read_bytes()
    subprocess.run([sys.executable, str(ROOT / "scripts/build_pi_pilot_gen52_quiescent.py")],
                   check=True, capture_output=True)
    assert ARM_E.read_bytes() == before, "the generator does not reproduce the committed arm E"
    assert "GENERATED from" in ARM_E.read_text()


def test_arm_e_leaves_the_model_facing_path_byte_identical():
    """The prompt the model sees is composed in one place. Arm E must not touch it."""
    def section(text: str, start: str, end: str) -> str:
        return text[text.index(start):text.index(end)]

    c, e = ARM_C.read_text(), ARM_E.read_text()
    for start, end in (("const IMMUTABLE_INSTRUCTIONS", "const canonical"),
                       ('pi.on("context"', 'pi.on("before_provider_request"')):
        assert section(c, start, end) == section(e, start, end), f"arm E changed {start!r}"

    # `recentWindow` decides which of the model's own turns survive, so it is
    # model-facing too. It has no stable following anchor in E, where the stop
    # module is inserted after it, so slice to the end of the function instead.
    def function_body(text: str, name: str) -> str:
        start = text.index(f"function {name}")
        return text[start:text.index("\n}\n", start)]

    assert function_body(c, "recentWindow") == function_body(e, "recentWindow")
    assert function_body(c, "interactionUnits") == function_body(e, "interactionUnits")


def test_arm_e_never_reads_the_hidden_verifier():
    stop_module = ARM_E.read_text().split("export class QuiescentStop")[1].split("\nexport default")[0]
    for forbidden in ("verifier", "reference_fix", "hidden"):
        assert forbidden not in stop_module


def test_the_stop_k_is_three_and_stated_as_calibrated():
    text = ARM_E.read_text()
    assert "export const STOP_K = 3;" in text
    assert "Gen51 offline calibration" in text


# --- the recorded preflight ---------------------------------------------------

@pytest.fixture(scope="module")
def preflight():
    path = RESULTS / "preflight.json"
    if not path.exists():
        pytest.skip("Gen52 preflight has not been generated")
    return json.loads(path.read_text())


def test_preflight_passed(preflight):
    assert preflight["passed"] is True


def test_trigger_semantics_are_all_proven(preflight):
    semantics = preflight["trigger_semantics"]
    assert semantics["k1_does_not_stop"] and semantics["k2_does_not_stop"]
    assert semantics["k3_stops"]
    assert semantics["mutation_resets_the_count"]
    assert semantics["failing_visible_check_resets"]
    assert semantics["pass_before_any_mutation_is_ineligible"]
    assert semantics["new_pass_after_mutation_rearms"]


def test_hidden_verifier_is_not_a_visible_check(preflight):
    assert preflight["hidden_verifier_excluded"] is True


def test_no_in_flight_tool_is_killed(preflight):
    guard = preflight["no_in_flight_tool_killed"]
    assert guard["stop_deferred_until_batch_drained"] is True
    assert guard["aborted_exactly_once"] is True
    assert guard["same_batch_overshoot_calls"] >= 1


def test_c_and_e_compose_identical_context(preflight):
    identity = preflight["model_facing_identity"]
    assert identity["composed_context_identical"] is True
    assert identity["compositions_compared"] >= 1


def test_the_ruler_is_gen48s_unchanged(preflight):
    assert preflight["ruler"]["unchanged"] is True
    assert preflight["ruler"]["tasks"] == ["IP1", "IP2", "IP3", "IP4"]


def test_order_manifest_is_frozen_and_counterbalanced():
    path = RESULTS / "gen52_order_manifest.json"
    if not path.exists():
        pytest.skip("order manifest has not been generated")
    manifest = json.loads(path.read_text())
    assert manifest["seed"] == 20260909
    assert manifest["runs"] == 24
    order = manifest["order"]
    for first, second in zip(order[::2], order[1::2]):
        assert first["task"] == second["task"]
        assert first["repetition"] == second["repetition"]
        assert first["arm"] != second["arm"]
    leading = [pair[0]["arm"] for pair in zip(order[::2], order[1::2])]
    assert len(set(leading)) == 2, "arm order is not counterbalanced across pairs"


# --- the live safety record ---------------------------------------------------

@pytest.fixture(scope="module")
def safety():
    path = RESULTS / "stop_and_safety_table.json"
    if not path.exists():
        pytest.skip("Gen52 has not produced a safety table")
    return json.loads(path.read_text())


def test_every_trigger_stopped_on_the_tree_its_receipt_was_bound_to(safety):
    """The rule's own guarantee, checked against what the harness recorded."""
    for row in safety:
        if row["triggered"]:
            assert row["tree_unchanged_between_receipt_and_stop"] is True, row["run"]


def test_no_trigger_killed_a_tool_that_was_still_running(safety):
    for row in safety:
        if row["triggered"]:
            assert row["same_batch_overshoot_calls"] is not None
            assert row["effective_stop_tool_index"] >= row["trigger_tool_index"]


def test_a_trigger_always_followed_at_least_one_mutation(safety):
    for row in safety:
        if row["triggered"]:
            assert (row["mutations_before_trigger"] or 0) >= 1


def test_the_safety_outcomes_are_recorded_rather_than_assumed(safety):
    """These may legitimately be non-zero; they must never be missing."""
    for row in safety:
        assert "live_stop_wrong_tree" in row
        assert "stopped_on_a_tree_identical_to_the_start" in row
        assert "net_tree_change" in row


def test_a_reverted_run_is_not_counted_as_an_ordinary_wrong_tree_stop(safety):
    """A run that undid its own work must be visible as such, not folded in."""
    reverted = [r for r in safety if r["stopped_on_a_tree_identical_to_the_start"]]
    for row in reverted:
        assert row["triggered"] is True
        assert row["net_tree_change"] is False
