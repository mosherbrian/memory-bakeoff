"""Gen58: independent challenge generation, and why its screen could not run."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import challenge_generation as C

RESULTS = ROOT / "results" / "pi_model_assisted_evidence_gen58"


# --- the contract -------------------------------------------------------------

def test_the_generator_is_denied_every_outcome_bearing_input():
    forbidden = C.contract()["generator_inputs_forbidden"]
    for item in ("any candidate final tree", "any diff", "any solver transcript",
                 "any historical outcome", "the hidden verifier", "the reference fix"):
        assert item in forbidden


def test_the_prompt_contains_only_instruction_and_shipped_tree(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "m.py").write_text("x = 1\n")
    prompt = C.build_prompt("do the thing", tmp_path)
    assert "do the thing" in prompt and "pkg/m.py" in prompt
    for leak in ("verifier", "reference_fix", "hidden"):
        assert leak not in prompt.lower()


def test_the_same_model_limitation_is_stated():
    assert "same pinned weights" in C.contract()["same_model_limitation"]


def test_a_generated_test_is_never_treated_as_truth():
    assert C.contract()["a_generated_test_is_not_truth"] is True


# --- the sanitizer, including the bug that forced a regeneration ---------------

def test_tests_inside_a_class_are_detected():
    """The defect that rejected nine valid banks in the first frozen attempt."""
    code = "```python\nclass TestThing:\n    def test_a(self):\n        assert True\n```"
    parsed = C.parse_output(code)
    assert parsed["accepted"] is True
    assert parsed["test_functions"] == ["test_a"]


def test_top_level_tests_are_still_detected():
    parsed = C.parse_output("```python\ndef test_a():\n    assert True\n```")
    assert parsed["accepted"] is True


def test_output_without_tests_is_rejected():
    assert C.parse_output("```python\nx = 1\n```")["accepted"] is False


def test_syntax_errors_and_missing_blocks_are_rejected():
    assert C.parse_output("no fence here")["accepted"] is False
    assert C.parse_output("```python\ndef test_a(:\n```")["accepted"] is False


def test_file_access_and_forbidden_names_are_rejected():
    assert C.parse_output("```python\ndef test_a():\n    open('x')\n```")["accepted"] is False
    assert C.parse_output(
        "```python\nimport subprocess\ndef test_a():\n    assert True\n```")["accepted"] is False


def test_self_assignment_in_a_test_method_is_allowed():
    """A method setting self.x is ordinary test code, not a production edit."""
    code = "```python\nclass TestThing:\n    def test_a(self):\n        self.x = 1\n        assert self.x\n```"
    assert C.parse_output(code)["accepted"] is True


# --- the recorded run ---------------------------------------------------------

@pytest.fixture(scope="module")
def generation():
    path = RESULTS / "generation_log.json"
    if not path.exists():
        pytest.skip("Gen58 generation has not run")
    return json.loads(path.read_text())


def test_twelve_calls_were_made_and_all_parsed(generation):
    assert len(generation["outputs"]) == 12
    assert generation["accepted"] == 12


def test_the_frozen_order_and_repetitions_were_honoured(generation):
    frozen = generation["frozen"]
    assert frozen["task_order"] == ["IP1", "IP2", "IP3", "IP4"]
    assert frozen["repetitions"] == 3
    assert frozen["total_calls"] == 12


def test_the_superseded_attempt_is_retained_and_labelled():
    """The first run was discarded, not silently reused."""
    readme = RESULTS / "superseded_attempt_1" / "README.md"
    if not readme.exists():
        pytest.skip("no superseded attempt recorded")
    text = readme.read_text()
    assert "not used" in text
    assert "before any bank was executed" in text


@pytest.fixture(scope="module")
def evaluation():
    path = RESULTS / "evaluation.json"
    if not path.exists():
        pytest.skip("Gen58 evaluation has not run")
    return json.loads(path.read_text())


def test_every_bank_was_checked_against_a_trusted_implementation(evaluation):
    for task, result in evaluation["reference_validity"].items():
        assert result["status"] in ("measured", "UNMEASURED"), task
        if result["status"] == "measured":
            assert "bank_passes_reference" in result


def test_banks_failing_their_reference_are_marked_unsafe_and_excluded(evaluation):
    unsafe = {t for t, r in evaluation["reference_validity"].items()
              if r.get("status") == "measured" and not r.get("bank_passes_reference")}
    assert unsafe, "this generation's finding is that some banks reject correct code"
    for task in unsafe:
        assert evaluation["reference_validity"][task]["unsafe_as_gate"] is True
        assert task in evaluation["crosstab"]["excluded_unmeasured_or_unsafe"]


def test_the_screen_population_contains_no_hidden_wrong_trees(evaluation):
    """The structural collision: valid banks and wrong work do not overlap."""
    crosstab = evaluation["crosstab"]
    assert crosstab["bank_fail_hidden_wrong"] == 0
    assert crosstab["bank_pass_hidden_wrong"] == 0
    assert evaluation["screen"]["hidden_wrong_flagged_rate"] is None


def test_no_correct_tree_was_challenged_by_a_valid_bank(evaluation):
    assert evaluation["crosstab"]["bank_fail_hidden_correct"] == 0


def test_the_ip4_partial_fix_is_caught_by_a_reference_valid_bank(evaluation):
    """The one genuine positive: evidence the shipped test lacked."""
    assert evaluation["reference_validity"]["IP4"]["bank_passes_reference"] is True
    sentinel = evaluation["sentinels"]["gen48-IP4-partial-fix"]
    assert sentinel["bank_fails"] is True


def test_the_successful_comparator_is_also_rejected_by_the_unsafe_bank(evaluation):
    """Catching the false assurance does not count when correct work is rejected too."""
    comparator = evaluation["sentinels"]["gen49-IP1-r1-D"]
    assert comparator["hidden"] is True
    assert comparator["bank_fails"] is True
    assert evaluation["reference_validity"]["IP1"]["unsafe_as_gate"] is True


@pytest.fixture(scope="module")
def retention():
    path = RESULTS / "raw_stream_manifest.json"
    if not path.exists():
        pytest.skip("Gen58 retention manifest missing")
    return json.loads(path.read_text())


def test_all_generation_streams_survived_cleanup(retention):
    assert len(retention["streams"]) == 12
    assert retention["retention_verified"] is True
    assert retention["failures"] == []
