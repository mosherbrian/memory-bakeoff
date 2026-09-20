# Second-seat check — required-metric guard (guard 14) + the canonical-schema crash

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 13:20 UTC · **Cost:** $0, local, one turn · **Trigger:** the adoption
note's open handoff ("second-seat re-check open for Assay/Alice — adopted rule +
extended self-test"). No tree modified.

**Subject:** `implementer/repo-glm-dsh3/scripts/check_required_metrics.py`
sha256 **`c6e2f38b…`**, `team/CORVID-REQUIRED-METRICS-ADOPTION.md`,
`team/ASSAY-U2-REQUIRED-METRICS-PROTOTYPE.md`.

## Verdict

**PASS / AGREE on the adopted rule, the hashes, the self-test, and the
three-tree smoke** — all reproduce. **One real defect:** the schema reader
guards the explicit `--schema` path but **not** the canonical
`results/SCHEMA.json` path, so a malformed, empty-object, or unreadable local
schema raises an uncaught traceback. **One minor gap:** a `*/summary.csv` that is
a directory is skipped silently and still counted as a summary.

## Verified claims

| Claim | Check | Result |
|---|---|---|
| sha `c6e2f38b…` (adopted; prototype `e6b50c25…`) | re-hashed | ✓ `c6e2f38be8ec…` |
| `--self-test` PASS (extended) | re-ran | ✓ PASS, rc 0 |
| three-tree smoke | re-ran | ✓ dsh3 `106 summaries, 1 skipped, 0 findings`; dsh2 `102/0/0`; repo `102/0/0` — match the note exactly |
| missing required column flagged; waiver suppresses; unknown schema skipped | read + probes | ✓ |
| unreadable explicit schema → structured | probe | ✓ `unreadable prerequisite` |

## Defect — the canonical local schema is the unguarded path

`_read_schema()` handles `--schema` carefully (`is_file`, `os.access`, try/except
around `json.loads`), then:

```python
local = results / "SCHEMA.json"
if local.is_file():
    return json.loads(local.read_text()), []     # no guard
```

The adoption note names `results/SCHEMA.json` as the **canonical home** ("until
it is written, the bundled `DEFAULT_SCHEMA` governs"), so this is the path most
likely to be exercised. Probes:

```
results/SCHEMA.json = "{not json"   -> rc 1, JSONDecodeError traceback
results/SCHEMA.json = "{}"          -> rc 1, KeyError: 'kinds'
results/SCHEMA.json chmod 000       -> rc 1, PermissionError traceback
```

Any of these also bypasses the intended `missing prerequisite` dialect. Fix:
send the local path through the same guarded reader (and validate
`schema["kinds"]["run_summary"]` exists, reporting a structured
`malformed schema: missing kinds.run_summary` rather than a `KeyError`).

## Minor gap — a directory at `*/summary.csv`

`summaries` includes directories (glob), and the loop does
`if not p.is_file(): continue` — silent. A tree whose only summary path is a
directory reports **`summaries 1, skipped 0, findings 0`, rc 0**. The suite's
other guards treat a directory at a required artifact path as a structured
finding; this one should too (or exclude non-files from the count so
"no scannable summaries" fires).

## Observation — header matching is case/whitespace-exact

`any(c in header for c in recognized)` is exact. A summary with `Hit@5` (capital
H) is not recognized, so it is either partially flagged or, if every column is
case-varied, **skipped as unknown-schema** and never checked for the missing
metric. Documenting "recognized columns are exact" (or normalizing case/space)
would prevent a silent skip on a real summary.

## Scope and limits

- Synthetic trees under `/tmp` + read-only three-tree runs; I did not edit the
  guard or the notes.
- The adopted *rule* (which columns are required) is a judgment call and I do
  not dispute it; these are robustness gaps on the code paths around it.
- `mean_context_chars` remains a proxy for "exact returned context size", as the
  note states.
