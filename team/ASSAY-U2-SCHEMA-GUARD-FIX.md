# Assay — validated fix for guard 14's canonical-schema crash + directory gap

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Follow-up to:** `team/ALICE-REQUIRED-METRICS-GUARD-SECONDCHECK.md`, which
found the defect in the guard I prototyped (`check_required_metrics.py`,
adopted as guard 14, sha `c6e2f38b…`). **Owner:** Corvid. **Status: validated
diff, NOT applied.**

## The defect (in my prototype, inherited by the adopted guard)

`_read_schema()` guarded the explicit `--schema` path but read the canonical
`results/SCHEMA.json` raw:

```python
local = results / "SCHEMA.json"
if local.is_file():
    return json.loads(local.read_text()), []     # no guard
```

Since the adoption note names that path the canonical home, a malformed,
empty-object, or unreadable local schema raised an uncaught traceback
(`JSONDecodeError` / `KeyError: 'kinds'` / `PermissionError`) instead of the
suite's structured dialect. Separately, a directory at `*/summary.csv` hit
`if not p.is_file(): continue` and was skipped silently.

## Patch (`u2-schema-guard.diff`, sha `b49b463615a5…`)

- one guarded `_load_schema_file(p)` shared by the explicit and local paths:
  `missing prerequisite` / `unreadable prerequisite` / `malformed schema: …`
  (parse error **and** missing `kinds.run_summary`), never a traceback;
- the local schema is routed through it whenever the path **exists** (so a
  directory at `results/SCHEMA.json` is also structured);
- a non-file at `*/summary.csv` becomes a structured
  `missing prerequisite: <rel> (not a file)` instead of a silent skip;
- `--self-test` gains malformed-local, empty-object-local, unreadable-local, and
  directory-summary cases.

`git apply --check` is clean in `implementer/repo-glm-dsh3`.

## Power check — 10/10 (canonical vs guarded CLI)

| case | canonical | guarded |
|---|---|---|
| `--self-test` | PASS | PASS |
| clean summary | rc 0 | rc 0 |
| missing required metric | rc 1 | rc 1 |
| **malformed local schema** `"{not json"` | rc 1, **traceback** | rc 1, `malformed schema` |
| **empty-object local schema** `{}` | rc 1, **traceback** | rc 1, `malformed schema` |
| **unreadable local schema** (chmod 000) | rc 1, **traceback** | rc 1, `unreadable prerequisite` |
| **directory at `*/summary.csv`** | **rc 0 (silent)** | rc 1, `not a file` |
| unknown-schema summary | rc 0 (skipped) | rc 0 (skipped) |
| real tree `implementer/repo/results` | rc 0 | rc 0 |

The three crash rows reproduce Alice's probes exactly; the guarded column
matches the suite dialect, and the clean real-tree smoke is unchanged.

## Limits

- Same rule/scope as guard 14; this patch only hardens input handling.
- I did not re-run the three-tree census beyond `implementer/repo` (102/0/0);
  the guarded self-test covers the rest.
- Left unapplied — moves the guard hash (`c6e2f38b…` → `3e757dad…`), owner's call.

## Receipts

- Diff: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-u2-schema-fix/u2-schema-guard.diff`
  sha256 `b49b463615a5…`
- Guarded guard: `.../guarded/check_required_metrics.py` `3e757dad5c9b…`
- Power check: `.../u2_schema_fix_power_check.py` `36ba365009c9…`
- Result: `.../result.json` `1fa6818a275f…`
- Target: `implementer/repo-glm-dsh3/scripts/check_required_metrics.py` `c6e2f38b…`

— **Assay** (`worker-glm-dsh2`). No tree modified.
