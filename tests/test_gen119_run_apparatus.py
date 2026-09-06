"""The v6 run apparatus, bound into the freeze BEFORE any run is authorised.

Gen118 bound five files and left the runner outside the contract. This file and
the runner it tests are now inside it, so the thing that will execute is frozen
with the thing that defines correctness.

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
from memory_bakeoff import reader_interference_v6 as V6

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_reader_v6.py"
SRC = RUNNER_PATH.read_text()

_spec = importlib.util.spec_from_file_location("_gen117_runner", RUNNER_PATH)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

def _head() -> str:
    """The commit under test. Gen120 made provenance a runtime input, so these
    gate tests must supply it; passing HEAD keeps them about the gate they name
    rather than about the new provenance check."""
    import subprocess
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def _canonical() -> "Path":
    """Read the canonical attempt rather than naming it.

    Hardcoding the path means pointing at a new freeze edits this file, which
    invalidates the freeze that was just made - the same circularity as pinning
    the contract hash in a file the contract hashes. The pointer is the single
    source of truth; the manifest guards the contents.
    """
    marker = ROOT / "results/gen118/CANONICAL_ATTEMPT.md"
    name = marker.read_text().split("`")[1]
    return ROOT / "results/gen118" / name


CANONICAL = _canonical()
SCHEDULE = json.loads((CANONICAL / "reader_interference_v6_schedule.json").read_text())
CASES = SCHEDULE["cases"]


# --- preflight ---------------------------------------------------------------
def test_every_preflight_gate_other_than_tree_cleanliness_passes():
    """Cleanliness is asserted separately: running the suite from a dirty tree is
    normal during development, but every scientific gate must be green now."""
    pf = R.preflight(_head())
    scientific = [p for p in pf["problems"] if "worktree not clean" not in p]
    assert scientific == [], scientific
    assert pf["cases"] == 60 and pf["cores"] == 12 and pf["unique_prompt_hashes"] == 60
    assert pf["canonical_verified"] and pf["lineage_green"]


def test_preflight_does_not_filter_untracked_files():
    """run_gen114_reader.py filtered '??' and shipped a runner absent from its
    own pinned commit. This check must see untracked files."""
    assert "startswith(\"??\")" not in SRC and "grep -v" not in SRC
    assert 'dirt = git("status", "--porcelain")' in SRC


def test_preflight_checks_every_required_gate():
    for needle in ("CANONICAL_ATTEMPT", "_expected_contract", "NON_EVIDENCE",
                   "unique_prompt_hashes", "prompt drift", "ontology is",
                   "success predicate", "lineage", "LEDGER.md"):
        assert needle in SRC, f"preflight does not gate on {needle}"


def test_prompt_drift_is_detected(monkeypatch):
    """If the live prompt bytes stop matching the frozen hashes, refuse."""
    monkeypatch.setattr(V6, "RULE", V6.RULE + " Prefer the first record.")
    pf = R.preflight(_head())
    assert not pf["passed"]
    assert any("drift" in p for p in pf["problems"]), pf["problems"]


def test_editing_a_frozen_source_blocks_the_run(tmp_path):
    """The whole point of 'no repair after exposure'.

    Before this gate existed, editing the value matcher and re-running produced a
    green preflight and a fresh attempt. The rule was a sentence in an
    instruction, not a property of the apparatus. Found by external review.

    This runs in a THROWAWAY WORKTREE. The first version mutated the real
    `src/memory_bakeoff/reader_interference_v6.py` and restored it in a `finally`,
    which left the shared checkout dirty for as long as the assertion took - and
    during the Gen120 review both rival reviewers, reading that same checkout,
    saw a tampered frozen source and reported it as a defect they could not
    attribute. A test may not make the tree lie to whoever else is reading it, and
    a `finally` is no protection against a crash between the two writes.
    """
    wt = tmp_path / "wt"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt), "HEAD"],
                   cwd=ROOT, capture_output=True, text=True, check=True)
    try:
        target = wt / "src/memory_bakeoff/reader_interference_v6.py"
        target.write_text(target.read_text() + "\n# a change after exposure\n")
        r = subprocess.run(
            [sys.executable, "scripts/run_reader_v6.py",
             "--generation", "120", "--source-commit", _head()],
            cwd=wt, capture_output=True, text=True,
            env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"}, timeout=600)
        out = r.stdout + r.stderr
        assert "FROZEN SOURCE CHANGED" in out, out[-2000:]
        assert "No attempt written, no calls made" in out
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=ROOT, capture_output=True)
    # Not "the tree is clean" - that would fail for anyone with unrelated work in
    # progress. The claim is narrower and exactly the one that was violated: THIS
    # test does not touch the frozen source in the primary checkout.
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "src/memory_bakeoff/reader_interference_v6.py"],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    assert not dirty, f"the frozen source was modified in the primary tree: {dirty}"


def test_preflight_pins_every_file_the_contract_names():
    import json as _json
    contract = _json.loads(
        (CANONICAL / "reader_interference_v6_contract.json").read_text())
    # Assert the SURFACES, not a count. Gen118's freeze bound five files and
    # omitted the future runner, the request projection, the capture and seal
    # path, the retry policy and the marker logic - the control plane's third
    # defect. A count would have passed that.
    bound = set(contract["source_sha256"])
    for required in ("src/memory_bakeoff/reader_interference_v6.py",
                     "src/memory_bakeoff/evidence.py",
                     "scripts/run_reader_v6.py",
                     "scripts/grade_gen118_v6.py",
                     "scripts/verify_gen118_contract.py",
                     "scripts/run_gen118_freeze.py",
                     "tests/test_gen118_reader_v6.py",
                     "tests/test_gen119_run_apparatus.py"):
        assert required in bound, f"{required} is not bound into the contract"
    assert "source_sha256" in RUNNER_PATH.read_text(), "preflight must read the pins"
    pf = R.preflight(_head())
    assert not any("FROZEN SOURCE" in p for p in pf["problems"]), pf["problems"]


def test_ontology_size_is_gated(monkeypatch):
    monkeypatch.setattr(V6, "ONTOLOGY", V6.ONTOLOGY + ("EXTRA_CLASS",))
    pf = R.preflight(_head())
    assert not pf["passed"]
    assert any("ontology" in p for p in pf["problems"])


# --- the contract is frozen before exposure ----------------------------------
def test_contract_binds_every_run_bearing_surface():
    c = R.freeze_contract(CASES, 120, _head(), '120')
    for key in ("request_body_sha256", "request_bodies_sha256_all", "runner_sha256",
                "grader_sha256", "v6_module_sha256", "capture", "reader"):
        assert key in c, key
    for key in ("model", "endpoint", "temperature", "seed_requested", "thinking",
                "timeout_s", "transport_retries"):
        assert key in c["reader"], key
    assert len(c["request_body_sha256"]) == 60


def test_seed_acceptance_is_not_authored():
    """Gen114 hardcoded seed_accepted: true. Never again."""
    c = R.freeze_contract(CASES, 120, _head(), '120')
    assert c["reader"]["seed_accepted"].startswith("NOT REPORTED")
    assert "seed_accepted\": True" not in SRC and "seed_accepted=True" not in SRC


def test_contract_moves_when_the_request_body_changes(monkeypatch):
    before = R.freeze_contract(CASES, 120, _head(), '120')["request_bodies_sha256_all"]
    monkeypatch.setattr(R, "TEMPERATURE", 0.7)
    assert R.freeze_contract(CASES, 120, _head(), '120')["request_bodies_sha256_all"] != before


def test_contract_moves_when_the_runner_changes():
    """The runner hashes its own bytes, so editing it moves the fingerprint."""
    c = R.freeze_contract(CASES, 120, _head(), '120')
    assert c["runner_sha256"] == R.sha(RUNNER_PATH.read_text())


def test_request_body_is_the_pinned_reader_at_temperature_zero():
    body = R.request_body(CASES[0])
    assert body["model"] == "qwen3.6-35b-vulkan-nothink"
    assert body["temperature"] == 0.0 and body["stream"] is False
    assert body["messages"][0]["content"] == V6.project_prompt(CASES[0])


# --- one call per case, sealing, linkage -------------------------------------
def test_exactly_sixty_cases_no_repetitions():
    assert len(CASES) == 60
    assert len({c["case_id"] for c in CASES}) == 60
    prompts = {V6.project_prompt(c) for c in CASES}
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
                     "answer_class": V6.CURRENT_ONLY, "citation_relation": "CONSISTENT"})
    gates = R.G116.control_gate(rows)
    assert gates["core01"]["interpretable"] is False
    assert gates["core01"]["status"] == "NOT_INTERPRETABLE_CONTROL_FAILURE"
    est = R.G116.estimands(rows, gates, unique_prompts=60)
    assert est["cores_interpretable"] == 11
    assert "core01" not in est["Q1_cores_selecting_current_in_both_orders"]
    assert any(r["core"] == "core01" for r in rows), "raw rows must be retained"


def test_independent_unit_is_the_core_not_the_cell():
    rows = [{"case_id": c["case_id"], "core": c["core"], "condition": c["condition"],
             "meets_success_state": True, "answer_class": V6.CURRENT_ONLY,
             "citation_relation": "CONSISTENT"} for c in CASES]
    est = R.G116.estimands(rows, R.G116.control_gate(rows), unique_prompts=60)
    assert est["independent_unit"] == "core"
    assert est["cells_are_not_observations"] is True
    assert est["no_binomial_ci_on_paired_cells"] is True


# --- retries may not shop for an answer --------------------------------------
def test_retries_are_transport_only():
    assert "scientific_response_may_never_be_replaced" in SRC
    assert R.TRANSPORT_RETRIES >= 0
    body = R.freeze_contract(CASES, 120, _head(), '120')["reader"]
    assert body["scientific_response_may_never_be_replaced"] is True


# --- immutability -------------------------------------------------------------
@pytest.mark.parametrize("path", [
    "results/gen116/attempt1", "results/gen116/attempt2",
    "results/gen116/attempt3", "results/gen116/attempt4",
    "results/gen117/attempt1",
    "results/gen118/attempt1", "results/gen118/attempt3",
])
def test_every_sealed_attempt_remains_verifiable(path):
    """Named explicitly rather than generated. A sed-rewritten range once
    asserted gen118 attempts 3 and 4, which do not exist."""
    assert EV.verify(ROOT / path)["verified"], path


def test_the_runner_consumes_the_canonical_pointer_and_writes_only_forward():
    """It reads the freeze through the pointer, and writes only under its own run.

    This used to assert `"results/gen116" in SRC`, on the reasoning that the
    runner reads from there. Gen120 removed that vestigial path - the runner
    resolves results/gen118/CANONICAL_ATTEMPT.md - so the assertion was pinning a
    defect in place. What actually matters is the direction of writes.
    """
    assert "results/gen118/CANONICAL_ATTEMPT.md" in SRC, (
        "the runner must resolve the canonical attempt through the pointer")
    assert "EV.next_attempt(ROOT, args.generation)" in SRC, (
        "evidence is written under the generation that ran it, never the freeze")
    for bad in ("write_evidence(CANONICAL", "write_raw(CANONICAL"):
        assert bad not in SRC, f"the runner must never write into the freeze: {bad}"


def test_dry_run_makes_no_calls_and_writes_no_attempt():
    before = {d.name for d in (ROOT / "results/gen119").iterdir()} if (ROOT / "results/gen119").exists() else set()
    r = subprocess.run([sys.executable, str(RUNNER_PATH), "--generation", "120",
                        "--source-commit", _head()], cwd=ROOT,
                       capture_output=True, text=True,
                       env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"})
    assert "DRY RUN" in r.stdout, r.stdout + r.stderr
    assert "zero calls made" in r.stdout or "no calls made" in r.stdout
    # Not "gen117 must not exist" - attempt1 is a real sealed run. A dry run must
    # not create a NEW attempt.
    after = {d.name for d in (ROOT / "results/gen119").iterdir()} if (ROOT / "results/gen119").exists() else set()
    assert after == before, f"a dry run created {after - before}"


def test_a_v6_run_refuses_without_explicit_authorisation():
    """Gen118 and Gen119 both forbid running. The runner must enforce that
    itself rather than relying on me remembering."""
    r = subprocess.run([sys.executable, str(RUNNER_PATH), "--fire", "--generation", "120"],
                       cwd=ROOT,
                       capture_output=True, text=True,
                       env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"})
    assert r.returncode != 0
    assert "REFUSING" in r.stdout + r.stderr
    assert "authorisation" in (r.stdout + r.stderr).lower()


def test_the_contract_binds_the_future_runner():
    """A contract that does not bind what will run is not a freeze."""
    import json as _json
    c = _json.loads((CANONICAL / "reader_interference_v6_contract.json").read_text())
    bound = set(c["source_sha256"])
    for required in ("scripts/run_reader_v6.py",
                     "src/memory_bakeoff/evidence.py",
                     "tests/test_gen119_run_apparatus.py"):
        assert required in bound, f"{required} is not bound into the contract"
