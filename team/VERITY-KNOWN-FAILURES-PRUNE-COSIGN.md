# Verity co-sign — KNOWN_FAILURES.json prune (QUEUE row 29)

**Co-sign: PASS.** The landed prune (implementer/repo commit `c30e8fa`,
2026-09-13 00:47 PDT, executed by Kiln) does exactly what its `_pruned`
provenance block and the queue row claim, and the post-prune baseline state
reproduces. All four asks re-derived independently; $0, no LLM, no writes to
the implementer tree (`-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`,
`external/MemConflict` status clean after all runs).

## 1. The 21 removed ids pass with the dataset present

Ran the three MemConflict suites (a superset of the 21 removed ids — all 21
live in these files per the c30e8fa diff):

```
PYTHONPATH=src:vendor/membukkit/src:<user-site> python3 -m pytest -q \
  -p no:cacheprovider tests/test_memconflict_gen36_contract.py \
  tests/test_memconflict_gen37_products.py tests/test_memconflict_gen38_full_release.py
→ 61 passed in 7.99s
```

Matches the receipt's "61/61 green". The removed set was exactly
`memconflict_dataset_absent` ×16 (FAILED) + `memconflict_collection_errors`
×5 (ERROR) per the diff — no other cluster touched, membukkit ×8 and gen119
×2 preserved verbatim.

## 2. The 10 remaining ids still fail — exactly those, no more

```
python3 -m pytest -q -p no:cacheprovider tests/test_membukkit_gen41_round1.py \
  tests/test_gen119_run_apparatus.py
→ 10 failed, 42 passed in 3.12s
```

The failing set is byte-identical to the 10 listed node ids (8
membukkit recorded-run provenance + 2 gen119 attempt19 frozen-source drift).
Nothing unlisted failed in either file.

## 3. `_pruned` provenance accurate

Independently re-verified all three pins against the materialized
`external/MemConflict` (not by re-reading Kiln's receipt):

| Pin | Frozen (memconflict.py:27-28 / KNOWN_FAILURES `_pruned`) | Measured |
|---|---|---|
| upstream commit | `ec51d5d36e87f7665d1337f3a88cbde95fc2a964` | `git rev-parse HEAD` — identical |
| dataset blob (`Data/Step4_4.jsonl`) | `6dcbf9e536ea3e5d52f015ba75b15bdcd3377c94` | `git ls-tree HEAD` — identical |
| dataset sha256 | `8ef9ec8589eccb86f63ab3a819a9180217405351a8d5846866721ea74babe092` | `sha256sum` — identical |

Upstream repo/commit are taken verbatim from the frozen contract in
`src/memory_bakeoff/memconflict.py` (lines 27-28), the checkout is clean,
and `docs/PORTFOLIO-P1-discovery/MEMCONFLICT-MATERIALIZATION.md` exists and
agrees with what I measured. The prune arithmetic is internally consistent:
26 failed − 16 = 10 failed; 5 errors − 5 = 0 errors; `_totals` updated to
10/1621/3/0. "Pruned by Kiln per this file's own rule" is accurate — the
file's `_why` demands a listed-then-passing id be removed, and a
dataset-absent failure that heals is exactly that case.

## 4. Sentinel green

```
python3 -m pytest -v -p no:cacheprovider tests/test_known_failures_baseline.py
→ 5 passed in 42.47s
```

The sentinel's module fixture subprocess-runs the whole suite (excluding
itself) and requires run evidence before comparing, so this is not a vacuous
pass: zero unlisted failures, zero stale baseline entries, every cluster
count equals its listed ids, and both guard self-tests pass.

## Disclosures

- Verified at current HEAD `66d1f2b`, not at `c30e8fa` — legitimate because
  `tests/KNOWN_FAILURES.json` has no commits after `c30e8fa`
  (`git log c30e8fa..HEAD -- tests/KNOWN_FAILURES.json` is empty), so the
  reviewed bytes are the landed bytes. The sentinel is content-based (node-id
  sets), so tests added by later commits (miner dedupe work) cannot mask a
  prune defect; they could only add unlisted failures, and none appeared.
- `_totals.passed=1621` is an as-of-`c30e8fa` claim I did not re-count at
  HEAD (HEAD adds later tests); the sentinel's set-equality checks, not the
  count, are what the co-sign stands on.
- Host quirk for future re-runs: pytest 9.0.3 lives in
  `/home/bmosher/.local/lib/python3.14/site-packages` and user-site is not on
  the default path here — add it to PYTHONPATH (same finding as row 27).

— Verity (worker-glm-3), 2026-09-13 21:5x PDT. One turn, flash, $0. Read-only
on the implementer tree per lane rules; this receipt and the QUEUE.md
row-29 status edit are my only writes.
