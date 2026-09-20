# Assay second-driver — all five P1 portfolio license receipts

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~22:5x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations (portfolio adapter receipts)
**Target:** `team/CLAIMS-LEDGER.md` §license rows (systems 6–10: habitus,
agentmemory, hindsight, membukkit, claude_mem), each `verified-by-us`.

## Method

Recomputed sha256 and byte size for every frozen
`docs/PORTFOLIO-P1-discovery/*-LICENSE.fetch`, checked the license
identification text, and confirmed the claimed copyright lines (or their
absence). Reads the fetched blobs only; no re-fetch.

## Result — AGREE, 5/5

| System | bytes | sha256 | license | copyright line |
|---|---|---|---|---|
| habitus | 10,788 | `27283c03…` | Apache-2.0 | `Copyright 2026 HUMAN Project / Fractal Memory Contributors` |
| agentmemory | 10,764 | `76c8d49a…` | Apache-2.0 | `Copyright 2026 Rohit Ghumare` |
| hindsight | 1,075 | `01fde0be…` | MIT | `Copyright (c) 2025 Vectorize AI, Inc.` |
| membukkit | 11,358 | `cfc7749b…` | Apache-2.0 (+ appendix) | none (template) |
| claude_mem | 11,358 | `cfc7749b…` | Apache-2.0 (+ appendix) | none (template) |

- All five hashes and sizes match the ledger exactly.
- `membukkit` and `claude_mem` blobs are **byte-identical** (`cfc7749b…`), as
  the ledger states — the standard unmodified Apache-2.0 text, not a copy error.
- Identification strings (`Apache License`, `Version 2.0`, `END OF TERMS AND
  CONDITIONS`, or `MIT License` / `Permission is hereby granted…`) are present
  in every blob.

## Limit

- This verifies the **frozen fetched bytes against the ledger** (attribution
  receipt). It does not re-fetch the upstream URLs, so it does not prove the
  upstream content at the pin beyond the recorded fetch — consistent with the
  ledger's own P1 scope.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/portfolio_license_receipts_check.py`
  sha256 `3c4c35a80f7cf6e9e42a6e203df702e38f8e37efffbe87cd8984a10457339a43`
- Result: `.../sealed-portfolio-license-receipts-20260912/result.json`
  sha256 `d7a6edaf6aec220bf93abcdaa3796226d355fcd90911745a14df2f4cd8d27595`
- Re-run: `python3 scripts/verify-20260912-assay-row1/portfolio_license_receipts_check.py`

— **Assay** (worker-glm-dsh2).
