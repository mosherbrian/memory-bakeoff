"""Gen56: a receipt may describe only what it checked, and breadth is not the fix."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import scoped_receipt as S

RESULTS = ROOT / "results" / "pi_artifact_authority_gen56"
BROAD = "python -m pytest tests/ -q"


# --- the descriptor -----------------------------------------------------------

def test_a_receipt_never_claims_task_correctness():
    made = S.receipt(tree_digest="abc", command=BROAD, cwd="/x", exit_status=0,
                     event_index=1, provenance="harness_validation_record",
                     project_wide_command=BROAD)
    assert made["establishes_task_correctness"] is False
    assert made["authority"].startswith("command ")
    lowered = json.dumps(made).lower()
    for forbidden in ("task correct", "requirements satisfied", "implementation complete"):
        assert forbidden not in lowered


def test_the_contract_forbids_semantic_claims_and_hidden_input():
    contract = S.contract()
    assert contract["hidden_verifier_is_never_an_input"] is True
    assert contract["changes_no_control_behaviour"] is True
    assert "task correct" in contract["forbidden_claims"]


def test_running_the_whole_test_directory_is_project_wide_whatever_the_flags():
    """The bug that would have called a full run a subset."""
    for command in ("python -m pytest tests/ -q",
                    "cd /w/run_14 && python -m pytest tests/ -v 2>&1",
                    "python -m pytest tests/"):
        assert S.classify_scope(command, BROAD)["scope_class"] == "project_wide_visible"


def test_a_cd_prefix_is_navigation_not_a_target():
    """The bug that scraped `/pilot-gen45-work/` into the target list."""
    scope = S.classify_scope("cd /var/home/x/pilot-gen45-work/run_14 && python -m pytest tests/ -v",
                             BROAD)
    assert scope["scope_class"] == "project_wide_visible"
    assert scope["targets"] == ["tests/"]


def test_narrower_invocations_are_classified_as_such():
    assert S.classify_scope("python -m pytest tests/test_gauge.py", BROAD)["scope_class"] \
        == "explicit_subset"
    assert S.classify_scope("python -m pytest tests/test_gauge.py::test_r", BROAD)["scope_class"] \
        == "single_test_or_selector"
    assert S.classify_scope("python -m pytest -k ratio", BROAD)["scope_class"] \
        == "single_test_or_selector"
    assert S.classify_scope("python run_checks.py", BROAD)["scope_class"] == "unknown_scope"
    assert S.classify_scope("", BROAD)["scope_class"] == "unknown_scope"


# --- the frozen broad command -------------------------------------------------

@pytest.fixture(scope="module")
def frozen():
    path = RESULTS / "broad_visible_commands.json"
    if not path.exists():
        pytest.skip("Gen56 broad command has not been frozen")
    return json.loads(path.read_text())


def test_the_broad_command_was_chosen_from_the_fixture_alone(frozen):
    assert sorted(frozen["tasks"]) == ["IP1", "IP2", "IP3", "IP4"]
    for task in frozen["tasks"].values():
        assert task["broadest_visible_validation"] == BROAD
        assert "hidden verifier" in task["selected_without_consulting"]
        assert "run outcomes" in task["selected_without_consulting"]


# --- the audit ----------------------------------------------------------------

@pytest.fixture(scope="module")
def audit():
    path = RESULTS / "run_audit_72.json"
    if not path.exists():
        pytest.skip("Gen56 audit has not been generated")
    return json.loads(path.read_text())


def test_all_seventy_two_runs_are_audited(audit):
    assert len(audit["runs"]) == 72
    assert {r["generation"] for r in audit["runs"]} == {49, 52, 55}


def test_unreconstructable_runs_are_carried_as_unknown_not_guessed(audit):
    for row in audit["runs"]:
        if not row["fully_reconstructable"]:
            assert row["primary_class"] == "reconstruction_or_instrumentation_unknown"


def test_the_hidden_verifier_never_entered_scope_classification(audit):
    """Scope depends on the command text only; nothing else may reach it."""
    for row in audit["runs"]:
        receipt = row["last_valid_visible_receipt"]
        if not receipt:
            continue
        expected = S.classify_scope(receipt["validation_command"],
                                    receipt["broadest_visible_validation_for_this_task"])
        assert receipt["scope_class"] == expected["scope_class"]


def test_breadth_would_have_contradicted_nothing(audit):
    """The generation's finding: 0 narrow-receipt contradictions, not zero by luck."""
    counts = audit["hidden_wrong_with_valid_receipt"]
    assert counts.get("narrow_receipt_broader_visible_contradicts", 0) == 0
    assert counts.get("visible_artifact_coverage_gap", 0) >= 1
    assert all(r["broad_visible_offline"]["passed"] for r in audit["runs"])


# --- sentinels and counterfactual ---------------------------------------------

@pytest.fixture(scope="module")
def sentinels():
    path = RESULTS / "sentinels.json"
    if not path.exists():
        pytest.skip("Gen56 sentinels have not been generated")
    return json.loads(path.read_text())


def test_all_six_frozen_sentinels_are_present_without_substitution(sentinels):
    names = {s["sentinel"] for s in sentinels}
    assert names == {"gen49-IP1-r1-C", "gen49-IP1-r1-D", "gen49-IP1-r3-D",
                     "gen55-IP1-r1-F", "gen55-IP1-r2-F",
                     "gen48-IP4-partial-fix-fixture-diagnostic"}


def test_no_live_sentinel_would_have_been_caught_by_a_broader_command(sentinels):
    for row in sentinels:
        if row.get("found"):
            assert row["would_a_broader_shipped_visible_check_have_contradicted_the_receipt"] is False


def test_ip4_shows_the_broadest_shipped_check_is_itself_insufficient(sentinels):
    ip4 = next(s for s in sentinels if s["sentinel"].startswith("gen48-IP4"))
    probe = ip4["recorded_probe_in_manifest"]
    assert probe["visible_check_passes"] is True
    assert probe["hidden_verifier_passes"] is False


@pytest.fixture(scope="module")
def counterfactual():
    path = RESULTS / "breadth_counterfactual.json"
    if not path.exists():
        pytest.skip("Gen56 counterfactual has not been generated")
    return json.loads(path.read_text())


def test_the_counterfactual_was_not_implemented(counterfactual):
    assert counterfactual["implemented_live"] is False


def test_requiring_breadth_would_block_nothing_and_charge_many(counterfactual):
    categories = counterfactual["categories"]
    assert categories.get("would_block_false_assurance", 0) == 0
    assert categories.get("would_add_validation_only", 0) >= 1
    assert counterfactual["deterministic_cost_only"]["extra_broad_check_runs"] >= 1
