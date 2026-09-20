# Assay second-driver — Habitus real-runtime stress finding

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~22:2x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations
**Target:** protected finding (AGENTS.md §"Existing findings to protect"):
**Habitus real runtime: stress Hit@5 0.792 with prohibited@5 0.025.**

## Method

Recomputed the metrics for `results/habitus_stress` (450-distractor runtime arm)
from its 26 per-case rows using the harness's aggregate convention (negatives
excluded → 24 scored positives), compared to `summary.csv`, and recorded the run
provenance.

## Result — AGREE

| Metric | recomputed | summary |
|---|---|---|
| Hit@5 | **0.791667** | 0.791667 |
| all-relevant@5 | 0.666667 | 0.666667 |
| MRR | 0.701389 | 0.701389 |
| prohibited@5 | **0.025** | 0.025 |

- `provider=habitus`, `mode=raw`, `distractors=450`, `status=ok`.
- Probe note (provenance): *"Stock Habitus recall; stock record_outcome credits
  output-decision paths, not retrieval paths."*

The protected figures — Hit@5 0.792 and prohibited@5 0.025 — reproduce exactly
from the per-case records.

## Limit

- This re-derives the stored result's metrics and provenance; it does not re-run
  the Habitus engine. The runtime identity rests on the recorded probe note.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/habitus_stress_rederive.py`
  sha256 `b505b5cf5d7a873fc4a102f8fe7f5f90edfb09159a3bad9067729d6087617860`
- Result: `.../sealed-habitus-stress-rederive-20260912/result.json`
  sha256 `66f487403f16c2bf5e2fbe7f3ba1d83ffcf688688c0a10378c9714d8a04d9454`
- Re-run: `python3 scripts/verify-20260912-assay-row1/habitus_stress_rederive.py`

— **Assay** (worker-glm-dsh2).
