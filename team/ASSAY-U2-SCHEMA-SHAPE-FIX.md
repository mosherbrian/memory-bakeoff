# Assay — validated schema-shape patch for guard 14

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Follow-up to:** `team/ALICE-REQUIRED-METRICS-SCHEMA-REV2-CHECK.md` (Alice's
rev-2 residual on the just-adopted guard). **Owner:** Corvid.
**Status: validated diff, NOT applied.**

## Residual being fixed

The adopted guard (`check_required_metrics.py` `3e757dad…`) validates that
`kinds.run_summary` **exists** but not its **shape**:

| local schema | current behavior |
|---|---|
| `{"kinds":{"run_summary":{}}}` | `KeyError: 'required_columns'` **traceback** |
| `required_columns` a string (`"hit@5"`) | every summary **silently skipped**, rc 0 |
| `required_columns: []` | every summary **silently skipped**, rc 0 |
| `waiver_file: 1` | `TypeError` **traceback** |
| `glob: 1` | `TypeError` **traceback** |

So a typo'd index can either crash or turn the guard into a no-op.

## Patch (`u2-schema-shape.diff`, sha `c9b1c69611b6…`)

New `_validate_schema()` called after the existence check:

- `kinds.run_summary` must be an object;
- `required_columns` must be a **non-empty list of non-empty strings**;
- `recognized_columns` (if present) a list of strings;
- `waiver_file` / `glob` (if present) non-empty strings;

any violation → structured `malformed schema: <path>: <reason>` (exit 1). The
self-test gains the five shape cases.

`git apply --check` is clean in `implementer/repo-glm-dsh3`.

## Power check — 10/10 (canonical vs guarded)

| case | canonical | guarded |
|---|---|---|
| `--self-test` | PASS | PASS |
| valid full schema | rc 0 | rc 0 |
| **empty run_summary object** | rc 1, **traceback** | rc 1, `malformed schema` |
| **`required_columns` string** | **rc 0 (silent skip)** | rc 1, `malformed schema` |
| **`required_columns: []`** | **rc 0 (silent skip)** | rc 1, `malformed schema` |
| **`waiver_file: 1`** | rc 1, **traceback** | rc 1, `malformed schema` |
| **`glob: 1`** | rc 1, **traceback** | rc 1, `malformed schema` |
| unparseable JSON (regression) | rc 1, structured | rc 1, structured |
| real tree `implementer/repo/results` | rc 0 | rc 0 |

## Limits

- Pure input validation; the U2 rule is unchanged.
- Left unapplied (moves the guard hash `3e757dad…` → `3ae6cf05…`), owner's call.
- Real-tree smoke covers `implementer/repo` only; the guarded self-test covers
  the rest of the shape matrix.

## Receipts

- Diff: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-u2-schema-shape/u2-schema-shape.diff`
  sha256 `c9b1c69611b6…`
- Guarded guard: `.../guarded/check_required_metrics.py` `3ae6cf05632e…`
- Power check: `.../u2_schema_shape_power_check.py` `7b16c6f7419c…`
- Result: `.../result.json` `cb7be6b1e6d8…`
- Target: `implementer/repo-glm-dsh3/scripts/check_required_metrics.py` `3e757dad…`

— **Assay** (`worker-glm-dsh2`). No tree modified.
