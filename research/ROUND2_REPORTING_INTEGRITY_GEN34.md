# Round-2 reporting integrity — Gen34

## Status

`complete_reporting_integrity_audit_all_conclusions_survive`.

A no-product-run generation. Every Round-2 cross-engine number has been rebuilt
from committed leaf evidence through a fail-closed reporting layer, and every
published conclusion survived independent derivation unchanged.

No engine, database, service, reader, LLM or GPU was used. Pure offline Python
over normalized JSON.

## Why this generation exists

Gen33's own test caught a benchmark-integrity defect. Gen31's lifecycle collector
ran three queries that failed silently — `document_id` read from `documents` when
it lives on `memory_units`, a `state` column that does not exist in that schema
because curation is the `invalidated_memory_units` side table, and a `sql()`
helper that returned an empty string on failure instead of raising. Each produced
a plausible answer: every record inactive, zero invalidations.

Separately, `false_supersession` is scored by `score_lifecycle_state` and never
appears in the case-level table. Aggregating case totals and reporting
"false_supersession 0" was therefore structurally guaranteed rather than observed.

In a benchmark about memory loss, a failed query reads as *nothing was lost*.

## The contract

`round2-reporting-v1`, hash
`9673f1d98091e89fec9758425fc640f7fe8addc84e885ad64edc1cab3b82b149`.

Four evidence streams are distinguished: `case_scorer`, `lifecycle_scorer`,
`product_lifecycle_event`, and `capability_diagnostic`. A canonical registry
gives every failure class its legal stream(s); `false_supersession` is
lifecycle-only, and asking the case stream for it raises rather than returning
zero.

Measurement is tri-state — `PRESENT(n)`, `MEASURED_ZERO`, `UNMEASURED` — and an
`UNMEASURED` value carries no integer at all, so it cannot be summed by accident.
A missing key, absent file, failed parse or absent stream becomes `UNMEASURED`,
never `0`.

Every helper raises. There is no equivalent of the old `sql()` that turned an
exception into `""`, `[]`, `{}`, `0` or `False`.

## How the numbers were rebuilt

Case totals were recomputed from each repetition's `cases[].failure_classes`,
case by case. Lifecycle totals were recomputed by calling the **frozen**
`score_lifecycle_state` on every checkpoint's normalized state. Both were then
reconciled against the stored aggregates, with any disagreement fatal and named
by engine, repetition and class.

Stored `summary.json` files were verification targets, never inputs. A corrupted
summary cannot corrupt the derived result; a test proves it is caught instead.

All twelve repetitions — four engines, three runs each — passed schema
validation: exactly 20 cases with no duplicates and no unknown ids, exactly 9
checkpoints, and complete lifecycle fields.

## What the independent derivation found

**Nothing moved.**

| claim | independently derived |
|---|---|
| the seven preregistered classes recur in all three append-only engines | **true** |
| five are identical across them | **true** — `configuration_collapse`, `failed_procedure_adoption`, `false_persistence`, `late_history_corruption`, `unsupported_evidence` |
| `false_supersession` is 0 in Perseus, Hindsight and Mem0 | **true**, and now MEASURED_ZERO from the lifecycle scorer rather than absent from the wrong table |
| `false_supersession` is 3 in agentmemory | **true**, agreeing with the harness's independent classification of the product's own retirements |
| retirement halves configuration collapse | **true** (6 → 3) |
| retirement reduces false persistence | **true** (9 → 6) |

The conclusions were right. What they had been missing was a derivation path that
could have proven them wrong.

## What we now know, classified

**A. Measurements that were always valid.** Every case-level result across all
four engines. All twelve repetitions reproduce their stored case totals exactly
from leaf evidence. Gen33's treatment activation — two native supersessions per
repetition, `L001→L003` false and `L002→L004` legitimate — is unaffected.

**B. Corrected but substantively unchanged.** Gen31's lifecycle stream. The
original collector never measured it; the corrected rerun shows a genuinely clean
lifecycle, and Gen31's case results are byte-identical to what was published.

**C. Claims whose provenance changed.** "The append-only engines never falsely
supersede" was published from the case-level stream, where the class cannot
appear. It is now derived from the lifecycle scorer and is `MEASURED_ZERO`. The
statement is unchanged; its evidential basis is entirely different.

## Audit of the existing summarisers

Counted mechanically across the six Round-2 scripts: **45 default-fallback
patterns** — `.get(key, 0)`, `or "0"`, `or []`, bare excepts — each a place where
missing evidence can become a number. `summarise_gen33.py` alone has 17. All
three summarisers embed `datetime.now()` in hashed content, so none can produce a
stable digest.

Historical scripts are left intact for reproducibility, with their defects
recorded here. Future publication routes through the common reporter, which has
no fail-open paths and regenerates byte-identically: two consecutive runs produced
content digest `edbae67b09769e7165a6ec1199d8f2adcaca6e8e25ee5c2191c4fad495495d51`.

## Lineage

Every aggregate cell carries its provenance to engine → repetition file → source
stream → individual case ids, in `results/round2_gen34_integrity/evidence-ledger.json`.

## Verification

Focused tests: 14, each naming a way the reporting layer failed on 2026-09-03 and
asserting the reporter now raises — lifecycle-only class read from case totals, an
empty lifecycle checkpoint, a missing file, a missing required key, a vanished
`canonical_id`, a wrong case count, a duplicate case id, an unknown class, a
corrupted stored aggregate, and an `UNMEASURED` value used as a number.

The wider point, recorded because it cost most of a night: across five engine
profiles the runs were deterministic, reproducible and provenance-exact
throughout. **Every error was in the code that compares, aggregates and presents
results.** The ruler and the adapters carried hashes and tests; the reporting
layer carried neither. It does now.
