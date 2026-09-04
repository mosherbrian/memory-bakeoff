"""Raw-evidence retention, `raw-evidence-retention-v1`.

Gen47 and Gen49 lost 48 runs of model output because the script that hashed the
raw streams deleted them, while its own manifest note said they were retained.
This module exists so that cannot happen again: archiving and hashing are
separate operations, hashing never touches the archived bytes, and a manifest
may not claim retention unless the bytes are still there **after** cleanup.

The rule the old code broke, stated plainly: a claim about a file is only worth
what a `stat` of that file says after everything else has run.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CONTRACT_VERSION = "raw-evidence-retention-v1"

RETENTION_POLICIES = ("archive_and_retain", "temporary_capture_only")


class RetentionError(RuntimeError):
    """A stream that was claimed to be retained is missing or has changed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class ArchivedStream:
    """One durable copy, described by what is actually on disk."""

    run_id: str
    name: str
    archive_path: Path
    sha256: str
    bytes: int

    def to_record(self, root: Path) -> dict[str, Any]:
        # Only the archive-relative path is published; host layout is not evidence.
        return {"run_id": self.run_id, "name": self.name,
                "archive_relative_path": str(self.archive_path.relative_to(root)),
                "sha256": self.sha256, "bytes": self.bytes,
                "retention_policy": "archive_and_retain"}


def archive_stream(source: Path, archive_root: Path, run_id: str, name: str = "stdout.txt") -> ArchivedStream:
    """Finalize a capture into the durable archive: copy, fsync, atomic rename.

    The source is left alone. Cleanup of the ephemeral capture is a separate,
    later decision, and it happens only once this copy is verified.
    """
    destination_dir = archive_root / run_id
    destination_dir.mkdir(parents=True, exist_ok=True)
    final = destination_dir / name
    staging = destination_dir / f".{name}.partial"
    with open(source, "rb") as src, open(staging, "wb") as dst:
        shutil.copyfileobj(src, dst)
        dst.flush()
        os.fsync(dst.fileno())
    os.replace(staging, final)
    return ArchivedStream(run_id=run_id, name=name, archive_path=final,
                          sha256=sha256_file(final), bytes=final.stat().st_size)


def build_manifest(streams: Iterable[ArchivedStream], archive_root: Path) -> dict[str, Any]:
    """Read-only. Hashing must never mutate what it measures."""
    records = {}
    for stream in streams:
        record = stream.to_record(archive_root)
        record["exists_when_manifest_written"] = stream.archive_path.exists()
        records[f"{stream.run_id}/{stream.name}"] = record
    return {"contract_version": CONTRACT_VERSION, "streams": records,
            "retention_verified": False,
            "note": ("retention_verified stays false until verify_retention has re-read every "
                     "archived file after cleanup")}


def cleanup_capture(paths: Iterable[Path], manifest: dict[str, Any], archive_root: Path) -> dict[str, Any]:
    """Remove ephemeral captures only, and only if the archive already holds them.

    A capture whose archived copy is missing or mismatched is kept, and the
    generation fails, rather than being tidied away.
    """
    removed, kept = [], []
    for path in paths:
        matching = [r for r in manifest["streams"].values()
                    if (archive_root / r["archive_relative_path"]).exists()
                    and (archive_root / r["archive_relative_path"]).stat().st_size == path.stat().st_size]
        if matching and path.exists():
            path.unlink()
            removed.append(path.name)
        else:
            kept.append(path.name)
    return {"removed_capture_files": removed, "kept_because_unverified": kept}


def verify_retention(manifest: dict[str, Any], archive_root: Path) -> dict[str, Any]:
    """Re-read every claimed stream. This is the check the old code never had."""
    results, failures = {}, []
    for key, record in manifest["streams"].items():
        path = archive_root / record["archive_relative_path"]
        if not path.exists():
            results[key] = {"exists_after_cleanup": False, "reason": "missing"}
            failures.append(key)
            continue
        size = path.stat().st_size
        digest = sha256_file(path)
        ok = size == record["bytes"] and digest == record["sha256"]
        results[key] = {"exists_after_cleanup": True, "size_matches": size == record["bytes"],
                        "sha256_matches": digest == record["sha256"]}
        if not ok:
            failures.append(key)
    manifest["per_stream_verification"] = results
    manifest["retention_verified"] = not failures
    manifest["failures"] = failures
    return manifest


def assert_retained(manifest: dict[str, Any], archive_root: Path) -> None:
    """Fail closed. A generation that cannot prove retention is not complete."""
    verified = verify_retention(manifest, archive_root)
    if not verified["retention_verified"]:
        raise RetentionError(f"raw evidence not retained: {verified['failures']}")


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "retention_policies": list(RETENTION_POLICIES),
        "properties": [
            "streams are archived outside ephemeral worktrees before any cleanup runs",
            "manifest generation is read-only with respect to archived bytes",
            "cleanup removes only ephemeral captures, and only once the archive holds them",
            "finalization is copy, fsync, atomic rename, then hash",
            "retention_verified is false until every archived file is re-read after cleanup",
            "a missing or changed stream is a hard generation-completion failure",
        ],
        "historical_note": ("the Gen47 and Gen49 manifests are left corrected as lost; this "
                            "contract is not applied retroactively to them"),
        "contract_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
