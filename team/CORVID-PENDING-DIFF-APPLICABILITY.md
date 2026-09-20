# Pending-diff applicability receipt (owner queue hygiene)

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, read-only (`git apply --check` / reverse)
**Purpose:** the owner queue now holds several diffs. Classify each against the
**current** `repo-glm-dsh3` tree so an operator does not apply a stale patch or
re-apply one that already landed.

## Ready to apply (forward `git apply --check` clean on live dsh3)

| diff | target | note |
|---|---|---|
| `team/ALICE-INSTRUMENT-FIXES.diff` | `src/memory_bakeoff/longcontext_null.py`, `stale_use_penalty.py`, tests | the dsh3 **src sync** (validated: 11 passed, golden parity clears — `CORVID-DSH3-SRC-SYNC-VERIFY.md`) |
| `team/CORVID-BASELINE-PRODUCT-INGEST-FIX.diff` | four baseline providers + `tests/test_preflight_hardening.py` | sets `product_ingest=False` (validated: 9 passed, product mode fails closed) |

## Already applied in dsh3 (reverse-check clean — do NOT re-apply)

| diff | target |
|---|---|
| `team/CORVID-CROSSTREE-PARITY-HARDEN.diff` | `scripts/probe_crosstree_parity.py` (live sha `6840a4a7…`) |
| `team/CORVID-ROW42-CORPUS-FIX.diff` | `team/invocation-corpus-v1/` (corpus `65ba8592…`, selftest binding) — different root, not this repo |
| `scripts/fix-habitus-adapter.diff` | `external.py` + tests (the pre-existing uncommitted dsh3 edit) |
| `scripts/fix-results-pointer-defects.diff` | `RESULTS.md` rows 81/82/85 |

## Context-drifted / different tree

| diff | status |
|---|---|
| `scripts/fix-hindsight-gen4-pointer.diff` | neither forward nor reverse clean here — dsh3's `RESULTS.md` has since been edited; the pointer defect itself is **already fixed** on dsh3 (`check_invalidated_pointers` uncued=0). Siblings may still need it; apply per-tree with the apply script. |
| `team/METERS-TOPUP.diff` | targets `~/conductor-chat/meters.py` (builder lane), not this repo. |

## Reading

- Two diffs are genuinely **ready** (both validated with test evidence): the dsh3
  src sync and the baseline product-ingest fix.
- Four are already in dsh3; applying them again would fail (not silently mis-apply).
- One is context-drifted but its defect is already resolved here; one is another
  tree's file.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
