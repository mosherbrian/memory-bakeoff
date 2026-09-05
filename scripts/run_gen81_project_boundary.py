#!/usr/bin/env python3
"""Gen81: where does agentmemory's project boundary disappear?

Gen80 showed `project` does not separate configurations inside one agent. This
localises the loss. Two projects, one fixed `agentId`, one distinct marker each:

1. write marker A to project A and marker B to project B, recording the exact
   request bodies sent;
2. read the stored records back and check whether `project` survived ingestion
   at all;
3. query each project separately and see what comes back.

Three outcomes are distinguishable, and the point is to tell them apart rather
than to fix anything:

- **write-time loss** - the stored record carries no project, so no search could
  ever filter on it;
- **search-time ignoring** - the record carries the right project and search
  returns the other one anyway;
- **both** - stored without project *and* unfiltered.

No alternative isolation scheme is attempted.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys, tempfile, time
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results" / "project_boundary_gen81"
PROJECT_A, PROJECT_B = "gen81-project-a", "gen81-project-b"
MARKER_A = "Alpha marker: the rig reading for project A is 111 units."
MARKER_B = "Beta marker: the rig reading for project B is 222 units."


def load(script: str):
    loader = SourceFileLoader(f"frozen_{Path(script).stem}", str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def project_of(row: dict) -> object:
    """Whatever the record calls its project, or a sentinel when it carries none."""
    for key in ("project", "projectId", "project_id", "namespace"):
        if key in row:
            return row[key]
    metadata = row.get("metadata") or {}
    for key in ("project", "projectId", "project_id"):
        if key in metadata:
            return metadata[key]
    return "<absent>"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=int, default=91)
    args = parser.parse_args()

    g33 = load("run_agentmemory_gen33_longitudinal.py")
    g13 = g33.g13
    state = Path(tempfile.mkdtemp(prefix="agentmemory-gen81-", dir="/private/tmp"))
    agent = "gen81-single-agent"
    findings: dict = {"requests": [], "stored": [], "queries": []}
    launcher = None
    try:
        base, _startup, launcher = g13.start_service(g33.AGENTMEMORY, state,
                                                     args.instance, agent)
        for project, marker, tag in ((PROJECT_A, MARKER_A, "A"),
                                     (PROJECT_B, MARKER_B, "B")):
            body = {"agentId": agent, "project": project, "content": marker,
                    "sourceObservationIds": [f"GEN81-{tag}"]}
            findings["requests"].append({"path": "/agentmemory/remember",
                                         "body": body})
            g13.request_json(base, "/agentmemory/remember", body=body)
            time.sleep(0.1)

        rows = g13.isolated_rows(base, agent)
        rows = rows.get("results") or rows.get("memories") or []
        for row in rows:
            findings["stored"].append({
                "id": row.get("id"),
                "sourceObservationIds": row.get("sourceObservationIds"),
                "project_field": project_of(row),
                "keys_present": sorted(row)[:20],
            })

        for project, tag in ((PROJECT_A, "A"), (PROJECT_B, "B")):
            body = {"agentId": agent, "project": project,
                    "query": "rig reading units", "limit": 5}
            findings["requests"].append({"path": "/agentmemory/smart-search",
                                         "body": body})
            raw = g13.request_json(base, "/agentmemory/smart-search", body=body)
            returned = []
            for hit in (raw.get("results") or []):
                returned.append({
                    "obsId": hit.get("obsId"),
                    "sourceObservationIds": hit.get("sourceObservationIds"),
                    "content": (hit.get("content") or "")[:70],
                    "project_field": project_of(hit),
                })
            findings["queries"].append({"queried_project": project,
                                        "returned": returned})
    finally:
        try:
            g13.stop_service(g33.AGENTMEMORY, state, args.instance, agent, launcher)
        except Exception:
            pass

    stored_projects = {entry["project_field"] for entry in findings["stored"]}
    project_survives_write = stored_projects and stored_projects != {"<absent>"}

    crossed = False
    for query in findings["queries"]:
        wanted = "A" if query["queried_project"] == PROJECT_A else "B"
        for hit in query["returned"]:
            sources = hit.get("sourceObservationIds") or []
            if any(s and not s.endswith(wanted) for s in sources):
                crossed = True

    if not project_survives_write and crossed:
        verdict = "BOTH"
        why = ("the stored record carries no project field, so no search could "
               "filter on it, and search returns the other project's marker")
    elif not project_survives_write:
        verdict = "WRITE_TIME_LOSS"
        why = ("the stored record carries no project field; the boundary is lost "
               "at ingestion, before any query is asked")
    elif crossed:
        verdict = "SEARCH_TIME_IGNORING"
        why = ("the stored record carries the right project and search returns "
               "the other one anyway")
    else:
        verdict = "NO_CROSSING_OBSERVED"
        why = "each query returned only its own project's marker"

    payload = {
        "engine": "agentmemory", "generation": 81,
        "design": "two projects, ONE fixed agentId, one distinct marker each",
        "no_alternative_schemes_tried": True,
        "project_survives_write": bool(project_survives_write),
        "stored_project_values": sorted(str(p) for p in stored_projects),
        "cross_project_results_returned": crossed,
        "verdict": verdict, "why": why,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **findings,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "boundary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: payload[k] for k in
                      ("verdict", "why", "project_survives_write",
                       "stored_project_values", "cross_project_results_returned")},
                     indent=1))
    for query in findings["queries"]:
        print(query["queried_project"], "->",
              [h["sourceObservationIds"] for h in query["returned"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
