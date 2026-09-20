# Second-driver — leakage-field census (Assay): AGREE, with the exact per-run split

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-14 02:3x UTC · **Cost:** $0, static benchmark-data recount, one turn.
**Trigger:** `ASSAY-LEAKAGE-FIELD-CENSUS.md` (the G-B step-1 census). Independent
driver: `row-leakage-census-check/alice_leakage_census.py` (`84f2724e…`), result
`result.json` (`d2bd5ae9…`). Benchmark corpus only; no transcript content; no
tree modified.

## Verdict

**AGREE — the detail-derived trigger is non-discriminating, so a fail-closed
guard keyed on it would red the corpus.** Independent recount across the three
trees:

| tree | summaries | detail.csv present | detail carries prohibited fields | summary scope/leak col |
|---|---:|---:|---:|---:|
| `implementer/repo` (canonical) | 102 | 102 | **102/102** | **0** |
| `repo-glm-dsh3` | 106 | 106 | **105/106** | **0** |
| `repo-glm-dsh2` | 102 | 102 | **102/102** | **0** |

- `wrong_scope_context_present` appears in **0 of 102** canonical `detail.csv`
  (column-set check), exactly as Assay reports.
- `prohibited_count > 0` **and** non-empty `prohibited_ids` hold for **every**
  run that carries those columns — so the field is universal and cannot
  discriminate a leakage-bearing run. Confirmed.
- Two canonical summary schemas (20 and 22 columns; 31+71 runs), matching
  Assay's split. (dsh3 has a third 8-column schema.)

## Refinements (no change to the recommendation)

1. **The dsh3 "105" is column-presence, not file-presence.** All 106 dsh3 runs
   have a `detail.csv`; **one** of them lacks the `prohibited_count`/
   `prohibited_ids` columns. Canonical and dsh2 are 102/102 with the fields.
   Worth stating as "105 of 106 carry the prohibited fields" so a future
   trigger-count cannot drift.
2. **The reader JSON carries two of the three wrong-scope names.** The one
   `.../reader_results/reader.json` present has `wrong_scope_answer_rate` and
   `wrong_scope_context_present`; the aggregate `wrong_scope_context_case_rate`
   is **computed by `frozen_reader.py` (`4f4649d7…`)**, not stored. So step 1's
   "reuse the rate `frozen_reader.py` computes" is right, but a guard cannot read
   it straight from the artifact — it must invoke or re-derive the aggregate.

## Recommendation unchanged

Assay's step-1 answer stands: declare the trigger (manifest marker) with a
waiver-first floor for the legacy 102/105/102, rather than deriving it from
`detail.csv`. My G-B answer (no guard mentions `leakage|wrong_scope`;
guard 14 `3ae6cf05…` requires only the three base columns) is the complementary
half.

## Scope and limits

- Static CSV/JSON header and row scan across the three trees; counts are
  point-in-time. I did not re-run `frozen_reader.py` or inspect any run's model
  behaviour.
