#!/usr/bin/env python3
"""Close the substrate findings that need no reviewer and no control plane.

Finding 121: stale-earlier / current-later was SAMPLED, not verified.
Finding 125: the dataset is not content-pinned.
Plus: the 4 items whose gold value looked like it sits in the EARLIER session.

Reads only. Runs no reader. Touches no held-out item.
"""
import json, hashlib, re
from pathlib import Path

SRC = Path("/home/bmosher/.cache/huggingface/hub/datasets--xiaowu0162--longmemeval-cleaned/"
           "snapshots/98d7416c24c778c2fee6e6f3006e7a073259d48f/longmemeval_oracle.json")

raw = SRC.read_bytes()
pin = {"path": SRC.name, "snapshot": SRC.parent.name,
       "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
print("CONTENT PIN (finding 125):"); print(json.dumps(pin, indent=2))

d = json.loads(raw)
ku = [x for x in d if x["question_type"] == "knowledge-update"
      and not x["question_id"].endswith("_abs")]
clean = [x for x in ku
         if [sum(1 for t in s if t.get("has_answer")) for s in x["haystack_sessions"]] == [1, 1]]

def marked(x):
    return [[t["content"] for t in s if t.get("has_answer")][0] for s in x["haystack_sessions"]]

print(f"\nGOLD LOCATION (finding 121), {len(clean)} clean items:")
rows = []
for x in clean:
    g = str(x["answer"]).strip().rstrip(".")
    e, l = marked(x)
    gl, el, ll = g.lower(), e.lower(), l.lower()
    nums = re.findall(r"\d[\d,:.]*", g)
    in_e = gl in el or (bool(nums) and all(n in e for n in nums))
    in_l = gl in ll or (bool(nums) and all(n in l for n in nums))
    rows.append((x["question_id"], in_e, in_l, g))
only_l = [r for r in rows if r[2] and not r[1]]
only_e = [r for r in rows if r[1] and not r[2]]
both = [r for r in rows if r[1] and r[2]]
neither = [r for r in rows if not r[1] and not r[2]]
print(f"  gold ONLY in later (expected):   {len(only_l)}")
print(f"  gold ONLY in earlier (WRONG):    {len(only_e)}")
print(f"  gold in BOTH (ambiguous):        {len(both)}")
print(f"  gold in NEITHER (matcher blind): {len(neither)}")
print("\n  items where gold sits ONLY in the EARLIER session - these break the")
print("  stale-earlier assumption and must be excluded or read individually:")
for qid, _, _, g in only_e:
    print(f"    {qid}  gold={g!r}")
print("\n  items the matcher could not locate at all (string answers, not a defect):")
for qid, _, _, g in neither[:12]:
    print(f"    {qid}  gold={g!r}")
Path("research/pilot_ordering/SUBSTRATE_VERIFY.json").write_text(json.dumps(
    {"content_pin": pin,
     "gold_only_later": [r[0] for r in only_l],
     "gold_only_earlier": [r[0] for r in only_e],
     "gold_both": [r[0] for r in both],
     "gold_unlocatable_by_matcher": [r[0] for r in neither],
     "note": "String-answer items are matcher-blind, not dataset defects. The "
             "gold_only_earlier set is the one that threatens the design."}, indent=2))
print("\nwritten: research/pilot_ordering/SUBSTRATE_VERIFY.json")
