#!/usr/bin/env python3
"""Check for query-referent provenance forks across frozen runs.

Corvid, R&D pulse 2026-09-12 (Muse batch3 ACCEPT 3.2, instantiated at the
query level). Two runs that report the same `query_id` must mean the same
thing: same `category`, same `relevant_ids`, same `prohibited_ids`. If the
referent changes between runs, the runs are not comparable and a score quoted
across them forks silently.

`detail.csv` carries `query_id`, `category`, `relevant_ids`, `prohibited_ids`
but not record text, so this checks query referents, not record-content
identity. It cannot prove two `M###` records hold the same text across corpora.

Usage:
  python3 check_query_fork.py [roots...]     # exit 1 on any fork
  python3 check_query_fork.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path


def parse_ids(cell: str) -> tuple:
    try:
        value = json.loads(cell.replace("'", '"'))
    except (ValueError, AttributeError):
        return ()
    return tuple(value) if isinstance(value, list) else ()


def scan(root: Path) -> tuple[dict[str, dict[tuple, list[str]]], list[dict]]:
    by_q: dict[str, dict[tuple, list[str]]] = defaultdict(dict)
    unreadable: list[dict] = []
    results = root / "results"
    if not results.is_dir():
        return by_q, unreadable
    for d in sorted(results.iterdir()):
        p = d / "detail.csv"
        if not p.is_file():
            continue
        try:
            rows = list(csv.reader(p.read_text(encoding="utf-8", errors="replace").splitlines()))
        except OSError:
            # An unreadable source is a finding, not "no data" (Assay/Alice 09:31-34).
            unreadable.append({"finding": f"unreadable prerequisite: {d.name}/detail.csv",
                               "got": "unreadable", "want": "readable"})
            continue
        if not rows or "query_id" not in rows[0]:
            continue
        header = rows[0]
        for row in rows[1:]:
            if len(row) < len(header):
                continue
            rec = dict(zip(header, row))
            qid = rec.get("query_id", "")
            key = (rec.get("category", ""), parse_ids(rec.get("relevant_ids", "[]")),
                   parse_ids(rec.get("prohibited_ids", "[]")))
            by_q[qid].setdefault(key, []).append(d.name)
    return by_q, unreadable


def forks(by_q: dict) -> dict:
    return {q: ks for q, ks in by_q.items() if len(ks) > 1}


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
        for name, qid, rel in (("run_a", "Q001", "['M001']"),
                               ("run_b", "Q001", "['M002']"),
                               ("run_c", "Q002", "['M003']")):
            (root / "results" / name).mkdir(parents=True)
            (root / "results" / name / "detail.csv").write_text(
                "query_id,category,relevant_ids,prohibited_ids\n"
                f"{qid},exact,\"{rel}\",\"[]\"\n")
        by_q, _ = scan(root)
        f = forks(by_q)
        assert set(f) == {"Q001"}, f
        assert len(f["Q001"]) == 2, f
        dirs = sorted(d for names in f["Q001"].values() for d in names)
        assert dirs == ["run_a", "run_b"], dirs
    with tempfile.TemporaryDirectory() as td:
        assert missing_prerequisites(Path(td)), "empty root not reported"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = root / "results" / "run_u"
        d.mkdir(parents=True)
        p = d / "detail.csv"
        p.write_text("query_id,category,relevant_ids,prohibited_ids\nQ001,exact,\"['M001']\",\"[]\"\n")
        os.chmod(p, 0)
        if not os.access(p, os.R_OK):
            _, unreadable = scan(root)
            assert unreadable, "unreadable source not reported"
        os.chmod(p, 0o644)
    print("self-test: PASS (same referent agrees; changed referent forks; "
          "source-less and unreadable sources reported, not silently clean)")
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
        by_q, unreadable = scan(root)
        f = forks(by_q)
        print(f"=== {root}\n    query_ids={len(by_q)}  forked={len(f)}")
        for q, ks in sorted(f.items()):
            print(f"    FORK {q}: {len(ks)} referents")
            for k in ks:
                print(f"      cat={k[0]} rel={list(k[1])[:5]} proh={list(k[2])[:3]} "
                      f"dirs={ks[k][:4]}{'…' if len(ks[k]) > 4 else ''} (n={len(ks[k])})")
        for u in unreadable:
            print(f"    {u['finding']}")
        if f or unreadable:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
