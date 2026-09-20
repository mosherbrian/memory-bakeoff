#!/usr/bin/env python3
"""Alice second-seat of MUSE-IDEATION-06 (declared-list hygiene).

Answers the handoff question with live probes, not re-reads:
  U6  vacuous pass when the only non-exempt input is absent  -> demonstrate
  U7  inert `skip:`/`log:` entry                             -> demonstrate
  U8  undeclared shared copy                                  -> demonstrate
  U9  index misses a ledger-recorded supersession             -> marker census
  item 4 DUPLICATE (meta-guard covered-set)                   -> cite my applied check
  item 5c DUPLICATE (canary)                                  -> nuance only

Synthetic fixtures in temp dirs; read-only over the repo/team. Counts only.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DSH3 = Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3")
LIFE = DSH3 / "scripts" / "check_identifier_lifecycle.py"
XCOPY = DSH3 / "scripts" / "check_cross_copy_drift.py"
LEDGER = Path("/var/home/bmosher/memory-bake-off/team/CLAIMS-LEDGER.md")

STALE = "The class for L-HS-02 is contradicted.\n"
SUP = "superseded: L-HS-02 -> L-HS-02a, L-HS-02b\n"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(*cmd, cwd=None):
    p = subprocess.run([sys.executable, *map(str, cmd)], capture_output=True,
                       text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    out = {"hashes": {"lifecycle": sha(LIFE), "xcopy": sha(XCOPY)}, "checks": {},
           "findings": []}

    # ---- U6: vacuous pass ----
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "DOC.md").write_text(STALE)
        idx_skip = root / "IDX_SKIP.txt"
        idx_skip.write_text(SUP + "skip: DOC.md\n")
        idx_plain = root / "IDX.txt"
        idx_plain.write_text(SUP)
        rc_skip, txt_skip = run(LIFE, root, "--index", idx_skip)
        rc_plain, txt_plain = run(LIFE, root, "--index", idx_plain)
        out["checks"]["U6_vacuous"] = {
            "skip_rc": rc_skip,
            "skip_citations_uncued": "citations=0  uncued=0" in txt_skip,
            "plain_rc": rc_plain,
            "plain_flags": "UNCUED-ID" in txt_plain,
        }

    # ---- U7: inert declared entries ----
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "DOC.md").write_text(STALE)
        idx = root / "IDX.txt"
        idx.write_text(SUP + "skip: DOES-NOT-EXIST.md\nlog: ALSO-MISSING.md\n")
        rc, txt = run(LIFE, root, "--index", idx)
        out["checks"]["U7_inert"] = {
            "rc": rc,
            "flags_real_doc": "UNCUED-ID" in txt,
            "mentions_missing_entry": ("DOES-NOT-EXIST" in txt) or ("ALSO-MISSING" in txt),
        }

    # ---- U8: undeclared shared copy ----
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        a, b = base / "a", base / "b"
        a.mkdir(), b.mkdir()
        for t in (a, b):
            (t / "X.md").write_text("same\n")
        (a / "Y.md").write_text("a-only\n")
        (b / "Y.md").write_text("b-only\n")
        d1, d2 = base / "d1.txt", base / "d2.txt"
        d1.write_text("shared: X.md\n")
        d2.write_text("shared: X.md\nshared: Y.md\n")
        rc1, txt1 = run(XCOPY, "--trees", a, b, "--declaration", d1, "--fail")
        rc2, txt2 = run(XCOPY, "--trees", a, b, "--declaration", d2, "--fail")
        out["checks"]["U8_undeclared"] = {
            "only_X_declared_rc": rc1,
            "only_X_declared_findings": "findings: 0" in txt1,
            "Y_declared_rc": rc2,
            "Y_declared_flags": "cross-copy drift: Y.md" in txt2,
        }

    # ---- U9: ledger supersession-marker census ----
    lines = LEDGER.read_text().splitlines()
    markers = [(i + 1, ln.strip()) for i, ln in enumerate(lines)
               if re.search(r"supersed", ln, re.I)]
    # An identifier move is the all-caps ledger marker on a row that maps ids;
    # the other hits are class-label/prose/process supersessions.
    id_moves = [n for n, ln in markers if "SUPERSEDED" in ln]
    out["checks"]["U9_markers"] = {
        "marker_lines": len(markers),
        "id_move_lines": id_moves,
        "non_id_lines": [n for n, _ in markers if n not in id_moves],
        "id_move_preview": [ln[:110] for n, ln in markers if n in id_moves],
    }

    ch = out["checks"]
    if not (ch["U6_vacuous"]["skip_rc"] == 0 and ch["U6_vacuous"]["plain_rc"] == 1):
        out["findings"].append("U6 not reproduced")
    if ch["U7_inert"]["mentions_missing_entry"]:
        out["findings"].append("U7: inert entries are visible (already covered?)")
    if not (ch["U8_undeclared"]["only_X_declared_rc"] == 0
            and ch["U8_undeclared"]["Y_declared_rc"] == 1):
        out["findings"].append("U8 not reproduced")

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
