# RUN-AS-COMMITTED

- `bun ts_side.ts` (from this dir) — builds `receipts/differential.db` with
  the extension's own `createSchema`/`seedConversation`, runs the
  extension's `queryMessages`, writes `receipts/ts-hits.json`.
- `PYTHONPATH=/home/bmosher/.local/lib/python3.14/site-packages python3 py_side.py` — runs the PORTED `query_messages` over the same
  store file, writes `receipts/py-hits.json`.
- `diff receipts/ts-hits.json receipts/py-hits.json` — **must be empty**.
- State coupling: **SCRATCH** (this dir's receipts only). Covers the FTS5
  MATCH path on this host (sqlite 3.50.2, FTS5 native); the LIKE fallback
  path is parity-tested in `tests/test_pi_lcm_store_reader_contract.py`.
  Masked as display-only: JS `toISOString` vs Python `isoformat` timestamp
  strings.
