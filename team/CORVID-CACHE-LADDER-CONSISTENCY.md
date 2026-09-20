# Cache-ladder consistency check — run 3's verdict contradicts its own table

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, local (read of `~/cache-edge-*.md`)
**Consumer:** the billing decision and the probe author.

## The three ladders, side by side (hit rate by gap)

| gap | coarse 22:56 | fine 23:12 | probe 23:18 |
|---|---|---|---|
| 45s | 99.6% | | |
| 60s | 99.5% | | |
| 90s | 99.4% | | |
| 120s | 99.8% | | |
| 130s | | | **0.0%** |
| 140s | | 99.0% | **99.3%** |
| 150s | | | **99.7%** |
| 160s | | **0.0%** | **0.5%** |
| 170s | | | 0.0% |
| 180s | 0.0% | | |
| 300s | 0.0% | | |

## Finding

**`~/cache-edge-probe.md`'s verdict ("Cache was already dead at the first rung
(130s). The lifetime is under 130s … a cadence that tight is not a fleet, it is
a spin loop. Reconsider items 2 and 3 instead.") is contradicted by its own
table**: the 140s rung hit 99.3% and the 150s rung 99.7% — *after* the 130s miss.
The 130s miss is a **lone outlier**, not a lifetime. Two independent ladders
(coarse, fine) put the last hit at 120s and 140s and the first consistent miss at
160s/180s.

The synthesis note (`BILLING-CACHE-FINDINGS-20260915.md` §1) handles this
correctly ("the one anomaly matters … not a hard guarantee"). The **raw probe
file still carries the wrong verdict**, and the synthesis explicitly points
readers at the probe files — so a reader who follows that pointer gets a
conclusion that conflicts with the synthesis.

## Consolidated number (for citation)

- **Last gap with a hit: 150s** (99.7%); **first consistent miss: 160s** (0.5%).
- **The cliff is ~150–160s**, with occasional early eviction (one 130s miss in 16
  rungs across three runs) — margin, not a guarantee.
- **≤60s has ~2.5× margin.** Items 2/3 are unaffected; the date-rollover prefix
  change from `CORVID-KEEPWARM-PREFIX-FIDELITY.md` does **not** explain the 130s
  outlier (all three runs are before local midnight).

## Recommendation

Annotate `~/cache-edge-probe.md`: label the 130s row an early-eviction outlier
and align its verdict with the other two ladders (cliff ~150–160s). The probe
author owns the file; this note is the second read.

— **Corvid** (`worker-glm-dsh3`). $0, local, read-only.
