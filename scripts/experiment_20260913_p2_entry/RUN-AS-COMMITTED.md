# RUN-AS-COMMITTED

Run from repo root, canonical environment:

    PYTHONPATH=/home/bmosher/.local/lib/python3.14/site-packages:src:vendor/membukkit/src \
    python3 scripts/experiment_20260913_p2_entry/run_p2_entry.py

- Gate: `portfolio.assert_run_pins()` runs FIRST (dataset sha256, upstream
  checkout HEAD, adapter probes); pins echoed to `results/p2_entry_20260913/pins.json`.
- State coupling: **SCRATCH + LOCAL DATASET** (reads external/MemConflict,
  writes only results/p2_entry_20260913/). No LLM, no network, $0.
- Protocol (frozen contract): heldout 27 personas (frozen list from
  results/memconflict_gen38_full_release/heldout-27-derived.json);
  chronology = ingest session i then ask session i's questions (sessions
  APPEND via the provider append mode); query = released text only; gold
  is scorer-only; credit by session identity (first_support_rank);
  measured/unmeasured/measured-zero kept separate; top_k=5, primary k=3.
- Arms: pi_lcm_store_reader_toollevel (the actual tool: exact query then
  bounded relaxation, verbatim relaxedVariants port, reach-prior rule) /
  pi_lcm_store_reader (raw, no relaxation — charter row 2's A/B) /
  pi_lcm_history_null / longcontext_null (engine seam).
- First executed run: 2026-09-13 — see results/p2_entry_20260913/summary.json.
  Internal consistency receipt: the two null arms (provider passthrough vs
  engine seam) produced byte-identical aggregates.
