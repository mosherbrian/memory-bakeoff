#!/usr/bin/env python3
"""Gen32 preflight: what Mem0 2.0.19 raw infer=False actually does.

Unrelated synthetic domain only. Determines semantics; never tunes scoring.
"""
from __future__ import annotations

import argparse, json, os, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
UPSTREAM = ROOT / "external/mem0"
if str(UPSTREAM) not in sys.path:
    sys.path.insert(0, str(UPSTREAM))

USER = "memory-bakeoff"
GH, ORCH = "site:greenhouse", "site:orchard"

ITEMS = [
    ("Q001", "Greenhouse bench A humidity target is 55 percent.", "2026-01-10T00:00:00+00:00", GH),
    ("Q002", "Greenhouse bench B humidity target is 62 percent.", "2026-01-12T00:00:00+00:00", GH),
    ("Q003", "Audit corrected bench A humidity: the valid target was 58 percent, not 55 percent.", "2026-01-20T00:00:00+00:00", GH),
    ("Q004", "Recovered log: bench A ran the coarse perlite mix on 2026-01-05.", "2026-01-05T00:00:00+00:00", GH),
    ("Q005", "The orchard drip schedule failed without a prewarm cycle.", "2026-01-23T00:00:00+00:00", ORCH),
    ("Q006", "The orchard drip schedule succeeded with a prewarm cycle and fixed interval.", "2026-01-24T00:00:00+00:00", ORCH),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    from importlib.metadata import version
    from mem0 import Memory
    import mem0, fastembed, qdrant_client, onnxruntime

    temp = tempfile.TemporaryDirectory(prefix="gen32-preflight-", dir="/private/tmp")
    qpath = str(Path(temp.name) / "qdrant")
    config = {
        # Mem0 constructs an LLM client at init even for infer=False; Gen10 used a
        # placeholder key for exactly this reason. It is never called on the raw path.
        "llm": {"provider": "openai", "config": {"api_key": "not-used-in-raw-mode"}},
        "embedder": {"provider": "fastembed", "config": {"model": "thenlper/gte-large", "embedding_dims": 1024}},
        "vector_store": {"provider": "qdrant", "config": {"path": qpath, "collection_name": "preflight",
                                                          "embedding_model_dims": 1024, "on_disk": True}},
        "history_db_path": str(Path(qpath) / "history.db"),
    }
    findings = {"versions": {"mem0ai": version("mem0ai"), "fastembed": fastembed.__version__,
                             "qdrant_client": version("qdrant-client"), "onnxruntime": onnxruntime.__version__,
                             "onnx_providers": onnxruntime.get_available_providers()},
                "spacy_present": False}
    try:
        import spacy  # noqa: F401
        findings["spacy_present"] = True
    except ImportError:
        pass

    memory = Memory.from_config(config)

    # Prove the raw path makes no outbound call rather than asserting it.
    import socket
    real_socket, real_connect = socket.socket, socket.create_connection

    def _refuse(*a, **k):
        raise AssertionError("raw infer=False path must not open a socket")

    added = []
    for marker, text, ts, scope in ITEMS:
        result = memory.add(text, user_id=USER, infer=False,
                            metadata={"record_id": marker, "source_ref": f"src-{marker}", "scope": scope, "timestamp": ts})
        added.append({"marker": marker, "result": json.loads(json.dumps(result, default=str))})
    findings["add_results"] = added
    socket.socket, socket.create_connection = _refuse, _refuse
    try:
        probe = memory.add("A spare synthetic note about bench humidity.", user_id=USER, infer=False,
                           metadata={"record_id": "Q007", "source_ref": "src-Q007", "scope": GH,
                                     "timestamp": "2026-01-26T00:00:00+00:00"})
        findings["raw_add_makes_no_network_call"] = True
        added.append({"marker": "Q007", "result": json.loads(json.dumps(probe, default=str))})
    except AssertionError as exc:
        findings["raw_add_makes_no_network_call"] = False
        findings["network_call_detail"] = str(exc)
    finally:
        socket.socket, socket.create_connection = real_socket, real_connect

    everything = memory.get_all(filters={"user_id": USER})
    rows = everything.get("results") if isinstance(everything, dict) else everything
    findings["point_count_after_6_adds"] = len(rows or [])
    findings["stored_payload_sample"] = json.loads(json.dumps((rows or [None])[0], default=str))
    expected_adds = len(ITEMS) + (1 if findings.get("raw_add_makes_no_network_call") else 0)
    findings["expected_adds"] = expected_adds
    findings["dedup_or_merge_on_add"] = len(rows or []) != expected_adds

    def search(label, query, extra_filters=None, **kw):
        filters = {"user_id": USER}
        if extra_filters:
            filters.update(extra_filters)
        try:
            raw = memory.search(query, filters=filters, limit=5, threshold=0.1, **kw)
            hits = raw.get("results") if isinstance(raw, dict) else raw
            findings[label] = [{"record_id": (h.get("metadata") or {}).get("record_id"),
                                "score": h.get("score"), "id": h.get("id")} for h in (hits or [])]
        except Exception as exc:
            findings[label] = {"error": f"{type(exc).__name__}: {exc}"[:200]}
        return findings[label]

    search("search_plain", "bench A humidity target")
    search("search_repeat", "bench A humidity target")
    findings["reads_identical_on_repeat"] = findings["search_plain"] == findings["search_repeat"]
    search("search_scope_orchard", "drip schedule prewarm cycle")
    search("search_negative", "wind turbine gearbox lubrication schedule")
    search("search_backdated", "perlite mix bench A")

    # capability probe only, NOT the scored identity
    search("capability_metadata_filter", "humidity target", extra_filters={"scope": GH})

    findings["temporal_api_surface"] = sorted(
        name for name in dir(memory)
        if any(token in name.lower() for token in ("time", "as_of", "history", "temporal", "date")))
    findings["public_mutation_apis_not_used"] = sorted(
        name for name in dir(memory) if name in ("update", "delete", "delete_all", "history", "reset"))

    after = memory.get_all(filters={"user_id": USER})
    after_rows = after.get("results") if isinstance(after, dict) else after
    history_db = Path(qpath) / "history.db"
    findings["history_db_present"] = history_db.exists()
    if history_db.exists():
        import sqlite3
        con = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
        try:
            tables = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
            findings["history_tables"] = tables
            findings["history_row_counts"] = {t: con.execute(f"select count(*) from {t}").fetchone()[0] for t in tables}
        finally:
            con.close()
    findings["point_count_after_searches"] = len(after_rows or [])
    findings["searches_changed_point_count"] = findings["point_count_after_6_adds"] != findings["point_count_after_searches"]

    out = json.dumps(findings, indent=2, sort_keys=True, default=str)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(out + "\n")
        print("wrote", args.out)
        print(" versions:", json.dumps(findings["versions"]))
        print(" no network on raw add:", findings.get("raw_add_makes_no_network_call"))
        print(" points:", findings["point_count_after_6_adds"], "of", findings["expected_adds"], "expected | dedup/merge:", findings["dedup_or_merge_on_add"])
        print(" reads identical:", findings["reads_identical_on_repeat"], "| searches changed count:", findings["searches_changed_point_count"])
        print(" temporal api surface:", findings["temporal_api_surface"])
        print(" history rows:", findings.get("history_row_counts"))
        for k in ("search_plain", "search_backdated", "search_negative", "capability_metadata_filter"):
            print(" ", k, "->", json.dumps(findings[k])[:170])
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
