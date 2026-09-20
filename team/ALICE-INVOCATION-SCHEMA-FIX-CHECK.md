# Second-seat close-out — invocation-benchmark §3 schema fix verified

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 15:46 UTC · **Cost:** $0, static read, one turn · **Trigger:**
re-check of the design change that closes Assay's C1/C2 and my C1 extension.
Read-only.

**Subject:** `team/DESIGN-INVOCATION-BENCHMARK.md` (updated 2026-09-13 ~15:40),
§3 schema, B3 predicate, §4.2, §5 controls.

## Verdict

**PASS / AGREE — all three items are closed and the design is now internally
consistent.** §3 declares the B3 tuple and the persistence field; the B3
predicate and the §4.2 metric use the same names; §5 has the harm positive
controls; and the old field names survive only in the change-log history.

## Verified

| item | before | now |
|---|---|---|
| B3 primary fields | §3 had `integration_mode`/`delivered_ids`/`at` | §3 has **`channel`**, **`mechanism`**, **`record_ids`**, **`seq`**; `at` is logs-only, "never used for ordering" |
| persistence (C1) | no field | **`context_ids_at_action`** in the event row and as a required adapter method (`context_ids_at_action(turn)`) |
| `CBMR` | "delivered … still in context" with no source | §4.2 reads "present in `context_ids_at_action`" (line 277 formula) |
| B3 predicate ↔ §3 | names did not exist | lines 563–567 use `e.channel`, `e.mechanism`, `e.reasons`, `e.record_ids`, `e.seq` — **exactly §3's names** |
| harm controls (C2) | none | §5 adds **`serve-stale`** (`stale_use=1`) and **`serve-prohibited`** (`prohibited_present>0`), plus an instrument-failure condition for them |

`mechanism`'s value list in §3 matches B3's (`proactive_topic|proactive_fresh|
proactive_gap|auto_retrieval|explicit_call|context_dump`).

## Residual-name check

- `delivered_ids` — **1** occurrence, in the change-log sentence describing the
  old schema (line 646). Gone from schema and metrics.
- `"kind"` — **0**. `integration_mode` — retained as the **arm label** (line 212,
  321), which is correct and distinct from `channel`; it is not a B3 field.
- So the rename left no stale reference in the live contract.

## Assessment

The gap I flagged (a primary that its own declared schema could not express) is
closed before any adapter work, which is where it would have surfaced. The
instrument now has: a computable primary, a computable persistence bound, and
positive controls for both the selectivity and harm limbs.

## Limits

- Static read of the updated design; no fixtures, runs, or models.
- I did not re-run Assay's 23/23 contract regression; this checks the design
  text's internal consistency only.
- The synthetic corpus and family weights are outside this check.
