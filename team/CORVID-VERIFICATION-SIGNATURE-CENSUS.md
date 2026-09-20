# Verification-signature census (batch-8 disposition 3 probe)

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, read-only
**Artifact:** `implementer/repo-glm-dsh3/scripts/census_verification_signatures.py`
sha256 `e01ccf208ecebfd4cec2fe94b3aeea5b59e907430c30432f1ccde69c7a337613`
(`--self-test` PASS).
**Instantiates:** `team/MUSE-IDEATION-08.md` disposition 3 — the six-field
auditable signature `(verifier-id, artifact-hash, check-id/version, timestamp,
exposure-flag, result)`. This is a **census, not a gate**: it measures how far
the convention already holds so the team can decide whether to enforce it.

## Census (team/ receipt-shaped filenames, n=114)

| field | receipts carrying it | share |
|---|---|---|
| timestamp | 114 | 100.0% |
| verifier-id | 113 | 99.1% |
| result (PASS/AGREE/…) | 107 | 93.9% |
| artifact-hash | 90 | 78.9% |
| check-id/version | 74 | 64.9% |
| **exposure-flag** | **21** | **18.4%** |

By verifier (n): Alice 67, Assay 29, Verity 5, Anvil 4, Corvid 3, Kiln 2, Cairn 1
(+ three heuristic false-positive prefixes: DIGEST/SPARK/R2H).

## Reading

- **The first three fields are already habitual** — dates, a verifier name, and
  a verdict are in nearly every receipt. That is the cheap half of the format.
- **Artifact-hash is the real gap** (~1 in 5 receipts states a verdict with no
  artifact hash), which is exactly where "verified" can float free of the bytes.
- **check-id/version at 64.9%** reflects that many receipts name the artifact in
  prose rather than a pinned id/rev.
- **exposure-flag at 18.4%** is the field the convention newly introduces; it is
  understandably absent from receipts written before batch 8. This is the
  adoption baseline, not a defect list.
- Receipts with the near-empty ANVIL/SPARK score (0–1 fields) are mostly
  read-only syntheses, not verifications — a sign the filename filter over-counts
  non-verification notes.

## Recommendation

Enforce the fields in order of cost/benefit, not all six at once:

1. **exposure-flag** on any verification that touches a blinded/recused artifact
   — cheapest and highest-value (the blind-quorum collapse in row 37 was exactly
   an unlabeled exposure).
2. **artifact-hash** on every `verified-by-us` claim — closes the 21% that state
   a verdict without bytes.
3. check-id/version can map to the target artifact path + its recorded sha, so it
   rides (2); timestamp/verifier/result already hold.

Do **not** gate on all six retroactively — that would fail 80%+ of historical
receipts for a convention that did not exist. A forward-only requirement (new
verification notes) is the honest form; owner decision.

## Limits

- Presence-only regex census: it does not validate that a stated hash matches
  the cited bytes, nor that the named verifier signed it.
- Filename-prefix grouping has named false positives; the field counts are the
  load-bearing output, not the per-verifier rows.

— **Corvid** (`worker-glm-dsh3`). $0, local.
