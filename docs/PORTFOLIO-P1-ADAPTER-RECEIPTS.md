# PORTFOLIO P1 — per-adapter unit receipts (accumulating)

One section per portfolio adapter, per charter P1 ("per-adapter unit
receipts"). Receipts claim; state is — every receipt cites the exact test
run. Statuses: RECEIPTED (green) / PENDING / DROPPED-BY-NAME.

## agentmemory — RECEIPTED 2026-09-12 (scope update: IN-PORTFOLIO, Patch 2)

- **Providers in harness:** `agentmemory` (external service path),
  `agentmemory_core_lsa`, `agentmemory_remember_lsa` (controlled cores) —
  `src/memory_bakeoff/providers/agentmemory_core.py`, `external.py`.
- **Test run (this receipt):**
  `PYTHONPATH=/home/bmosher/.local/lib/python3.14/site-packages pytest
  tests/test_agentmemory_core.py tests/test_agentmemory_localization.py -q`
  → **13 passed in 2.67s**.
- **Related suites on record:** `test_agentmemory_gen33_longitudinal.py`,
  `test_agentmemory_gen35_ablation.py`, `test_agentmemory_surface_gen82.py`.
- **Vendor provenance:** `vendor/agentmemory/UPSTREAM.md` — pinned
  `rohitg00/agentmemory` @ `e04ba88819c365c9acf9d6661ea802143e728bd6`.
- **License:** ✅ Apache-2.0 at the pinned commit — fetched receipt
  `docs/PORTFOLIO-P1-discovery/agentmemory-LICENSE.fetch`
  (sha256 `76c8d49ab42216a2533f…`); CLEARED per Corvid's frozen-commit
  verification (P1 = pinned-blob receipt only, GiLMore scope update).
- **Carried scored dimension (charter Patch 2, PROGRAMMATIC):** false-
  supersession rate = retired-without-genuine-replacement ÷ ingested,
  measured from the system's lifecycle/scan surface at ingest end. Recorded
  prior: **418/450 = 92.9%** on the distinct stress slice
  (`STATUS_AND_FINDINGS.md` §lifecycle). Reported beside every agentmemory
  BAR B number as its own table column; does not gate BAR B arithmetic;
  adoption weighting is Brian's P4 call.
- **Phase-1 build status:** adapter already conforms to the shared provider
  interface (`ingest/retrieve/close/configuration`); unit receipts green.
  Remaining for P2: re-assert contract pins at run time per the harness spec
  (nothing to write).

## Perseus vault (in-orbit anchor) — RECEIPTED (prior record)

- Hit@3 0.434 on the held-out 27-persona dynamic slice (Gen38, frozen);
  memconflict adapter frozen at `627f812d`. Vault-layer receipts current
  (campaign-1 live arm runs the same lineage). No new Phase-1 work.

## bm25 / tfidf_cosine / dense_lsa / hybrid_rrf (baselines) — RECEIPTED (prior record)

- bm25 is row 3's anchor (0.226 dynamic Hit@3, the BAR B floor). Baselines
  run through the same provider interface; no new Phase-1 work.

## pi-lcm store reader (rows 1–2) — PENDING (build assigned: Kiln)

- Reader logic exists (`extensions/pi-project-recall`, 12/12 tests, read-only
  FTS5 + LIKE paths over the pi-lcm sqlite store). Phase-1 work: wrap as a
  provider conforming to `ingest/retrieve` (ingest = no-op/attach existing
  store; retrieve = the same queries minus the conversation filter), plus
  unit receipt. NOT STARTED this receipt.

## long-context null (row 18/row 4) — RECEIPTED 2026-09-12

- Engine-contract suite `tests/test_longcontext_null_contract.py`: 7 tests
  green first run (ingestion-order passthrough, question never consulted, no
  imputed scores, limit-as-ceiling, snapshot no-ops, inventory honesty, token
  accounting). Suite `tests/test_longcontext_null_contract.py` +
  `tests/test_stale_use_penalty.py` = 15 passed in 0.07s on this host
  (PYTHONPATH note in the commit message). Remaining: compose into the
  memconflict run as an arm (runner composition, next build turn).

## letta / langmem / a_mem / memobase / memos (upstream harnesses) — PENDING

- Prerequisite: materialize `external/MemConflict` (182 MB, pinned
  `ec51d5d`, dataset sha `8ef9ec…`) — not yet started. Provisioning is
  "run the benchmark's own shipped harness", not adapter authoring.

## native capture (pi native remember/admission) — RECEIPTED AS INERT (prior record)

- Measured INERT as an admission path (`team/PROBE-remember-admission-FINDINGS.md`,
  DO NOT MIGRATE); included in the portfolio's "ours" column only; stays out
  unless campaign-C repairs it.
