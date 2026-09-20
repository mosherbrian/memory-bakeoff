# Assay second-driver — Gen38 dynamic Hit@3 scores (closes register gap #3)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~21:1x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations
**Targets:** the frozen numbers used as anchors — perseus dynamic Hit@3
`0.434` (`docs/PORTFOLIO-P1-ADAPTER-RECEIPTS.md`) and bm25 dynamic Hit@3 `0.226`
(the BAR B floor; `research/MEMCONFLICT_GEN38_FULL_RELEASE.md:186`).

## What I did

Recomputed the numbers from the stored derived counts
(`results/memconflict_gen38_full_release/heldout-27-derived.json`), checked the
rank distribution against the hit count and denominator, and re-hashed the
per-persona dataset/adapter pins.

## Result — AGREE

| Engine | dynamic Hit@3 = hits / 2631 | cited | rank 1-3 sum | dist sums | dataset pin |
|---|---|---|---|---|---|
| perseus | 1142 / 2631 = **0.4341** | 0.434 | 606+359+177=1142 | yes | `8ef9ec…` |
| mem0 | 1103 / 2631 = **0.4192** | 0.419 | 634+278+191=1103 | yes | `8ef9ec…` |
| bm25 | 594 / 2631 = **0.2258** | 0.226 | 297+163+134=594 | yes | `8ef9ec…` |

- Rank distributions sum to `measured = 2631` (with `no_hit`), and
  `hit@3 == rank1+rank2+rank3` for all three engines.
- `dataset_sha256 = 8ef9ec8589eccb86f63ab3a819a9180217405351a8d5846866721ea74babe092`
  identical across all 30 persona files per engine and all three engines.
- perseus adapter pin is exactly `627f812d5296130c…`, matching the receipt.

## Limit (stated)

This is a **counts/provenance** re-derivation. A raw retrieval replay would need
the MemConflict gold to map returned `{session_id,message,turn}` to "first
support," and `external/MemConflict` (182 MB) is absent by policy. So the
retrieval itself was not re-executed; the aggregate, its denominator, the rank
arithmetic, and the input pins all reproduce exactly.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/memconflict_gen38_score_rederive.py`
  sha256 `37b89644a6babd272bb4bc50796258a1d17d2801b826839518b3d1bd6b5d8fc2`
- Result: `.../sealed-gen38-score-rederive-20260912/result.json`
  sha256 `a7f6f2d53219678631bf52597a0a6eb034c0cf1bfbb726e3c207f9f8427dff7b`
- Re-run: `python3 scripts/verify-20260912-assay-row1/memconflict_gen38_score_rederive.py`

— **Assay** (worker-glm-dsh2).
