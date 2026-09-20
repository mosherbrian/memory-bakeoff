# Assay — meta-guard coverage completeness (closes Alice's exit-contract carry)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Thread:** Assay — instrument power checks.
**Trigger:** Alice's carried finding in
`team/ALICE-EXIT-CONTRACT-COVERAGE-SECONDCHECK.md` (on the applied 16/16 patch).
**Status:** patch validated, **not applied**; owner **Corvid**.

## Defect

`scripts/check_checker_exit_contracts.py` (`6a072f30…`, the applied 16/16 patch)
has a **hardcoded** covered set. Nothing compares it to the live `check_*.py`
siblings, so a new or renamed guard is silently uncovered:

- staged real guard set + a synthetic 17th sibling `check_zzz_synthetic.py`
  (exits 0) → canonical driver prints **`16/16 hold`, rc 0, never names `zzz`**.

The coverage map and suite receipt would then keep claiming "all siblings".
Same class as the map-hash completeness gap fixed in guard 15 rev 2.

## Fix

`coverage_gaps(scripts, covered, driver_name)` reports both directions —
`live check_*.py siblings − covered` (`uncovered guard: <name>`) and
`covered − live` (`control names a missing guard: <name>`). `main()` prints the
gaps, appends `; coverage gaps: N` to the summary, and returns 1. The self-test
gains the uncovered/absent-guard cases.

`meta-coverage-completeness.diff` sha256 `c19e0589…`; guarded file sha256
`7e289fdd…`; `git apply --check` clean on the current `repo-glm-dsh3` working
tree (base `6a072f30…`).

## Power check

`meta_coverage_completeness_power_check.py` sha256 `710c68b4…`; sealed result
`sealed-meta-coverage-20260913/result.json` sha256 `caec34f7…`. **5/5**:

1. patched `--self-test` PASS;
2. patched on the real 16-sibling set → **16/16, no gaps, rc 0** (no false positive);
3. canonical + synthetic 17th → **16/16, rc 0, never names it** (defect reproduced);
4. patched + synthetic 17th → `uncovered guard: check_zzz_synthetic.py; coverage gaps: 1`, **rc 1**;
5. patched + one real sibling removed → `control names a missing guard: check_orphan_evidence.py`, **rc 1**.

## Self-caught bug (recorded, not hidden)

The first draft passed the check **names** (no `.py`) to `coverage_gaps`, which
globs **file names**; on the real staged set it printed 32 phantom gaps. The
driver's own self-test did **not** catch it, because its fixtures already used
`.py` names — only the real-set case (case 2) did. Fixed at the call site with
`{f"{n}.py" for n in checks}`. This is the second time in this thread that a
check-against-the-real-set caught a defect a synthetic self-test missed; the
power check is what makes the fix trustworthy.

## Composition

- Independent of my earlier `checker-exit-coverage.diff` (already applied) and of
  the lifecycle `split`-cue work.
- Mirrors `check_map_hashes.py`'s live-vs-covered check, so the two suite-level
  completeness holes are now closed by the same rule.
- If applied, the driver gates on a new/renamed guard; the coverage map's Layer A
  count becomes self-guarding rather than a claim.

## Limits

Synthetic staged guard sets and one read-only real-set copy; no tree, result
directory, or live packet touched; counts/booleans only.

— **Assay** (`worker-glm-dsh2`).
