#!/usr/bin/env python3
"""Gen33 preflight: does agentmemory's write-time supersession fire, and what does it leave behind?

Unrelated synthetic domain only. Validates the pinned rule against live native
behaviour before any scored exposure.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys, tempfile, time
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
loader = SourceFileLoader("g13", str(ROOT / "scripts/run_agentmemory_gen13.py"))
spec = importlib.util.spec_from_loader("g13", loader)
g13 = importlib.util.module_from_spec(spec)
loader.exec_module(g13)

AGENTMEMORY = ROOT / "external/agentmemory"
PROJECT = "gen33-preflight"

# Unrelated synthetic domain. Designed to straddle the >0.7 lexical threshold.
WRITES = [
    ("S001", "Greenhouse bench alpha humidity target measured 55 percent."),
    # two-character difference only: mirrors a config-labelled pair without any fixture vocabulary
    ("S002", "Greenhouse bench alpha humidity target measured 62 percent."),
    ("S003", "The orchard irrigation controller runs a dawn cycle on weekdays."),
    ("S004", "Seedling trays use a coarse perlite blend for drainage."),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None)
    ap.add_argument("--instance", type=int, default=7)
    args = ap.parse_args()

    state = Path(tempfile.mkdtemp(prefix="agentmemory-gen33-preflight-", dir="/private/tmp"))
    agent = "memory-bakeoff-gen33-preflight"
    findings: dict = {"state_dir": str(state), "agent_id": agent, "project": PROJECT}
    launcher = None
    try:
        base, startup, launcher = g13.start_service(AGENTMEMORY, state, args.instance, agent)
        findings["startup"] = startup
        writes = []
        for record_id, content in WRITES:
            response = g13.request_json(base, "/agentmemory/remember", body={
                "agentId": agent, "project": PROJECT, "content": content,
                "sourceObservationIds": [record_id],
            })
            writes.append({"record_id": record_id, "response": response})
            time.sleep(0.1)
        findings["writes"] = writes

        rows = g13.isolated_rows(base, agent)
        memories = rows.get("results") or rows.get("memories") or []
        findings["memory_rows"] = [{
            "id": m.get("id"), "obsId": m.get("obsId"),
            "sourceObservationIds": m.get("sourceObservationIds"),
            "isLatest": m.get("isLatest"), "version": m.get("version"),
            "parentId": m.get("parentId"), "supersedes": m.get("supersedes"),
            "content": (m.get("content") or "")[:70],
        } for m in memories]
        findings["row_count"] = len(memories)
        superseded = [m for m in findings["memory_rows"] if m["isLatest"] is False]
        findings["superseded_rows"] = superseded
        findings["supersession_fired"] = bool(superseded)
        findings["supersession_count"] = len(superseded)

        search = g13.request_json(base, "/agentmemory/smart-search", body={
            "agentId": agent, "project": PROJECT, "query": "bench alpha humidity target", "limit": 5})
        results = search.get("results", [])
        findings["search_hits"] = [{"obsId": r.get("obsId"), "content": (r.get("content") or "")[:60]} for r in results]
        visible = {r.get("obsId") for r in results}
        findings["superseded_still_in_kv"] = all(m["id"] for m in superseded) if superseded else None
        findings["superseded_absent_from_search"] = (
            all(m["sourceObservationIds"] and m["sourceObservationIds"][0] not in visible for m in superseded)
            if superseded else None)
    finally:
        if launcher is not None:
            findings["shutdown"] = g13.stop_service(AGENTMEMORY, state, args.instance, agent, launcher)

    out = json.dumps(findings, indent=2, sort_keys=True, default=str)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(out + "\n")
        print("wrote", args.out)
        print(" rows:", findings.get("row_count"), "| supersession fired:", findings.get("supersession_fired"),
              "| count:", findings.get("supersession_count"))
        for m in findings.get("superseded_rows", []):
            print("   superseded:", m["sourceObservationIds"], "isLatest", m["isLatest"], "version", m["version"])
        for m in findings.get("memory_rows", []):
            print("   row:", m["sourceObservationIds"], "v", m["version"], "latest", m["isLatest"],
                  "supersedes", m["supersedes"])
        print(" superseded still in KV:", findings.get("superseded_still_in_kv"),
              "| absent from search:", findings.get("superseded_absent_from_search"))
        print(" search hits:", [h["obsId"] for h in findings.get("search_hits", [])])
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
