#!/usr/bin/env python3
"""Alice second-seat of the shipped identifier-lifecycle guard rev 3.

Confirms the case I reported (benchmark `split` on the citation's own line) is
closed, and probes the *remaining* self-satisfiable subject words (`row`, `id`,
`identifier`) that the rev-3 subject set still accepts. Also re-hashes the live
guard/index.

Read-only; temp fixtures only; counts/booleans printed, no document bodies.
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

REV3 = "087fc3f9"

# name -> (body, expected_cued)
FIX = {
    # my reported rev-2 residual: must now be DETECTED
    "A_same_line_id_only": (
        "The class for L-HS-02 (LongMemEval split unspecified) is contradicted.\n",
        False),
    # remaining self-satisfiable subjects on the citation line
    "B_same_line_row": (
        "The L-HS-02 row gives LongMemEval (split unspecified) as current.\n", True),
    "C_same_line_id_word": (
        "For id L-HS-02, LongMemEval (split unspecified) is the claim.\n", True),
    "D_same_line_identifier": (
        "The L-HS-02 identifier is paired with LongMemEval (split unspecified).\n", True),
    # genuine lifecycle cues
    "E_genuine_ledger": ("The L-HS-02 split is recorded in the ledger.\n", True),
    "F_genuine_strong": ("L-HS-02 was superseded on 2026-09-12.\n", True),
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    g = load(GUARD, "lifecycle")
    out = {"hashes": {"guard": sha(GUARD), "index": sha(INDEX),
                      "guard_is_rev3": sha(GUARD).startswith(REV3)},
           "fixtures": {}, "findings": []}

    sup, wd, logs, skips, _ = g.load_index(INDEX)
    cites, findings, unreadable = g.scan(TEAM, sup, wd, logs, skips, INDEX.resolve())
    out["census"] = {"tracked_ids": len(sup) + len(wd), "citations": len(cites),
                     "uncued": sum(1 for c in cites if not c["cued"]),
                     "skips": sorted(skips)}

    for name, (body, exp) in FIX.items():
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            idx = root / "INDEX.txt"
            idx.write_text("superseded: L-HS-02 -> L-HS-02a, L-HS-02b\n")
            (root / "DOC.md").write_text(body)
            s, w, lo, sk, _ = g.load_index(idx)
            c, _, _ = g.scan(root, s, w, lo, sk, idx.resolve())
            got = c[0]["cued"]
            out["fixtures"][name] = {"cued": got, "expected_cued": exp,
                                     "as_expected": got == exp}

    f = out["fixtures"]
    if not f["A_same_line_id_only"]["as_expected"]:
        out["findings"].append("reported rev-2 residual is NOT closed")
    residual = [n for n in ("B_same_line_row", "C_same_line_id_word",
                            "D_same_line_identifier")
                if f[n]["cued"]]
    if residual:
        out["findings"].append(
            "remaining false negative(s): same-line benchmark 'split' still cues "
            "when the citation context supplies a subject word: " + ", ".join(residual))

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
