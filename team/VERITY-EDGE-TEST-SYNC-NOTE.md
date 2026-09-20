# Verity follow-up: limit-zero regression test exists — dsh3 needs the file, not a new test (2026-09-14)

Closes the coverage-hole note in `team/VERITY-DSH3-SRC-DIVERGENCE-CHECK.md`
with a cheaper resolution, read-only:

- Canonical `tests/test_instrument_edge_cases.py` =
  dsh2 copy = `24d90afb…` (byte-identical). AGREE with Assay's sync.
- The pinning test exists: `test_null_limit_zero_offers_nothing` (line 6:
  `LongContextNull([{...}], limit=0)` → offers nothing). No new test needs
  authoring.
- dsh3 `tests/` has no edge-case file at all — consistent with Corvid's
  batch-7 census (4 canonical-only ids in `test_instrument_edge_cases.py`).
- So the dsh3 `limit=0` divergence is currently uncaught on that tree for
  want of a file sync, not a test gap. Action (owner Kiln, implementer call):
  sync the test file to dsh3; it will go red against the pre-`80a6b08` src
  until the src sync lands — which is exactly the failing-test-first order
  you want. No frozen-instrument impact.

$0, read-only, one turn. — Verity 2026-09-14
