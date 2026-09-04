"""Gen53: the v2 stop rule, its evidence path, and what the 72-run replay found."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import quiescent_v2 as Q

EXT = ROOT / "extensions" / "pi_state_control"
ARM_C = EXT / "pi_pilot_harness_state.ts"
ARM_V1 = EXT / "pi_pilot_quiescent.ts"
ARM_V2 = EXT / "pi_pilot_quiescent_v2.ts"
RESULTS = ROOT / "results" / "pi_quiescent_completion_gen53"

FROZEN_ARM_C = "205279d9c1db4659459ccd9e504421f21623c6d9a74c14142b322450bad848df"
FROZEN_ARM_V1 = "bb76f46bcb1367fb581419db68e7d66664c18229b2976ae41709f76c0cd3913c"

T0, TA, TB = "tree-initial", "tree-A", "tree-B"
CHECK = "cd . && python -m pytest tests/ -q"


def sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def drive(steps, k=3):
    rule = Q.QuiescentV2(k=k)
    rule.initial_tree, rule.current_tree = T0, T0
    stops = []
    for tool, command, tree in steps:
        rule.observe_call(tool)
        check = Q.is_visible_check(command)
        passed = (not command.endswith("#fail")) if check else None
        if rule.observe_result(passed=passed, tree=tree, fresh_check=check):
            stops.append(rule.tool_index)
    return rule, stops


def edit(tree): return ("edit", "", tree)
def bash(command, tree): return ("bash", command, tree)


# --- the two Gen52 defects ----------------------------------------------------

def test_repeated_pass_on_one_tree_no_longer_resets_the_count():
    """The Gen52 starvation defect: 144 repeats used to postpone the stop forever."""
    rule, stops = drive([edit(TA), bash(CHECK, TA), bash(CHECK, TA), bash(CHECK, TA), bash(CHECK, TA)])
    assert stops, "a run repeating its passing check must still reach quiescence"
    assert rule.same_tree_passes_counted_idle >= 3


def test_a_run_back_at_its_starting_tree_is_never_eligible():
    """The Gen52 revert defect, on a digest that reflects only the source."""
    rule, stops = drive([edit(TA), edit(T0), bash(CHECK, T0)] + [bash("ls", T0)] * 12)
    assert not stops
    assert rule.became_eligible is False
    assert rule.mutations >= 2, "the run really did mutate; eligibility must still be refused"


def test_the_initial_tree_must_be_set_before_the_first_result():
    rule = Q.QuiescentV2(k=3)
    with pytest.raises(ValueError):
        rule.observe_result(passed=None, tree=TA, fresh_check=False)


# --- v1 semantics that must survive unchanged ---------------------------------

def test_ordinary_quiescence_still_fires():
    _rule, stops = drive([edit(TA), bash(CHECK, TA), bash("ls", TA), bash("ls", TA), bash("ls", TA)])
    assert stops


def test_a_failing_check_invalidates_and_a_later_pass_rearms():
    _rule, stops = drive([edit(TA), bash(CHECK + "#fail", TA), bash(CHECK, TA),
                          bash("ls", TA), bash("ls", TA), bash("ls", TA)])
    assert stops


def test_a_pass_before_any_mutation_is_ineligible():
    _rule, stops = drive([bash(CHECK, T0), bash("ls", T0), bash("ls", T0), bash("ls", T0)])
    assert not stops


def test_a_second_tree_counts_fresh():
    _rule, stops = drive([edit(TA), bash(CHECK, TA), edit(TB), bash(CHECK, TB),
                          bash("ls", TB), bash("ls", TB), bash("ls", TB)])
    assert stops


def test_the_hidden_verifier_is_not_a_visible_check():
    assert Q.is_visible_check("python /outside/verifier.py") is False
    assert Q.is_visible_check(CHECK) is True


# --- provenance ---------------------------------------------------------------

def test_arm_c_and_the_v1_arm_are_untouched():
    """Gen52's recorded hashes are evidence; v2 is a new file, not an edit."""
    assert sha256(ARM_C) == FROZEN_ARM_C
    assert sha256(ARM_V1) == FROZEN_ARM_V1


def test_the_v2_arm_is_generated_and_reproducible():
    before = ARM_V2.read_bytes()
    subprocess.run([sys.executable, str(ROOT / "scripts/build_pi_pilot_gen53_quiescent_v2.py")],
                   check=True, capture_output=True)
    assert ARM_V2.read_bytes() == before
    assert "GENERATED from" in ARM_V2.read_text()


def test_the_contract_names_exactly_two_changes():
    contract = Q.contract()
    assert contract["contract_version"] == "quiescent-completion-toolcall-v2"
    assert len(contract["changes_from_v1"]) == 2
    assert contract["k_unit"] == "tool calls"


# --- the recorded Gen53 artifacts ---------------------------------------------

@pytest.fixture(scope="module")
def evidence():
    path = RESULTS / "evidence_path_and_equivalence.json"
    if not path.exists():
        pytest.skip("Gen53 evidence-path record has not been generated")
    return json.loads(path.read_text())


def test_the_snapshot_survives_an_abrupt_kill(evidence):
    abrupt = evidence["abrupt_termination"]
    assert abrupt["killed_with"] == "SIGKILL"
    assert abrupt["snapshot_exists"] and abrupt["internally_consistent"]
    assert abrupt["initial_tree_recorded_before_first_action"]
    assert abrupt["no_partial_files_left"]


def test_typescript_and_python_decide_identically(evidence):
    assert evidence["typescript_python_equivalence"]["disagreements"] == []
    assert len(evidence["typescript_python_equivalence"]["traces"]) >= 10


@pytest.fixture(scope="module")
def replay():
    path = RESULTS / "replay_72_runs.json"
    if not path.exists():
        pytest.skip("Gen53 replay has not been generated")
    return json.loads(path.read_text())


def test_the_replay_covers_all_seventy_two_recorded_runs(replay):
    assert len(replay["runs"]) == 72
    assert {r["generation"] for r in replay["runs"]} == {47, 49, 52}


def test_no_k_truncates_observed_progress(replay):
    for summary in replay["per_k"].values():
        assert summary["would_truncate_observed_progress"] == 0


def test_every_recorded_runaway_is_caught_at_every_k(replay):
    for summary in replay["per_k"].values():
        assert summary["timeout_runs_caught"] == summary["timeout_runs_total"]


def test_the_repeated_check_timeout_is_now_caught(replay):
    for outcome in replay["focal_runs"]["23-IP1-r2"].values():
        assert outcome["triggered"] is True


def test_change_a_is_reported_as_not_working(replay):
    """The honest finding: the digest counts build artifacts, so the predicate never engages."""
    assert replay["change_a_effectiveness"]["answer"].startswith("no")
    for k in ("1", "2", "3"):
        assert replay["focal_runs"]["11-IP1-r1"][k]["triggered"] is True


def test_the_censored_run_is_labelled(replay):
    censored = [r for r in replay["runs"] if r["trajectory_censored_by_prior_live_stop"]]
    assert len(censored) == 1
    assert censored[0]["run"].startswith("11-IP1-r1")


def test_arm_b_receipts_stay_labelled_as_reconstructions(replay):
    for row in replay["runs"]:
        if row["generation"] == 47 and row["arm"] == "pi_state_control_v1":
            assert row["receipt_source"] == "offline_reconstructed_observable_receipt"
