# Second-driver re-derivation — membukkit core5 (charter row 9) verified from per-case rows

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 13:09 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-driver duty; independent check of `team/KILN-REDERIVE-MEMBUKKIT-CORE5.md`.
Read-only.

**Subject:** `implementer/repo/results/current_full_core5/run.json` (and the
stress cross-slice), provider `membukkit`.

## Verdict

**AGREE — Kiln's row-9 numbers reproduce exactly from the per-case rows**, not
just from the summary: **core5 Hit@5 0.958333, MRR 0.525000**; stress cross-slice
**0.583333 / 0.329167**. Recomputed independently from `run.json` `details`; the
three trees carry byte-identical run files.

## Re-derivation

Method: parse the `membukkit` item's 26 per-case `details`, drop the **2
`negative` cases** (the run's convention), and average `hit_at_k` /
`reciprocal_rank` over the remaining **24**:

| slice | cases | scored | Hit@5 (mine) | MRR (mine) | summary.csv | Kiln |
|---|---:|---:|---:|---:|---|---|
| `current_full_core5` | 26 | 24 | **0.958333** | **0.525000** | 0.958333 / 0.525 | 0.958 / 0.525 ✓ |
| `current_full_stress4505` | 26 | 24 | **0.583333** | **0.329167** | 0.583333 / 0.329167 | 0.583 / 0.329 ✓ |

Exact to 1e-9 against `summary.csv` in both slices (`MATCH=True`).

**Cross-tree consistency:** `run.json` is byte-identical across
`repo`, `repo-glm-dsh2`, `repo-glm-dsh3` — core5 `3d735687…`, stress `d3eab190…`
— so the row's numbers do not depend on which checkout is read.

## Denominator caveat (worth binding to the citation)

The convention is **26 − 2 `negative` = 24 scored**. If `temporal_asof` is
*also* excluded (22 cases), the same rows give **Hit@5 1.000 / MRR 0.5273**
(core5) and **0.5909 / 0.3364** (stress) — different numbers from the same
artifact. So the citation should carry "Hit@5 0.958 (24 scored: 26 cases − 2
negatives)" so a reader cannot half-exclude and get 1.000. This is the same
denominator-trap family the ledger already flags for agentmemory (418/450) and
memobase (question-weighted overall).

## Why this is a second driver, not a restatement

Kiln re-read `run.json`; this pass recomputes the metric **from the 26 per-case
rows** and independently derives the 24-case denominator, then checks both
against `summary.csv` and across the three trees. The summary is therefore
consistent with its own rows, not merely self-asserted.

## Limits

- Stored-artifact re-derivation only; the engine was not re-run and no live
  window was read.
- I did not re-derive the other providers' rows (membukkit parity vs `dense_lsa`
  is a separate guard, `check_membukkit_parity.py`).
- `hit_at_k`/`reciprocal_rank` are the run's own per-case fields; I did not
  recompute them from `retrieved_ids`/`relevant_ids` (the parity guard and
  Assay's routing check cover the id-level view).
