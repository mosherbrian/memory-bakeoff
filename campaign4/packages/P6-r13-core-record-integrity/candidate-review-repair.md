# P6-r13 — repair verification (finding #11 identity-from-provenance + bound files)

- **Reviewer:** corvid-dsh
- **Action:** `P6r13-repair-verify-1` (existing ≤30 m grant)
- **Repair:** `amendment-1-worker-verifier-independence.md`; claim
  `completion-claims/ex-p6r13-repair-1.json`
- **Candidate bytes:** `lifecycle.py` `ea61a75c…` (was initial `5a41d291…`),
  `ingress.py` `fe7f528d…`, `store.py` `b72d4fb3…`; claim `new_bytes` all match.
- **Evidence:** `candidate-review-repair-evidence/probe_identity.py`. No source
  edit, no live effect.

## Verdict

**PASS (bounded).** The #11 author-is-not-verifier invariant is now enforced from
authentic producer provenance: same-principal `verify_pass`/`verify_fail` reject
before any row/cache/state/atomic mutation, a caller-supplied `worker_seat` is
ignored, a distinct legitimate verifier still completes, producer identity
persists across reopen, and missing provenance fails closed. Old-fails on both
immutable baselines. **Two manifest binding defects are noted** (one matching the
claim's own note, one additional), plus one gate residual. These do not affect
runtime behavior but the binding must be corrected before final acceptance.

## Identity-from-provenance (independent public-ingress probe)

`python3 candidate-review-repair-evidence/probe_identity.py candidate/src/r3harness`
(module `lifecycle ea61a75c`, `store b72d4fb3`):

| probe | candidate (new) | R11 baseline `7ebaf466` | P5-r2 `7ebaf466` |
|---|---|---|---|
| same-principal `verify_pass` + atomic decide | **rejected `E_SELF_VERIFY`, zero change** | **ACCEPTED** (COMPLETE, writes) | **ACCEPTED** |
| same-principal `verify_fail` + atomic decide | rejected `E_SELF_VERIFY`, zero change | accepted | accepted |
| same-principal plain verify | rejected `E_SELF_VERIFY` | `E_MISSING_DISPOSITION` (incidental) | same |
| claimed `worker_seat` override on verify | rejected `E_SELF_VERIFY` (field ignored) | accepted | accepted |
| distinct verifier (corvid) | **COMPLETE + disposition**, `producer_seat=kiln` | COMPLETE, `producer_seat=None` | same |
| reopen | `producer_seat=kiln` preserved | `None` | `None` |
| missing producer identity (internal invariant) | **`E_UNKNOWN_PRODUCER`** | ACCEPTED | ACCEPTED |

Clean old-fails/new-passes. Implementation: `lifecycle.py` binds
`producer_seat` at PUBLISH from the trusted-ingress actor (`:312-317`), ignores
`worker_seat`, and `_require_distinct_verifier` guards `VERIFY_PASS`/`VERIFY_FAIL`;
`new_revision` starts `producer_seat=None`; each publish (incl. repair) rebinds.
**Change is confined to `lifecycle.py`; `store.py`/`ingress.py` unchanged** from
the initial candidate, and `HostClock.now` and the A–E behaviors are retained.

## Retained gates (independently re-run)

- `candidate/tests-retained/p5r2` → **83 passed** (0.09 s).
- `candidate/tests-retained/p3r3` → **59 passed** (16.36 s).
- `candidate/tests/test_r13_identity_independence.py` + `test_r13_record_integrity.py`
  → **15 passed** (7 identity + 8 A–E).

## Manifest / bound-file notes (must correct before acceptance)

1. **`candidate/composition-manifest.json` is STALE on `lifecycle.py`**:
   declares `5a41d291…` (initial candidate) while the actual repair byte is
   `ea61a75c…`. This matches the repair claim's `new_bytes.lifecycle`; the other
   manifest (`candidate/manifest.json`) carries the correct `ea61a75c…`. The
   stale entry does not match the claim's bound bytes.
2. **`candidate/manifest.json` self-entry is circular/stale**: it lists
   `candidate/manifest.json` declaring `06d2b926…` while the actual file is
   `cddc2eb8…` (a file cannot carry its own final hash). The entry for
   `candidate/composition-manifest.json` (`84add19a…`) does match.
3. **Gate residual:** the full composed R11 **42**-case gate was not run (claim
   ran only the focused 8: routing/rejection). Admission obligation (b) is
   therefore only partially met; the 42-gate must run on the final composed
   bytes before final acceptance.

No other self-entries: `composition-manifest.json` (74 entries) has none.

## Scope / unchanged

Host-only findings #1/#3/#4/#8/#9 are untouched; #5 remains **NOT REPRODUCED**
as recorded; live-release hold persists. No candidate except
`lifecycle.py` + tests/docs/manifests; stdlib-only; no host-adapter import.

## Effect

One bounded verdict: **PASS (bounded)** — identity-from-provenance is correct and
independently reproduced old-fails/new-passes with bound `store`/`ingress` and
retained core gates; correct the two manifest binding defects and run the full
composed 42-case gate on final bytes before acceptance. Returned to Tern.
