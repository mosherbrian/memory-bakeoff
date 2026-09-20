# Second-driver re-derivation — Habitus core row (fills the coverage-index gap)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 14:50 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-driver duty; `ASSAY-VERIFICATION-COVERAGE.md` lists the habitus **stress**
row (the AGENTS protected finding) but not the **core** row. Read-only.

**Subject:** `implementer/repo/results/habitus_core/detail.csv` (26 per-case
rows), provider `habitus`, mode `raw`, top_k 5.

## Verdict

**AGREE — the core row re-derives exactly**, including the `21/22 = 0.955`
positive non-as-of subset. This puts the core row on the independently
second-driven list, where only the stress row had been.

## Re-derived from per-case rows

Method: drop the **2 `negative`** cases → 24 scored; average the per-case
columns. (Same convention as `summary.csv` / the membukkit core5 pass.)

| metric | mine (24 scored) | artifact |
|---|---:|---:|
| Hit@5 | **0.875000** | 0.875 |
| all-relevant@5 | **0.750000** | 0.750 |
| MRR | **0.784722** | 0.784722 |
| prohibited@5 | **0.097222** | 0.097222 |

Positive non-as-of subset (drop `negative` **and** `temporal_asof` → 22 cases):
**21 hits = 0.954545**, i.e. the README's **0.955** — reproduced.

Category census (26 rows): exact 3, semantic 3, temporal_current 4, temporal_asof
2, multihop 2, procedure 5, scope 3, conflict 1, protocol 1, negative 2.

## Why this is worth recording

- `AGENTS.md` protects **only** the stress row ("Habitus real runtime: stress
  Hit@5 0.792 with prohibited@5 0.025"), and Assay's coverage index follows it.
  The core row is nonetheless encoded in `check_protected_findings.py` and cited
  in the survey, so it is load-bearing — it now has a per-case second driver.
- Together with Assay's stress re-derivation, both habitus slices are now
  independently recomputed from raw rows, not just guarded by a consistency
  check.

## Convention note (bind it to any citation)

Denominator is **26 − 2 `negative` = 24**. Dropping `temporal_asof` as well (22)
gives the 0.955 subset; dropping only the two `negative` gives 0.875. Cite
"Hit@5 0.875 (24 scored: 26 − 2 negatives)" so the two numbers cannot be
conflated.

## Limits

- Stored-artifact re-derivation only; the engine was not re-run and no live
  window was read.
- I used the per-case metric columns, not a re-scoring from `retrieved_ids`
  (the provenance/ID path is covered by the frozen-ID and habitus provenance
  probes).
