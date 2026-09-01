#!/usr/bin/env python3
"""Run a small chronological, non-scored agentmemory lifecycle diagnostic.

The script uses only documented REST endpoints and preserves raw native responses
and a full live-memory snapshot after every write.  It is intentionally not a
benchmark scorer: callers supply a new output directory and evaluate the trace
against harness truth separately.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from memory_bakeoff.corpus import build_corpus


def request_json(base_url: str, path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    try:
        with urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"agentmemory request failed for {method} {path}: {exc}") from exc


def live_snapshot(base_url: str, project: str) -> dict:
    # This pin's list endpoint accepts `project` but does not apply it to the
    # returned rows.  Preserve the raw response and derive the operation-local
    # snapshot from the stored native project field instead of trusting that
    # query parameter as isolation.
    raw = request_json(base_url, "/agentmemory/memories?" + urlencode({"project": project}))
    rows = raw.get("memories", [])
    if not isinstance(rows, list):
        raise RuntimeError(f"agentmemory memories response is not a list: {raw!r}")
    memories = [memory for memory in rows if memory.get("project") == project]
    return {
        "requested_project": project,
        "server_response": raw,
        "memories": memories,
        "total": len(memories),
        "live_count": sum(memory.get("isLatest") is not False for memory in memories),
        "retired_count": sum(memory.get("isLatest") is False for memory in memories),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:3111")
    parser.add_argument("--project", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.out.exists():
        raise SystemExit(f"refusing to overwrite existing output directory: {args.out}")
    args.out.mkdir(parents=True)

    corpus_records, _ = build_corpus()
    records = {record.id: record for record in corpus_records}
    operations = [
        ("old_build_coordinator", "M011", records["M011"].text),
        ("explicit_correction", "M012", records["M012"].text),
        ("exact_duplicate", "M012", records["M012"].text),
        (
            "paraphrase_of_correction",
            "M012",
            "The authoritative build coordinator is strix07; it replaced strix03.",
        ),
        ("near_neighbor_preview_redis", "M035", records["M035"].text),
        ("near_neighbor_development_redis", "M036", records["M036"].text),
        ("failed_generated_code_procedure", "M024", records["M024"].text),
        ("successful_generated_code_procedure", "M023", records["M023"].text),
    ]

    trace = {
        "diagnostic": "agentmemory_raw_product_lifecycle_smoke",
        "scored": False,
        "project": args.project,
        "base_url": args.base_url,
        "health_before": request_json(args.base_url, "/agentmemory/health"),
        "config_flags": request_json(args.base_url, "/agentmemory/config/flags"),
        "operations": [],
    }
    for sequence, (label, record_id, content) in enumerate(operations, start=1):
        payload = {
            "project": args.project,
            "content": content,
            "type": "fact",
            "sourceObservationIds": [record_id],
        }
        response = request_json(args.base_url, "/agentmemory/remember", "POST", payload)
        memory = response.get("memory", {})
        if not isinstance(memory.get("id"), str) or memory.get("sourceObservationIds") != [record_id]:
            raise RuntimeError(
                f"native provenance failed at {label}: expected one sourceObservationId {record_id}, got {memory!r}"
            )
        trace["operations"].append(
            {
                "sequence": sequence,
                "label": label,
                "canonical_record_id": record_id,
                "payload": payload,
                "native_response": response,
                "live_snapshot": live_snapshot(args.base_url, args.project),
            }
        )

    queries = [
        "What is the current build coordinator?",
        "Which Redis database does the preview environment use?",
        "What workflow succeeded for stale generated Go code?",
    ]
    trace["searches"] = [
        {
            "query": query,
            "native_response": request_json(
                args.base_url,
                "/agentmemory/smart-search",
                "POST",
                {"project": args.project, "query": query, "limit": 5, "includeLessons": False},
            ),
        }
        for query in queries
    ]
    (args.out / "trace.json").write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
