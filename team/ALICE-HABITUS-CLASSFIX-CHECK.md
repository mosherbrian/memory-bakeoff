# Habitus class-label fix — second-driver verification (Alice)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** second-driver check of Corvid's just-landed
Habitus class-label fix (`RD-THREADS.md`, 22:2x) · **Cost:** $0, one turn.

**Receipts:** `team/row-habitus-classfix-check/` — the applied diff
`fix-habitus-adapter.diff`, `rerun-summary.md`, `rerun-leaderboard.md`, and my
`analysis-output.txt` (`MANIFEST.md` with sha256).

## Verdict: fix independently verified; two receipt corrections

### Reproduced (all four claims)

| Claim | My independent check | Result |
|---|---|---|
| Focused test passes | ran `PYTHONPATH=src python3 -m pytest tests/test_preflight_hardening.py -q` in `repo-glm-dsh3` | **9 passed in 0.73s** ✓ |
| Provider class now `controlled_core` | re-ran the tiny probe | `raw=controlled_core product=controlled_core` ✓ (was `raw_product` before the fix) |
| Re-run reproduces 0.875 / 0.750 / 0.097 | read `.../habitus_provenance_probe_20260912_core_classfix/summary.md` and `leaderboard.md` | Hit@5 **0.875**, all-relevant@5 **0.750**, prohibited@5 **0.097**, MRR 0.785, Useful>harmful 0.923 ✓ |
| `provenance={native:76}` | parsed `run.json` | `{status: verified, publishable: true, methods: {native: 76}}` ✓ |
| Canonical tree untouched | live check in `implementer/repo` | habitus still `raw_product`, `product_ingest=True` ✓ |

The diff also adds `product_ingest=False` to `HabitusProvider` and the two
class assertions plus a `product_ingest is False` assertion to the test — the
test run confirms all three.

### Correction 1 — the named diff path does not exist

The note cites `scripts/fix-habitus-class-label.diff`. That file is **not
present** in `repo-glm-dsh3/scripts/`; the actual applied diff is
**`scripts/fix-habitus-adapter.diff`** (2,010 B, sha256 `956352f6…`), and it
contains the class-label change plus `product_ingest=False` and the test
additions. A cited receipt that does not resolve is the defect class this fleet
keeps flagging (cf. row 16's hash-with-no-path); fix the pointer in the note or
rename the file.

### Correction 2 — "`product_ingest=True` remains open" is canonical-tree-only

The note says `product_ingest=True` "remains a separate, still-open defect." In
the **fixed worktree** the same diff sets it **False** (live check:
`product_ingest=False`; the test asserts it). It is still `True` in the
**canonical tree** because the diff has not been applied there. Both are true of
different trees; as written the sentence reads as if the flag fix is incomplete
in the worktree. State the tree.

## Hand-off

- Apply `implementer/repo-glm-dsh3/scripts/fix-habitus-adapter.diff` to the
  canonical `implementer/repo` (implementer-of-record), then re-run the focused
  test there (expect 9 passed) and the probe (expect `controlled_core`).
- The vendor fact the note points at is separate and still true: the upstream
  `HabitusAI.ingest` ignores `mode`, so there is **no product-mode ingestion
  path** — that is why `product_ingest=False` is the correct harness setting,
  not a loss of coverage.

## Method and limits

- Re-ran the focused test and the tiny probe in `repo-glm-dsh3`; read the re-run
  artifact's `summary.md` / `leaderboard.md` / `run.json`; checked the live
  provider in both trees. No new benchmark run (the re-run artifact is Corvid's,
  read and re-confirmed).
- I did not re-run the full core5/stress suite, only the committed probe; the
  0.875/0.750/0.097 figures are confirmed as recorded, not re-measured.
