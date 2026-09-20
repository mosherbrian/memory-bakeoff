#!/usr/bin/env python3
"""S10-2 rankings capturer (kiln-flash, 2026-09-18).

Re-captures what team/S8-DOOR/results.jsonl threw away: the RANKED id list
each adapter returned, per condition and case, on the S6-2 frozen retrieve
cases under normal and under rung 1's declared pressure load.

Reuses the verified rung-1 harness BY IMPORT (team/S8-DOOR/run_door.py): the
pressure load is regenerated from the same seeded families (byte-identical to
the load rung 1 actually ran — the load under which the cited sel-005 top-two
swap was observed), record construction and adapter invocations are rung 1's.
Writes rankings.jsonl only after every assertion holds:
  - the S6-2 corpus and the S8-DOOR items freeze match their pins;
  - the S6-2 manifest's pre-run declared helpful map matches the map the
    S8-DOOR freeze was built from;
  - exactly 5 positive cases per adapter/condition, each with non-empty
    relevant_ids and a duplicate-free ranking.
Deterministic: seeded pressure families, fixed record timestamps, no
wall-clock in any decision."""
import sys

sys.dont_write_bytecode = True  # import-time pycache would write into lanes

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = HERE.parent
S8 = TEAM / "S8-DOOR"
S6 = TEAM / "S6-SELECTIVITY"
sys.path.insert(0, str(S8))
import run_door as r1  # rung-1 machinery, reused verbatim

ADAPTERS = ["bm25", "pi_lcm_toollevel", "claude_mem_chroma_lsa_no_recency"]


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def abort(msg: str) -> int:
    print(f"ABORT: {msg}")
    return 1


def retrieve(adapter, store, q):
    if adapter == "bm25":
        eng = r1.BM25Provider()
        eng.ingest(store)
        res = eng.retrieve(q, top_k=1)
    elif adapter == "pi_lcm_toollevel":
        eng = r1.PiLcmToolLevelProvider()
        eng.reset()
        eng.ingest(store)
        res = eng.retrieve(q, top_k=5)
        eng.close()
    elif adapter == "claude_mem_chroma_lsa_no_recency":
        eng = r1.ClaudeMemChromaLSANoRecencyProvider()
        eng.ingest(store)
        res = eng.retrieve(q, top_k=3)
    else:
        raise SystemExit(f"unknown adapter {adapter}")
    return [it.record_id for it in res.items]


def main() -> int:
    corpus_bytes = r1.CORPUS.read_bytes()
    if sha_bytes(corpus_bytes) != r1.CORPUS_SHA256:
        return abort("S6-2 corpus does not match its pin")
    corpus = {c["case_id"]: c for c in
              (json.loads(l) for l in corpus_bytes.decode().splitlines()
               if l.strip())}

    items_bytes = (S8 / "items.jsonl").read_bytes()
    s8_decl = json.loads((S8 / "declaration.json").read_bytes())
    if sha_bytes(items_bytes) != s8_decl["items_sha256"]:
        return abort("team/S8-DOOR/items.jsonl does not match its own pin")
    items = [json.loads(l) for l in
             items_bytes.decode().splitlines() if l.strip()]

    manifest = json.loads((S6 / "manifest.json").read_text(encoding="utf-8"))
    helpful = {i: list(m) for i, m in manifest["helpful"].items()}
    import declare as s8_declare  # S8-DOOR's freeze-time map, constants only
    for item in items:
        iid = item["item_id"]
        if helpful.get(iid) != [s8_declare.HELPFUL.get(iid)]:
            return abort(f"manifest helpful map disagrees with the S8-DOOR "
                         f"freeze on {iid}")
        if not helpful.get(iid):
            return abort(f"{iid} declares no relevant ids; the rank plane "
                         f"needs the five retrieve cases")
    helpful_all = [h for i in items for h in i["helpful_evidence"]]

    rows, n = [], 0
    for adapter in ADAPTERS:
        for condition in ("normal", "pressure"):
            counts = {}
            for item in items:
                iid = item["item_id"]
                case = corpus[iid]
                if case["expect"] != "retrieve":
                    return abort(f"{iid} is not a retrieve case")
                if condition == "pressure":
                    extra, total = r1.pressure_load(iid, helpful_all)
                else:
                    extra, total = [], 0
                ranked = retrieve(adapter, r1.records_for(case, extra),
                                  r1.query_for(item))
                if len(set(ranked)) != len(ranked):
                    return abort(f"{adapter}/{condition}/{iid}: duplicate ids "
                                 f"in the returned ranking")
                counts[iid] = ranked
                rows.append({"adapter": adapter, "condition": condition,
                             "case_id": iid, "category": case["expect"],
                             "relevant_ids": helpful[iid],
                             "ranked_ids": ranked})
                n += 1
                print(f"  {adapter:>34} {condition:>8} {iid}: "
                      f"{len(ranked)} ranked ({total}B load)")
            if len(counts) != 5:
                return abort(f"{adapter}/{condition}: {len(counts)} positive "
                             f"cases, the rank plane needs 5")

    (HERE / "rankings.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"rankings frozen: {n} rows (3 adapters x 2 conditions x 5 "
          f"retrieve cases), relevant_ids = the S6-2 manifest's pre-run "
          f"declared helpful records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
