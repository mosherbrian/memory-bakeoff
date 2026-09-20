#!/usr/bin/env python3
"""Guard the Gen38 dynamic-conflict Hit@3 anchor against the frozen artifacts.

Corvid, R&D pulse 2026-09-12. The portfolio's anchor is
`perseus 0.434 · mem0 0.419 · bm25 0.226` on the Gen38 held-out 27-persona
**dynamic_conflict** slice, cited in `PORTFOLIO-CHARTER-draft.md:127` and
`ECOSYSTEM-MAP.md`. This re-derives it from the frozen artifacts and fails if a
number stops matching, if the derived and scientific files disagree, or if the
fraction no longer equals hits/denominator.

Usage:
  python3 check_gen38_anchor.py [root]     # exit 1 on any mismatch
  python3 check_gen38_anchor.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

ANCHOR = {"perseus": 0.434, "mem0": 0.419, "bm25": 0.226}
REL = "results/memconflict_gen38_full_release"


def slice_rate(block: dict) -> tuple[float, int, int]:
    dc = block["by_conflict_type"]["dynamic_conflict"]
    return dc["hit_at"]["3"]["rate"], dc["hit_at"]["3"]["hits"], dc["measured_questions"]


def check(root: Path) -> list[dict]:
    # Missing/unreadable fixed artifacts are a structured verdict, not a traceback
    # (Assay 2026-09-13 sweeps).
    pre = []
    for rel in (f"{REL}/heldout-27-derived.json", f"{REL}/scientific.json"):
        p = root / rel
        if not p.is_file():
            pre.append({"finding": f"missing prerequisite: {rel}",
                        "got": "absent", "want": "present"})
        elif not os.access(p, os.R_OK):
            pre.append({"finding": f"unreadable prerequisite: {rel}",
                        "got": "unreadable", "want": "readable"})
    if pre:
        return pre
    der = json.loads((root / REL / "heldout-27-derived.json").read_text())
    sci = json.loads((root / REL / "scientific.json").read_text())
    findings = []
    for eng, want in ANCHOR.items():
        rate, hits, denom = slice_rate(der[eng])
        sci_rate = sci["engines"][eng]["primary_heldout_27"]["by_conflict_type"][
            "dynamic_conflict"]["hit_at"]["3"]["rate"]
        if round(rate, 3) != want:
            findings.append({"engine": eng, "what": "anchor", "got": rate, "want": want})
        if abs(rate - sci_rate) > 1e-9:
            findings.append({"engine": eng, "what": "artifact_disagreement",
                             "got": rate, "want": sci_rate})
        if round(hits / denom, 3) != want:
            findings.append({"engine": eng, "what": "fraction", "got": hits / denom,
                             "want": want, "hits": hits, "denom": denom})
    return findings


def _fixture(root: Path, perseus_rate: float = 0.4341) -> None:
    (root / REL).mkdir(parents=True, exist_ok=True)

    def block(rate):
        return {"by_conflict_type": {"dynamic_conflict": {
            "hit_at": {"3": {"rate": rate, "hits": round(rate * 2631)}},
            "measured_questions": 2631}}}

    der = {e: block(r) for e, r in
           (("perseus", perseus_rate), ("mem0", 0.4192), ("bm25", 0.2258))}
    sci = {"engines": {e: {"primary_heldout_27": block(r)} for e, r in
                       (("perseus", perseus_rate), ("mem0", 0.4192), ("bm25", 0.2258))}}
    (root / REL / "heldout-27-derived.json").write_text(json.dumps(der))
    (root / REL / "scientific.json").write_text(json.dumps(sci))


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _fixture(root)
        assert check(root) == [], check(root)
        _fixture(root, perseus_rate=0.4000)
        found = check(root)
        assert any(f["engine"] == "perseus" and f["what"] == "anchor" for f in found), found
    with tempfile.TemporaryDirectory() as td:
        miss = check(Path(td))
        assert any("missing prerequisite" in f.get("finding", "") for f in miss), miss
    print("self-test: PASS (correct anchor clean; shifted anchor flagged; "
          "missing artifacts reported, not crashed)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve()
    found = check(root)
    print(f"=== {root}\n    Gen38 dynamic_conflict anchor findings: {len(found)}")
    for f in found:
        print(f"    {f}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
