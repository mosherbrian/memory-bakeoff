#!/usr/bin/env python3
"""Corpus selftest for the standard tier: structure, manifest coverage, leak gate,
topic reachability. Exit 0 = green."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STOP = None
def tokens(t):
    return {x for x in re.findall(r"[a-z0-9][a-z0-9-]{3,}", t.lower())}
def main():
    corpus=[json.loads(l) for l in open(os.path.join(HERE,"corpus.jsonl")) if l.strip()]
    man=json.load(open(os.path.join(HERE,"manifest.json")))
    m={x["scenario_id"]:x for x in man["scenarios"]}
    errs=[]
    if len(corpus)!=60 or len(m)!=60: errs.append(f"count corpus={len(corpus)} manifest={len(m)}")
    fam={}
    for sc in corpus:
        sid=sc["scenario_id"]; rec=sc["records"][0]; mm=m[sid]
        fam[sc["family"]]=fam.get(sc["family"],0)+1
        if not (len(sc["turns"])==3 and sc["turns"][1]["turn"]==2): errs.append(f"{sid}: turn shape")
        if not sc["turns"][0]["type"]=="filler_plain": errs.append(f"{sid}: t1 not plain")
        moment=sc["turns"][1]
        shared=tokens(moment["text"]) & tokens(rec["summary"])
        if mm["topic_reachable"] and not shared: errs.append(f"{sid}: unreachable topic")
        if (not mm["topic_reachable"]) and shared: errs.append(f"{sid}: offtopic shares {shared}")
        for s in mm["correct_action_set"]+mm["wrong_action_set"]:
            if s in moment["text"]: errs.append(f"{sid}: action string in moment")
            for t in sc["turns"]:
                if not t["type"].startswith("moment") and len(s)>4 and s in t["text"]:
                    errs.append(f"{sid}: action string in filler")
    if set(fam)!={"env_fact","convention","negation","actually","repeated_instruction","wrong"}:
        errs.append(f"families {fam}")
    if any(v!=10 for v in fam.values()): errs.append(f"family weights {fam}")
    print(f"standard corpus selftest: scenarios={len(corpus)} families={fam} errors={len(errs)}")
    for e in errs[:10]: print("  ERR", e)
    return 1 if errs else 0
if __name__=="__main__": sys.exit(main())
