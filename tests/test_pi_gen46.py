"""Gen46 focused tests: deterministic derivation, receipts, bounds, isolation."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import harness_state as H  # noqa: E402
from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen46"


def _json(name: str) -> dict:
    path = OUT / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


def log(*events: dict) -> list[dict]:
    return [dict(event, id=f"e{index:06d}") for index, event in enumerate(events)]


READ_A = {"type": "tool_call", "tool": "read", "args": {"path": "a.py"}}
READ_B = {"type": "tool_call", "tool": "read", "args": {"path": "b.py"}}
EDIT_A = {"type": "tool_call", "tool": "edit", "args": {"path": "a.py"}}


def check(passed: bool, tree: str) -> dict:
    return {"type": "tool_result", "command": "python -m pytest",
            "exit_code": 0 if passed else 1, "tree_digest": tree}


# --- derivation --------------------------------------------------------------


def test_the_control_loop_runs_without_the_model_asking():
    events = log(READ_A, READ_B, EDIT_A, check(False, "t1"), EDIT_A, check(True, "t2"),
                 {"type": "session_end"})
    summary = H.derive(events).summary()
    assert summary["state"]["phase"] == "done"
    assert summary["transitions_accepted"] == 6
    assert [(t["from"], t["to"]) for t in summary["transitions"]] == [
        ("inspect", "plan"), ("plan", "implement"), ("implement", "validate"),
        ("validate", "implement"), ("implement", "validate"), ("validate", "done")]


def test_replay_is_byte_identical():
    events = log(READ_A, READ_B, EDIT_A, check(True, "t1"), {"type": "session_end"})
    assert len({H.replay_digest(events) for _ in range(5)}) == 1


def test_a_mutation_after_a_pass_invalidates_the_receipt():
    events = log(READ_A, READ_B, EDIT_A, check(True, "t1"), EDIT_A)
    derivation = H.derive(events)
    assert len(derivation.receipts) == 1
    assert len(derivation.invalidations) == 1
    assert derivation.valid_receipt() is None
    assert derivation.state.phase == "implement"


def test_a_receipt_is_bound_to_the_tree_it_checked():
    events = log(READ_A, READ_B, EDIT_A, check(True, "t1"))
    derivation = H.derive(events)
    assert derivation.valid_receipt() is not None
    derivation.state.tree_digest = "a-different-tree"
    assert derivation.valid_receipt() is None


def test_done_is_not_recorded_without_a_valid_receipt():
    events = log(READ_A, READ_B, EDIT_A, check(False, "t1"), {"type": "session_end"})
    derivation = H.derive(events)
    assert derivation.state.phase == "implement"
    assert derivation.valid_receipt() is None


def test_the_hidden_verifier_can_never_become_a_receipt():
    assert H.is_validation_command("python -m pytest")
    assert not H.is_validation_command("python ../verifier.py")
    assert not H.is_validation_command("cat verifier.py")
    events = log(READ_A, READ_B, EDIT_A,
                 {"type": "tool_result", "command": "python ../verifier.py", "exit_code": 0,
                  "tree_digest": "t1"}, {"type": "session_end"})
    derivation = H.derive(events)
    assert derivation.receipts == []
    assert derivation.state.phase == "implement"


def test_illegal_transitions_fail_closed():
    derivation = H.Derivation()
    derivation._move("done", "impossible", "e0")
    assert derivation.state.phase == "inspect"
    assert derivation.transitions[-1]["accepted"] is False


def test_state_stays_bounded_under_a_long_run():
    events = log(*[{"type": "tool_call", "tool": "read", "args": {"path": f"m{i}.py"}}
                   for i in range(60)])
    derivation = H.derive(events)
    assert derivation.state.bytes() <= H.STATE_BYTE_CAP
    assert len(derivation.state.files_read) == H.RECENT_FILES_BOUND


def test_only_objective_checkpoints_are_allowed():
    derivation = H.Derivation()
    with pytest.raises(H.DerivationError):
        derivation._checkpoint("the parser looks suspicious")


def test_unknown_events_are_refused_rather_than_guessed():
    with pytest.raises(H.DerivationError):
        H.derive([{"type": "vibes", "id": "e0"}])


# --- isolation ---------------------------------------------------------------


def test_the_derivation_imports_nothing_from_the_benchmark():
    source = (ROOT / "src/memory_bakeoff/pi_state_control/harness_state.py").read_text()
    assert "task_manifest" not in source
    assert "import" in source and "memory_bakeoff" not in source.replace("memory_bakeoff.pi_state_control", "")


def test_arm_b_composition_is_untouched():
    assert P.STATE_BYTE_CAP == 4096
    assert P.RECENT_WINDOW_UNITS == 2
    assert P.RECENT_WINDOW_BYTE_CAP == 8192


# --- artifact-backed ---------------------------------------------------------


def test_preflight_passed_including_cross_implementation_equivalence():
    pre = _json("preflight.json")
    assert pre["passed"] is True
    assert pre["python_typescript_equivalence"]["summaries_identical"] is True
    assert pre["arm_b_unchanged"]["identical"] is True
    assert pre["no_network"]["outbound_blocked"] is True


def test_arm_b_hash_changed_only_by_the_shared_observer_and_it_is_recorded():
    """Gen46 required arm B untouched; Gen47 then added one hook to BOTH arms.

    That was authorised explicitly - the observation-only provider-payload
    capture had to be identical across arms to be usable - so B's hash moves.
    The check is therefore not "unchanged forever" but "changed only for that
    reason, with both values written down".
    """
    live = ROOT / "extensions/pi_state_control/pi_pilot_live.ts"
    current = hashlib.sha256(live.read_bytes()).hexdigest()
    gen46 = _json("preflight.json")["arm_b_unchanged"]["recorded_sha256"]
    bindings_path = ROOT / "results/pi_state_control_gen47/preflight_bindings.json"
    if not bindings_path.exists():
        assert current == gen46
        return
    bindings = json.loads(bindings_path.read_text())["extension_hashes"]
    assert bindings["arm_b_gen45"] == gen46
    assert bindings["arm_b_now"] == current
    assert bindings["arm_b_changed_only_by_the_shared_observer"] is True
    observer = json.loads(bindings_path.read_text())["provider_payload_observer"]
    assert observer["added_to_both_arms"] is True and observer["returns"] == "nothing"


def test_gen47_order_uses_a_new_seed_and_the_two_new_arms():
    order = _json("gen47_order_manifest.json")
    assert order["seed"] != P.ORDER_SEED
    assert order["runs"] == 24
    arms = [row["arm"] for row in order["order"]]
    assert set(arms) == {"pi_state_control_v1", "pi_harness_state_control_v1"}
    assert arms.count("pi_state_control_v1") == 12
    firsts = [row["arm"] for row in order["order"] if row["position_in_pair"] == 1]
    assert firsts.count("pi_state_control_v1") == 6


def test_deferred_hypotheses_are_named_not_quietly_included():
    pre = _json("preflight.json")
    deferred = pre["composer_unchanged"]["deferred_hypotheses"]
    assert "persistent_task_prompt_floor" in deferred
    assert "on_demand_history_retrieval" in deferred


def test_committed_contract_matches_the_module():
    assert _json("contract.json")["contract_sha256"] == H.contract_sha256()
