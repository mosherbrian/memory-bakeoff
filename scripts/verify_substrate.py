#!/usr/bin/env python3
"""Eligibility per PREREGISTRATION section 2: memory_bakeoff.ordering_scorer.hit,
SESSION scope, both roles.

Closes the substrate findings that need no reviewer and no control plane.

Finding 121: stale-earlier / current-later was SAMPLED, not verified.
Finding 125: the dataset is not content-pinned.
Plus: the 4 items whose gold value looked like it sits in the EARLIER session.

Reads only. Runs no reader. Touches no held-out item.
"""
import json, hashlib, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from memory_bakeoff.ordering_scorer import hit  # noqa: E402

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

def sessions(x):
    """ALL text of each session, both roles - the scope PREREGISTRATION section 2
    now names. An earlier version of this script read only the has_answer TURN,
    which is a narrower scope than the words 'the later session', and that gap
    made three different frozen sets readable out of one sentence."""
    return [" ".join(t["content"] for t in s) for s in x["haystack_sessions"]]

print(f"\nGOLD LOCATION (finding 121), {len(clean)} clean items:")
rows = []
for x in clean:
    g = str(x["answer"])
    e, l = sessions(x)
    rows.append((x["question_id"], hit(g, e), hit(g, l), g.strip()))
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
