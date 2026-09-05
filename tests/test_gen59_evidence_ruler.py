"""Gen59: the ruler must actually contain the problem it claims to pose."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.evidence_ruler.tasks_gen59 import TASKS
from memory_bakeoff.pi_state_control import challenge_generation as C

RESULTS = ROOT / "results" / "pi_evidence_ruler_gen59"
FIXTURES = ROOT / "fixtures" / "evidence_generation_gen59_v1"
FORBIDDEN = ("verifier", "candidates.json", "failed_requirement", "VERIFIER OK")


# --- the task definitions -----------------------------------------------------

def test_every_task_declares_the_required_shape():
    for name, task in TASKS.items():
        assert len(task["positives"]) >= 2, name
        assert len(task["wrongs"]) >= 3, name
        assert sum(1 for w in task["wrongs"].values() if w["passes_visible"]) >= 2, name
        for label, wrong in task["wrongs"].items():
            assert wrong["failed_requirement"] in task["requirements"], f"{name}:{label}"
            assert wrong["why"], f"{name}:{label} needs a stated engineering reason"


def test_no_wrong_candidate_is_a_negated_verifier_assertion():
    """Negatives must be plausible mistakes, not the verifier run backwards."""
    for name, task in TASKS.items():
        for label, wrong in task["wrongs"].items():
            for path, text in wrong["overlay"].items():
                if path.startswith("tests/"):
                    continue      # a candidate's own test file may of course assert
                assert "assert" not in text, f"{name}:{label} looks derived from the verifier"


def test_specs_do_not_mention_the_evaluator():
    for name, task in TASKS.items():
        lowered = task["spec"].lower()
        for token in ("verifier", "hidden", "evaluator"):
            assert token not in lowered, f"{name} spec leaks {token!r}"


# --- the measured matrix ------------------------------------------------------

@pytest.fixture(scope="module")
def matrix():
    path = RESULTS / "candidate_matrix.json"
    if not path.exists():
        pytest.skip("Gen59 ruler has not been built")
    return json.loads(path.read_text())


def test_the_ruler_clears_the_gen60_bar(matrix):
    summary = matrix["summary"]
    assert summary["admitted"] >= 6, "fewer than six admitted tasks is a hard stop"
    assert summary["total_known_wrong_candidates"] >= 18
    assert summary["total_visible_pass_hidden_fail"] >= 12


def test_every_admitted_task_meets_every_invariant(matrix):
    for name, task in matrix["tasks"].items():
        if not task["admitted"]:
            continue
        assert all(task["checks"].values()), (name, task["checks"])


def test_positives_pass_both_checks_and_differ(matrix):
    for name, task in matrix["tasks"].items():
        if not task["admitted"]:
            continue
        positives = [r for r in task["rows"] if r["kind"] == "positive"]
        assert len(positives) >= 2, name
        assert all(r["visible"]["passed"] and r["hidden"]["passed"] for r in positives), name
        assert len({r["tracked_digest"] for r in positives}) == len(positives), name
        assert all(r["tracked_digest"] for r in positives), f"{name}: empty digests are not distinct"


def test_every_wrong_fails_the_hidden_evaluator(matrix):
    for name, task in matrix["tasks"].items():
        if not task["admitted"]:
            continue
        for row in task["rows"]:
            if row["kind"] == "wrong":
                assert row["hidden"]["passed"] is False, f"{name}:{row['candidate']} is not wrong"


def test_the_visible_tests_are_genuinely_incomplete(matrix):
    """If the shipped tests caught everything there would be nothing to study."""
    for name, task in matrix["tasks"].items():
        if not task["admitted"]:
            continue
        wrongs = [r for r in task["rows"] if r["kind"] == "wrong"]
        assert sum(1 for r in wrongs if r["visible"]["passed"]) >= 2, name


def test_the_self_modified_test_shape_is_present(matrix):
    found = [r for t in matrix["tasks"].values() for r in t["rows"]
             if r["kind"] == "wrong" and r.get("self_modified_visible_test")]
    assert found, "the Gen49-style false assurance shape must exist in the ruler"
    assert all(r["visible"]["passed"] for r in found)
    assert all(not r["hidden"]["passed"] for r in found)


# --- isolation and the frozen screen ------------------------------------------

def test_no_generator_visible_file_mentions_evaluator_truth():
    if not FIXTURES.exists():
        pytest.skip("fixtures not built")
    for task_dir in sorted(FIXTURES.iterdir()):
        prompt = C.build_prompt((task_dir / "spec.txt").read_text(), task_dir / "repo")
        for token in FORBIDDEN:
            assert token not in prompt, f"{task_dir.name} prompt leaks {token!r}"


def test_truth_is_outside_every_generator_visible_path():
    if not FIXTURES.exists():
        pytest.skip("fixtures not built")
    for task_dir in sorted(FIXTURES.iterdir()):
        assert (task_dir / "truth" / "verifier.py").exists(), task_dir.name
        assert not (task_dir / "repo" / "truth").exists(), task_dir.name


@pytest.fixture(scope="module")
def screen():
    path = RESULTS / "gen60_frozen_screen.json"
    if not path.exists():
        pytest.skip("Gen60 screen not frozen")
    return json.loads(path.read_text())


def test_the_gen60_screen_is_frozen_with_an_unevaluable_branch(screen):
    assert "UNEVALUABLE" in screen["coverage_requirement"]
    assert "50%" in screen["sensitivity"]
    assert "25%" in screen["specificity"]
    assert "no generated output exists yet" in screen["frozen_before"]
    assert screen["contract_sha256"]


def test_the_screen_targets_the_unchanged_gen58_generator(screen):
    assert "unchanged" in screen["applies_to"]


@pytest.fixture(scope="module")
def isolation():
    path = RESULTS / "isolation_preflight.json"
    if not path.exists():
        pytest.skip("isolation preflight not run")
    return json.loads(path.read_text())


def test_isolation_and_anti_triviality_sentinels_pass(isolation):
    assert isolation["passed"] is True
    assert isolation["isolation"]["clean"] is True
    assert isolation["corpus_level"]["not_eight_copies_of_one_shape"] is True
    assert isolation["corpus_level"]["some_task_has_a_self_modified_visible_test"] is True
