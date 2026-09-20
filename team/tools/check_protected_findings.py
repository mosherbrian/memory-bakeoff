#!/usr/bin/env python3
"""Guard the AGENTS.md "Existing findings to protect" against artifact drift.

Corvid, R&D pulse 2026-09-12. Four protected findings are machine-readable in
the tree; this re-derives each and fails if the artifact stops matching the
published number:

1. agentmemory controlled lifecycle: 418/450 stress distractors falsely
   superseded (0.929), 0 legitimate, 82 live.
2. Claude-Mem controlled: default 90-day window stress Hit@5 0.208; window
   disabled restores dense-LSA (stress 0.583, core 0.958).
3. Habitus real runtime: core Hit@5 0.875; stress Hit@5 0.792, prohibited@5 0.025.
4. Baseline reader trace: BM25/TF-IDF 12/14 (0.857) with one TF-IDF prohibited,
   dense LSA / hybrid RRF 14/14 (1.000).

A missing source artifact is reported as `missing prerequisite: <relpath>`
(exit 1), never an uncaught traceback.

Usage:
  python3 check_protected_findings.py [root]     # exit 1 on drift
  python3 check_protected_findings.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

AM = "results/agentmemory_raw_product_gen13_stress-r1/lifecycle.json"
CM_STRESS = "results/claude_mem_compare_stress450/summary.csv"
CM_CORE = "results/claude_mem_compare_core/summary.csv"
HAB_CORE = "results/habitus_core/summary.csv"
HAB_STRESS = "results/habitus_stress/summary.csv"
HAB_CORE_DETAIL = "results/habitus_core/detail.csv"
READER = "results/READER_FINDINGS.md"
CORE_RECORDS = 50  # stress corpus = 500 native - 50 core

REQUIRED = (AM, CM_STRESS, CM_CORE, HAB_CORE, HAB_STRESS, HAB_CORE_DETAIL, READER)


def _row(path: Path, provider: str) -> dict:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8", errors="replace").splitlines()))
    for r in rows:
        if r.get("provider") == provider:
            return r
    raise KeyError(f"{provider} not in {path.name}")


def check(root: Path) -> list[dict]:
    out: list[dict] = []

    # Missing/unreadable prerequisites are a structured verdict, never an
    # uncaught traceback (same class as the AGENTS guard; Assay 2026-09-13 sweeps).
    missing = []
    for rel in REQUIRED:
        p = root / rel
        if not p.is_file():
            missing.append({"finding": f"missing prerequisite: {rel}",
                            "got": "absent", "want": "present"})
        elif not os.access(p, os.R_OK):
            missing.append({"finding": f"unreadable prerequisite: {rel}",
                            "got": "unreadable", "want": "readable"})
    if missing:
        return missing

    def expect(name: str, got, want: float) -> None:
        if got is None or round(float(got), 3) != want:
            out.append({"finding": name, "got": got, "want": want})

    # 1. agentmemory
    d = json.loads((root / AM).read_text())
    for field, want in (("false_supersession_count", 418),
                        ("legitimate_benchmark_supersession_count", 0),
                        ("live_memory_count", 82)):
        if d.get(field) != want:
            out.append({"finding": f"agentmemory {field}", "got": d.get(field), "want": want})
    denom = d["native_memory_count"] - CORE_RECORDS
    expect("agentmemory false-supersession rate of distractors",
           d["false_supersession_count"] / denom, 0.929)

    # 2. Claude-Mem
    expect("claude_mem default 90-day stress hit@5",
           _row(root / CM_STRESS, "claude_mem_chroma_lsa")["hit@5"], 0.208)
    expect("claude_mem no-window stress hit@5",
           _row(root / CM_STRESS, "claude_mem_chroma_lsa_no_recency")["hit@5"], 0.583)
    expect("claude_mem no-window core hit@5",
           _row(root / CM_CORE, "claude_mem_chroma_lsa_no_recency")["hit@5"], 0.958)

    # 3. Habitus
    expect("habitus core hit@5", _row(root / HAB_CORE, "habitus")["hit@5"], 0.875)
    expect("habitus stress hit@5", _row(root / HAB_STRESS, "habitus")["hit@5"], 0.792)
    expect("habitus stress prohibited@5", _row(root / HAB_STRESS, "habitus")["prohibited@5"], 0.025)
    # Habitus positive non-as-of subset (README 0.955 = 21/22)
    detail = list(csv.DictReader((root / HAB_CORE_DETAIL).read_text().splitlines()))
    subset = [r for r in detail if r["category"] not in ("negative", "temporal_asof")]
    subset_hits = sum(1 for r in subset if float(r["hit_at_k"]) >= 1.0)
    if len(subset) != 22 or subset_hits != 21:
        out.append({"finding": "habitus positive non-as-of subset",
                    "got": f"{subset_hits}/{len(subset)}", "want": "21/22"})

    # 4. Baseline reader
    reader = (root / READER).read_text(encoding="utf-8", errors="replace")
    for provider, want in (("bm25", 0.857), ("tfidf_cosine", 0.857),
                           ("dense_lsa", 1.000), ("hybrid_rrf", 1.000)):
        m = re.search(rf"\|\s*{provider}\s*\|\s*14\s*\|\s*([0-9.]+)\s*\|", reader)
        expect(f"reader {provider} answer pass", m.group(1) if m else None, want)

    return out


def _fixture(root: Path, hab_hits: int = 21) -> None:
    def w(rel: str, text: str) -> None:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    w(AM, json.dumps({"false_supersession_count": 418,
                      "legitimate_benchmark_supersession_count": 0,
                      "live_memory_count": 82, "native_memory_count": 500}))
    w(CM_STRESS, "provider,hit@5,prohibited@5\n"
                 "claude_mem_chroma_lsa,0.20833333333333334,0.2\n"
                 "claude_mem_chroma_lsa_no_recency,0.5833333333333334,0.04\n")
    w(CM_CORE, "provider,hit@5,prohibited@5\n"
               "claude_mem_chroma_lsa_no_recency,0.9583333333333334,0.0\n")
    w(HAB_CORE, "provider,hit@5,prohibited@5\nhabitus,0.875,0.09722222222222221\n")
    w(HAB_STRESS, "provider,hit@5,prohibited@5\nhabitus,0.7916666666666666,0.025\n")
    detail = ["provider,query_id,category,hit_at_k"]
    detail += [f"habitus,Q{i + 1:03d},exact,{1.0 if i < hab_hits else 0.0}" for i in range(22)]
    detail += [f"habitus,Q{i + 23:03d},negative,0.0" for i in range(2)]
    detail += [f"habitus,Q{i + 25:03d},temporal_asof,0.0" for i in range(2)]
    w(HAB_CORE_DETAIL, "\n".join(detail) + "\n")
    w(READER, "| Provider | Cases | Answer pass | Required coverage | Prohibited-answer rate |\n"
              "|---|---:|---:|---:|---:|\n"
              "| bm25 | 14 | 0.857 | 0.857 | 0.000 |\n"
              "| tfidf_cosine | 14 | 0.857 | 0.857 | 0.071 |\n"
              "| dense_lsa | 14 | 1.000 | 1.000 | 0.000 |\n"
              "| hybrid_rrf | 14 | 1.000 | 1.000 | 0.000 |\n")


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _fixture(root)
        assert check(root) == [], check(root)
        (root / HAB_STRESS).write_text("provider,hit@5,prohibited@5\nhabitus,0.100,0.025\n")
        assert any(f["finding"] == "habitus stress hit@5" for f in check(root))
        _fixture(root)
        _fixture(root, hab_hits=20)
        assert any(f["finding"] == "habitus positive non-as-of subset" for f in check(root))

    # Missing source -> structured finding on the REAL CLI, not a traceback.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        missing = check(root)
        assert any(f["finding"].startswith("missing prerequisite: ") for f in missing), missing
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(root)],
                           capture_output=True, text=True, timeout=120)
        blob = p.stdout + p.stderr
        assert p.returncode == 1, (p.returncode, blob[-200:])
        assert "missing prerequisite: " in blob, blob[-200:]
        assert "Traceback (most recent call last)" not in blob, blob[-200:]
    print("self-test: PASS (protected findings clean; drifted habitus and 0.955 subset "
          "flagged; missing source reported as a structured prerequisite, not a crash)")
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
    print(f"=== {root}\n    protected-finding drift: {len(found)}")
    for f in found:
        print(f"    {f}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
