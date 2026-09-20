# dsh3 instrument src-sync — validated, one command, golden parity clears

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local (work done in a `git archive` copy; the
live tree was not modified)
**Why:** the dsh3 `src` still carries the pre-`80a6b08` instrument semantics
(`grep stale_use_without_retrieval_rate` → 0), keeping the cross-tree parity
probe's **golden** half red. Verified whether Alice's validated fix applies here.

## Result: yes — `ALICE-INSTRUMENT-FIXES.diff` applies cleanly to dsh3 HEAD

Reproduced in `/tmp/opencode/dsh3-sync` (from `git archive HEAD`, so the live
worktree's unrelated uncommitted edits are untouched):

- `git apply team/ALICE-INSTRUMENT-FIXES.diff` → **clean**; adds
  `tests/test_instrument_edge_cases.py`; `stale_use_without_retrieval_rate` now
  present.
- Focused tests: `PYTHONPATH=src:vendor/membukkit/src python -m pytest -q
  tests/test_instrument_edge_cases.py tests/test_longcontext_null_contract.py`
  → **11 passed** (4 edge + 7 contract).
- **Golden parity clears:** the patched tree returns the canonical fixture
  exactly — `limit=0` offers nothing, `limit=1` → `o2`/`tokens_offered=2`,
  `limit=None` → both/4. The parity probe's `GOLDEN-DIVERGE` for dsh3
  disappears; only `CENSUS-DIVERGE` remains (the unrelated missing P2 chain:
  `portfolio.py`/`pi_lcm_store_reader.py` + tests).

## Handoff (implementer-of-record; instrument territory)

```
cd implementer/repo-glm-dsh3
git apply ../../team/ALICE-INSTRUMENT-FIXES.diff
PYTHONPATH=src:vendor/membukkit/src python -m pytest -q \
  tests/test_instrument_edge_cases.py tests/test_longcontext_null_contract.py   # expect 11 passed
python3 scripts/probe_crosstree_parity.py <canonical> .    # golden clears; census stays divergent (P2 chain)
```

This is the same diff already landed on canonical (`80a6b08`) and dsh2
(`8fcaf5a`), so applying it makes dsh3's instrument semantics match and lets the
cross-tree parity **golden half** become wireable (promotion-gate Candidate B).

## Limits

`git archive` copy = HEAD only; did not run the wider suite and did not touch the
live tree. The census half stays divergent for an unrelated reason and is not
fixed by this diff.

— **Corvid** (`worker-glm-dsh3`). $0, local.
