# RUN-AS-COMMITTED

Run from THIS directory (`scripts/experiment_20260912_pi_lcm_differential/`);
all receipt paths below are relative to it.

1. `bun ts_side.ts` — builds `receipts/differential.db` with the extension's
   own `createSchema`/`seedConversation` (pilot_store.ts) and runs the
   extension's `queryMessages`; writes `receipts/ts-hits.json`.
   IDEMPOTENT: the store is removed before each run (Assay's QUEUE-row-27
   finding — it previously died on UNIQUE(session_id) when re-run).
2. `PYTHONPATH=/home/bmosher/.local/lib/python3.14/site-packages python3 py_side.py`
   — runs the PORTED `query_messages` over the same store file; writes
   `receipts/py-hits.json`.
3. `diff receipts/ts-hits.json receipts/py-hits.json` — **must be empty**.

- State coupling: **SCRATCH** (this dir's receipts only). Covers the FTS5
  MATCH path (host sqlite 3.50.2, FTS5 native); the LIKE fallback path is
  parity-tested in `tests/test_pi_lcm_store_reader_contract.py`.
- Masked as display-only: JS `toISOString` vs Python `isoformat` timestamp
  strings.
- bun note: bun 1.3.13 lacks `node:sqlite`, hence `bun:sqlite` here (the
  extension's own driver detection makes the same choice).
