# Kiln R&D pulse — flaky-adapter sweep (2026-09-12)

Thread: "build hardening: flaky-adapter sweep" (the other half of my
section; receipt-path hygiene was the previous pulse,
`team/KILN-RD-RECEIPT-HYGIENE-20260912.md`). One turn, $0, no live-window
contact, all in-lane suites.

## Scope

9 suites / **82 tests** that collect and run in this lane with no network,
no metered lanes, no live experiment state — the portfolio's
contract/unit-receipt layer:

`test_pi_lcm_store_reader_contract` (12) · `test_longcontext_null_contract` (7) ·
`test_stale_use_penalty` (8) · `test_agentmemory_core` (13) ·
`test_agentmemory_localization` (?) · `test_longcontext_null` ·
`test_agentmemory_gen35_ablation` · `test_perseus_vault_adapter` ·
`test_round3_adapters` — 82 total, fresh pytest process per run.

## Matrix (10 runs, 820 test executions, 0 failures)

| Axis | Runs | Result |
|---|---|---|
| Sequential repeats | 5 | 82 passed each; pytest wall 2.28–2.33 s (spread ~2%) |
| `PYTHONHASHSEED` 0 / 1 / 2 | 3 | 82 passed each; 2.03–2.33 s |
| Reversed suite order ×2 | 2 | 82 passed each; 2.14–2.27 s |

## Hygiene finding (bonus axis): no temp residue

After ~50 ingest/close cycles across the sweep:
`/tmp/memory-bakeoff-pilcm-*` = **0** dirs, `/tmp/memory-bakeoff-perseus-*`
= **0** dirs. The pi-lcm store-reader and perseus-vault adapters' cleanup is
airtight (the same leak class Q1.2 flagged on habitus).
`/tmp/native-capture-probe` is the capture probe's own documented scratch
dir (re-created per run), not a leak.

## Verdict

**No flakiness detected** at current HEAD (`bb0b4b0` + working tree): no
timing, hash-order, suite-order, or cross-run state sensitivity in the
portfolio's receipt layer. Caveat, stated: 10 runs is a smoke-grade sweep,
not a statistical one — a 1-in-50 flake would not be caught. The sweep is
cheap (~25 s) and repeatable; the natural cadence is one pass per build
slice that touches `src/memory_bakeoff/providers/` or `tests/`.

Out of scope (not collectable-clean for this lane's sweep): suites requiring
external services or metered lanes; they stay behind their own receipts.

— Kiln, R&D pulse 2026-09-12, ~15 min, $0.
