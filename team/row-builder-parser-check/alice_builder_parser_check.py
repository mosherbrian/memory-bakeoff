#!/usr/bin/env python3
"""Alice second-seat of Assay's builder S6 receipt-parser fix (`92cf3a63…`).

Verifies the claimed cases against the real `load_record_sets` on canonical and
patched builders, and probes one header form the fix changes silently: a
colon-delimited stamp (`# S6 scan-after-write: <iso>`) is parsed by canonical
but falls back to mtime under the patch (the sliced literal prefix leaves the
colon as the "first token").

Synthetic receipts only; tempdir only; no tree modified.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path

REPO = Path("/var/home/bmosher/memory-bake-off/implementer/repo")
CANON = REPO / "scripts" / "experiment_20260911_trial" / "build_s4_packets.py"
PDIR = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2"
            "/scripts/verify-20260913-assay-builder-receipt-parser")
PATCHED = PDIR / "build_s4_packets.patched.py"
DIFF = PDIR / "builder-receipt-parser.diff"

TS = 1789236300.0        # 2026-09-12T18:05:00Z
MTIME = 1234567890       # distinctive mtime for fallback detection
LINES = {"key": "active"}

RECEIPTS = {
    "space":     "# S6 scan-after-write 2026-09-12T18:05:00Z\n",
    "colon":     "# S6 scan-after-write: 2026-09-12T18:05:00Z\n",
    "trailing":  "# S6 scan-after-write 2026-09-12T18:05:00Z (comment)\n",
    "short":     "# S6 scan-after-write\n",
    "bad":       "# S6 scan-after-write notadate\n",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def call(mod, path: Path):
    try:
        sets = mod.load_record_sets([str(path)])
        return {"ts": sets[0][0], "name": sets[0][1], "keys": sets[0][2]}
    except Exception as e:  # noqa: BLE001 - report the failure class
        return {"error": f"{type(e).__name__}: {e}"}


def main() -> int:
    canon = load(CANON, "canon_builder")
    patched = load(PATCHED, "patched_builder")
    out = {"hashes": {"diff": sha(DIFF), "patched": sha(PATCHED)}, "cases": {},
           "findings": []}

    for name, header in RECEIPTS.items():
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / f"{name}.txt"
            p.write_text(header + json.dumps(LINES) + "\n")
            os.utime(p, (MTIME, MTIME))
            out["cases"][name] = {"canonical": call(canon, p),
                                  "patched": call(patched, p)}

    c = out["cases"]
    if c["trailing"]["canonical"].get("error", "").find("ValueError") < 0:
        out["findings"].append("canonical trailing-text crash not reproduced")
    if c["trailing"]["patched"].get("ts") != TS:
        out["findings"].append("patched trailing-text did not parse the stamp")
    if c["space"]["patched"].get("ts") != TS or c["space"]["canonical"].get("ts") != TS:
        out["findings"].append("space form changed")
    if c["short"]["patched"].get("ts") != float(MTIME):
        out["findings"].append("patched short-header mtime fallback wrong")
    # the regression: canonical parses colon form; patched silently uses mtime
    if c["colon"]["canonical"].get("ts") == TS and c["colon"]["patched"].get("ts") == float(MTIME):
        out["findings"].append(
            "REGRESSION: colon-form stamp parsed by canonical but silently "
            "mtime-fallback under the patch")

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
