#!/usr/bin/env python3
"""Combine the dated and date-stripped pilot arms into one table."""
import json, glob, re
from pathlib import Path

def load(pat):
    dirs = sorted(glob.glob(f"research/pilot_ordering/{pat}"))
    if not dirs: return None
    d = Path(dirs[-1])
    return json.loads((d / "rows.json").read_text()), d

def arm(rows):
    by = {}
    for r in rows: by.setdefault(r["question_id"], {})[r["order"]] = r["hit"]
    sf = sum(v["stale_first"] for v in by.values())
    cf = sum(v["current_first"] for v in by.values())
    only_sf = sum(1 for v in by.values() if v["stale_first"] and not v["current_first"])
    only_cf = sum(1 for v in by.values() if v["current_first"] and not v["stale_first"])
    return {"n": len(by), "chronological_hits": sf, "reversed_hits": cf,
            "right_only_chronological": only_sf, "right_only_reversed": only_cf}

dated = load("2*[!s]")
strip = load("*-nodates")
out = {"dated": arm(dated[0]) if dated else None,
       "dates_stripped": arm(strip[0]) if strip else None,
       "caveat": ("Header dates removed in the stripped arm; date words remain inside "
                  "the conversation text of most items, so the strip is partial."),
       "status": "PILOT. Exploratory. Crude string scorer. Held-out 34 untouched."}
Path("research/pilot_ordering/COMBINED.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
