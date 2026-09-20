#!/usr/bin/env python3
"""Census canonical-ID mapping across frozen result dirs (Corvid, R&D pulse).

The row-11 survey recorded a Habitus gap: the frozen `run.json` predates the
`provenance`/`publishability` schema, so "unknown whether record IDs were native
or fuzzy-matched." This checks the *artifact-level* half of that question for
every frozen run: do the delivered evidence IDs map to canonical benchmark IDs
(`M###`), and are any empty/unmapped?

It cannot recover the resolution *method* (native vs fuzzy_subtext vs
canonical_marker) for pre-schema runs — that field does not exist in them. A
canonical ID proves mapping, not method.

Usage:
  python3 check_frozen_id_provenance.py <root> [<root>...]   # exit 1 on empty/non-canonical
  python3 check_frozen_id_provenance.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import tempfile
from pathlib import Path

CANON = re.compile(r"^M\d{3}$")


def parse_ids(cell: str) -> list:
    try:
        value = json.loads(cell.replace("'", '"'))
    except (ValueError, AttributeError):
        return []
    return value if isinstance(value, list) else []


def analyze(directory: Path) -> dict | None:
    path = directory / "detail.csv"
    if not path.is_file():
        return None
    try:
        rows = list(csv.reader(path.read_text(encoding="utf-8", errors="replace").splitlines()))
    except OSError:
        # An unreadable source is a finding, not "no data" (Assay/Alice 09:31-34).
        return {"dir": directory.name, "ids": 0, "canonical": 0, "empty": 0,
                "other": 0, "samples": [], "unreadable": True}
    if not rows or "retrieved_ids" not in rows[0]:
        return None
    i = rows[0].index("retrieved_ids")
    total = canon = empty = other = 0
    samples: list[str] = []
    for row in rows[1:]:
        if len(row) <= i:
            continue
        for v in parse_ids(row[i]):
            total += 1
            if v in (None, ""):
                empty += 1
            elif CANON.match(str(v)):
                canon += 1
            else:
                other += 1
                if len(samples) < 3:
                    samples.append(str(v))
    return {"dir": directory.name, "ids": total, "canonical": canon,
            "empty": empty, "other": other, "samples": samples}


def scan(root: Path) -> list[dict]:
    out = []
    for d in sorted((root / "results").iterdir()) if (root / "results").is_dir() else []:
        r = analyze(d)
        if r is not None:
            out.append(r)
    return out


def missing_prerequisites(root: Path) -> list[dict]:
    # A root with no scannable detail.csv is a mis-root, not a clean tree.
    results = root / "results"
    if not results.is_dir() or not any(p.is_file() for p in results.glob("*/detail.csv")):
        return [{"finding": "missing prerequisite: results/*/detail.csv "
                            "(no scannable sources)", "got": "absent", "want": "present"}]
    return []


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "results" / "run_a").mkdir(parents=True)
        (root / "results" / "run_a" / "detail.csv").write_text(
            "provider,retrieved_ids\n"
            "e,\"['M001', 'M002']\"\n"
            "e,[]\n")
        (root / "results" / "run_b").mkdir(parents=True)
        (root / "results" / "run_b" / "detail.csv").write_text(
            "provider,retrieved_ids\n"
            "e,\"['M003', 'X9']\"\n")
        r = {x["dir"]: x for x in scan(root)}
        assert r["run_a"] == {"dir": "run_a", "ids": 2, "canonical": 2,
                              "empty": 0, "other": 0, "samples": []}, r["run_a"]
        assert r["run_b"]["canonical"] == 1 and r["run_b"]["other"] == 1, r["run_b"]
    with tempfile.TemporaryDirectory() as td:
        assert missing_prerequisites(Path(td)), "empty root not reported"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = root / "results" / "run_u"
        d.mkdir(parents=True)
        p = d / "detail.csv"
        p.write_text("provider,retrieved_ids\ne,\"['M001']\"\n")
        os.chmod(p, 0)
        if not os.access(p, os.R_OK):
            assert any(r.get("unreadable") for r in scan(root)), scan(root)
        os.chmod(p, 0o644)
    print("self-test: PASS (counts canonical/other correctly; source-less root and "
          "unreadable source reported, not silently clean)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=["."])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    rc = 0
    for raw in args.roots:
        root = Path(raw).resolve()
        pre = missing_prerequisites(root)
        if pre:
            print(f"=== {root}\n    missing prerequisites: {len(pre)}")
            for f in pre:
                print(f"    {f['finding']}")
            rc = 1
            continue
        rows = scan(root)
        tot = sum(r["ids"] for r in rows)
        bad = [r for r in rows if r["empty"] or r["other"] or r.get("unreadable")]
        print(f"=== {root}\n    dirs={len(rows)}  ids={tot}  "
              f"canonical={sum(r['canonical'] for r in rows)}  "
              f"empty={sum(r['empty'] for r in rows)}  "
              f"non-canonical={sum(r['other'] for r in rows)}  flagged_dirs={len(bad)}")
        for r in bad:
            tag = " UNREADABLE" if r.get("unreadable") else ""
            print(f"    {r['dir']}: ids={r['ids']} canonical={r['canonical']} "
                  f"empty={r['empty']} other={r['other']} samples={r['samples']}{tag}")
        if bad:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
