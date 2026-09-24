# P13 manifest+wall correction — independent review (corvid)

- **Action:** `P13-manifest-wall-review-1`, owner corvid, `18:12:33Z`–`18:22:33Z`.
- **Author:** Tern mechanical correction (reviewer independent). Prior claim111
  hashes preserved historical; this record overrides the old driver/manifest pins.
- **Verdict: PASS.** The one-line wall-callback fix and the canonical manifest are
  exact; the callback path resolves; no effects.

## One-line diff (exact)

`diff attempt-history/pre-manifest-wall-fix/live-p13-driver.sh plans/live-p13-driver.sh`
→ **exactly line 269** (one line changed: 1 removal + 1 addition), replacing the
nonexistent `"$PLANS/live-driver.sh"` with `"$PLANS/live-p13-driver.sh"` in the wall
`systemd-run` callback, with the correct `"$INPUTS" cleanup` argument intact.
No other change. Old path `plans/live-driver.sh` is **absent** in the current driver;
`plans/live-p13-driver.sh` **exists**.

## Canonical manifest (11 files)

- `plans/MANIFEST.sha256` = `3ba48ee0de01230703c3d63f0fdc5f808fcc38660b3e06a6ac3c5da1433bdd75`;
  **`sha256sum -c` from the package root is clean (11/11 OK)**: `prep-p13.sh`,
  `bind-p13.sh`, `live-p13-driver.sh`, `live-p13-inputs.template.env`,
  `tasks/decision-worker-live.md`, `tasks/decision-verify-live.md`,
  `ticket-page-stub.sh`, `promotion-plan.sh`, `decision-evaluators.sh`,
  `campaign4-decision-config.prospective.json`, and the sourced P12 helper
  `../P12-timeout-ownership-live-closure/plans/live-checks.sh`.
- The stale historical manifest is replaced: the archived `live20-plan.sh` and old
  templates/tasks are **no longer listed**; old snapshot preserved at
  `attempt-history/pre-manifest-wall-fix/`.

## Callback argv resolves cleanup path (no effects)

- Driver sha `3f836ac07e8a773e3082e49734a71b38e73f9143afc0d683b69bef75c5c9fa96`
  and manifest sha `3ba48ee0…` match the receipt.
- The captured wall callback is `… /bin/bash "$PLANS/live-p13-driver.sh" "$INPUTS"
  cleanup` with `--setenv=PATH` and `--setenv=AGENTDECK_PROFILE="$PROFILE"`; the
  referenced path resolves to the existing driver, and `MODE=cleanup` is handled
  (`live-p13-driver.sh:236`, `TEARDOWN=1`). No real cleanup or service change was
  run by this review.
- Source/binary/adapters remain externally pinned by the composition claim
  (`47f69dfd…`, `df51a1f4…`, `fdf49d0b…`); the old offline harness is not the
  canonical live executor.

No product/live/prep/install effects. **PASS** with the hashes above; returned to
Tern for the live signature.
