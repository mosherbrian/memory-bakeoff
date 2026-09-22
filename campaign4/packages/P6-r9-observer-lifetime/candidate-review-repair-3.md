# P6-r9 repair-3 — independent candidate verification (R3 hash refresh + observer hang + reconcile/callback)

- **Reviewer:** corvid (independent)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-repair3verify-1`, start `2026-09-22T15:37Z`, deadline
  `2026-09-22T15:44Z`
- **Receipt:** `repair-3-receipt.json` (`P6r9-repair-3`, kiln, start 14:44Z /
  deadline 15:24Z)
- **Claim:** `completion-claims/ex-p6r9-repair-3.json` (manifest_sha256
  `161afac5…`)
- **Authority:** `repair-3-authorization.md` `865d5cb` + already-admitted
  `amendment-2-host-timer.md` `592d24c1…` / `amendment-2-checklist.md`
  `5b8ae89f…`
- **Scope:** read-only verification. No live effect, no retry, no mutation.

## Verdict

**INCOMPLETE — bounded.** Every specific blocking defect that made repair-2
FAIL is independently confirmed resolved (the `E_R3_DRIFT` gate, the
previously-hanging observer test, and the two secondary coverage weaknesses
carry concrete new assertions). What I could **not** independently execute
inside this window is the complete O3 retained gate (full observer file
7/7, `r3_lifetimes`, `case_execution`, and the new reconcile 4/4). No failure
was found in anything I did run. The candidate is not called PASS because O3
explicitly requires the complete retained gate and checklist to be
independently reproduced, and that did not happen.

## Bound identity — correct

Recomputed against the working tree; all match the claim exactly:

| artifact | sha256 |
|---|---|
| `src/r3harness/harness.py` | `d7b4e517f9f846779a7da2edb57642c7c16c9050b027d2ea403a91fe532e7ea2` |
| `src/r3harness/host_adapter.py` | `231f45f0c1b62ce21799b7148bd240e04e148b7d93a6b4a079086f7359d58eea` |
| `src/r3harness/R3_REVISION.json` | `987ecef8d368953b0246a89fa2e84500e3d0236c5f11ba8c0e69ebad2b1dff01` |
| `composition-manifest.json` | `161afac5e212dbc99c77454f4d3cf6fd5ef1768e1c131663e60e7a26c7e78cca` |

`R3_REVISION.json` `copy_sha256` now records `harness.py d7b4e517…` and
`host_adapter.py 231f45f0…`; `parent_sha256` (`cd84e8dd…` / `68741f8e…`) and
provenance are untouched; no self-hash. **`composition-manifest.json` is
internally consistent: 29/29 declared file hashes match the working tree,
zero stale entries.**

## Blocking findings from repair-2 — independently resolved

1. **`E_R3_DRIFT` (was blocking finding 1).** `tests/test_host_composition.py`
   **5 passed in 23.07s**, including `test_d4_full_host_sequence`, the exact
   no-simulated five-case host composition that failed at rc3 / `E_R3_DRIFT`
   in repair-2. The refreshed `R3_REVISION.json` no longer rejects the edited
   working copy. Confirmed resolved.
2. **Observer hang (was blocking finding 2).** Ran the two decisive observer
   cases directly:
   `test_delayed_worker_commits_new` (the test that hung >170s and was killed
   in repair-2) and `test_delayed_verifier_observed_once` —
   **2 passed in 33.71s**. The shared-cause diagnosis (stale gate → fast
   `E_R3_DRIFT` → terminal path → ~120s emulator-proc teardown) is consistent
   with the observed old failure and the new pass; the previously-hanging case
   now completes in seconds. No timeout increase, assertion removal or polling
   replacement is present in the changed files I read. Confirmed resolved.
3. **Timer normalization/callback (repair-2 substance).**
   `tests/test_amendment2_timer.py` **3 passed in 2.19s** — reproduced
   independently.

## Secondary coverage weaknesses — addressed in the claim, not run by me

- `tests/test_amendment2_reconcile.py` (new, 4 tests) is claimed to exercise
  the production `run_fixture`/reopen branch with a faithful rejecting host
  model: reuse on matching active timer, reconstruct-on-missing for remaining
  grant only, `E_TIMER_UNKNOWN`/`E_TIMER_CONFLICT`/`E_TIMER_QUERY` owned
  failures, overdue `E_EXPIRED`. The file exists and is manifest-bound
  (`c46063c0…`). **I did not execute it (claimed 245s; outside window).**
- Callback two-DB strengthening is claimed in the same new file; **not
  independently executed.**

## Residuals (declared, blocking PASS)

1. **O3 retained gate not independently completed in-window.** Not re-run by
   me: full `test_observer_lifetime.py` 7/7 (claimed 341s), `test_r3_lifetimes`
   5/5 (claimed 160s), `test_case_execution` 7/7, `test_amendment2_reconcile`
   4/4 (claimed 245s). The claim's check5 is explicitly **PASS BOUNDED**.
2. **Whole-repo suite not re-run** in kiln's 40m window (claim residual) and
   not by me.
3. **Observer 7/7 predates the reconcile rework by minutes** in the claim;
   kiln argues the reworked branches are inactive under the run-case
   `FakeTimerService` path and are covered by the reconcile tests instead. I
   reproduced the two decisive observer cases after the rework (passing), but
   not the full file.
4. **Teardown cost:** failing-test teardown still burns 2×60s emulator waits
   (test hygiene, untouched, acknowledged).

## Effect

Repair-3 **resolves all three blockers** recorded against repair-2, and the
manifest/hash consistency defect is fixed and mechanically verified. The
verdict is **INCOMPLETE**, not FAIL: the remaining gap is independent
execution of the complete retained gate required by O3, which exceeded this
verification window. No live, prep, witness, service, timer or seat effect
occurred. Returned to cairn/Tern for either (a) a short independent gate run
under the remaining verifier budget, or (b) an explicit Tern decision to
accept on the bounded evidence with residuals 1–4 recorded. No automatic
repair or extension is implied.
