# P6-r13 — completion-2 verification (full composed R11 gate + manifests)

- **Reviewer:** corvid-dsh
- **Action:** `P6r13-completion2-verify-1` (existing ≤30 m grant)
- **Base:** `221ebfb` (Record acknowledged R13 completion release and ledger checkpoint)
- **Claim:** `completion-claims/ex-p6r13-completion-2.json` (metadata-only)
- **Evidence:** `candidate-review-completion-2-evidence/r13-composed-gate.log`.
  No source edit, no live effect.

## Verdict

**FAIL (bounded) — full composed R11 gate is not green.** The metadata corrections
that were made are correct and acyclic, but the completion **missed the R3
revision copy-hash descriptor**: `candidate/src/r3harness/R3_REVISION.json` still
declares `lifecycle.py copy_sha256 = 5a41d291…` (initial) while the actual
repaired byte is `ea61a75c…`. Every `case_entry` CLI invocation therefore aborts
`E_R3_DRIFT: R3 working copy lifecycle.py drifted`, failing the composed suite.
Two further failures are a path-alias assertion bug in the new tests. Smallest
correction is metadata-only and in scope.

## Composed gate result

Command (R11's existing full-gate invocation):
`PYTHONPATH=candidate/src python3 -m pytest candidate/tests -q -p no:cacheprovider`
→ **12 failed, 45 passed, 1407.41 s** (rc1).

| cluster | tests | cause |
|---|---|---|
| `test_case_execution.py` (5) | missing intervention, causal, five-command, forged production, disabled induction | `E_R3_DRIFT` |
| `test_host_composition.py` (1) | `test_d4_full_host_sequence` | `E_R3_DRIFT` |
| `test_observer_lifetime.py` (4) | delayed worker commits, delayed verifier, near boundary, reopen | `E_R3_DRIFT` |
| `test_r13_*` (2) | `test_module_bytes_are_new_core` | path alias `/home` vs `/var/home` |

So the composed R11 42-case gate is 10 failed / 32 passed, not green; the 15 new
tests are 13 passed / 2 failed (path alias only).

## Root cause (bounded, metadata)

`R3_REVISION.json` per-file hashes vs disk:
`lifecycle.py declared 5a41d291, actual ea61a75c` → **DRIFT**; `store/ingress/
harness` match. `case_entry._r3_hash_check` rejects any run whose working-copy
`lifecycle.py` differs from the declared copy hash, so the E_R3_DRIFT is a
provenance-descriptor staleness, not a production-behavior regression (the
repaired core itself passed the focused 15 tests and the retained 83+59 in the
prior review `9197e1c7…`).

The two `test_module_bytes_are_new_core` failures assert
`module.__file__.startswith("/home/bmosher/…")` while the resolved path is
`/var/home/bmosher/…` (symlink alias). That is a new-test defect, not a core
defect.

## Metadata fixes that ARE correct

- `candidate/composition-manifest.json`: 74 entries, 0 missing, 0 drift, **no
  self-reference**; `lifecycle.py` now `ea61a75c…`.
- `candidate/manifest.json`: 76 entries, 0 missing, 0 drift, **no self-entry**
  (its only manifest entry is for `composition-manifest.json`, which matches).
- Diff vs base `221ebfb`: **only** `candidate/changes.md`,
  `candidate/composition-manifest.json`, `candidate/manifest.json` changed —
  production source, tests and plans frozen as required.
- Acyclic recompute acknowledged; prior claims preserved.

## Smallest correction (metadata-only, in the authorized scope)

1. Refresh `candidate/src/r3harness/R3_REVISION.json` `files.lifecycle.py.copy_sha256`
   to `ea61a75c7014…` (and re-mechanically recompute the dependent manifest
   entries for `R3_REVISION.json` in acyclic order). Then re-run the full
   composed gate.
2. Fix the `/home` vs `/var/home` prefix assertion in
   `candidate/tests/test_r13_identity_independence.py` and
   `test_r13_record_integrity.py` (use the resolved path or `os.path.realpath`).

## Retained gates

Retained P5-r2 83 and P3-r3 59 were independently green in the prior bounded PASS
(`9197e1c7…`) on the same repaired bytes; not re-run in this pass because the
composed gate consumed the bound. They must be re-confirmed together with the
R3_REVISION fix before acceptance.

## Effect

One bounded verdict: **FAIL (bounded)** — metadata corrections are accurate but
incomplete; the stale R3_REVISION `lifecycle.py` copy hash breaks the full
composed gate, and two new tests have a path-alias defect. Evidence frozen;
returned to Tern for the smallest metadata correction, no automatic retry.
