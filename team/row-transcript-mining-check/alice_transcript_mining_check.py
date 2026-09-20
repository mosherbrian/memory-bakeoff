#!/usr/bin/env python3
"""Alice second-driver: recount Kiln's transcript-mining scale-up from its own
local rows, WITHOUT printing any transcript-derived content.

Reads the local JSONL outputs and `stats.json`, prints only aggregate counts and
booleans (class totals, id uniqueness, source-pointer presence, rows-vs-summary
agreement). The `excerpt` field is never read into or printed by this script's
output; it stays in the local process.

Run: python3 alice_transcript_mining_check.py
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path.home() / ".local/share/memory-bakeoff/transcript-mining/full-20260913"
CORR = OUT / "correction-events.jsonl"
FACT = OUT / "durable-facts.jsonl"
STATS = OUT / "stats.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def recount(path: Path):
    n = 0
    classes = Counter()
    with_id = Counter()
    full_ptr = Counter()
    ids_by_class = {}
    repeated = {"rows": 0, "occurrences_total": 0, "rows_with_id": 0,
                "rows_with_spots": 0}
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            n += 1
            cls = d.get("class")
            classes[cls] += 1
            if d.get("record_id"):
                with_id[cls] += 1
            if all(d.get(k) not in (None, "", 0) for k in ("file", "line", "session", "timestamp")):
                full_ptr[cls] += 1
            ids_by_class.setdefault(cls, set()).add(d.get("record_id"))
            if cls == "repeated_instruction":
                repeated["rows"] += 1
                repeated["occurrences_total"] += int(d.get("occurrences") or 0)
                repeated["rows_with_id"] += bool(d.get("record_id"))
                repeated["rows_with_spots"] += bool(d.get("spots"))
    return {"records": n, "by_class": dict(sorted(classes.items())),
            "rows_with_record_id_by_class": dict(sorted(with_id.items())),
            "rows_with_full_source_pointer_by_class": dict(sorted(full_ptr.items())),
            "unique_ids_by_class": {k: len(v) for k, v in sorted(ids_by_class.items())},
            "repeated_instruction_groups": repeated}


def main() -> int:
    stats = json.loads(STATS.read_text())
    corr = recount(CORR)
    fact = recount(FACT)
    out = {
        "hashes": {"correction_events": sha(CORR), "durable_facts": sha(FACT),
                   "stats": sha(STATS)},
        "correction_rows": corr,
        "durable_fact_rows": fact,
        "stats_summary": {
            "files_scanned": stats.get("files_scanned"),
            "files_excluded_open": stats.get("files_excluded_open"),
            "user_text_turns": stats.get("user_text_turns"),
            "correction_classes": stats.get("correction_classes"),
            "fact_classes": stats.get("fact_classes"),
            "exclude_mtime_within_minutes": stats.get("exclude_mtime_within_minutes"),
        },
        "agreement": {
            "correction_rows_eq_stats": (corr["records"]
                                         == sum((stats.get("correction_classes") or {}).values())
                                         == sum(corr["by_class"].values())),
            "fact_rows_eq_stats": (fact["records"]
                                   == sum((stats.get("fact_classes") or {}).values())),
        },
    }
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
