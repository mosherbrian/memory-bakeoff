#!/usr/bin/env python3
"""Copy pinned model artifacts out of temp directories into durable storage.

Authorized by Gen33 AFTER scoring completed. It copies only: no evaluated path
changes, no model identity changes, nothing enters Git. Writes a SHA-256 manifest
so a future run can prove the durable copy is the artifact that was scored.
"""
from __future__ import annotations

import hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path

DEST = Path.home() / ".local/share/memory-bakeoff-pinned-models"
# Copy the WHOLE model directory: HF snapshots/ are symlinks into blobs/, so
# copying a snapshot alone yields dangling links and a zero-file "archive".
SOURCES = {
    "hindsight_e5_small_onnx": (Path("/private/tmp/hindsight-hf-cache/hub/models--intfloat--multilingual-e5-small"),
                                "614241f622f53c4eeff9890bdc4f31cfecc418b3"),
    "mem0_gte_large_onnx": (Path("/var/folders/bj/hcb5scdd2118xg6k8vrfkl780000gn/T/fastembed_cache/models--qdrant--gte-large-onnx"),
                            "770e825c74a004f165b78793f7c8fc4a95280878"),
    "mem0_bm25": (Path("/var/folders/bj/hcb5scdd2118xg6k8vrfkl780000gn/T/fastembed_cache/models--Qdrant--bm25"),
                  "22b8d2af71a76161e18dd432d2cee0eefa66e412"),
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "note": "durable copies of pinned model snapshots; evaluated paths unchanged, nothing in Git",
                "artifacts": {}}
    empty = []
    for name, (source, revision) in SOURCES.items():
        if not source.exists():
            manifest["artifacts"][name] = {"source": str(source), "status": "MISSING at archive time"}
            print(f"  {name}: MISSING {source}")
            continue
        target = DEST / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target, symlinks=False)  # resolve HF symlinks into real bytes
        files = sorted(p for p in target.rglob("*") if p.is_file())
        if not files:
            empty.append(name)
        entry = {"source": str(source), "snapshot_revision": revision, "status": "copied",
                 "file_count": len(files), "bytes": sum(p.stat().st_size for p in files),
                 "files": {str(p.relative_to(target)): digest(p) for p in files if p.stat().st_size < (400 << 20)}}
        manifest["artifacts"][name] = entry
        print(f"  {name}: {entry['file_count']} files, {entry['bytes'] / 1e6:.1f} MB -> {target}")
    if empty:
        raise SystemExit(f"archive produced zero files for {empty}; refusing to record it as done")
    (DEST / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote {DEST}/MANIFEST.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
