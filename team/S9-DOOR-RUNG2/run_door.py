#!/usr/bin/env python3
"""S10-1 rung-2 door runner (kiln-flash, 2026-09-18).

Reuses the rung-1 harness (team/S8-DOOR/run_door.py) BY IMPORT: same corpus
loading, record construction, adapter invocations, composition rule and
scoring — only the load is new, read from pressure_chunks.jsonl as declared
and frozen (chunks sha pinned in declaration.json). Writes results.jsonl
(run order, every row sha-bound to this rung's declaration) and verdict.json
(rung-1 cells quoted from the prior, rung-2 cells recomputed here, reach
re-derived with the gate's own 40-char-window rule).

Pre-run hard assertions (nothing is written if any fails):
  - items.jsonl is the rung-1 file byte for byte (three-way sha check);
  - pressure_chunks.jsonl matches the declaration's chunks sha256;
  - adapters, budget and scoring equal rung 1's declaration; the declared
    load is not below rung 1's;
  - every item has its full declared load at or above the declared floor;
  - no chunk contains any item's helpful evidence string (the pre-run
    assertion, recomputed here on the frozen file);
  - every chunk shares at least two query words with its item's query
    (the gate's own mechanical rule);
  - the S6-2 corpus matches the pin rung 1 froze items from.
Deterministic: the load was generated from a seeded RNG at declare time and
is read back frozen; record timestamps are the S4-12/S4-14 fixed stamp; row
ts is bookkeeping only."""
import sys

sys.dont_write_bytecode = True  # import-time pycache would write into lanes

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = HERE.parent
S8 = TEAM / "S8-DOOR"
sys.path.insert(0, str(S8))
import run_door as r1  # rung-1 machinery, reused verbatim

WINDOW, STRIDE = 40, 20  # the rung-2 gate's reach detection, mirrored
PRESENCE, BYTES = r1.PRESENCE, r1.BYTES

# the gate's adjacency rule, copied so the pre-run re-check is the same
# mechanical test the gate recomputes
STOP = {"what", "which", "when", "where", "does", "that", "this", "with",
        "from", "have", "will", "should", "would", "there", "their", "about"}


def words(text: str) -> set:
    return set(re.findall(r"[a-z0-9][a-z0-9-]{3,}", text.lower())) - STOP


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def reached(chunks: list, delivered: str) -> bool:
    d = r1.norm(delivered)
    for c in chunks:
        n = r1.norm(c)
        if any(n[i:i + WINDOW] in d for i in
               range(0, max(len(n) - WINDOW, 0) + 1, STRIDE)):
            return True
    return False


def abort(msg: str) -> int:
    print(f"ABORT: {msg}")
    return 1


