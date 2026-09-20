# ADOPTION — U2 required-metric guard (guard 14)

**Author:** Corvid (`worker-glm-dsh3`), ledger custodian / suite owner
**Date:** 2026-09-13 · **Cost:** $0, static, no model
**Prototype:** Assay (`worker-glm-dsh2`), `ASSAY-U2-REQUIRED-METRICS-PROTOTYPE.md`,
guard sha `e6b50c25…`, power check `0c81dd3a…`.
**Artifact:** `implementer/repo-glm-dsh3/scripts/check_required_metrics.py`
sha256 `c6e2f38be8ecf829f37812942b89e0b511cfdf8d9de09ec5369fc23de4199a54`.

## Why it exists (coverage-map U2 / Muse 4.5)

A cited `summary.csv` can pass guards 1–3 and still omit a metric AGENTS
requires ("always report exact returned context size and harmful/prohibited
presence; do not rely on prohibited fraction alone"). The guard's schema index
requires `hit@5`, `prohibited@5`, and a context-size proxy
(`mean_context_chars`) to be exposed; a missing required column is a finding
unless the result dir's `METRIC-WAIVER.json` lists it. Unknown-schema summaries
are **skipped, not failed**.

## Second-driver verification (Corvid, before adoption)

Re-ran Assay's prototype independently on all three trees:

| tree | result |
|---|---|
| `repo-glm-dsh3/results` | 106 summaries, 1 skipped, **0 findings**, rc 0 |
| `repo-glm-dsh2/results` | 102 summaries, 0 skipped, **0 findings**, rc 0 |
| canonical `implementer/repo/results` | 102 summaries, 0 skipped, **0 findings**, rc 0 |

This matches his real-tree smoke (102/102 conformant), so the three-column
required set yields no false positives today.

## Adoption

- Copied to `scripts/check_required_metrics.py`; **rule unchanged**, prototype
  authorship credited in the docstring.
- Extended `--self-test` (beyond Assay's) to reject: unknown-schema summary
  skipped; missing results dir; missing explicit `--schema`; zero summaries —
  all structured, matching the suite dialect.
- Added to `team/CORVID-RD-CHECKER-SUITE.md` as **guard 14**; coverage-map U2
  marked closed; the map's verdict now lists only U3/U4/U5 as open.

## Verification

- `--self-test` **PASS**.
- Three-tree run: **0 findings** each (table above).
- Not added to the exit-contract meta-guard's fixture set: the guard takes a
  results dir (not a tree root), so its own self-test is the positive control —
  same treatment as the label/ledger/orphan guards.

## Limits (adopted from Assay's note)

- The required set is a judgment call and deliberately minimal; adding metrics
  grows false positives.
- `mean_context_chars` is a machine-checkable **proxy** for "exact returned
  context size", not proof the size was reported in the right row.
- Covers `summary.csv` run summaries only; other result kinds need their own
  schema entry.
- It does not verify cited numbers (guard 3 does); it verifies the required
  metrics are present to be cited at all.

## Handoff

- Second-seat re-check open for Assay/Alice (adopted rule + extended self-test).
- The canonical home for the index is `results/SCHEMA.json`; until it is
  written, the bundled `DEFAULT_SCHEMA` governs.

## Guarded canonical-schema fix (2026-09-13, closes Alice's second check)

Alice's second-seat check (`ALICE-REQUIRED-METRICS-GUARD-SECONDCHECK.md`, sha
`b8751993…`) found the canonical `results/SCHEMA.json` path was read unguarded:
malformed JSON, `{}`, and `chmod 000` each raised a traceback, and a directory at
`*/summary.csv` was skipped silently. Assay built `u2-schema-guard.diff`
(`b49b4636…`); Corvid applied it to this tree. `_load_schema_file()` now guards
the explicit and canonical paths, returning structured `missing prerequisite` /
`unreadable prerequisite` / `malformed schema` (parse error **and** missing
`kinds.run_summary`), and the directory case is a structured `not a file`
finding. Verified independently by Corvid: all three schema faults → rc 1, **0
tracebacks**; directory summary → rc 1; three-tree smoke unchanged (0 findings).
The applied file is byte-identical to Assay's guarded seal
(`c6e2f38b…` → **`3e757dad…`**).

## Schema-shape fix (2026-09-13, closes Alice's rev-2 residual)

Alice's re-check (`ALICE-REQUIRED-METRICS-SCHEMA-REV2-CHECK.md`, sha `0a84c425…`)
found `_load_schema_file` checked `kinds.run_summary` **existence** but not its
shape: `{"kinds":{"run_summary":{}}}` → `KeyError` traceback, `required_columns`
as a string → summaries **silently skipped** (rc 0), `waiver_file: 1` →
`TypeError` traceback. Assay built `u2-schema-shape.diff` (`c9b1c696…`); Corvid
applied it. `_validate_schema()` now requires `kinds.run_summary` to be an
object, `required_columns` a non-empty list of non-empty strings,
`recognized_columns` a list of strings, and `waiver_file`/`glob` non-empty
strings; any violation → structured `malformed schema: <path>: <reason>`.

Verified independently by Corvid: all five shape faults (`{}` kind,
`required_columns` string, `required_columns` `[]`, `waiver_file:1`, `glob:1`) →
rc 1, **0 tracebacks**, no silent skip; three-tree smoke unchanged (0 findings).
Applied file byte-identical to Assay's guarded seal
(`3e757dad…` → **`3ae6cf05…`**). Note: Assay's earlier fix note's "NOT applied"
line is stale — the live guard is applied through both fixes.
