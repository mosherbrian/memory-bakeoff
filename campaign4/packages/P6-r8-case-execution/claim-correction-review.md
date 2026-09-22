# P6-r8-case-execution — claim correction check (independent)

- **Reviewer:** corvid (independent)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Receipt:** `correction-check-receipt.json`, action `P6r8-correction-1`,
  start `2026-09-22T08:52Z`, deadline `2026-09-22T08:57Z`
- **Authority:** `claim-correction.json` (tern, `SUPERSEDING_CLAIM_FIELD_CORRECTION`)
- **Original claim:** `completion-claims/ex-p6r8-repair-3.json`
  `5ed58392e050…`
- **Scope:** mechanical check only — correction vs original claim vs file vs
  manifest; rehash all manifest entries; no code/test changes.

## Verdict

**PASS.** The superseding correction names exactly the defective field, carries
the value the disk and the manifest independently hold, leaves the original
claim byte-preserved, and every one of the 27 manifest entries re-hashes clean.
The repair-3 substance I verified earlier is unchanged.

## Checks (all mechanical, all pass)

- **Original preserved:** on-disk sha256 of `ex-p6r8-repair-3.json` is
  `5ed58392e0500d7e4197024447b47fa8de01a29031826e1d7a19b38c7f23627d`, equal to
  the correction's `original_sha256`. The original still contains the bad
  61-char value at `/changed_artifacts/1/sha256`; it was not edited.
- **Field is real and singular:** `changed_artifacts` has 3 entries; entry `1`
  is `tests/test_fault_ordering.py` and its old value is exactly
  `8b60d34e…cea07` (61 hex chars — no sha256 can produce it).
- **Correct value verified from bytes:** sha256 of
  `tests/test_fault_ordering.py` is
  `34548dc2c30daa696c8fe69c9c8445d17f8026bad8f2145550082a17447e343d`, equal to
  the correction's `correct`, and equal to the manifest entry.
- **Manifest rehash:** all **27** listed files hash-match on disk; 0
  mismatches. Manifest sha256 is `1e230862…`, equal to the correction's
  `manifest_sha256` and to the value bound in the original claim.
- **No other drift:** `case_entry.py` `ed392e66…`, `test_fault_ordering.py`
  `34548dc2…`, `composition-manifest.json` `1e230862…` and the contract pin
  `package.md` `1e0305fe…` are identical to what the repair-3 review bound; no
  artifact, test or clock was touched after that review.

## Effect

Claim binding corrected to the true artifact hash. Repair-3 causal fix,
manifest integrity and D1–D4 host composition remain verified PASS. No code,
test, timer, grant or live effect. Returned to Tern; residual triage, fresh
binding/signature and live readiness remain director gates.
