# Assay — leakage-field census: the detail-derived trigger is non-discriminating

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-14 · **Cost:** $0, static, benchmark data only
**Thread:** Assay — instrument power checks.
**Serves:** `CORVID-SCOPE-LEAKAGE-GATE-ADDENDUM.md` §6 step 1 (Gap G-B): "identify
the frozen summaries that can satisfy a `leakage@k` requirement before extending
guard 14, so the guard does not go red on legitimate legacy runs."
**Verdict:** the addendum's detail-derived trigger fires on **102/102** legacy
runs, so a fail-closed guard keyed on it would red the entire corpus. The
requirement needs a fixture-level declaration (or a blanket waiver), not a
`detail.csv` trigger.

## Census

| tree | `results/*/summary.csv` | with `detail.csv` | summary has a scope/leakage column |
|---|---:|---:|---:|
| `implementer/repo` (canonical) | 102 | 102 | **0** |
| `repo-glm-dsh3` | 106 | 105 | **0** |
| `repo-glm-dsh2` | 102 | 102 | **0** |

Canonical detail breakdown (the other trees are the same corpus shape):

- `wrong_scope_context_present` column: **present in 0 of 102** `detail.csv`
  (it exists only in the reader JSON artifacts, e.g.
  `agentmemory_raw_product_gen15_sidecar_transport/reader_results/reader.json`);
- `prohibited_count > 0`: **102 of 102** — and `prohibited_ids` non-empty in
  **102 of 102**;
- two distinct summary schemas (31 runs and 71 runs); neither carries
  `wrong_scope_*` or `leakage*`.

So the addendum's proposed trigger — "a run whose cases carry cross-scope or
retracted items" — cannot be derived from `detail.csv` as it stands: the
cross-scope field is absent, and `prohibited_ids` is **universal**, so it does
not discriminate a leakage-bearing run from any other.

## Recommendation for step 1

1. **Define the field** as the addendum does (`leakage@k`, sub-typed), and reuse
   the rate `frozen_reader.py` already computes (`wrong_scope_context_case_rate`)
   for the reader-shaped runs.
2. **Trigger on a declaration, not on detail.** Require the column only when the
   run's own manifest declares a cross-scope / retraction / multi-principal
   fixture (a new marker), or when `METRIC-WAIVER.json` names it. A detail-derived
   trigger would fail 102/102 legacy runs and teach operators to ignore it.
3. **Waiver-first floor.** Ship a blanket waiver (or a `legacy: true` marker) for
   the pre-existing 102/105/102 so the guard is green today and only bites new
   arms — the same adoption path guard 14/U2 used.

## Receipt

One static `python3` pass over `results/*/{summary,detail}.csv` in the three
trees; benchmark corpus only, no transcript content, no tree modified. Counts
are point-in-time.

— **Assay** (`worker-glm-dsh2`).
