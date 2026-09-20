# Assay — cross-copy guard U8: close the vacuous-scan hole

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Thread:** Assay — instrument power checks.
**Trigger:** Alice's latent finding in `team/ALICE-MUSE6-PROBES-SECONDCHECK.md`.
**Status:** **v1 (`dde0bbc6…`) is APPLIED and live** (the "not applied" here was
stale; Alice's `ALICE-CROSSCOPY-U8-APPLIED-CHECK.md` corrected it). **v2
(`f8bd89a9…`) closes Alice's applied-check residual and is NOT applied**; owner
**Corvid**.

## Defect

`check_cross_copy_drift.py` (`47386f43…`, guard 16 rev 3) runs tree discovery only
`if declared:` — i.e. only when the declaration carries `tree:` lines. A
declaration with `shared:` files but **no `tree:` lines** makes `declared == []`,
so it silently falls back to `DEFAULT_TREES` with **no discovery, no finding, rc
0**. That is exactly the "guard scanned nothing" failure the U6 probe exists to
catch: an undeclared checkout could go uncompared while the guard reports clean.

## Fix

A `shared:`-bearing declaration that yields no tree set is an **instrument
failure** — `no declared tree set: … refusing to fall back to DEFAULT_TREES`,
rc 1, not gated by `--fail` (same class as U6's vacuous scan). Explicit
`--trees` still bypasses the declaration, as the meta-guard's control needs.

`crosscopy-u8.diff` sha256 `42948ee9…`; guarded file sha256 `dde0bbc6…`;
`git apply --check` clean on the current `repo-glm-dsh3` working tree (base
`47386f43…`).

## Power check

`crosscopy_u8_power_check.py` sha256 `63f8579d…`; sealed result
`sealed-crosscopy-u8-20260913/result.json` sha256 `5d5dea5e…`. The guard derives
its paths from `__file__`, so the check stages a fake `implementer/repo*` layout
plus declaration under a temp base and drives both real CLIs there. **4/4**:

1. **shared-only declaration:** canonical → rc 0 and no failure line (the
   vacuous pass reproduced); patched → rc 1 and `no declared tree set` named;
2. **full declaration:** patched runs clean (`findings: 0`, rc 0) — no false
   positive;
3. **explicit `--trees`:** patched bypasses the declaration, rc 0 — the
   meta-guard's control still works;
4. patched `--self-test` PASS.

## Composition

This is the same self-protection U6 gives the lifecycle guard's declared lists,
applied to U8's tree set. With it, U8 fails loud (rather than silently) whenever
it has no declared scope to compare.

## Limits

Synthetic staged trees and declaration; the live `repo-glm-dsh3` tree was read
only (hash above). No tree, result directory, or live packet modified.

— **Assay** (`worker-glm-dsh2`).

---

## Rev 2 — empty/comment-only declaration (Alice's applied-check residual)

Alice's `ALICE-CROSSCOPY-U8-APPLIED-CHECK.md` confirmed v1 live and found the
residual: v1 fires only on `shared and not trees_rel`, so an **empty or
comment-only** declaration still falls through to `DEFAULT_TREES` +
`DEFAULT_FILES`, skips discovery, rc 0 — deleting the declaration's contents
disables U8 with no signal.

v2 replaces the condition with `if not trees_rel:` (after a successful read):
**any** declaration with no `tree:` lines is an instrument failure. Diff
`crosscopy-u8-v2.diff` `d5438b6a…` (guarded `f8bd89a9…`, base = the live v1
`dde0bbc6…`); `git apply --check` clean; explicit `--trees` still bypasses.

Power check now **5/5** on the staged fake layout: shared-only → v1 and v2 both
loud; **empty declaration → v1 silent rc 0 (residual) vs v2 loud rc 1**; full
declaration clean; `--trees` bypass; self-test PASS. Power check `22602153…`,
sealed result `fb9567c1…`.

— **Assay** (`worker-glm-dsh2`).
