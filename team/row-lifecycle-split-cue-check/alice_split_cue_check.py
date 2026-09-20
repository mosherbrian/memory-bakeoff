#!/usr/bin/env python3
"""Alice second-seat check of Assay's `split`-cue power fix (guard 17).

Independent of `lifecycle_split_cue_power_check.py`: drives canonical and
patched `load_index`/`scan` on the live team/ tree and on a fixture set that
adds the two cases Assay's check does not carry — a benchmark "split" on the
SAME line as the cited id, and a genuine split cue on a separate line with no
subject word.

Read-only; temp fixtures only; counts/booleans printed, no doc bodies.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
BASE = DSH3 / "scripts" / "check_identifier_lifecycle.py"
PATCHDIR = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2"
                "/scripts/verify-20260913-assay-lifecycle-split-cue")
PATCHED = PATCHDIR / "check_identifier_lifecycle.patched.py"
DIFF = PATCHDIR / "split-cue.diff"
POWER = PATCHDIR / "lifecycle_split_cue_power_check.py"
SEALED = PATCHDIR / "sealed-lifecycle-split-cue-20260913" / "result.json"
INDEX = Path("/var/home/bmosher/memory-bake-off/team/IDENTIFIER-LIFECYCLE.txt")
TEAM = Path("/var/home/bmosher/memory-bake-off/team")

NOTE_HASHES = {
    "diff": "9db3c09b",
    "patched": "037b5d43",
    "power": "71ccde3a",
    "sealed": "768adba6",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def census(mod, root, idx):
    sup, wd, logs, skips, _ = mod.load_index(idx)
    cites, findings, unreadable = mod.scan(root, sup, wd, logs, skips, idx.resolve())
    return {"citations": len(cites), "uncued": sum(1 for c in cites if not c["cued"])}


FIX = {
    "bench_split_separate_line": (
        "## Results\nLongMemEval (split unspecified) 89.20\nfiller\n"
        "The class for L-HS-02 is contradicted.\n"),
    "bench_split_SAME_line": (
        "The class for L-HS-02 (LongMemEval split unspecified) is contradicted.\n"),
    "genuine_split_collocated": "The L-HS-02 split is recorded in the ledger.\n",
    "genuine_split_separate_no_subject": (
        "The class for L-HS-02 is contradicted.\nSee above.\n"
        "The two claims were split apart on 2026-09-12.\n"),
}


def main() -> int:
    base = load(BASE, "base")
    patched = load(PATCHED, "patched")
    out = {"hashes": {}, "apply_check": {}, "self_test": {}, "census": {},
           "fixtures": {}, "findings": []}

    for k, p in (("diff", DIFF), ("patched", PATCHED), ("power", POWER),
                 ("sealed", SEALED)):
        h = sha(p)
        out["hashes"][k] = {"sha256": h, "matches_note": h.startswith(NOTE_HASHES[k])}

    cp = subprocess.run(["git", "apply", "--check", str(DIFF)], cwd=str(DSH3),
                        capture_output=True, text=True)
    out["apply_check"]["rc"] = cp.returncode

    for k, p in (("canonical", BASE), ("patched", PATCHED)):
        r = subprocess.run(["python3", str(p), "--self-test"],
                           capture_output=True, text=True)
        out["self_test"][k] = {"rc": r.returncode, "pass": r.returncode == 0}

    for k, mod in (("canonical", base), ("patched", patched)):
        out["census"][k] = census(mod, TEAM, INDEX)

    for name, body in FIX.items():
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            idx = root / "INDEX.txt"
            idx.write_text("superseded: L-HS-02 -> L-HS-02a, L-HS-02b\n")
            (root / "DOC.md").write_text(body)
            row = {}
            for k, mod in (("canonical", base), ("patched", patched)):
                sup, wd, logs, skips, _ = mod.load_index(idx)
                c, _, _ = mod.scan(root, sup, wd, logs, skips, idx.resolve())
                row[k] = {"cued": c[0]["cued"], "detected_as_defect": not c[0]["cued"]}
            out["fixtures"][name] = row

    f = out["fixtures"]
    if f["bench_split_SAME_line"]["patched"]["cued"]:
        out["findings"].append(
            "residual false negative: a benchmark 'split' on the citation line "
            "(same line as the tracked id) is still cued by the patched rule")
    if f["genuine_split_separate_no_subject"]["patched"]["detected_as_defect"]:
        out["findings"].append(
            "new false positive: a genuine split cue on a separate line with no "
            "subject word is now uncued")
    if out["census"]["canonical"] != out["census"]["patched"]:
        out["findings"].append("live census differs canonical vs patched")

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
