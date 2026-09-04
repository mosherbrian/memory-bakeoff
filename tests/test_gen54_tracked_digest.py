"""Gen54: the fingerprint must ignore build output and nothing else."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import tracked_digest as T

RESULTS = ROOT / "results" / "pi_quiescent_completion_gen54"
ARM = ROOT / "extensions" / "pi_state_control" / "pi_pilot_quiescent_tracked.ts"


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "units.py").write_text("X = 4\n")
    for command in (["git", "init", "-q"], ["git", "add", "-A"],
                    ["git", "-c", "user.email=p@x.invalid", "-c", "user.name=p",
                     "commit", "-qm", "base"]):
        subprocess.run(command, cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_build_artifacts_do_not_move_the_digest(repo):
    before = T.tracked_digest(repo)
    cache = repo / "pkg" / "__pycache__"
    cache.mkdir()
    (cache / "units.cpython-313.pyc").write_bytes(b"\x00compiled")
    (repo / ".pytest_cache").mkdir()
    (repo / ".pytest_cache" / "CACHEDIR.TAG").write_text("x")
    assert T.tracked_digest(repo) == before
    assert T.whole_worktree_digest(repo) != before, "the old digest really was moved by artifacts"


def test_a_real_edit_moves_the_digest(repo):
    before = T.tracked_digest(repo)
    (repo / "pkg" / "units.py").write_text("X = 8\n")
    assert T.tracked_digest(repo) != before


def test_a_revert_returns_to_the_starting_digest(repo):
    before = T.tracked_digest(repo)
    (repo / "pkg" / "units.py").write_text("X = 8\n")
    (repo / "pkg" / "units.py").write_text("X = 4\n")
    assert T.tracked_digest(repo) == before


def test_a_new_source_file_is_still_visible(repo):
    """A tracked-files-only digest would miss this, and adding a module is progress."""
    before = T.tracked_digest(repo)
    (repo / "pkg" / "extra.py").write_text("Y = 1\n")
    assert T.tracked_digest(repo) != before


def test_a_deletion_is_still_visible(repo):
    before = T.tracked_digest(repo)
    (repo / "pkg" / "units.py").unlink()
    assert T.tracked_digest(repo) != before


def test_the_digest_never_touches_the_real_index(repo):
    before = (repo / ".git" / "index").read_bytes()
    (repo / "pkg" / "units.py").write_text("X = 8\n")
    T.tracked_digest(repo)
    assert (repo / ".git" / "index").read_bytes() == before


def test_the_contract_names_what_it_excludes():
    contract = T.contract()
    assert contract["contract_version"] == "tracked-tree-digest-v1"
    assert any("__pycache__" in pattern for pattern in contract["excludes"])
    assert "newly added source files" in contract["still_sees"]


def test_the_arm_is_generated_and_uses_the_tracked_digest():
    before = ARM.read_bytes()
    subprocess.run([sys.executable, str(ROOT / "scripts/build_pi_pilot_gen54_quiescent_tracked.py")],
                   check=True, capture_output=True)
    assert ARM.read_bytes() == before
    text = ARM.read_text()
    assert "tracked-tree-digest-v1" in text
    assert ':(exclude)**/__pycache__/**' in text


# --- the recorded Gen54 artifacts ---------------------------------------------

@pytest.fixture(scope="module")
def focal():
    path = RESULTS / "focal_run_reconstruction.json"
    if not path.exists():
        pytest.skip("Gen54 focal reconstruction has not been generated")
    return json.loads(path.read_text())


def test_the_reverted_run_is_genuinely_rejected(focal):
    """Sol's precondition: refused for current == initial, not merely avoided by K."""
    assert focal["v2_would_genuinely_reject_this_run"] is True
    assert focal["answer"]["tracked_digest_returns_to_initial_after_the_revert"] is True
    assert focal["answer"]["whole_worktree_digest_returns_to_initial_after_the_revert"] is False
    assert focal["edits_skipped"] == []


@pytest.fixture(scope="module")
def replay():
    path = RESULTS / "replay_72_runs_tracked_digest.json"
    if not path.exists():
        pytest.skip("Gen54 replay has not been generated")
    return json.loads(path.read_text())


def test_the_replay_covers_all_seventy_two_runs(replay):
    assert len(replay["runs"]) == 72


def test_no_run_is_stopped_on_a_tree_equal_to_its_start(replay):
    for summary in replay["per_k"].values():
        assert summary["triggered_on_a_tree_equal_to_initial"] == 0


def test_no_k_truncates_observed_progress(replay):
    for summary in replay["per_k"].values():
        assert summary["would_truncate_observed_progress"] == 0


def test_every_runaway_is_still_caught(replay):
    for summary in replay["per_k"].values():
        assert summary["timeout_runs_caught"] == summary["timeout_runs_total"]


def test_the_reverted_run_is_ineligible_at_every_k(replay):
    for outcome in replay["focal_runs"]["11-IP1-r1"].values():
        assert outcome["triggered"] is False
        assert outcome["became_eligible"] is False


def test_the_repeated_check_loop_is_caught_at_every_k(replay):
    for outcome in replay["focal_runs"]["23-IP1-r2"].values():
        assert outcome["triggered"] is True


def test_unreplayable_mutations_are_reported_not_hidden(replay):
    reconstruction = replay["reconstruction"]
    assert reconstruction["runs_fully_reconstructable"] + len(
        reconstruction["runs_with_unreplayable_mutations"]) == reconstruction["of_runs"]
