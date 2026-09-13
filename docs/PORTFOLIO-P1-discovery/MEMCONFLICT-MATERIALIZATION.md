# MemConflict dataset materialization receipt (2026-09-13, Kiln)

The P2 prerequisite named in the charter and the adapter receipts file is
CLEARED: `external/MemConflict` is materialized, gitignored (uncommitted,
local only), and triple-pinned against the frozen contract in
`src/memory_bakeoff/memconflict.py`.

## Pins (all verified)

| Pin | Frozen value | Measured |
|---|---|---|
| upstream commit | `ec51d5d36e87f7665d1337f3a88cbde95fc2a964` | HEAD after checkout: identical |
| dataset git blob (`Data/Step4_4.jsonl`) | `6dcbf9e536ea3e5d52f015ba75b15bdcd3377c94` | `git ls-tree HEAD` — identical |
| dataset sha256 | `8ef9ec8589eccb86f63ab3a819a9180217405351a8d5846866721ea74babe092` | `sha256sum` — identical |

Source: `git clone https://github.com/TaoZhen1110/MemConflict
external/MemConflict` + `git checkout ec51d5d…` (upstream repo/commit
taken verbatim from `UPSTREAM_REPO`/`UPSTREAM_COMMIT` in
`src/memory_bakeoff/memconflict.py` — no URLs guessed). Size on disk:
183 MB. The dataset does NOT enter git (`external/` is ignored).

## Consequences (all measured, same turn)

- Adapter-side loader: `memory_bakeoff.memconflict.dataset_sha256()`
  returns the pinned sha; `load_personas()` loads **30 personas**.
- Dataset-dependent contract suites heal: gen36_contract + gen37_products
  + gen38_full_release = **61/61 passed**.
- `tests/KNOWN_FAILURES.json` pruned per its own rule (a listed failure
  that now passes must be removed): `memconflict_dataset_absent` (16) and
  `memconflict_collection_errors` (5) removed, with provenance in the
  file's `_pruned` block. Post-prune sentinel run (whole-suite
  subprocess): **5 passed** — zero unlisted failures, zero stale entries.
- Post-prune suite state (measured): **10 failed / 1621 passed / 3
  skipped / 0 errors** — the remaining red is exactly the recorded red
  (membukkit recorded-run provenance ×8; gen119 attempt19 frozen-source
  drift ×2, clears at attempt20).

P2 entry is now unblocked: the run matrix can compose arms by the
declared names in `src/memory_bakeoff/portfolio.py` against the real
benchmark dataset.

— Kiln, 2026-09-13. $0 (disk only). No LLM, no service.
