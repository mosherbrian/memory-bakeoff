# Assay — U2 required-metric guard prototype (selective-metric omission)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static, no model
**Closes the design gap named in** `team/CORVID-CHECKER-COVERAGE-MAP.md` Layer C
**U2** (Muse batch-4 ACCEPT 4.5): a cited summary can pass every check while a
required harm/context metric is simply never present. AGENTS: *"always report
exact returned context size and harmful/prohibited presence; do not rely on
prohibited fraction alone."*
**Status:** validated prototype, not wired into the suite. Owner for adoption:
Corvid.

## Design

Small schema index (bundled as `DEFAULT_SCHEMA`, canonical home
`results/SCHEMA.json`):

```json
{"kinds": {"run_summary": {
  "glob": "*/summary.csv",
  "recognized_columns": ["hit@5", "prohibited@5", "mean_context_chars"],
  "required_columns": ["hit@5", "prohibited@5", "mean_context_chars"],
  "waiver_file": "METRIC-WAIVER.json"}}}
```

`check_required_metrics.py [results_dir] [--schema PATH]`:

- a `*/summary.csv` is a benchmark summary iff it carries any recognized column;
- every required column must be present, or the result dir's
  `METRIC-WAIVER.json` must list it explicitly (waived count reported);
- a summary with none of the recognized columns is **skipped**, not failed
  (unknown schemas do not false-positive);
- missing results dir / explicit schema / zero summaries / unreadable summary →
  structured prerequisite findings (exit 1), matching the suite dialect.

The guard takes a results root, so it can join the meta-guard's fixture set.

## Power check — 10/10

| case | rc | observed |
|---|---:|---|
| `--self-test` | 0 | complete clean; missing metric flagged; waiver suppresses |
| missing results dir | 1 | `missing prerequisite` |
| missing explicit `--schema` | 1 | `missing prerequisite` |
| no summaries | 1 | `no scannable summaries` |
| complete `summary.csv` | 0 | clean |
| missing `mean_context_chars` | 1 | `required metric not reported` |
| + `METRIC-WAIVER.json` | 0 | waived, suppressed |
| unknown-schema summary (`foo,bar`) | 0 | skipped, not failed |
| unreadable summary (`chmod 000`, euid 1000) | 1 | `unreadable prerequisite` |
| **real tree** `implementer/repo/results` | 0 | **102/102 summaries carry all three** |

## Real-tree smoke (the feasibility datum)

On the canonical tree, all **102** `results/*/summary.csv` already expose
`hit@5`, `prohibited@5`, and `mean_context_chars` — so the three-column required
set produces **zero false positives today**. That is what makes U2 adoptable
now: the index is small and the current tree is already conformant.

## Limits

- The required-column choice is a judgment call; it is deliberately minimal (hit,
  prohibited, exact context size). Adding metrics grows false positives.
- Presence of `mean_context_chars` is a machine-checkable proxy for "exact
  returned context size", not a proof the size was *reported* in the right row.
- Covers `summary.csv` run summaries only; reader/other result schemas would
  need their own `kinds` entry.
- It does not verify cited numbers against the file (that is suite guard #3);
  it verifies the required metrics are present to be cited at all.

## Receipts

- Guard: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-u2-required-metrics/check_required_metrics.py`
  sha256 `e6b50c25f9aa…`
- Power check: `.../u2_required_metrics_power_check.py` `0c81dd3a100d…`
- Result: `.../result.json` `bdec01b596e6…`
- Re-run: `python3 u2_required_metrics_power_check.py` (rc 0)
- Gap named in: `team/CORVID-CHECKER-COVERAGE-MAP.md` Layer C U2

— **Assay** (`worker-glm-dsh2`). No tree modified.
