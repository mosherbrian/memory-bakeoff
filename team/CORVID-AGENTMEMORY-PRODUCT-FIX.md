# AgentMemory product-flag fix — option 1 diff (owner chooses the option)

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local (validated in a temp tree; live tree untouched)
**Diff:** `team/CORVID-AGENTMEMORY-PRODUCT-FIX.diff` (sha256
`be9609c56c15b290ab0d9860dc2bed00aece734d60e0b00c77e22eea473c48a2`)
**Closes:** option 1 of `team/CORVID-AGENTMEMORY-PRODUCT-FLAG.md`.

## Change (option 1 — the habitus precedent)

`AgentMemoryProvider` advertises `product_ingest=True` while its `ingest` ignores
`mode` (0 body refs), so a `mode="product"` run is eligible and would be labeled
`product` while executing the raw service path. Set `product_ingest=False` (fail
closed) and add a regression assertion beside the habitus one.

## Verification

- Live working tree overlaid on a `git archive` copy:
  `tests/test_preflight_hardening.py` → **9 passed** (new assertion included).
- `run_provider("agentmemory", mode="product")` in-process → **`ineligible`**,
  "provider does not expose product-mode ingestion" (raw mode unchanged).
- `git apply --check` clean on the live dsh3 tree; handoff receipt via
  `probe_patch_handoff_receipt.py`: post-apply hashes
  `external.py cd84d3d8…`, `test_preflight_hardening.py 11ef590f…`.

## Effect on recorded results

None — no recorded run used agentmemory in product mode (the only product-mode
record ever is the habitus ineligible probe), and its class becomes
`raw_product` for all real runs.

## Owner choice

This is **option 1 of three** (`CORVID-AGENTMEMORY-PRODUCT-FLAG.md`): (1) this
fail-closed flag; (2) make the product distinction real; (3) gate raw like
Hindsight/Claude-Mem. The habitus precedent favors (1); it is a one-line,
reversible change with a test.

— **Corvid** (`worker-glm-dsh3`). $0, local.
