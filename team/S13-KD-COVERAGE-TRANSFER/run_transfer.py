#!/usr/bin/env python3
"""Replay the frozen S11 corpus-coverage rule on the frozen KnowledgeDrift sample.

No parameter is tuned here. The rule, its stopword list, its frequency floor
and its threshold grid are read from S11-ABSTAIN3/declaration.json and used as
they stand. The worlds and the 120-probe item list are the sha-pinned ones from
S10-KD-CROSS. Criteria were registered in PREREGISTRATION.md before this ran.
"""
import json, re, collections, hashlib, pathlib, sys

TEAM = pathlib.Path(__file__).resolve().parent.parent
HERE = TEAM / "S13-KD-COVERAGE-TRANSFER"
DECL = json.loads((TEAM / "S11-ABSTAIN3/declaration.json").read_text())
RULE, GRID = DECL["rule"], DECL["thresholds"]
STOP = set(RULE["content_stopwords"])
MINDF = RULE["min_document_frequency"]
WORLDS = TEAM / "S7-KD-WORLDS/upstream/KnowledgeDrift/worlds/v2"
PIN = json.loads((TEAM / "S10-KD-CROSS/declaration.json").read_text())["worlds"]["files"]

tok = lambda s: re.findall(r"[a-z0-9]+", (s or "").lower())

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def load(seed):
    name = f"knowledgedrift-500-seed{seed}-v2.json"
    p = WORLDS / name
    got = sha(p)
    assert got == PIN[name], f"{name} sha mismatch: {got} != {PIN[name]}"
    w = json.loads(p.read_text())
    # the document collection: every record the stream inscribes
    df = collections.Counter()
    ndocs = 0
    for op in w["ops"]:
        if op["op"] == "inscribe":
            r = op["record"]
            ndocs += 1
            for t in set(tok(r.get("title", "")) + tok(r.get("body", ""))):
                df[t] += 1
    q = {op["id"]: op["query"] for op in w["ops"] if "query" in op and "id" in op}
    return {"probes": {p["id"]: p for p in w["probes"]}, "df": df,
            "queries": q, "ndocs": ndocs, "sha": got}

worlds = {s: load(s) for s in (1, 2)}
for s, w in worlds.items():
    print(f"  seed {s}: {w['ndocs']} records, {len(w['df'])} distinct terms, "
          f"{len(w['queries'])} queries  sha {w['sha'][:12]}")

items = [json.loads(l) for l in (TEAM / "S10-KD-CROSS/items.jsonl").read_text().splitlines() if l.strip()]
print(f"  {len(items)} frozen probes")

rows, unresolved, degenerate = [], [], []
for it in items:
    seed, pid = it["seed"], it["item_id"].split("-", 1)[1]
    w = worlds[seed]
    query = w["queries"].get(pid)
    probe = w["probes"].get(pid)
    if query is None or probe is None:
        unresolved.append(it["item_id"]); continue
    # S11 coverage(): sorted(set(query)) - stopwords. DISTINCT content tokens,
    # not occurrences. Repaired 2026-09-20 after Tern found the deviation;
    # the grid was identical at all five thresholds either way.
    terms = sorted(set(tok(query)) - STOP)
    if not terms:
        degenerate.append(it["item_id"]); continue
    supported = sum(1 for t in terms if w["df"][t] >= MINDF)
    rows.append({"item_id": it["item_id"], "family": it["family"], "seed": seed,
                 "expect": probe.get("expect"), "terms": len(terms),
                 "supported": supported, "fraction": supported / len(terms)})

print(f"  resolved {len(rows)}, unresolved {len(unresolved)}, "
      f"no content terms {len(degenerate)}")

ABST = [r for r in rows if r["family"] == "Abstention"]
USEFUL = [r for r in rows if r["family"] in ("Retrieval", "Rationale")]

out = {"rule_family": RULE["family"], "decision": RULE["decision"],
       "min_document_frequency": MINDF, "thresholds": GRID,
       "worlds": {f"seed{s}": w["sha"] for s, w in worlds.items()},
       "prereg_sha256": sha(HERE / "PREREGISTRATION.md"),
       "n_abstention": len(ABST), "n_useful": len(USEFUL),
       "unresolved": unresolved, "no_content_terms": degenerate, "by_threshold": []}

print(f"\n{'thr':>5} {'correct abstentions':>22} {'useful lost':>24}")
for t in GRID:
    ab = sum(1 for r in ABST if r["fraction"] < t)
    lost = sum(1 for r in USEFUL if r["fraction"] < t)
    per_fam = {f: sum(1 for r in USEFUL if r["family"] == f and r["fraction"] < t)
               for f in ("Retrieval", "Rationale")}
    per_seed = {f"seed{s}": sum(1 for r in ABST if r["seed"] == s and r["fraction"] < t)
                for s in (1, 2)}
    out["by_threshold"].append({"threshold": t, "correct_abstentions": ab,
                                "useful_lost": lost, "useful_lost_by_family": per_fam,
                                "abstentions_by_seed": per_seed})
    print(f"{t:>5} {ab:>10}/{len(ABST):<11} {lost:>12}/{len(USEFUL):<11}")

(HERE / "results.json").write_text(json.dumps(out, indent=1) + "\n")
print(f"\nwrote {HERE/'results.json'}")
