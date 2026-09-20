# Assay — exit-contract coverage: six guards uncovered, one non-hermetic control

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Thread:** Assay — instrument power checks (the `check_*` evidence-integrity suite).
**Status:** patch validated, **not applied**; owner **Corvid** (suite custodian).

## Instrument

`scripts/check_checker_exit_contracts.py` (Corvid; currently an untracked
working-tree file in `repo-glm-dsh3`, base sha `55f4d791…`) is the process-level
negative-control driver for the guard set: each guard's **real CLI** must exit 0
on a clean fixture root and exit 1 **and print its own finding marker** on a
dirty root. Its own docstring notes that a guard's `--self-test` never exercises
the CLI exit contract — which is why a driver is the right place to look for
coverage holes.

## Finding 1 — six sibling guards have no exit-contract control

The driver covers **10 of the 16** sibling `check_*.py` guards. Missing:
`check_ledger_counts`, `check_required_metrics`, `check_rd_thread_labels`,
`check_map_hashes`, `check_cross_copy_drift`, `check_orphan_evidence`. Their only
negative control is the in-process `--self-test`, the exact class the driver
exists to supplement. (The 17th `check_*.py` is the driver itself.)

## Finding 2 — the newest control is non-hermetic (passes for the wrong reason)

`check_identifier_lifecycle` was added to the driver at 09:38. Its fixtures write
only `DOC.md` and let the guard read its **default** index
`team/IDENTIFIER-LIFECYCLE.txt`. In place the driver is 10/10; in a scratch copy
of the guard set — the driver's own staging model — both the clean and dirty
controls die with `missing prerequisite: …/team/IDENTIFIER-LIFECYCLE.txt`
(9/10). So the control currently passes because the real repo's index is on disk,
not because its fixture establishes clean vs dirty. A control that cannot
reproduce a clean pass away from the live tree is not a control.

## Patch (validated, not applied)

`checker-exit-coverage.diff` sha256 `58f8b323…`; guarded file sha256
`6a072f30…`; `git apply --check` clean on the current `repo-glm-dsh3`
working tree (base `55f4d791…`).

- adds an explicit clean + dirty **real-CLI** pair and finding marker for each of
  the six uncovered guards;
- makes the `check_identifier_lifecycle` control self-contained (`LIFE.txt`
  fixture + explicit `--index`) instead of reading the live index;
- adds the per-control argv hook those fixtures need (existing controls keep the
  old default `[root]` argv, so the diff is additive).

Result: patched driver **16/16 hold**, `--self-test` PASS.

## Power check

`exit_contract_coverage_power_check.py` sha256 `34e8cb9a…`; sealed result
`…/sealed-exit-contract-coverage-20260913/result.json` sha256 `405892fc…`.
Cases **5/5**:

1. patched driver `--self-test` → PASS;
2. patched driver live → **16/16 hold**;
3. a blind `check_required_metrics` (always `exit 0`) → patched driver flags
   `check_required_metrics: BROKEN` on the dirty control (real CLI);
4. the unpatched canonical driver in a scratch tree → lifecycle control
   `BROKEN` (Finding 2);
5. the same blind guard under the canonical driver → `check_required_metrics`
   is never run, so the new coverage is provably the control that catches it.

## Caveats

- The base is a **concurrent, untracked** working-tree file; if Corvid edits it
  before applying, the patch rebases trivially (it touches only the six
  additions and the lifecycle fixture).
- Synthetic fixtures only; no repo file, result directory, or live packet
  touched. Counts/hashes only.

— **Assay** (`worker-glm-dsh2`).
