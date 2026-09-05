"""Gen106: an experimental run may never overwrite an evidence set."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV


def test_path_names_the_run_that_writes_it(tmp_path):
    assert EV.attempt_dir(tmp_path, 105, 2) == tmp_path / "results/gen105/attempt2"


def test_next_attempt_skips_what_exists(tmp_path):
    EV.attempt_dir(tmp_path, 105, 1).mkdir(parents=True)
    EV.attempt_dir(tmp_path, 105, 2).mkdir(parents=True)
    assert EV.next_attempt(tmp_path, 105).name == "attempt3"


def test_a_write_refuses_an_existing_evidence_set(tmp_path):
    """The Gen105 failure, now impossible: the second write raises."""
    out = EV.next_attempt(tmp_path, 105)
    EV.write_evidence(out, "perseus-on.json", {"rows": [1]})
    with pytest.raises(FileExistsError, match="will not be overwritten"):
        EV.write_evidence(out, "perseus-on.json", {"rows": [2]})
    assert json.loads((out / "perseus-on.json").read_text()) == {"rows": [1]}


def test_every_artefact_is_hashed_into_a_manifest(tmp_path):
    out = EV.next_attempt(tmp_path, 106)
    EV.write_evidence(out, "a.json", {"x": 1})
    EV.write_evidence(out, "b.json", {"y": 2})
    manifest = json.loads((out / EV.MANIFEST).read_text())
    assert sorted(manifest["artifacts"]) == ["a.json", "b.json"]
    assert all(len(e["sha256"]) == 64 for e in manifest["artifacts"].values())


def test_verify_detects_a_tampered_artefact(tmp_path):
    out = EV.next_attempt(tmp_path, 106)
    EV.write_evidence(out, "a.json", {"x": 1})
    assert EV.verify(out)["verified"] is True
    (out / "a.json").write_text('{"x": 999}')
    result = EV.verify(out)
    assert result["verified"] is False and result["mismatched"] == ["a.json"]


def test_a_directory_with_no_manifest_is_unknown_not_verified(tmp_path):
    """Historical artefacts stay honestly unrecoverable; nothing is back-dated."""
    tmp_path.mkdir(exist_ok=True)
    result = EV.verify(tmp_path)
    assert result["manifest_present"] is False and result["verified"] is None


def test_no_runner_writes_to_a_fixed_results_directory():
    """The idiom that lost the Gen105 evidence, banned at the source."""
    root = Path(__file__).resolve().parents[1]
    offenders = []
    for path in sorted((root / "scripts").glob("run_gen1*.py")):
        text = path.read_text()
        if 'ROOT / "results"' in text and "evidence" not in text:
            offenders.append(path.name)
    assert offenders == [], f"fixed results path in {offenders}"
