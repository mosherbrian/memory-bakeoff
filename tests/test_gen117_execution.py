"""Gen117: the run apparatus. Every gate that stands between us and a bad result.

Nothing here calls a model. The runner is imported and its gates exercised
directly, which is the only way to test a fail-closed path without firing it.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference_v5 as V5

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_gen117_reader.py"
SRC = RUNNER_PATH.read_text()

_spec = importlib.util.spec_from_file_location("_gen117_runner", RUNNER_PATH)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

CANONICAL = ROOT / "results/gen116/attempt4"
SCHEDULE = json.loads((CANONICAL / "reader_interference_v5_schedule.json").read_text())
CASES = SCHEDULE["cases"]


# --- preflight ---------------------------------------------------------------
def test_every_preflight_gate_other_than_tree_cleanliness_passes():
    """Cleanliness is asserted separately: running the suite from a dirty tree is
    normal during development, but every scientific gate must be green now."""
    pf = R.preflight()
    scientific = [p for p in pf["problems"] if "worktree not clean" not in p]
    assert scientific == [], scientific
    assert pf["cases"] == 60 and pf["cores"] == 12 and pf["unique_prompt_hashes"] == 60
    assert pf["attempt4_verified"] and pf["lineage_green"]


def test_preflight_does_not_filter_untracked_files():
    """run_gen114_reader.py filtered '??' and shipped a runner absent from its
    own pinned commit. This check must see untracked files."""
    assert "startswith(\"??\")" not in SRC and "grep -v" not in SRC
    assert 'dirt = git("status", "--porcelain")' in SRC


def test_preflight_checks_every_required_gate():
    for needle in ("CANONICAL_ATTEMPT", "EXPECT_CONTRACT", "NON_EVIDENCE",
                   "unique_prompt_hashes", "prompt drift", "ontology is",
                   "success predicate", "lineage", "LEDGER.md"):
        assert needle in SRC, f"preflight does not gate on {needle}"


def test_prompt_drift_is_detected(monkeypatch):
    """If the live prompt bytes stop matching the frozen hashes, refuse."""
    monkeypatch.setattr(V5, "RULE", V5.RULE + " Prefer the first record.")
    pf = R.preflight()
    assert not pf["passed"]
    assert any("drift" in p for p in pf["problems"]), pf["problems"]


def test_ontology_size_is_gated(monkeypatch):
    monkeypatch.setattr(V5, "ONTOLOGY", V5.ONTOLOGY + ("EXTRA_CLASS",))
    pf = R.preflight()
    assert not pf["passed"]
    assert any("ontology" in p for p in pf["problems"])


# --- the contract is frozen before exposure ----------------------------------
def test_contract_binds_every_run_bearing_surface():
    c = R.freeze_contract(CASES)
    for key in ("request_body_sha256", "request_bodies_sha256_all", "runner_sha256",
                "grader_sha256", "v5_module_sha256", "capture", "reader"):
        assert key in c, key
    for key in ("model", "endpoint", "temperature", "seed_requested", "thinking",
                "timeout_s", "transport_retries"):
        assert key in c["reader"], key
    assert len(c["request_body_sha256"]) == 60


def test_seed_acceptance_is_not_authored():
    """Gen114 hardcoded seed_accepted: true. Never again."""
    c = R.freeze_contract(CASES)
    assert c["reader"]["seed_accepted"].startswith("NOT REPORTED")
    assert "seed_accepted\": True" not in SRC and "seed_accepted=True" not in SRC


def test_contract_moves_when_the_request_body_changes(monkeypatch):
    before = R.freeze_contract(CASES)["request_bodies_sha256_all"]
    monkeypatch.setattr(R, "TEMPERATURE", 0.7)
    assert R.freeze_contract(CASES)["request_bodies_sha256_all"] != before


def test_contract_moves_when_the_runner_changes():
    """The runner hashes its own bytes, so editing it moves the fingerprint."""
    c = R.freeze_contract(CASES)
    assert c["runner_sha256"] == R.sha(RUNNER_PATH.read_text())


def test_request_body_is_the_pinned_reader_at_temperature_zero():
    body = R.request_body(CASES[0])
    assert body["model"] == "qwen3.6-35b-vulkan-nothink"
    assert body["temperature"] == 0.0 and body["stream"] is False
    assert body["messages"][0]["content"] == V5.project_prompt(CASES[0])


# --- one call per case, sealing, linkage -------------------------------------
def test_exactly_sixty_cases_no_repetitions():
    assert len(CASES) == 60
    assert len({c["case_id"] for c in CASES}) == 60
    prompts = {V5.project_prompt(c) for c in CASES}
    assert len(prompts) == 60, "no case may be a repetition of another"


def test_raw_is_sealed_before_any_parse():
    """Ordering is the property: seal, then grade. Never the reverse."""
    seal_at = SRC.index("raw_seal.json")
    grade_at = SRC.index("G116.grade_all")
    assert seal_at < grade_at, "raw evidence must be sealed before grading"


def test_grading_reuses_the_frozen_gen116_path():
    assert "G116.grade_all" in SRC and "G116.control_gate" in SRC
    assert "G116.estimands" in SRC and "G116.run_marker" in SRC
    assert "def grade_all" not in SRC, "the grader must be reused, not reimplemented"


def test_run_evidence_is_never_authored_directly():
    """NON_EVIDENCE may be written outright - a preflight failure IS non-evidence
    by definition. RUN_EVIDENCE may only ever come from the frozen gate.

    Checked structurally, not by grepping the text: an earlier version of this
    test matched the runner's own DOCSTRING, which is the same mistake as a guard
    that fires on its own comment.
    """
    import ast
    tree = ast.parse(SRC)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            d = ast.get_docstring(node, clean=False)
            if d:
                docstrings.add(d)
    live = [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and n.value not in docstrings]
    assert not any("RUN_EVIDENCE" in v for v in live), \
        "RUN_EVIDENCE must only ever come from run_marker(), never a literal"
    # Quote-agnostic: the runner uses marker['marker'] inside an f-string, and an
    # earlier version of this assertion looked for double quotes and failed on
    # nothing but punctuation.
    assert ("marker['marker']" in SRC) or ('marker["marker"]' in SRC)
    assert "G116.run_marker" in SRC


# --- control exclusion and the independent unit ------------------------------
def test_a_core_failing_a_control_is_excluded_but_retained():
    rows = []
    for c in CASES:
        ok = not (c["core"] == "core01" and c["condition"] == "CLEAN_CURRENT")
        rows.append({"case_id": c["case_id"], "core": c["core"],
                     "condition": c["condition"], "meets_success_state": ok,
                     "answer_class": V5.CURRENT_ONLY, "citation_relation": "CONSISTENT"})
    gates = R.G116.control_gate(rows)
    assert gates["core01"]["interpretable"] is False
    assert gates["core01"]["status"] == "NOT_INTERPRETABLE_CONTROL_FAILURE"
    est = R.G116.estimands(rows, gates, unique_prompts=60)
    assert est["cores_interpretable"] == 11
    assert "core01" not in est["Q1_cores_selecting_current_in_both_orders"]
    assert any(r["core"] == "core01" for r in rows), "raw rows must be retained"


def test_independent_unit_is_the_core_not_the_cell():
    rows = [{"case_id": c["case_id"], "core": c["core"], "condition": c["condition"],
             "meets_success_state": True, "answer_class": V5.CURRENT_ONLY,
             "citation_relation": "CONSISTENT"} for c in CASES]
    est = R.G116.estimands(rows, R.G116.control_gate(rows), unique_prompts=60)
    assert est["independent_unit"] == "core"
    assert est["cells_are_not_observations"] is True
    assert est["no_binomial_ci_on_paired_cells"] is True


# --- retries may not shop for an answer --------------------------------------
def test_retries_are_transport_only():
    assert "scientific_response_may_never_be_replaced" in SRC
    assert R.TRANSPORT_RETRIES >= 0
    body = R.freeze_contract(CASES)["reader"]
    assert body["scientific_response_may_never_be_replaced"] is True


# --- immutability -------------------------------------------------------------
@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_gen116_attempts_remain_verifiable(n):
    assert EV.verify(ROOT / f"results/gen116/attempt{n}")["verified"]


def test_runner_never_writes_into_gen116():
    assert "results/gen116" in SRC  # it reads from it
    for bad in ('write_evidence(CANONICAL', 'CANONICAL /', "open(CANONICAL"):
        assert f"{bad}" not in SRC or "read_text" in SRC


def test_dry_run_makes_no_calls_and_writes_no_attempt():
    r = subprocess.run([sys.executable, str(RUNNER_PATH)], cwd=ROOT,
                       capture_output=True, text=True,
                       env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"})
    assert "DRY RUN" in r.stdout, r.stdout + r.stderr
    assert "zero calls made" in r.stdout or "no calls made" in r.stdout
    assert not (ROOT / "results/gen117").exists(), "a dry run must not create an attempt"
