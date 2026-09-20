#!/usr/bin/env python3
"""Alice second-driver: independently recount Assay's leakage-field census."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

TREES = {
    "repo": Path("/var/home/bmosher/memory-bake-off/implementer/repo/results"),
    "dsh3": Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh3/results"),
    "dsh2": Path("/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2/results"),
}

def header(p):
    with p.open(newline="", encoding="utf-8", errors="replace") as fh:
        try:
            return next(csv.reader(fh))
        except StopIteration:
            return []

out = {"trees": {}, "findings": []}
for name, root in TREES.items():
    if not root.is_dir():
        out["trees"][name] = {"missing": True}; continue
    summaries = sorted(root.glob("*/summary.csv"))
    details = sorted(root.glob("*/detail.csv"))
    with_detail = sum(1 for s in summaries if (s.parent/"detail.csv").is_file())
    schemas = Counter(tuple(header(s)) for s in summaries)
    leak_cols = sum(1 for s in summaries
                    if any(("scope" in c.lower() or "leak" in c.lower()) for c in header(s)))
    wrong_scope = 0; prohib_pos = 0; prohib_nonempty = 0
    for d in details:
        h = header(d)
        if "wrong_scope_context_present" in h:
            wrong_scope += 1
        if "prohibited_count" in h or "prohibited_ids" in h:
            try:
                with d.open(newline="", encoding="utf-8", errors="replace") as fh:
                    r = csv.DictReader(fh)
                    for row in r:
                        try:
                            if int(float(row.get("prohibited_count") or 0)) > 0:
                                prohib_pos += 1
                        except ValueError:
                            pass
                        if (row.get("prohibited_ids") or "").strip() not in ("", "[]"):
                            prohib_nonempty += 1
            except OSError:
                pass
    out["trees"][name] = {
        "summaries": len(summaries), "details": len(details),
        "with_detail": with_detail, "summary_schemas": len(schemas),
        "schema_sizes": sorted(c for c in set(len(k) for k in schemas)),
        "summaries_with_scope_or_leak_col": leak_cols,
        "detail_with_wrong_scope_col": wrong_scope,
        "detail_rows_prohibited_count_pos": prohib_pos,
        "detail_rows_prohibited_ids_nonempty": prohib_nonempty,
    }
# reader JSON check
import glob
rj = glob.glob("/var/home/bmosher/memory-bake-off/implementer/repo/results/**/reader_results/reader.json", recursive=True)
out["reader_json"] = {"files": len(rj)}
for f in rj[:3]:
    try:
        d = json.load(open(f))
        s = json.dumps(d)
        out["reader_json"].setdefault("has_wrong_scope_keys", []).append(
            {k: (k in s) for k in ("wrong_scope_context_case_rate", "wrong_scope_answer_rate", "wrong_scope_context_present")})
    except Exception as e:
        out["reader_json"].setdefault("errors", []).append(str(e))
print(json.dumps(out, indent=1)); raise SystemExit(0)
