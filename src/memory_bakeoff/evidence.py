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
import os
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
    # Atomic. A crash midway through write_text leaves a truncated MANIFEST.json,
    # which is a durability hole in the machinery guarding "the one file that can
    # never be made again". Verification would fail loudly rather than silently,
    # so it failed safe - but a temp file plus os.replace costs nothing. Found by
    # glm-5.3 at Gen120 round 4.
    tmp = manifest_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    os.replace(tmp, manifest_path)
    return manifest


def write_raw(directory: Path, name: str, text: str) -> Path:
    """Write a verbatim artefact and manifest it from the bytes on disk.

    `write_evidence` serialises a payload; raw reader responses are captured
    verbatim and must not be re-serialised. Gen120 review found the runner wrote
    `reader_raw.jsonl` with a bare `write_text` and recorded its hash only in
    `raw_seal.json` - so `verify`, which walks the manifest, never checked the
    single most important evidence file in the run. A hash stored in a seal is
    not manifest-binding: the file could be edited afterwards and verification
    would still report success.

    The digest is taken from the file after writing, never from the argument, so
    a manifest entry cannot describe bytes that are not the ones on disk.
    """
    directory = Path(directory)
    path = directory / name
    if path.exists():
        raise FileExistsError(
            f"{path} already holds raw evidence and will not be overwritten; "
            "raw capture is the one artefact that can never be regenerated")
    directory.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    record(directory, name, path.read_text())
    return path


def journal_append(path: Path, record: "Any") -> None:
    """Append one record and force it to disk BEFORE returning.

    The reader run used to hold all sixty responses in memory and serialise them
    after the last call returned, which meant a crash at call 59 destroyed
    fifty-nine scientific outcomes that had already happened. Exposure is not
    reversible: once the model has answered, that answer exists whether or not we
    kept it.

    `flush` alone is not enough - it moves bytes to the OS, not to the platter.
    The `fsync` is the whole point of this function.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True, default=str) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def manifest_existing(directory: Path, name: str) -> dict[str, "Any"]:
    """Bind a file that already exists on disk into the manifest.

    `write_evidence` and `write_raw` both create the file they record, which an
    append-only journal cannot use: the journal is written a line at a time
    during the run and can only be sealed once the run is over. The digest is
    taken from the bytes on disk, so this cannot describe anything else.
    """
    directory = Path(directory)
    path = directory / name
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist; nothing to bind")
    return record(directory, name, path.read_text())


def verify_closed(directory: Path, required: "Any") -> dict[str, Any]:
    """`verify`, plus: is the manifest EXACTLY the required inventory?

    `verify` answers "is every listed artefact unchanged", which is silent about
    an artefact that was never listed - the F1 hole. Closure asks the other
    question: is the set of manifested artefacts exactly the set this run was
    required to produce? Missing and unexpected are reported separately because
    they mean different things; either one denies closure.

    This exists so an evidence gate can be derived from an observation instead of
    authored as a constant.
    """
    result = verify(directory)
    manifest_path = Path(directory) / MANIFEST
    manifested = (set(json.loads(manifest_path.read_text())["artifacts"])
                  if manifest_path.exists() else set())
    required = set(required)
    # Files present on disk that the manifest never listed. Computing `unexpected`
    # from manifest keys alone answers only "what did we claim", so a smuggled
    # file sitting beside the evidence was invisible - the same blind spot as F1
    # one level up. Found by glm-5.3 reviewing the F1 fix.
    on_disk = {f.name for f in Path(directory).iterdir()
               if f.is_file() and f.name != MANIFEST} if Path(directory).is_dir() else set()
    unmanifested = sorted(on_disk - manifested)
    missing_required = sorted(required - manifested)
    unexpected = sorted((manifested - required) | set(unmanifested))
    result.update({
        "required": sorted(required),
        "manifested": sorted(manifested),
        "on_disk": sorted(on_disk),
        "unmanifested": unmanifested,
        "missing_required": missing_required,
        "unexpected": unexpected,
        "closed": bool(result["verified"]) and not missing_required and not unexpected,
    })
    return result


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
