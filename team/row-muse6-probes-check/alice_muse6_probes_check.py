#!/usr/bin/env python3
"""Alice second-seat of the four Muse-batch-6 probes built into the guards:
U6 vacuous scan + U7 inert entry (guard 17 rev 7), U9 ledger<->index (rev 8),
and U8 declared-tree discovery (guard 16 rev 3).

Drives the real CLIs on synthetic fixtures; reads no document content.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
LIFE = DSH3 / "scripts" / "check_identifier_lifecycle.py"
XCOPY = DSH3 / "scripts" / "check_cross_copy_drift.py"
IMPL = DSH3.parent
SUP = "superseded: L-HS-02 -> L-HS-02a, L-HS-02b\n"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(script: Path, *args):
    p = subprocess.run([sys.executable, str(script), *map(str, args)],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    out = {"hashes": {"lifecycle": sha(LIFE), "xcopy": sha(XCOPY)},
           "checks": {}, "findings": []}

    # U6 vacuous + U7 inert, in one skipped-only root.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "DOC.md").write_text("L-HS-02a and L-HS-02b are current.\n")
        idx = root / "IDX.txt"
        idx.write_text(SUP + "skip: DOC.md\nlog: GONE.md\n")
        rc, txt = run(LIFE, root, "--index", idx)
        out["checks"]["U6_U7"] = {
            "rc": rc,
            "vacuous": "vacuous scan: 0 non-exempt" in txt,
            "inert_gone": "inert declared-list entry: GONE.md" in txt,
            "no_false_inert_for_existing_skip": "inert declared-list entry: DOC.md" not in txt,
            "advisory_still_fails_vacuous": None,
        }
        rc_adv, txt_adv = run(LIFE, root, "--index", idx, "--advisory")
        out["checks"]["U6_U7"]["advisory_still_fails_vacuous"] = (
            rc_adv == 1 and "vacuous scan" in txt_adv)

    # U9 ledger<->index.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "OK.md").write_text("L-HS-02a and L-HS-02b are current.\n")
        idx = root / "IDX.txt"
        idx.write_text(SUP)
        ledger = root / "LEDGER.md"
        ledger.write_text(
            "| Row | Claim | Source | Class |\n|---|---|---|---|\n"
            "| L-HS-02 | x | y | ~~old~~ **SUPERSEDED — see split: L-HS-02a** |\n"
            "| L-NEW-99 | x | y | **SUPERSEDED — see split: L-NEW-99a** |\n"
            "\nprose: this supersedes the `third-party` label\n")
        base = run(LIFE, root, "--index", idx)
        with_ledger = run(LIFE, root, "--index", idx, "--ledger", ledger)
        out["checks"]["U9"] = {
            "no_ledger_rc": base[0],
            "with_ledger_rc": with_ledger[0],
            "flags_new99": "ledger supersession missing from index: L-NEW-99" in with_ledger[1],
            "flags_third_party_label": "third-party" in with_ledger[1],
            "flags_indexed_id": "missing from index: L-HS-02\n" in with_ledger[1],
        }

    # U8 declared-tree discovery.
    with tempfile.TemporaryDirectory() as td:
        d1 = Path(td) / "d1.txt"
        d1.write_text("tree: implementer/repo-glm-dsh3\nshared: AGENTS.md\n")
        rc1, txt1 = run(XCOPY, "--declaration", d1)
        d2 = Path(td) / "d2.txt"
        d2.write_text("tree: implementer/repo-glm-dsh3\n"
                      "tree: implementer/repo-nope\nshared: AGENTS.md\n")
        rc2, txt2 = run(XCOPY, "--declaration", d2)
        rc3, txt3 = run(XCOPY, "--declaration", d1, "--trees",
                        IMPL / "repo", IMPL / "repo-glm-dsh2", IMPL / "repo-glm-dsh3")
        # latent: a declaration with shared: but no tree: silently runs no discovery
        d3 = Path(td) / "d3.txt"
        d3.write_text("shared: AGENTS.md\n")
        rc5, txt5 = run(XCOPY, "--declaration", d3)
        out["checks"]["U8"] = {
            "undeclared_rc": rc1,
            "undeclared_names": txt1.count("undeclared tree:"),
            "declared_gone": "declared tree missing:" in txt2,
            "explicit_trees_no_discovery": "undeclared tree:" not in txt3,
            "no_tree_lines_skips_discovery": ("undeclared tree:" not in txt5
                                              and "no declared tree" not in txt5),
            "no_tree_lines_rc": rc5,
        }
        # real declaration census
        rc4, txt4 = run(XCOPY)
        out["checks"]["U8_live"] = {
            "rc": rc4, "findings_line": [l.strip() for l in txt4.splitlines()
                                         if "findings:" in l]}

    c = out["checks"]
    if not (c["U6_U7"]["vacuous"] and c["U6_U7"]["inert_gone"]
            and c["U6_U7"]["no_false_inert_for_existing_skip"]
            and c["U6_U7"]["advisory_still_fails_vacuous"]):
        out["findings"].append("U6/U7 behaviour differs from the note")
    if not (c["U9"]["with_ledger_rc"] == 1 and c["U9"]["flags_new99"]
            and not c["U9"]["flags_third_party_label"]
            and not c["U9"]["flags_indexed_id"]):
        out["findings"].append("U9 behaviour differs from the note")
    if not (c["U8"]["undeclared_names"] >= 2 and c["U8"]["declared_gone"]
            and c["U8"]["explicit_trees_no_discovery"]):
        out["findings"].append("U8 behaviour differs from the note")

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
