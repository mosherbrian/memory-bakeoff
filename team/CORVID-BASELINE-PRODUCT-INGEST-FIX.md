# Baseline product-ingest fix — validated diff (closes product-path census item 1)

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local (validated in a temp tree; live tree
untouched)
**Diff:** `team/CORVID-BASELINE-PRODUCT-INGEST-FIX.diff` (sha
`005ee114c72ad9ceb9bd53fef6f78d4fcdfb6eab14f055daa7fede5573a46ae7`)
**Closes:** recommendation 1 of `team/CORVID-PRODUCT-PATH-CENSUS.md`.

## Change

The four baselines advertise `product_ingest=True` while their `ingest` ignores
`mode` — the habitus defect's shape. Set `product_ingest=False` on
`bm25`, `dense_lsa`, `tfidf_cosine`, `hybrid_rrf` (their classes already stay
`baseline` in both modes), and add a regression assertion beside the habitus one
in `tests/test_preflight_hardening.py`.

## Verification (live working-tree state overlaid onto a `git archive` copy)

- `PYTHONPATH=src:vendor/membukkit/src pytest -q tests/test_preflight_hardening.py`
  → **9 passed** (the new loop assertion included).
- `run_provider(p, mode="product")` in-process, per baseline → **`ineligible`**,
  reason "provider does not expose product-mode ingestion" — product mode now
  fails closed instead of running raw-as-product. Raw mode unchanged.
- Diff `git apply --check` → **clean** on the live dsh3 tree.

## Effect on recorded results

None. No result dir uses a baseline in product mode (the only product-mode
record ever is the habitus ineligible probe), and baseline classes were already
`baseline`, so no existing number moves.

## Handoff

Implementer-of-record applies:
```
git apply team/CORVID-BASELINE-PRODUCT-INGEST-FIX.diff
```
Second seat open (Assay/Alice). The other half of the census — the five external
providers that keep `product_ingest=True` (evidence or mark ineligible) — is a
separate owner call, unchanged.

— **Corvid** (`worker-glm-dsh3`). $0, local.
