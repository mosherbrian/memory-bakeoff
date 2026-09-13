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

## pi-lcm store reader (rows 1–2) — RECEIPTED 2026-09-12 (locked baseline arm, Patch 3)

- **Providers in harness:** `pi_lcm_store_reader` (corpus mode — materializes
  the prepared corpus into a fresh temporary store in the exact pi-lcm
  schema, controlled core) and `pi_lcm_store_reader_attach` (read-only attach
  of an existing store, `raw_product`) —
  `src/memory_bakeoff/providers/pi_lcm_store_reader.py`.
- **Ported surface:** `extensions/pi-project-recall` `queryMessages` /
  `querySummaries` verbatim — FTS5 sanitize rule, FTS5 MATCH with the LIKE
  fallback (including its faithful substring-only asymmetry), recency order
  `m.timestamp DESC, m.seq DESC`, no relevance scores — minus the
  current-conversation filter. `as_of` maps to the reader's `before` filter.
  Tool-level relaxation deliberately NOT ported (charter row 2's A/B is
  exactly tool-level vs raw store; recorded in `configuration()`).
- **Canonical identity (corpus mode):** one conversation per distinct
  `record.session_id`; mapping keyed by message rowid in adapter bookkeeping —
  the retrieval decision itself is made only by the ported queries over
  `content_text`. Attach mode returns `record_id=None` (real session text is
  unmappable; provenance honest: exploratory_only) and is byte-unchanged on
  the store file (sha256-checked in tests).
- **Test run (this receipt):**
  `PYTHONPATH=/home/bmosher/.local/lib/python3.14/site-packages pytest
  tests/test_pi_lcm_store_reader_contract.py -q` at commit `2bed095` →
  **12 passed** (canonical mapping, recency-not-relevance order, no imputed
  scores, as_of visibility, LIKE-fallback parity, read-only attach,
  fail-closed lifecycle, top-k ceiling, configuration honesty, sanitize
  parity, registry).
- **No-regression neighbors (same command line, same commit):**
  `test_longcontext_null_contract.py + test_stale_use_penalty.py +
  test_agentmemory_core.py + test_agentmemory_localization.py` → **28
  passed**.
- **Host note:** sqlite 3.50.2, FTS5 native (the LIKE fallback path is also
  tested by disabling it).
- **P2 composition receipt (this slice):** composed at `962f6c6` —
  `src/memory_bakeoff/portfolio.py` declares the three locked baseline arms
  in one place (`LOCKED_BASELINE_ARMS` = longcontext_null engine seam +
  `pi_lcm_store_reader` + `pi_lcm_history_null` provider arms) and
  `validate_composition()` raises on any drift (renamed arm, changed
  experiment class, engine version), so a P2 run cannot silently compose a
  different portfolio. Composition suite `tests/test_portfolio_composition.py`
  **6/6**: declaration-vs-registry, both pi-lcm arms end-to-end through the
  shared harness (`runner.run_provider` on the shared corpus, status ok +
  publishable), history-null passthrough semantics, same-store proof.
  As-committed run at HEAD: composition 6/6 + reader contract 12/12 = **18
  passed**; full sweep rings 1+2 = **471 passed** + the one pre-existing
  documented KNOWN_FAILURES-staleness alarm.
- **Remaining for P2:** the dataset prerequisite is CLEARED (2026-09-13,
  receipt `docs/PORTFOLIO-P1-discovery/MEMCONFLICT-MATERIALIZATION.md`) —
  the run matrix can now compose arms by the declared names in
  `portfolio.py` against the real benchmark dataset. Attach mode remains
  the anchor arm against Brian's real store and is not corpus-scoreable
  by construction.

## long-context null (row 18/row 4) — RECEIPTED 2026-09-12

- Engine-contract suite `tests/test_longcontext_null_contract.py`: 7 tests
  green first run (ingestion-order passthrough, question never consulted, no
  imputed scores, limit-as-ceiling, snapshot no-ops, inventory honesty, token
  accounting). Suite `tests/test_longcontext_null_contract.py` +
  `tests/test_stale_use_penalty.py` = 15 passed in 0.07s on this host
  (PYTHONPATH note in the commit message). Composition: `portfolio.py`
  declares its engine seam (`ENGINE_ARMS`, version-pinned
  `longcontext-null-v1`); the new `pi_lcm_history_null` provider arm
  delegates to `LongContextNull` itself, so the null semantics are literally
  this instrument's code (`962f6c6`).

## letta / langmem / a_mem / memobase / memos (upstream harnesses) — PENDING

- Prerequisite CHANGED 2026-09-13: `external/MemConflict` is now
  MATERIALIZED and triple-pin-verified (commit `ec51d5d…`, blob
  `6dcbf9e5…`, sha256 `8ef9ec…` — receipt
  `docs/PORTFOLIO-P1-discovery/MEMCONFLICT-MATERIALIZATION.md`); the
  dataset-dependent contract suites are green (61/61) and the known-
  failures baseline was pruned accordingly. What remains for these rows
  is provisioning the benchmark's own shipped harnesses (182 MB dataset
  landed; harness provisioning is "run the shipped harness", not adapter
  authoring).

## native capture (pi native remember/admission) — RECEIPTED AS INERT (prior record)

- Measured INERT as an admission path (`team/PROBE-remember-admission-FINDINGS.md`,
  DO NOT MIGRATE); included in the portfolio's "ours" column only; stays out
  unless campaign-C repairs it.
