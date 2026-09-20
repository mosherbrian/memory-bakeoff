#!/usr/bin/env python3
"""Alice second-seat check of `check_identifier_lifecycle.py` (Corvid, guard 17).

Independent of the guard's own `--self-test`: this drives the real
`load_index`/`scan` path on synthetic fixtures and the live team/ tree and adds
a detector-power probe for the `split` cue, which collides with the corpus's
benchmark-split vocabulary.

Read-only. Writes only under a temp dir; prints counts, never doc bodies.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
GUARD = DSH3 / "scripts" / "check_identifier_lifecycle.py"
INDEX = Path("/var/home/bmosher/memory-bake-off/team/IDENTIFIER-LIFECYCLE.txt")
TEAM = Path("/var/home/bmosher/memory-bake-off/team")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    g = load(GUARD, "lifecycle")
    out = {
        "hashes": {"guard": sha(GUARD), "index": sha(INDEX)},
        "boundary": {},
        "census": {},
    }

    # Live census (team/ only; repo root has 0 tracked ids today).
    sup, wd, logs, skips, pre = g.load_index(INDEX)
    cites, findings, unreadable = g.scan(TEAM, sup, wd, logs, skips, INDEX.resolve())
    out["census"] = {
        "tracked_ids": len(sup) + len(wd),
        "citations": len(cites),
        "uncued": sum(1 for c in cites if not c["cued"]),
        "unreadable_or_findings": len(findings) + len(unreadable),
        "logs_declared": sorted(logs),
    }

    # Detector-power probe: same stale citation with and without a nearby
    # benchmark "split" mention (the corpus's dominant use of the word).
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        idx = root / "INDEX.txt"
        idx.write_text("superseded: L-HS-02 -> L-HS-02a, L-HS-02b\n")
        (root / "PLAIN.md").write_text(
            "## Results\n"
            "Something else entirely about the run.\n"
            "\n"
            "The class for L-HS-02 is contradicted.\n")
        (root / "NEAR_SPLIT.md").write_text(
            "## Results\n"
            "LongMemEval (split unspecified) 89.20 / PersonaMem v2 40.58\n"
            "HaluMem 80.91\n"
            "The class for L-HS-02 is contradicted.\n")
        sup2, wd2, logs2, skips2, _ = g.load_index(idx)
        for name in ("PLAIN.md", "NEAR_SPLIT.md"):
            c, _, _ = g.scan(root, sup2, wd2, logs2, skips2, idx.resolve())
            row = [x for x in c if x["file"] == name][0]
            out["boundary"][name] = {"cued": row["cued"], "detected_as_defect": not row["cued"]}
        # The only difference between the files is the "split unspecified" line.
        out["boundary"]["split_cue_collision"] = (
            out["boundary"]["PLAIN.md"]["detected_as_defect"]
            and not out["boundary"]["NEAR_SPLIT.md"]["detected_as_defect"])

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
