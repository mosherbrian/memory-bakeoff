# Cross-copy file census: the "2 known drifts" is declaration-scoped

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, read-only (find + sha256)
**Trigger:** `check_cross_copy_drift.py` reports "2 known drifts, 0 tree gaps"
and reads as the fork-drift total. It is scoped to the 6 declared `shared:`
files, so I hashed `src/` and `tests/` across all three trees directly.

## Missing vs canonical `implementer/repo`

| tree | missing `src/*.py` | missing `tests/*.py` |
|---|---|---|
| `repo-glm-dsh2` | `portfolio.py`, `providers/pi_lcm_store_reader.py` | `test_pi_lcm_store_reader_contract.py`, `test_portfolio_composition.py`, `test_portfolio_realdata_smoke.py`, `test_team_sync.py`, `test_transcript_mining.py` |
| `repo-glm-dsh3` | same two | the same five **+ `test_instrument_edge_cases.py`** |

Both forks also lack the entire **P2 entry chain** — `portfolio.py`,
`pi_lcm_store_reader.py`, and the portfolio/pi-lcm/transcript-mining/team_sync
tests. So the pi-lcm store-reader arm and portfolio composition cannot run in
either fork, independent of the instrument divergence.

## Differing where present

| file | canonical | dsh2 | dsh3 | reading |
|---|---|---|---|---|
| `src/.../longcontext_null.py` | `cf59db82` | same | `31ae0f16` | known — Alice's 4 edge fixes absent in dsh3 (owner Kiln) |
| `src/.../stale_use_penalty.py` | `a1576482` | same | `4eddf84a` | known — same fix set |
| `src/.../providers/__init__.py` | `95a69953` | `c890121f` | `c890121f` | canonical imports `pi_lcm_store_reader` (module absent in forks) |
| `src/.../providers/external.py` | `0b3f1294` | same | `9cc32ba4` | dsh3 working-tree edit (habitus class/product fix), uncommitted |
| `tests/test_known_failures_baseline.py` | `7b601ae6` | `faf933a2` | `faf933a2` | canonical has Kiln's loud-failure guard; forks lack it |
| `tests/test_preflight_hardening.py` | `1c6a3443` | same | `3e4e52fe` | dsh3 working-tree edit (habitus assertions), uncommitted |

## Finding

`check_cross_copy_drift.py`'s "2 known drifts" is **honest about its declared
scope** (map rev 5 / guard 16) but is **not the fork delta**. At the file level
the forks differ from canonical on at least **2 missing `src` files + 5–6 missing
tests** and **4–6 differing files**. Any statement of the form "the guard ran
across all three trees" therefore reflects canonical behavior only where the
files exist; for the P2 chain and the instrument fixes it does not.

## Recommendation

1. **Declare the P2 chain + the canonical-only safety files** in
   `team/REPO-CANONICAL.txt`'s `shared:` set (`portfolio.py`,
   `pi_lcm_store_reader.py`, `providers/__init__.py`,
   `test_known_failures_baseline.py`, the four P2 tests, plus the instrument
   files) so the drift guard reports missing-in-tree as drift instead of silence.
   Guard 16 would then surface this census automatically.
2. **State the fork-lag explicitly** in the tree README/AGENTS (forks are
   experimental copies that lag canonical on the P2 chain and instrument fixes) —
   a one-paragraph note prevents the "all three trees" over-read.
3. **Classify the two uncommitted dsh3 edits** (`external.py`,
   `test_preflight_hardening.py`) as intended local work or revert them; today
   they are an undocumented divergence.

## Limits

Hash-only census; canonical is treated as the reference, and I do not adjudicate
which fork is "right" (the forks are experimental). Did not diff file contents
for every differing pair beyond the classification above.

— **Corvid** (`worker-glm-dsh3`). $0, local.
