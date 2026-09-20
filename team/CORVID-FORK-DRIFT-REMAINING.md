# The two remaining cross-copy drifts — what they are and why no diff is filed

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity / landing steward
**Date:** 2026-09-15 · **Cost:** $0, read-only
**Context:** after the fork-lag/extension declaration (map rev 25), the live
cross-copy guard reports exactly 4-plus-2 = the two owned `known-drift` plus:

| file | canonical | forks | cause |
|---|---|---|---|
| `src/memory_bakeoff/providers/__init__.py` | `95a69953` | `c890121f` | canonical imports the `pi_lcm_store_reader` providers; the module is **absent in the forks** (P2 chain) |
| `tests/test_known_failures_baseline.py` | `7b601ae6` | `faf933a2` | canonical carries **Kiln's loud-failure guard** (env merge + subprocess-death refusal); forks lack it |

## Why I did not file a sync diff

- `providers/__init__.py` cannot be synced without the P2 module
  (`pi_lcm_store_reader.py`), which is a **declared `canonical-only:`** file — so
  this drift clears only if the forks take the P2 chain (an owner call), not with
  a one-file patch.
- `test_known_failures_baseline.py` **can** be copied canonical→fork and I
  generated such a diff (`git apply --check` clean on dsh3), but it is **not
  validated**: the loud-failure guard runs the whole suite as a subprocess and
  compares against the tree's own `tests/KNOWN_FAILURES.json`, and the forks'
  baseline differs from canonical's (`7da171eb` vs `1164fbc8` — 26 failures vs
  the pruned 10). Applying it unvalidated could turn the fork sentinel red or,
  worse, pass vacuously. It needs a fork-side run (~55 s full-suite subprocess),
  which is a Kiln/owner slice, not a pulse.
- The unvalidated diff was **deleted** rather than left in the queue.

## Recommendation

Sync the forks **whole** (P2 chain + safety files + instruments) as one owner
slice, with `tests/KNOWN_FAILURES.json` reconciled first; then both remaining
`(NEW)` drifts clear together. Until then the guard's advisory is correct and the
declaration keeps them visible.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
