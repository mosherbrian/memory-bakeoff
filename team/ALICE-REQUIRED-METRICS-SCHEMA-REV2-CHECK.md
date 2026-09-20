# Second-seat re-check — required-metric schema guard re-verified (`3e757dad…`) + shallow shape validation

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 13:31 UTC · **Cost:** $0, local, one turn · **Trigger:** re-check of
`ASSAY-U2-SCHEMA-GUARD-FIX.md`, which closes my
`ALICE-REQUIRED-METRICS-GUARD-SECONDCHECK.md`. No tree modified.

**Subject:** `implementer/repo-glm-dsh3/scripts/check_required_metrics.py`
sha256 **`3e757dad…`** (was `c6e2f38b…`); diff `b49b4636…`.

## Verdict

**PASS — all four cases I raised are closed**, the power check re-runs rc 0, and
the real tree still reads clean. **One application-status note:** the fix note
says "NOT applied", but the live guard **is** `3e757dad…` (applied with the
13:29 adoption update), so the note's status line is stale. **One residual
refinement:** the new loader validates that `kinds.run_summary` exists but not
its **shape**, so a schema that is present-but-wrong still crashes.

## Verified — my cases closed

| my finding | rev-2 behavior (probed) | result |
|---|---|---|
| malformed local `SCHEMA.json` (`"{not json"`) | `malformed schema: …` | ✓ structured, rc 1 |
| empty-object local schema (`{}`) | `malformed schema: … missing kinds.run_summary` | ✓ structured |
| unreadable local schema (`chmod 000`) | `unreadable prerequisite` | ✓ structured |
| directory at `*/summary.csv` | `missing prerequisite: … (not a file)` | ✓ structured (was silent rc 0) |
| clean real tree | `102 summaries, 0 findings` | ✓ unchanged |

`--self-test` PASS; power check `rc 0`; guarded file `3e757dad…` matches the live
tree.

## Residual — schema-shape validation is shallow

`_load_schema_file()` stops at `kinds.run_summary` presence. Probes against the
live guard:

```
{"kinds":{"run_summary":{}}}                          -> KeyError: 'required_columns'  (traceback)
{"kinds":{"run_summary":{"required_columns":"hit@5"}}} -> rc 0, summary SILENTLY SKIPPED
{"kinds":{"run_summary":{"required_columns":["hit@5"],"waiver_file":5}}}
                                                      -> TypeError: PosixPath / int  (traceback)
```

So a hand-edited `results/SCHEMA.json` with a missing/misnamed `required_columns`
(a likely typo: `required_column`), or a non-string `waiver_file`, still violates
the patch's stated rule ("a malformed/empty/unreadable schema must be a
structured finding, never an uncaught traceback"). The string case is worse than
a crash in one sense: it disables the check silently.

**Fix (small):** in `_load_schema_file`, after confirming `run_summary`, require
`required_columns` to be a **non-empty list of strings**, and `recognized_columns`
/ `waiver_file` / `glob` to be the right types when present; otherwise return a
`malformed schema: …` finding. Add one self-test case for `required_columns`
missing/typed.

## Note

- `glob` set to an invalid pattern (`"["`) did **not** crash (structured
  "no scannable summaries"), so pattern errors are already benign.
- The adopted column set and rule are unchanged; this is input-shape robustness
  only.

## Limits

- Synthetic trees under `/tmp` + read-only real run; I did not edit the guard or
  the notes. The rule itself (which columns are required) is not in dispute.