def main() -> int:
    decl_bytes = (HERE / "declaration.json").read_bytes()
    decl = json.loads(decl_bytes)
    decl_sha = sha_bytes(decl_bytes)
    r1_decl = json.loads((S8 / "declaration.json").read_bytes())

    items_bytes = (HERE / "items.jsonl").read_bytes()
    items = [json.loads(l) for l in
             items_bytes.decode().splitlines() if l.strip()]
    if not (sha_bytes(items_bytes) == decl["items_sha256"]
            == r1_decl["items_sha256"] == sha_bytes((S8 / "items.jsonl").read_bytes())):
        return abort("items.jsonl is not the rung-1 file byte for byte")
    if decl["adapters"] != r1_decl["adapters"] \
            or decl["budget_chars"] != r1_decl["budget_chars"] \
            or decl["scoring"] != r1_decl["scoring"]:
        return abort("adapters, budget or scoring differ from rung 1; only "
                     "the load may change")
    if decl["pressure"]["tool_output_bytes"] < r1_decl["pressure"]["tool_output_bytes"]:
        return abort("declared load is below rung 1's")

    chunk_rows = [json.loads(l) for l in
                  (HERE / "pressure_chunks.jsonl").read_text().splitlines()
                  if l.strip()]
    if decl["pressure"]["chunks_sha256"] != sha_bytes(
            (HERE / "pressure_chunks.jsonl").read_bytes()):
        return abort("pressure_chunks.jsonl does not match the declaration's "
                     "chunks pin: the load changed after it was declared")

    chunks = {c["item_id"]: [t for t in c["chunks"] if t.strip()]
              for c in chunk_rows}
    load_floor = decl["pressure"]["tool_output_bytes"]
    totals = {}
    for item in items:
        iid = item["item_id"]
        if not chunks.get(iid):
            return abort(f"no pressure chunks for {iid}")
        totals[iid] = sum(len(t.encode("utf-8")) for t in chunks[iid])
        if totals[iid] < load_floor:
            return abort(f"load for {iid} is {totals[iid]} bytes, below the "
                         f"declared {load_floor}")
    all_evidence = [r1.norm(h) for i in items for h in i["helpful_evidence"]
                    if h.strip()]
    for iid, texts in chunks.items():
        q = words(next(i["query"] for i in items if i["item_id"] == iid))
        for n, t in enumerate(texts):
            if any(h in r1.norm(t) for h in all_evidence):
                return abort(f"chunk {iid}#{n} contains helpful evidence; the "
                             f"frozen load is corrupt")
            if len(q & words(t)) < min(2, len(q)):
                return abort(f"chunk {iid}#{n} is not query-adjacent")
    if sha_bytes(r1.CORPUS.read_bytes()) != r1.CORPUS_SHA256:
        return abort("S6-2 corpus does not match the pin rung 1 froze from")
    print("pre-run assertions held: items are rung-1 bytes; the frozen load "
          f"is sha-bound, evidence-free and query-adjacent; "
          f"{min(totals.values())}+ bytes/item against rung 1's declared "
          f"{r1_decl['pressure']['tool_output_bytes']}")

    budget = decl["budget_chars"]
    corpus = {c["case_id"]: c for c in
              (json.loads(l) for l in r1.CORPUS.read_text().splitlines()
               if l.strip())}

    rows, delivered_index = [], {}

    def run_cell(adapter, condition, item):
        iid = item["item_id"]
        if condition == "pressure":
            extra = [r1.MemoryRecord(id=f"{iid}-tool-{i:02d}", text=t,
                                     timestamp=r1.RECORD_TS,
                                     session_id=f"sess-{iid}")
                     for i, t in enumerate(chunks[iid])]
            comp_bytes = totals[iid]
        else:
            extra, comp_bytes = [], 0
        store = r1.records_for(corpus[iid], extra)
        q = r1.query_for(item)
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
            return abort(f"unknown adapter {adapter}")
        text = r1.compose([it.text for it in res.items], budget)
        rows.append({"ts": now(), "adapter": adapter, "condition": condition,
                     "item_id": iid, "delivered_text": text,
                     "competing_bytes": comp_bytes,
                     "declaration_sha256": decl_sha})
        delivered_index[(adapter, condition, iid)] = text
        print(f"  {adapter:>34} {condition:>8} {iid}: "
              f"{len(res.items)} rec(s), {len(text)} chars")

    t0 = time.perf_counter()
    for adapter in decl["adapters"]:
        for condition in ("normal", "pressure"):
            for item in items:
                run_cell(adapter, condition, item)
    print(f"ran {len(rows)} cells in {time.perf_counter() - t0:.1f}s")

    over = [r for r in rows if len(r["delivered_text"]) > budget]
    if over:
        return abort(f"{len(over)} delivered texts exceed the budget; "
                     f"composition rule violated")
    (HERE / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    rung2 = {}
    for adapter in decl["adapters"]:
        for condition in ("normal", "pressure"):
            cells = [r1.score_one(delivered_index[(adapter, condition, i["item_id"])],
                                  i["helpful_evidence"]) for i in items]
            rung2[(adapter, condition)] = {
                PRESENCE: sum(p for p, _ in cells) / len(cells),
                BYTES: sum(b for _, b in cells) / len(cells),
            }
    reach = {a: sum(1 for i in items if reached(
        chunks[i["item_id"]],
        delivered_index[(a, "pressure", i["item_id"])]))
        for a in decl["adapters"]}

    prior_cells = json.loads(
        (S8 / "verdict.json").read_text(encoding="utf-8"))["per_adapter"]
    per = {}
    for a in decl["adapters"]:
        per[a] = {
            "rung1": {"normal": dict(prior_cells[a]["normal"]),
                      "pressure": dict(prior_cells[a]["pressure"])},
            "rung2": {"normal": rung2[(a, "normal")],
                      "pressure": rung2[(a, "pressure")]},
            "load_reached_door": reach[a],
        }

    def clause(a):
        n, p = rung2[(a, "normal")], rung2[(a, "pressure")]
        r1n = prior_cells[a]["normal"]
        return (f"{a} presence {r1n[PRESENCE]:.2f} -> {n[PRESENCE]:.2f} -> "
                f"{p[PRESENCE]:.2f}, irrelevant bytes {r1n[BYTES]:.0f} -> "
                f"{n[BYTES]:.0f} -> {p[BYTES]:.0f}")

    reach_clauses = []
    for a in decl["adapters"]:
        if reach[a] == 0:
            reach_clauses.append(
                f"for {a} a piece of the load never reached the door")
        else:
            reach_clauses.append(
                f"{a}: a piece of the load reached the door on {reach[a]} of "
                f"{len(items)} items")

    finding = (
        "At the declared 600-char door on the same 5 frozen items and "
        "adapters, rung 2's query-adjacent load (>= "
        f"{decl['pressure']['tool_output_bytes']} bytes/item against rung 1's "
        "declared 20000, chunks sharing each item's query vocabulary): "
        + "; ".join(clause(a) for a in decl["adapters"])
        + " (each cell reads normal -> normal -> pressure: rung 1, rung 2 "
        "unloaded, rung 2 loaded). Reach: "
        + "; ".join(reach_clauses)
        + ". The load competed for relevance by declaration; what that "
        "competition did to the door is what the rung-2 cells above show. "
        "The two numbers stay separate: evidence presence says "
        "was-it-handed, irrelevant delivered bytes says how much came with "
        "it.")

    verdict = {
        "finding": finding,
        "prior": ("rung 1: team/S8-DOOR/verdict.json and "
                  "team/S8-DOOR/results.jsonl, VERIFIED PASS 2026-09-18; its "
                  "cells are quoted verbatim in rung1 and re-measured here "
                  "as rung2 under the harsher query-adjacent load declared "
                  "in declaration.json"),
        "budget_chars": budget,
        "per_adapter": per,
    }
    (HERE / "verdict.json").write_text(
        json.dumps(verdict, indent=1) + "\n", encoding="utf-8")
    for a in decl["adapters"]:
        print(f"{a}: rung2 normal {rung2[(a, 'normal')][PRESENCE]:.2f}/"
              f"{rung2[(a, 'normal')][BYTES]:.0f} pressure "
              f"{rung2[(a, 'pressure')][PRESENCE]:.2f}/"
              f"{rung2[(a, 'pressure')][BYTES]:.0f}, "
              f"load reached the door on {reach[a]}/{len(items)} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
