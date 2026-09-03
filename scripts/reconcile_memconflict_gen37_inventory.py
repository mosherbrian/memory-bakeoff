#!/usr/bin/env python3
"""Gen37: reconcile what each product actually holds against what we wrote.

Runs AFTER the calibration passes, read-only, against the persisted stores.

Mem0's `get_all()` takes `top_k`, which defaults to 20 and ignores a `limit`
kwarg, so the count captured during the run is a page size rather than an
inventory. The true count is read here from the vector store itself.
"""
from __future__ import annotations

import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict_engines as E
from memory_bakeoff.round2_reporting import ReportingError


def perseus_count(state_dir: Path, persona_id: str) -> dict:
    db = state_dir / f"perseus-{persona_id}" / "vault.sqlite"
    if not db.exists():
        raise ReportingError(f"perseus store missing for {persona_id}: {db}")
    stats = json.loads(subprocess.run([str(E.PERSEUS_BIN), "stats", "--db", str(db)],
                                      text=True, capture_output=True, check=True).stdout)
    return {"source": "perseus-vault stats --db", "active_entities": stats["active_entities"],
            "total_entities": stats["total_entities"], "archived": stats["archived_entities"],
            "journal_events": stats["total_journal_events"]}


def mem0_count(state_dir: Path, persona_id: str) -> dict:
    from qdrant_client import QdrantClient

    path = state_dir / f"mem0-{persona_id}" / "qdrant"
    if not path.exists():
        raise ReportingError(f"mem0 store missing for {persona_id}: {path}")
    client = QdrantClient(path=str(path))
    try:
        collections = [c.name for c in client.get_collections().collections]
        counts = {name: client.count(collection_name=name, exact=True).count for name in collections}
    finally:
        client.close()
    return {"source": "qdrant client.count(exact=True)", "collections": counts,
            "points": sum(counts.values())}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default=str(ROOT / "results/memconflict_gen37_calibration"))
    ap.add_argument("--perseus-state", required=True)
    ap.add_argument("--mem0-state", required=True)
    args = ap.parse_args()

    base = Path(args.results)
    out: dict[str, dict] = {}
    problems: list[str] = []
    for engine, state_root, counter in (("perseus", Path(args.perseus_state), perseus_count),
                                        ("mem0", Path(args.mem0_state), mem0_count)):
        directory = base / engine
        if not directory.is_dir():
            continue
        out[engine] = {}
        for leaf_path in sorted(directory.glob("persona-*.json")):
            leaf = json.loads(leaf_path.read_text())
            persona_id = leaf["persona_id"]
            written = leaf["operations"]["distinct_native_ids"]
            native = counter(state_root, persona_id)
            held = native.get("active_entities", native.get("points"))
            row = {"written": written, "native_held": held, "difference": written - held,
                   "native_evidence": native,
                   "write_actions": leaf["operations"]["write_actions"]}
            if held != written:
                explained = [action for action in leaf["operations"]["write_actions"]
                             if action != "created" and action != "ADD"]
                row["explained_by_native_actions"] = explained
                if not explained:
                    problems.append(f"{engine}/{persona_id}: {written - held} records unaccounted for")
            out[engine][persona_id] = row

    payload = {"reconciliation": out, "unexplained": problems,
               "note": "mem0 leaf inventory 'points' is get_all's top_k page size (default 20), "
                       "not a store count; the count here comes from the vector store itself"}
    (base / "inventory-reconciliation.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    for engine, rows in out.items():
        for persona_id, row in rows.items():
            print(f"{engine} {persona_id[:12]}: wrote {row['written']}, holds {row['native_held']}, "
                  f"difference {row['difference']} {row.get('explained_by_native_actions', '')}")
    if problems:
        raise SystemExit("inventory could not be reconciled: " + "; ".join(problems))
    print("inventory reconciled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
