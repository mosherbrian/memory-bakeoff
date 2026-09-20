# GUARD — CLAIMS-LEDGER class-count consistency

**Author:** Corvid (`worker-glm-dsh3`), ledger custodian / evidence-integrity
**Date:** 2026-09-13 · **Cost:** $0, local, no LLM, no network
**Artifact:** `implementer/repo-glm-dsh3/scripts/check_ledger_counts.py`
sha256 `d74ab1e99775c677d8d3436aacd59e5a5a9e5c373756feeef818c41422e42060`
(rev 2; rev 1 `20d8ef5c…`).

## Why

The ledger's `## CLASSIFICATION` section states a `**Counts:**` line and a
`**Located and byte-checked:** N of M rows` line. Both went stale once when
L-S14-02 moved `unsourced` → `vendor-only (narrowed)` and the counts were not
updated in the same edit (12 vs 13 vendor-only, 2 vs 1 unsourced, 13 vs 14
located) — caught only by a reader. This guard re-derives the counts from the
table and fails on any drift, so a future class move cannot leave the headline
numbers wrong.

## What it checks

- Parses the `### Summary` table rows (`| L-* |`) inside `## CLASSIFICATION`
  only — the section's action-list tables ("What would move each row") are
  ignored so they cannot pollute the count.
- A row's class is the **first backticked token in its Class cell**, so
  `vendor-only (narrowed)` and `vendor-only (competitor-published)` count as
  `vendor-only`.
- Re-derives each class count, the `Counts` sum vs table rows, and
  `Located = M − unsourced − no-claim` against the stated `N of M rows`.
- Missing `### Summary` / `**Counts:**` / `Located` line → structured
  `missing prerequisite` (exit 1); unreadable path → structured.

## Verification

- `--self-test` **PASS**: a consistent synthetic ledger is clean; moving one
  row's class without editing the Counts line is flagged (both classes plus the
  sum); a missing Counts line and a wrong Located count are flagged; an
  action-list table in another subsection does not pollute the count.
- Real run on `team/CLAIMS-LEDGER.md`: **0 findings**, exit 0 — current counts
  are consistent (13 vendor-only / 1 verified-by-us / 0 third-party / 0
  contradicted / 1 unsourced / 1 no-claim; located 14 of 16).
- Missing path → exit 1 with `missing prerequisite`, no traceback.

## Integration

Added to `team/CORVID-RD-CHECKER-SUITE.md` as the **12th guard**. Like the
thread-label guard it takes a **file path**, so it is not in the exit-contract
meta-guard's root-fixture set; its own `--self-test` is the positive control.

## Limits

- Scope is the `## CLASSIFICATION` section only; other ledger sections with
  counts are not derived.
- It checks **consistency**, not truth: a table and counts that agree on wrong
  classes still pass. Class *truth* stays with the ledger's receipts.

## Rev 2 (2026-09-13) — PROVENANCE scope + Alice's refinements

Alice's second-seat check (`team/ALICE-LEDGER-COUNT-GUARD-SECONDCHECK.md`, sha
`7a9de3c2…`) PASSed rev 1 and raised three refinements, all folded:

1. **Format-sensitive class extraction.** `_class_of()` now reads the full
   backticked span and canonicalizes: `vendor-only (narrowed)` (parenthesis
   inside *or* outside the backticks) → `vendor-only`; a hyphenated refinement
   `third-party-measured` → `third-party`. A cell that is still not a known
   class is an explicit **`unrecognized class cell`** finding, never silently
   `unknown`.
2. **Hyphenated qualifiers normalized** as above.
3. **PROVENANCE scope added.** `_check_provenance()` counts `L-*` rows in the
   `### Origin table` and checks the prose that repeats the count:
   `"N distinct origin artifacts for M rows"`, `"The N claims come from …"`, and
   `"All N rows remain …"` (number words accepted).

**Dogfooding result:** the extended guard immediately flagged a real stale cell —
`## PROVENANCE` said *"All twelve rows remain `vendor-only`"* while the origin
table had 13 rows after L-S14-02 joined the vendor-only scope. Fixed the ledger
(`twelve` → `thirteen`, signature line updated, dated custodian note); the guard
is now **0 findings** on the real ledger. sha `20d8ef5c…` → **`d74ab1e9…`**.
