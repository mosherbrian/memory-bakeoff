# P6-r9-observer-lifetime — candidate review (independent)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Dispatch receipt:** `dispatch-receipt.json` (`P6r9-candidate-1`), start
  `2026-09-22T09:24Z`, deadline `2026-09-22T09:59Z`
- **Contract:** `package.md` `bb103f35b857…` @ commit `7585aec` (unchanged)
- **Checklist:** `acceptance-checklist.md` `f52a876fcae0…` (unchanged)
- **Claim:** `completion-claims/ex-p6r9-candidate-1.json` `55780a080a4f…`
- **Manifest:** `composition-manifest.json`
  `9e59378dacc8524f5e156d0fc4ac4d50c4298af5855189cefb38308d0a7dd437`
- **Admission:** `admission-review.md` `a3a8ec84…`; parent terminal EXHAUSTED

## Verdict

**FAIL — one retained parent gate regresses; the candidate is not acceptable
as bound.** The observer-lifetime fix is well-formed and its new O1-O4
regressions pass (7/7), the manifest is clean (27/27, no self-hash), and the
parent defect is independently reproduced. But the full retained suite is
**1 failed, 24 passed**: `tests/test_r3_lifetimes.py::test_r3_first_run_identical_to_parent`
times out (120 s) under the candidate harness, in isolation as well as under
load. The candidate's own claim admits the retained suites were "copied into
this package but NOT re-run here (time)". A changed-entry regression is red, so
the candidate cannot be certified.

## Manifest / integrity — PASS

`composition-manifest.json` hash equals the claim's `manifest_sha256`
(`9e59378d…`); **27/27** listed files hash-match on disk; **0** self-hash
entries. `contract_sha256` re-derives to `bb103f35b857…`; parent pins recorded
(parent entry `P6-r8 62701f7`, parent R3 `dad98827` harness `cd84e8dd`,
retained in `R3_REVISION.json`). Diff vs parent is small and scoped:
`case_entry.py` (signed-bound overrides, `live_stop_utc`, positive reattach) and
`r3harness/harness.py` (`_observe_until`, `_wait_bound_end(until_utc)`,
verifier wait to escalation grant), plus `R3_REVISION.json` R4. `wait_s` stays
8 — no magic-constant substitution.

## O1-O4 targeted regressions — PASS (7/7)

`tests/test_observer_lifetime.py` (exact CLI, no `--simulated`): parent
delayed-worker 18 s → `no-end` FAILS (old-fails reproduced); new delayed worker
18 s commits with `sends {worker:1, verifier:1}`, settled 2, `accept`; delayed
verifier 15 s observed once; near-boundary small grant (40 s / 25 s) commits
once; expiry (15 s / 40 s) → rc3, never accept; outer `live_stop_utc` 12 s →
rc3, never accept; concurrent reopen during the worker wait commits with
`{1,1}`, settled 2. These satisfy O1/O2/O3/O4 on their own.

## Retained parent gate — FAIL (the blocking finding)

`tests/test_r3_lifetimes.py::test_r3_first_run_identical_to_parent` (a retained
parent parity gate) runs the parent harness, then the candidate R3 harness,
with no verifier end staged and `timeout=120`. The parent iteration passes and
returns `verifier-no-end`; the **candidate iteration times out at 120 s**:

```
subprocess.TimeoutExpired: [.../P6-r9-observer-lifetime/src/r3harness/harness.py
  --live ... run-fixture] timed out after 120 seconds
1 failed, 24 passed in 683.34s
```

Reproduced twice — once under the full suite and once in isolation (single-test
run: `1 failed in 122.27s`). Cause: the candidate's verifier observer now waits
`_observe_until(manifest, esc_deadline)` instead of the legacy `wait_s` slice,
so an unstaged verifier end is not escalated to `verifier-no-end` within the
test's bound. This is a first-run behavior change in the R3 resume seam, which
the contract requires to remain parent-identical; the R3 first-run parity gate
is exactly the check that catches it. The candidate left the retained test
unchanged and did not re-run it.

## Checklist disposition

- O1/O2/O3 targeted: PASS as above.
- O3/retention: **FAIL** — "retain ... parent gates" and "run changed-entry
  regressions" are not met; a retained parent test is red.
- O4: manifest/claim/inventory present; proposed live plan explicitly
  `FILL+SIGN` with no fabricated runtime values and no r8p1 reuse — PASS.
- Residuals disclosed by the worker (retained suites not re-run, single
  host/load point, reopen-during-verifier/post-commit only asserted indirectly)
  are honest but the first of them is now confirmed as an actual failure.

## Effect

Observer-lifetime design direction verified; the bound candidate is **FAIL**
because a retained parent regression is broken by the harness change. Return to
Tern for an explicit decision: keep first-run parent parity for the verifier
path (or update and justify the R3 gate with a reproducer), then re-run the
full retained suite. No live effect; no r8p1 reuse; old live signatures remain
expired. Independent verification of any successor remains a separate gate.
