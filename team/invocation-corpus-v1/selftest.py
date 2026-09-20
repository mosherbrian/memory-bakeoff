#!/usr/bin/env python3
"""Corpus v1 self-test — re-verifies team/invocation-corpus-v1/ deterministically.
Usage: python3 selftest.py  (rc 0 = all green; $0, stdlib only, no network)
Checks: hashes match files; 12 scenarios x (1 moment + 2 fillers); 2/family;
9 open / 3 heldout; topic/offtopic split == binding trigger reachability;
leak gate (no action string in wrong place); no adjacent moments.
"""
import json, hashlib, re, sys
from pathlib import Path
D = Path(__file__).parent
fails = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not cond: fails.append(name)

corpus = [json.loads(l) for l in (D/"corpus.jsonl").read_text().splitlines()]
manifest = json.loads((D/"manifest.json").read_text())["scenarios"]
hashes = json.loads((D/"hashes.json").read_text())
check("hashes match files",
      hashlib.sha256((D/"corpus.jsonl").read_bytes()).hexdigest() == hashes["corpus_sha256"]
      and hashlib.sha256((D/"manifest.json").read_bytes()).hexdigest() == hashes["manifest_sha256"])
check("12 scenarios", len(corpus) == 12 == len(manifest), f"{len(corpus)}/{len(manifest)}")
struct = all(len(s["turns"]) == 3 and sum(t["type"].startswith("moment") for t in s["turns"]) == 1
         and s["turns"][1]["type"].startswith("moment") for s in corpus)
check("1 moment + 2 fillers, moment centered", struct)
from collections import Counter
fam = Counter(s["family"] for s in corpus)
check("2 scenarios per family x6", set(fam.values()) == {2}, dict(fam))
split = Counter(s["split"] for s in corpus)
check("9 open / 3 heldout", split.get("open") == 9 and split.get("heldout") == 3, dict(split))
# Binding trigger predicate, mirroring extensions/pi-change-trigger/index.ts:96-112:
# tokens len >= 4, trigger STOPWORDS, topic set = record SUMMARIES only.
STOP = {"this","that","with","from","into","have","been","will","shall",
        "they","them","their","there","then","than","when","what","which",
        "where","were","been","also","only","over","under","about","after",
        "before","while","being","does","done","each","such","some","more",
        "most","other","same","very","upon","said","create","created",
        "decision","environment","project","trial","record","tool","call",
        "confirm","confirmed","draft","pending","campaign1","campaign-1",
        "window","opening","exists","never","still","uses","using","used"}
def toks(s): return {w for w in re.findall(r"[a-z0-9][a-z0-9-]{3,}", s.lower()) if w not in STOP}
topic_bad, leak = [], []
for m in manifest:
    s = next(x for x in corpus if x["scenario_id"] == m["scenario_id"])
    rec = next(r for r in s["records"] if r["id"] == m["record_set"][0])
    prompt = next(t["text"] for t in s["turns"] if t["type"].startswith("moment"))
    shared = toks(prompt) & toks(rec["summary"])
    if (len(shared) >= 1) != m["topic_reachable"]: topic_bad.append(m["scenario_id"])
    for t in s["turns"]:
        low = t["text"].lower()
        if t["type"].startswith("moment"):
            leak += [(s["scenario_id"], c) for c in m["correct_action_set"] if c.lower() in low]
        else:
            leak += [(s["scenario_id"], x) for x in m["correct_action_set"] + m["wrong_action_set"]
                     if len(x) > 4 and x.lower() in low]
check("topic split == binding trigger reachability", not topic_bad, str(topic_bad))
check("leak gate 0 violations", not leak, str(leak))
print("SELFTEST: " + ("ALL GREEN" if not fails else f"{len(fails)} FAILING: {fails}"))
sys.exit(1 if fails else 0)
