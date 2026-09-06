"""Gen120: the raw response bytes must be manifest-bound, and the marker must be
derived from an observation rather than authored.

Sol found the hole at the Gen119 freeze: `reader_raw.jsonl` was written with a
bare `write_text`, its hash stored in `raw_seal.json`, and never registered in
`MANIFEST.json`. `EV.verify` walks the manifest and nothing else, so the single
most important file in an experimental run - the verbatim reader responses -
could be edited afterwards and verification would still report success. A hash
in a seal is not manifest-binding.

The second hole was next to it: the runner passed `manifest_ok=True` into the
marker gate, so "the evidence is intact" was an assertion by the author of the
run rather than a measurement of it.

These tests exercise the real write/verify/marker path. A test that only checks
a helper's return value would have passed against the defective code.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV  # noqa: E402

RUNNER = ROOT / "scripts/run_reader_v6.py"
REQUIRED = ("preflight.json", "execution_contract.json", "reader_raw.jsonl",
            "raw_seal.json", "graded_rows.json", "control_gates.json",
            "estimands.json")


def _head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def _run_like_evidence(d: Path) -> None:
    """Everything a real run writes before its marker, by the real helpers."""
    for name in ("preflight.json", "execution_contract.json", "graded_rows.json",
                 "control_gates.json", "estimands.json"):
        EV.write_evidence(d, name, {"stub": name})
    raw = '{"case_id": "c1", "text": "current"}\n'
    EV.write_raw(d, "reader_raw.jsonl", raw)
    EV.write_evidence(d, "raw_seal.json",
                      {"file": "reader_raw.jsonl", "sha256": EV.digest(raw),
                       "sealed_before_parse": True})


# ------------------------------------------------------------------ F1 witnesses
def test_raw_jsonl_is_listed_in_the_manifest(tmp_path):
    _run_like_evidence(tmp_path)
    manifest = json.loads((tmp_path / EV.MANIFEST).read_text())
    assert "reader_raw.jsonl" in manifest["artifacts"], (
        "the raw responses are not manifest-bound; EV.verify would never look at "
        "them, which is the Gen119 defect")
    assert EV.verify(tmp_path)["verified"] is True


def test_changing_one_raw_byte_fails_verification(tmp_path):
    _run_like_evidence(tmp_path)
    raw = tmp_path / "reader_raw.jsonl"
    body = raw.read_text()
    raw.write_text(body.replace("current", "currenT"))   # one byte
    result = EV.verify(tmp_path)
    assert result["verified"] is False
    assert "reader_raw.jsonl" in result["mismatched"]


def test_deleting_raw_jsonl_fails_verification(tmp_path):
    _run_like_evidence(tmp_path)
    (tmp_path / "reader_raw.jsonl").unlink()
    result = EV.verify(tmp_path)
    assert result["verified"] is False
    assert "reader_raw.jsonl" in result["missing"]


def test_a_seal_that_disagrees_with_the_bytes_is_detectable(tmp_path):
    """The seal, the manifest and the disk must all agree - three sources.

    Comparing only two is how a hash in a seal came to be mistaken for binding.
    """
    _run_like_evidence(tmp_path)
    seal = json.loads((tmp_path / "raw_seal.json").read_text())
    disk = EV.digest((tmp_path / "reader_raw.jsonl").read_text())
    entry = json.loads((tmp_path / EV.MANIFEST).read_text())["artifacts"]["reader_raw.jsonl"]
    assert seal["sha256"] == entry["sha256"] == disk

    lying = dict(seal, sha256="0" * 64)
    (tmp_path / "raw_seal.json").write_text(json.dumps(lying))
    reread = json.loads((tmp_path / "raw_seal.json").read_text())
    assert reread["sha256"] != entry["sha256"], "a lying seal must be visible"
    assert EV.verify(tmp_path)["verified"] is False, (
        "rewriting the seal must also break the seal file's own manifest entry")


def test_raw_capture_refuses_to_overwrite(tmp_path):
    _run_like_evidence(tmp_path)
    with pytest.raises(FileExistsError):
        EV.write_raw(tmp_path, "reader_raw.jsonl", "different bytes")


def test_the_manifest_digest_comes_from_disk_not_from_the_argument(tmp_path):
    """A manifest entry may never describe bytes that are not the ones on disk."""
    EV.write_raw(tmp_path, "raw.jsonl", "abc\n")
    entry = json.loads((tmp_path / EV.MANIFEST).read_text())["artifacts"]["raw.jsonl"]
    assert entry["sha256"] == EV.digest((tmp_path / "raw.jsonl").read_text())


# ------------------------------------------------------------------ F2 witnesses
def test_closure_reports_a_complete_required_set(tmp_path):
    _run_like_evidence(tmp_path)
    assert EV.verify_closed(tmp_path, REQUIRED)["closed"] is True


def test_an_incomplete_pre_marker_set_denies_closure(tmp_path):
    _run_like_evidence(tmp_path)
    (tmp_path / "estimands.json").unlink()
    closure = EV.verify_closed(tmp_path, REQUIRED)
    assert closure["closed"] is False
    assert "estimands.json" in closure["missing"]


def test_an_unmanifested_artefact_denies_closure(tmp_path):
    """A file the manifest never listed is exactly the F1 shape."""
    for name in REQUIRED:
        if name != "reader_raw.jsonl":
            EV.write_evidence(tmp_path, name, {"stub": name})
    (tmp_path / "reader_raw.jsonl").write_text("smuggled\n")   # bare write, no record
    closure = EV.verify_closed(tmp_path, REQUIRED)
    assert closure["closed"] is False
    assert "reader_raw.jsonl" in closure["missing_required"]


def test_an_unexpected_artefact_denies_closure(tmp_path):
    _run_like_evidence(tmp_path)
    EV.write_evidence(tmp_path, "surprise.json", {"not": "required"})
    closure = EV.verify_closed(tmp_path, REQUIRED)
    assert closure["closed"] is False
    assert "surprise.json" in closure["unexpected"]


def test_the_marker_gate_is_never_handed_an_authored_true():
    source = RUNNER.read_text()
    assert "manifest_ok=True" not in source, (
        "the strongest claim in the apparatus - the evidence is intact - was "
        "authored as a literal instead of measured")
    assert "manifest_ok=closure[" in source, (
        "manifest_ok must come from an actual verification of the pre-marker set")


def test_the_marker_is_written_after_the_closure_check():
    """Order is the property. A marker inside its own required set verifies itself."""
    source = RUNNER.read_text()
    assert "REQUIRED_PRE_MARKER" in source
    checked = source.index("closure = EV.verify_closed(")
    written = source.index('EV.write_evidence(out, f"{marker[\'marker\']}.json"')
    assert checked < written, "closure must be observed before the marker is written"
    marker_names = ("RUN_EVIDENCE.json", "NON_EVIDENCE.json")
    required_block = source[source.index("REQUIRED_PRE_MARKER"):source.index("def main")]
    assert not any(n in required_block for n in marker_names), (
        "the marker may not be part of the set whose closure decides the marker")


def test_seal_agreement_is_a_three_way_check():
    source = RUNNER.read_text()
    assert "seal_ok = seal_agrees(out)" in source
    assert "seal_ok=bool(" not in source, "seal_ok must not be derived from truthiness"


# ------------------------------------------------------------------ F3 witnesses
def _refuses(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(RUNNER), *args], cwd=ROOT,
                          capture_output=True, text=True, timeout=300)


def test_a_stale_authorisation_generation_fails_with_zero_calls():
    r = _refuses(["--fire", "--generation", "121", "--authorised-by", "120",
                  "--source-commit", _head()])
    assert r.returncode != 0
    assert "generation" in (r.stderr + r.stdout).lower()
    assert not (ROOT / "results/gen121").exists(), "no attempt may be written"


def test_authorisation_must_be_more_than_a_non_empty_string():
    r = _refuses(["--fire", "--generation", "120", "--authorised-by", "yes please",
                  "--source-commit", _head()])
    assert r.returncode != 0, "any non-empty string used to be accepted"


def test_fire_without_a_source_commit_is_refused():
    r = _refuses(["--fire", "--generation", "120", "--authorised-by", "120"])
    assert r.returncode != 0
    assert "source-commit" in (r.stderr + r.stdout)


def test_head_differing_from_the_authorised_commit_fails_before_any_call():
    r = _refuses(["--generation", "120", "--source-commit", "0" * 40])
    assert "not the authorised source commit" in (r.stdout + r.stderr)
    assert "DRY RUN" in r.stdout and "No attempt written, no calls made" in r.stdout


def test_the_runner_carries_no_hardcoded_generation_or_commit():
    source = RUNNER.read_text()
    assert "GENERATION = 119" not in source
    assert "1c36483e835732364145d551d25a8144ce44bd09" not in source
    assert "--generation" in source and "--source-commit" in source


def test_the_output_path_follows_the_authorised_generation():
    source = RUNNER.read_text()
    assert "EV.next_attempt(ROOT, args.generation)" in source, (
        "evidence must be filed under the generation that actually ran it")


def test_the_contract_records_the_runtime_authorisation():
    source = RUNNER.read_text()
    for field in ("authorised_by_generation", "source_commit",
                  "supplied_at_runtime_not_hardcoded"):
        assert field in source


# ------------------------------------------------- prior evidence stays immutable
@pytest.mark.parametrize("attempt", [1, 2, 3, 4, 5])
def test_every_prior_gen118_attempt_still_verifies(attempt):
    d = ROOT / f"results/gen118/attempt{attempt}"
    if not d.exists():
        pytest.skip(f"attempt{attempt} does not exist")
    assert EV.verify(d)["verified"] is True, f"attempt{attempt} no longer verifies"


@pytest.mark.parametrize("attempt", [1, 2, 3, 4, 5])
def test_no_prior_attempt_contains_a_reader_result(attempt):
    d = ROOT / f"results/gen118/attempt{attempt}"
    if not d.exists():
        pytest.skip(f"attempt{attempt} does not exist")
    assert not (d / "reader_raw.jsonl").exists(), "a freeze may not hold reader output"
    assert (d / "NON_EVIDENCE.json").exists()
    assert json.loads((d / "NON_EVIDENCE.json").read_text())["reader_calls"] == 0
