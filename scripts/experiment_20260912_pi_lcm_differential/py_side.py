"""Differential harness, Python side: runs the ported query_messages over
the SAME store file ts_side.ts built. Normalized output must be
byte-identical to receipts/ts-hits.json (see RUN-AS-COMMITTED.md)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from memory_bakeoff.providers.pi_lcm_store_reader import _connect_read_only, query_messages

QUERIES = ["ledger convention", "docker compose", "helm kite", "deploy", "the", "zzz-nothing"]

here = Path(__file__).resolve().parent
con = _connect_read_only(here / "receipts" / "differential.db")
out = {}
for q in QUERIES:
    out[q] = [
        {"source": h["source"], "conversation_id": h["conversation_id"], "role": h["role"], "snippet": h["snippet"]}
        for h in query_messages(con, q, 5)
    ]
(here / "receipts" / "py-hits.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
con.close()
print("py-side done:", len(QUERIES), "queries")
