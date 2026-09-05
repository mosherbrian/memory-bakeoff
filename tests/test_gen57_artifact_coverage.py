"""Gen57: the coverage diagnostics, and the screen they failed."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import artifact_coverage as A

RESULTS = ROOT / "results" / "pi_artifact_coverage_gen57"


# --- the contract -------------------------------------------------------------

def test_the_contract_names_both_diagnostics_and_forbids_correctness_claims():
    contract = A.contract()
    assert contract["contract_version"] == "artifact-coverage-diagnostics-v1"
    assert set(contract["diagnostics"]) == {"changed-line-execution-v1",
                                            "change-reversion-sensitivity-v1"}
    line = contract["diagnostics"]["changed-line-execution-v1"]
    assert "proof of correctness" in line["explicitly_not"]
    reversion = contract["diagnostics"]["change-reversion-sensitivity-v1"]
    assert any("semantic sufficiency" in claim for claim in reversion["explicitly_not"])
    assert contract["hidden_verifier_is_never_an_input"] is True


def test_requirement_traceability_is_recorded_as_unavailable_not_as_a_result():
    trace = A.contract()["requirement_traceability"]
    assert trace["instantiated"] is False
    assert "structurally unavailable" in trace["status"]


def test_the_traced_runner_puts_the_tree_on_the_path():
    """Without this the project does not import and every line looks unexecuted."""
    assert "sys.path.insert(0, os.getcwd())" in A.TRACE_RUNNER


def test_executable_lines_ignore_comments_and_blanks(tmp_path):
    source = tmp_path / "m.py"
    source.write_text("# a comment\n\nx = 1\n\n\ndef f():\n    return x\n")
    lines = A.executable_lines(source)
    assert 1 not in lines and 2 not in lines
    assert 3 in lines and 7 in lines


def test_production_paths_exclude_tests_and_build_output(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "m.py").write_text("x = 1\n")
    (tmp_path / "pkg" / "__pycache__").mkdir()
    (tmp_path / "pkg" / "__pycache__" / "m.pyc").write_bytes(b"\x00")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_m.py").write_text("def test(): pass\n")
    found = {str(p.relative_to(tmp_path)) for p in A.production_paths(tmp_path)}
    assert found == {"pkg/m.py"}


# --- the synthetic preflight --------------------------------------------------

@pytest.fixture(scope="module")
def preflight():
    path = RESULTS / "synthetic_preflight.json"
    if not path.exists():
        pytest.skip("Gen57 preflight has not been generated")
    return json.loads(path.read_text())


def test_every_synthetic_property_passed(preflight):
    assert preflight["passed"] is True
    assert all(preflight["checks"].values())


def test_the_probes_separate_touching_code_from_constraining_it(preflight):
    """Executed-but-unasserted must survive reversion; asserted must be killed."""
    unasserted = preflight["fixtures"]["executed_but_never_asserted"]
    asserted = preflight["fixtures"]["executed_and_asserted"]
    assert unasserted["line"]["all_changed_executable_lines_hit"] is True
    assert unasserted["reversion"]["any_survived_reversion"] is True
    assert asserted["line"]["all_changed_executable_lines_hit"] is True
    assert asserted["reversion"]["killed"] >= 1


def test_probe_isolation_never_disturbs_the_reconstruction(preflight):
    for fixture in preflight["fixtures"].values():
        assert fixture["reversion"]["final_digest_unchanged_after_probes"] is True


# --- the audit ----------------------------------------------------------------

@pytest.fixture(scope="module")
def audit():
    path = RESULTS / "run_audit_72.json"
    if not path.exists():
        pytest.skip("Gen57 audit has not been generated")
    return json.loads(path.read_text())


def test_all_seventy_two_runs_are_audited(audit):
    assert len(audit["runs"]) == 72
    assert {r["generation"] for r in audit["runs"]} == {49, 52, 55}


def test_unreconstructable_runs_stay_unknown(audit):
    for row in audit["runs"]:
        if not row["reconstructable"]:
            assert row["changed_line_execution"]["category"] == "reconstruction_unknown"
            assert row["change_reversion_sensitivity"]["category"] == "reconstruction_unknown"


def test_runs_without_production_change_are_not_scored(audit):
    for row in audit["runs"]:
        block = row["changed_line_execution"]
        if block.get("category") == "no_production_change":
            assert "hit_fraction" not in block


def test_neither_diagnostic_meets_the_frozen_screen(audit):
    """The generation's finding: sensitive, but nowhere near specific enough."""
    for name, screen in audit["screening"].items():
        assert screen["meets_frozen_screen"] is False, name
        assert screen["coverage_gap_rate"] >= 0.5, f"{name} should still be sensitive"
        assert screen["hidden_correct_rate"] > 0.25, f"{name} fails on specificity"


def test_the_screen_thresholds_were_not_moved(audit):
    thresholds = audit["contract"]["frozen_screening_thresholds"]
    assert "50%" in thresholds["flags_at_least"]
    assert "25%" in thresholds["flags_at_most"]


# --- sentinels ----------------------------------------------------------------

@pytest.fixture(scope="module")
def sentinels():
    path = RESULTS / "sentinels.json"
    if not path.exists():
        pytest.skip("Gen57 sentinels have not been generated")
    return json.loads(path.read_text())


def test_all_six_sentinels_present_without_substitution(sentinels):
    assert {s["sentinel"] for s in sentinels} == {
        "gen49-IP1-r1-C", "gen49-IP1-r3-D", "gen55-IP1-r1-F", "gen55-IP1-r2-F",
        "gen49-IP1-r1-D", "gen48-IP4-partial-fix-fixture-diagnostic"}


def test_the_known_false_assurance_is_clean_under_both_probes(sentinels):
    """The result that sinks the whole approach: wrong run, no signal."""
    row = next(s for s in sentinels if s["sentinel"] == "gen49-IP1-r1-C")
    assert row["hidden_verifier_passed"] is False
    assert row["all_changed_lines_hit"] is True
    assert row["any_survived_reversion"] is False


def test_the_successful_comparator_is_flagged_by_both_probes(sentinels):
    """And its mirror image: correct run, both signals fire."""
    row = next(s for s in sentinels if s["sentinel"] == "gen49-IP1-r1-D")
    assert row["hidden_verifier_passed"] is True
    assert row["all_changed_lines_hit"] is False
    assert row["any_survived_reversion"] is True


def test_the_ip4_sentinel_is_reported_not_fabricated(sentinels):
    row = next(s for s in sentinels if s["sentinel"].startswith("gen48-IP4"))
    assert row["partial_implementation_reconstructed"] is False
    assert "note" in row
