# P7-expose-status — verification (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P7-verify-1` (existing ≤20 m grant)
- **Brief:** `dispatch-receipt.json` (`P7-initial-1`), contract `e4adcd51…`,
  admission `ce08567f…`.
- **Claim:** `completion-claim.json` (`COMPLETE-view`).
- **Scope:** read-only; view-only, no shared/core edits.

## Verdict

**PASS (bounded).** Every pinned blocking check holds, the render is stable and
non-mutating, and the view truthfully distinguishes accepted vs terminated/historical
evidence. One bounded packaging defect: the bound `manifest.json` includes five
`.pytest_cache/` cache-debris entries that should be removed before the director
publishes the derived view.

## Blocking checks (PASS)

- **Open judgment:** `pending-decisions.json.pending` carries the real `S13-1` row
  with exact question, owner `tern`, affected dependents (`S13-1 verdict`),
  options, raised date, source link, and `next_action: owner decision required;
  dependents blocked`.
- **Resolved ceases pending:** the `2026-09-21 07:36` false-alarm row is in
  `resolved_not_pending` with its `RETRACTED 07:38 — FALSE ALARM` resolution and
  source link — it does not inflate the pending list (`pending: 1`).
- **Missing/stale/conflict never healthy:** `costs` is `unknown (allocations are
  ceilings, not costs)`; the `architecture` input is explicitly `stale=True`; the
  view states nothing is live/scheduled/inferred PASS.
- **Accepted vs historical:** R18 `ACCEPTED_SCOPED_CANDIDATE` (7857c0ce) vs R19
  `TERMINATED` (`live_executed:false`, boundary not failure) are distinguished;
  R9 remains a pinned historical witness, not transferred to later bytes.
- **Activity ≠ truth:** TSV counts labelled "edited activity log … not immutable
  truth; counts are activity, not cost"; per-owner counts only.
- **No scheduling / no invented sponsor decision:** P8 owns dependent enforcement;
  the eight checks show 3 met-at-boundary / 5 partial with owners, and no decision
  is fabricated.

## Render stability / non-mutation (PASS)

- Single documented command: `python3 src/render_status.py --out-dir <dir>
  [--as-of UTC]`; two renders at the same `--as-of`
  (`2026-09-23T04:00:00Z`) produced **byte-identical** `status.md` +
  `pending-decisions.json`.
- Inputs (`campaign4/pending-decisions.md`, `inputs-index.json`) hashed before and
  after a render — **unchanged**; the renderer writes only the output dir.
- Outputs are host-stamped with an explicit as-of; no server/deps/state/live.

## Tests

`python3 -m pytest tests -q -p no:cacheprovider` → **6 passed** (open judgment
exact; retracted not pending; UNKNOWN/CONFLICT never healthy; 3-met/5-partial;
stable+non-mutating; pointers+links).

## Bound manifest

`manifest.json` 17 entries: 0 hash drift, 0 missing. **Bounded defect:** 5 entries
are cache debris — `.pytest_cache/.gitignore`, `CACHEDIR.TAG`, `README.md`,
`v/cache/lastfailed`, `v/cache/nodeids` — spurious published files (contrast the
R18 standard excluding bytecode/cache debris). Remove `.pytest_cache/` and re-emit
the manifest before director publish; the view/claim hashes are otherwise exact.

## Effect

One bounded verdict: **PASS (bounded)** — blocking checks, render stability and
non-mutation verified; remove the `.pytest_cache/` debris and re-emit the manifest
before publishing. Returned to Tern.
