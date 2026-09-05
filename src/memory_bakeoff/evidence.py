"""`immutable-evidence-v1`: an experimental run may never overwrite an evidence set.

Gen105 re-ran corrected arms into the same fixed directory the original run had
used, and the pre-correction artefacts were gone. The aggregate comparison
survived only because the old numbers happened to be quoted in a committed
report; the cell-level evidence was not recoverable. That is a provenance loss
the harness made easy, so the harness is what changes.

Three rules, each enforced rather than described:

- **A path names the run that wrote it**, not the generation that first created
  the directory. `results/gen105/attempt1/perseus-on.json`, never
  `results/supersession_ablation_gen102/perseus-on.json` written by Gen105.
- **A write refuses an existing file.** Re-running is how evidence dies, so the
  second write raises and names the attempt directory to use instead.
- **Every artefact is hashed into a manifest** as it is written, so a later
  reader can tell whether a file is the one the report was computed from.

Artefacts already lost stay lost. Nothing here reconstructs them, and no
manifest is back-dated over a file whose provenance is unknown.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "immutable-evidence-v1"
MANIFEST = "MANIFEST.json"


def attempt_dir(root: Path, generation: int, attempt: int = 1) -> Path:
    """`results/gen<N>/attempt<M>` - the run that writes it names it."""
    if generation < 1 or attempt < 1:
        raise ValueError("generation and attempt are 1-based")
    return Path(root) / "results" / f"gen{generation}" / f"attempt{attempt}"


def next_attempt(root: Path, generation: int) -> Path:
    """The first attempt directory that does not exist yet."""
    attempt = 1
    while attempt_dir(root, generation, attempt).exists():
        attempt += 1
    return attempt_dir(root, generation, attempt)


def digest(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()


def write_evidence(directory: Path, name: str, payload: Any) -> Path:
    """Write one artefact, refusing to overwrite, and record its hash.

    The refusal is the whole point: a re-run that lands on an existing evidence
    set is the failure mode Gen105 hit, and it must stop rather than succeed.
    """
    directory = Path(directory)
    path = directory / name
    if path.exists():
        raise FileExistsError(
            f"{path} already holds an evidence set and will not be overwritten; "
            "write to the next attempt directory instead - re-running into a "
            "fixed path is how the Gen105 cell-level evidence was lost")
    directory.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, indent=1, sort_keys=True, default=str)
    path.write_text(body)
    record(directory, name, body)
    return path


def record(directory: Path, name: str, body: str) -> dict[str, Any]:
    """Append one entry to the directory's manifest."""
    directory = Path(directory)
    manifest_path = directory / MANIFEST
    manifest = (json.loads(manifest_path.read_text())
                if manifest_path.exists()
                else {"contract_version": CONTRACT_VERSION, "artifacts": {}})
    manifest["artifacts"][name] = {
        "sha256": digest(body),
        "bytes": len(body.encode()),
        "written_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    return manifest


def verify(directory: Path) -> dict[str, Any]:
    """Does each artefact still hash to what the manifest recorded?

    A report cites a manifest; this is how a later reader checks that the file
    on disk is the one the report was computed from.
    """
    directory = Path(directory)
    manifest_path = directory / MANIFEST
    if not manifest_path.exists():
        return {"manifest_present": False, "verified": None,
                "why": "no manifest; provenance of these files is unknown and "
                       "is not reconstructed"}
    manifest = json.loads(manifest_path.read_text())
    mismatched, missing = [], []
    for name, entry in sorted(manifest["artifacts"].items()):
        path = directory / name
        if not path.exists():
            missing.append(name)
        elif digest(path.read_text()) != entry["sha256"]:
            mismatched.append(name)
    return {"manifest_present": True, "artifacts": len(manifest["artifacts"]),
            "missing": missing, "mismatched": mismatched,
            "verified": not (missing or mismatched)}


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "rules": {
            "path_names_the_writing_run": "results/gen<N>/attempt<M>/<name>",
            "write_refuses_to_overwrite": "a second write to an existing "
                                          "evidence set raises",
            "every_artefact_hashed": f"{MANIFEST} carries sha256, size and time",
        },
        "why": "Gen105 re-ran corrected arms into the directory the original run "
               "had used; the pre-correction cell-level evidence was destroyed "
               "and the aggregate survived only because it was quoted in a "
               "committed report",
        "not_reconstructed": "artefacts already lost stay lost; no manifest is "
                             "back-dated over a file of unknown provenance",
    }
