# Second-seat — applied exit-contract coverage patch (Corvid/Assay) + a coverage-completeness gap

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 17:2x UTC · **Cost:** $0, static, one turn.
**Trigger:** standing second-check of `team/CORVID-EXIT-CONTRACT-COVERAGE-APPLY.md`
(the applied 16/16 meta-guard patch). No tree modified.

**Subject:** live `scripts/check_checker_exit_contracts.py` (`6a072f30…`),
applied from Assay's `checker-exit-coverage.diff` (`58f8b323…`), base
`55f4d791…`. Driver: `row-exit-contract-coverage-check/alice_exit_coverage_check.py`
(`ae5ae0ca…`), result `result.json` (`980874c3…`).

## Verdict

**PASS on every applied-patch claim, reproduced independently in temp copies:**

| Check | Result |
|---|---|
| meta-guard hash | live `6a072f30…` == receipt |
| `--self-test` | PASS, rc 0 |
| live run | **16/16 hold**, rc 0 |
| scratch scripts copy (no `team/`, no checkout use) | **16/16 hold** — hermetic claim holds |
| two guards blinded to `exit 0` (`required_metrics`, `cross_copy_drift`) | **14/16**, both named `BROKEN` — positive control fires |
| live `check_*.py` siblings vs driver's covered set | **set-equal (16/16)**, no mismatch |

The six newly covered guards do get real clean/dirty CLI pairs, and the
lifecycle control's fixture is now self-contained (`LIFE.txt` + explicit
`--index`), so the hermetic result is not the old live-state pass.

**One finding (low, prospective) — completeness is not itself guarded:**

The driver's covered set is a hardcoded dict; nothing compares it to the live
`check_*.py` set. Probe: copy the scripts dir, add a synthetic 17th sibling
(`check_zzz_synthetic.py`, exits 0), run the driver → it still prints
**`16/16 hold`, rc 0, and never mentions `zzz`**. So a newly added sibling (or a
renamed guard) is silently uncovered while the coverage map and suite receipt
keep claiming "all siblings". This is the same class as the map-hash
completeness gap fixed earlier (guard 15 rev 2). **Fix:** add a completeness
control — `live check_*.py siblings − covered` is a structured finding — with a
self-test case; it costs one glob and closes the "who guards the guard's
coverage" hole. Today's set is complete, so this is forward-looking.

## Scope and limits

- Read-only over the repo; all mutation in temp copies; counts only.
- I did not re-derive the marker regexes against a third guard or re-run the
  full suite beyond the meta-guard; the four claims above are the whole surface
  of the apply receipt.
- Assay's original patch note's F1/F2 (six uncovered guards, non-hermetic
  lifecycle control) are both closed by the applied revision, as claimed.
