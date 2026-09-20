#!/usr/bin/env python3
"""Verify the MemBukkit shared-LSA routing == full dense scan parity claim.

Corvid, R&D pulse 2026-09-12. `RESULTS.md` row 81 and the survey claim that
MemBukkit's controlled bucket routing matches full dense scan. Row 81 was
repointed to `current_full_stress4505` / `current_full_core5`; this guard
asserts the two providers carry identical `hit@5` and `all_relevant@5` there.

Usage:
  python3 check_membukkit_parity.py [root]     # exit 1 on any mismatch
  python3 check_membukkit_parity.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import os
import tempfile
from pathlib import Path

FILES = ("results/current_full_stress4505/summary.csv",
         "results/current_full_core5/summary.csv")
PROVIDERS = ("membukkit", "dense_lsa")
METRICS = ("hit@5", "all_relevant@5")


def check_file(path: Path) -> list[dict]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8", errors="replace").splitlines()))
    by = {r["provider"]: r for r in rows if r.get("provider") in PROVIDERS}
    if set(by) != set(PROVIDERS):
        return [{"file": path.name, "what": "missing_provider", "have": sorted(by)}]
    out = []
    for m in METRICS:
        a, b = float(by["membukkit"][m]), float(by["dense_lsa"][m])
        if abs(a - b) > 1e-9:
            out.append({"file": path.name, "metric": m, "membukkit": a, "dense_lsa": b})
    return out


def scan(root: Path) -> list[dict]:
    # A missing/unreadable fixed artifact is a finding, not a skip: a half-applied
    # row-81 repoint (or a mis-rooted run) must not read green (Assay 2026-09-13
    # sweeps: absent/directory/unreadable).
    out = []
    for rel in FILES:
        p = root / rel
        if not p.is_file():
            out.append({"finding": f"missing prerequisite: {rel}",
                        "got": "absent", "want": "present"})
        elif not os.access(p, os.R_OK):
            out.append({"finding": f"unreadable prerequisite: {rel}",
                        "got": "unreadable", "want": "readable"})
        else:
            out.extend(check_file(p))
    return out


def _fixture(root: Path, mb_hit: float = 0.5833333, dl_hit: float = 0.5833333) -> None:
    for rel in FILES:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            "provider,hit@5,all_relevant@5\n"
            f"dense_lsa,{dl_hit},0.5416666666666666\n"
            f"membukkit,{mb_hit},0.5416666666666666\n")


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _fixture(root)
        assert scan(root) == [], scan(root)
        _fixture(root, mb_hit=0.4)
        found = scan(root)
        assert any(f.get("metric") == "hit@5" and f["membukkit"] == 0.4 for f in found), found
    # A missing fixed artifact must fail closed (partial repoint / mis-root).
    with tempfile.TemporaryDirectory() as td:
        empty = Path(td)
        assert len(scan(empty)) == 2, scan(empty)
        (empty / FILES[0]).parent.mkdir(parents=True)
        (empty / FILES[0]).write_text(
            "provider,hit@5,all_relevant@5\ndense_lsa,0.5,0.5\nmembukkit,0.5,0.5\n")
        partial = scan(empty)
        assert any("missing prerequisite" in f.get("finding", "") for f in partial), partial
    print("self-test: PASS (equal pair clean; divergence flagged; "
          "missing/partial fixed artifacts flagged, not skipped)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve()
    found = scan(root)
    print(f"=== {root}\n    MemBukkit/dense-LSA parity findings: {len(found)}")
    for f in found:
        print(f"    {f}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
