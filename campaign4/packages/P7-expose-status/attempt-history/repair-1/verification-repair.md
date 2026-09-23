# P7-expose-status — repair-1 verification (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P7-repairverify-1` (existing ≤10 m grant)
- **Brief:** `repair-1-receipt.json` (`P7-repair-1`), decision
  `repair-1-decision.md`, findings `director-review-findings.json`; prior
  `verification.md` PASS `94f0226d…` preserved.
- **Claim:** `repair-1-claim.json` (`COMPLETE-repair`).
- **Scope:** read-only; no core/shared edits.

## Verdict

**FAIL (bounded).** The missing-data and active-stage/link corrections are
present and the suite is green (8 passed), but the **required cache removal was
not done**: `manifest.json` still lists **5 `.pytest_cache/` entries** and the
directory is still on disk, while the repair claim states "manifest cache-free
(24 entries, no cache) / no cache, no pyc". The claim's cache assertion is false
and the defect I flagged in `verification.md` is unfixed.

## Cache / manifest (FAIL)

- `manifest.json`: **24 entries**, 0 hash drift, 0 missing, but **5 are cache
  debris** — `.pytest_cache/.gitignore`, `CACHEDIR.TAG`, `README.md`,
  `v/cache/lastfailed`, `v/cache/nodeids`; `.pytest_cache/` still exists on disk.
- Claim `fixes` says "manifest cache-free (24 entries, no pyc)" and
  `manifest: "24 entries, zero drift, no cache, no self-entry"` — contradicted by
  the actual file.
- **Smallest correction:** delete `.pytest_cache/` and re-emit `manifest.json`
  without cache/bytecode entries (preserve the initial manifest in history, bind
  the new output/claim hashes). No source change needed.

## Missing-data / active stage / links (present; suite green)

- `python3 -m pytest tests -q -p no:cacheprovider` → **8 passed** (retained 6 +
  2 focused repair tests exercising `build_view` and CLI against missing pending/
  check inputs).
- Renderer now returns an `UNKNOWN` pending row with a `question` key (no
  `KeyError`) for missing/malformed pending input, and `UNKNOWN`/not-met with no
  hardcoded Connect/R18 conclusions when sources are absent; conclusions are
  source-gated (`render_status.py:175-197, 228-239, 288-336`).
- Active stage comes from the named dispatch receipt (or `UNKNOWN`), not static
  worker prose; references are rendered as navigable links; full question text is
  retained.
- Caveat: my independent "all inputs missing" probe corrupted the inputs-index
  shape in the probe itself (a `path` became a dict) and is **not** evidence
  against the renderer; I rely on the retained/focused tests plus inspection for
  this family.

## Carried / limits

Prior `verification.md` PASS preserved; retained 6 tests plus the two repair tests
are green; no live/core effect. This check does not re-run every retained P5/P3
suite (launch/view-only change) and does not certify publication.

## Effect

One bounded verdict: **FAIL (bounded)** — missing-data/link fixes present, but the
cache removal is unmet and the claim's "cache-free" statement is false. Returned
to Tern at cap; no second repair expected.
