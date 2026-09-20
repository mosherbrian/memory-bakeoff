# Second-seat — applied meta-guard completeness check (`6cd289e7…`) + the added drift guard

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 17:4x UTC · **Cost:** $0, static, one turn.
**Trigger:** Corvid's applied implementation differs from Assay's reviewed patch
(`CORVID-EXIT-CONTRACT-COVERAGE-APPLY.md` follow-up; "second-seat re-check
open"). No tree modified.

**Subject:** live `scripts/check_checker_exit_contracts.py` (`6cd289e7…`),
superseding Assay's `meta-coverage-completeness.diff` (`c19e0589…` / guarded
`7e289fdd…`, base `6a072f30…`). Driver:
`row-meta-coverage-applied-check/alice_meta_applied_check.py` (`936d720c…`),
result `result.json` (`48b96711…`).

## Verdict

**PASS — and the applied version is stronger than the patch it supersedes.**
Verified on the live file and in temp copies:

| case | rc | output |
|---|---|---|
| live | 0 | `16/16 hold` |
| `--self-test` | 0 | PASS |
| copied scripts **+** `check_zzz_synthetic.py` | 1 | `check_zzz_synthetic: NO CONTROL (live guard not in the covered set)`; summary `INCOMPLETE -- 1 live guard(s) uncovered … (16 declared covered)`; **no `hold` line** |
| copied scripts **−** `check_query_fork.py` | 1 | `check_query_fork: CONTROL WITHOUT A LIVE GUARD`; `INCOMPLETE -- 0 … uncovered, 1 … without a live guard`; **no `hold` line** |
| `_build_checks` key removed while still declared | 1 | `INTERNAL ERROR -- _build_checks keys != declared covered set: ['check_query_fork']` |

The fourth row is the direction Assay's patch did **not** have: the applied
version compares `_build_checks()` keys to the declared `_COVERED_NAMES`, so a
fixture-table regression cannot silently drop a control even when the file set
looks complete. Both filesystem directions run before fixtures, so a stray or
missing guard fails in a staging copy too. My earlier parse nit is closed: the
INCOMPLETE path never prints `N/N hold`.

**Observation (not a finding):** gap lines name the guard **stem** without
`.py` (`check_zzz_synthetic`), consistent with `_COVERED_NAMES` being stems; a
reader grepping the filename with `.py` will not match — my first harness
assertion made exactly that mistake, the guard is self-consistent. No action.

## Scope and limits

- Read-only over the repo; all mutation in temp copies; counts/lines only.
- I did not re-run Assay's sealed power check or Corvid's live verification; I
  rebuilt the four cases independently, including the new drift direction.
- Assay's parallel `meta-coverage-completeness.diff` is genuinely superseded:
  do not apply it on top of `6cd289e7…`.
