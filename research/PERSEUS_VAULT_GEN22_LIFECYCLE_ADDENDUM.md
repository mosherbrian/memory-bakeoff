# Perseus Vault Gen21 lifecycle addendum

This is a Generation 22 **post-run, read-only analysis** of the frozen audited
Gen21 `run.json` artifacts. It did not invoke Perseus Vault, alter a database,
or recompute a retrieval score. The Gen21 raw-product retrieval results remain
unchanged.

## Established state loss

Every audited stress repetition had 500 successful native CLI-write receipts,
393 scanned active entities, and 107 receipt-mapped canonical IDs absent from
the post-ingest active scan. The exact same 107 IDs were missing in r1, r2,
and r3 (intersection 107/107). The machine-readable, receipt-to-native-ID
audit is [perseus_vault_gen22_lifecycle_analysis.json](../results/perseus_vault_gen22_lifecycle_analysis.json).

| Repetition | Receipts | Active scan | Missing active | Class under frozen truth |
|---|---:|---:|---:|---|
| r1 | 500 | 393 | 107 | `false_consolidation_distinct_valid` |
| r2 | 500 | 393 | 107 | `false_consolidation_distinct_valid` |
| r3 | 500 | 393 | 107 | `false_consolidation_distinct_valid` |

All 107 are stress-only deterministic near-neighbor records (M051–M500), not
core correction pairs, required answers, or equivalent duplicates. Under the
frozen harness truth each is a distinct valid, scope-qualified fact. Therefore
none qualifies as an exact-duplicate collapse, explicit benchmark correction,
or truth-authorized equivalent consolidation. This is a current-retrieval
lifecycle loss: it removed valid hard competitors from active state.

## What the frozen artifacts cannot establish

The scans were requested with `include_archived=true`, yet reported
`archived_entities=0`; native stats report `total_history_rows=0` and the
captured active rows have no links or archive reason. The Gen21 trace did not
capture a native source-to-survivor consolidation relation for any missing
receipt. Thus the following are explicitly **unknown**, not inferred:

- whether each missing entity was deleted, hidden before persistence, or
  recoverable by an unrecorded native history/as-of operation;
- any source→survivor mapping or exact consolidation cause;
- a deletion rate distinct from the 21.4% active-state-loss rate.

The appropriate provenance label is consequently
`unknown_unattributed_state_loss` for historical recoverability, alongside the
truth-level classification `false_consolidation_distinct_valid`. No credit is
given for automatic correction, scope-aware consolidation, or historical
preservation.

## Retrieval confound

Stress Hit@5/all-relevant@5 remains 0.958/0.958 with prohibited@5 0.108.
That result is valid raw-product evidence for the stated operator-CLI seed plus
native hybrid-recall profile, but it was produced after 107 valid near-neighbor
competitors were absent from active state. The frozen candidate traces cannot
reconstruct rankings with those rows restored, so no counterfactual metric is
published. The direction of the confound is nevertheless clear: removing
valid, scope-qualified near-neighbors can make active retrieval easier. It
particularly affects the stress families that resemble release branches,
generated-client paths, NDJSON/logging, credentials, generated-code fixes,
and race procedures.

This mechanism is not equated with agentmemory's documented 418/450 (92.9%)
false supersessions: agentmemory exposed a Jaccard write-time supersession
rule and its pairs; Perseus Gen21 establishes stable active-state loss but
lacks frozen native lineage for an absorber claim.
