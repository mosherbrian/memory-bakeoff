# P6-r9 verification completion — independent full retained gate on frozen bytes

- **Reviewer:** corvid (independent)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-verify-completion-1`, host start `2026-09-22T15:45Z`,
  deadline `2026-09-22T16:15Z`
- **Receipt:** `verify-completion-receipt.json` (corvid)
- **Authorization:** `verification-completion-authorization.md` `d9a510c`
- **Frozen base:** `f1d7c86f0b38fb653734beb9d906dae44a10a41a`
- **Bound manifest:** `composition-manifest.json` sha256
  `161afac5e212dbc99c77454f4d3cf6fd5ef1768e1c131663e60e7a26c7e78cca`
- **Scope:** read-only verification on frozen bytes. No code/test/manifest edit,
  no live effect, no retry.
- **Predecessor:** `candidate-review-repair-3.md` (INCOMPLETE, bounded).

## Verdict

**PASS.** The complete current-package retained gate runs green on the frozen
bytes: **34 passed, 0 failed, 0 errors, 0 skipped in 840.35s (14m00s), rc0**.
The manifest and `R3_REVISION.json` are re-verified before and after the run
(29/29, zero drift), the working tree is byte-identical to `f1d7c86`, and the
admitted checklist's missing-host-timer / query-failure / callback
intended-state-change / foreign-unchanged / dedup obligations are exercised by
executing the exact-CLI tests, not by reading them.

## Frozen identity — correct (pre and post)

| artifact | sha256 |
|---|---|
| `src/r3harness/harness.py` | `d7b4e517f9f846779a7da2edb57642c7c16c9050b027d2ea403a91fe532e7ea2` |
| `src/r3harness/host_adapter.py` | `231f45f0c1b62ce21799b7148bd240e04e148b7d93a6b4a079086f7359d58eea` |
| `src/r3harness/R3_REVISION.json` | `987ecef8d368953b0246a89fa2e84500e3d0236c5f11ba8c0e69ebad2b1dff01` |
| `composition-manifest.json` | `161afac5e212dbc99c77454f4d3cf6fd5ef1768e1c131663e60e7a26c7e78cca` |

- Pre-run manifest check: 29 entries, 0 mismatches.
- Post-run manifest check: 29 entries, 0 mismatches (tests mutated nothing).
- `R3_REVISION.json` `copy_sha256` equals the on-disk `harness.py` /
  `host_adapter.py` hashes (True/True); parent provenance untouched.
- `git diff f1d7c86 -- packages/P6-r9-observer-lifetime/` = empty; no
  untracked files in the package. Verified bytes are the frozen candidate.

## Newly executed — complete retained gate

**Command** (in `campaign4/packages/P6-r9-observer-lifetime`,
`PYTHONPATH=src`):

```
python -m pytest -q \
  tests/test_observer_lifetime.py tests/test_r3_lifetimes.py \
  tests/test_case_execution.py tests/test_amendment2_reconcile.py \
  tests/test_host_composition.py tests/test_amendment2_timer.py \
  tests/test_fault_ordering.py
```

**Result:** `34 passed in 840.35s (0:14:00)`, real 14m00.574s,
**rc0**. Start `15:45:59Z`, end `15:59:59Z`. stdout/commands/rc/timing saved at
`verification-completion-evidence/full-gate.log`.

Coverage decomposition (retained 27 + updated 7 = 34):

| file | tests | status |
|---|---|---|
| `test_observer_lifetime.py` | 7 | PASS (full observer file, after final reconcile edits) |
| `test_r3_lifetimes.py` | 5 | PASS |
| `test_case_execution.py` | 7 | PASS |
| `test_host_composition.py` | 5 | PASS (incl. `test_d4_full_host_sequence`, no-simulated five-case) |
| `test_fault_ordering.py` | 3 | PASS (known tamper-order regression) |
| `test_amendment2_reconcile.py` | 4 | PASS (new) |
| `test_amendment2_timer.py` | 3 | PASS (updated) |

The **full observer pass post-dates the final reconcile edits** as required:
observer ran in this same invocation, after the 07:58/07:59 reconcile edits,
on the frozen `f1d7c86` bytes.

## Newly executed — checklist obligations

**Command:** `python -m pytest -v tests/test_amendment2_reconcile.py
tests/test_amendment2_timer.py` → **7 passed in 247.33s**, rc0
(`verification-completion-evidence/checklist-obligations.log`). Each required
obligation has an independently executed test whose body asserts the property,
not return-code tolerance:

- **Missing host timer (checklist 3):**
  `test_reattach_reconstructs_missing_host_timer_bounded` — host `units.json`
  emptied after first run; reattach reconstructs for the remaining grant with
  exactly two creates and exactly two sends (no duplicate effects).
- **Query failure (checklist 3):** `test_reattach_query_failure_owned_failure`
  — `P6R9_FAIL_QUERY=1` yields `decision=owned-failure` /
  `E_TIMER_QUERY`, not a silent reuse.
- **Matching timer reuse:** `test_reattach_reuses_matching_host_timer_no_recreate`
  — exactly one create, worker+verifier each sent once.
- **Conflict:** `test_reattach_conflicting_deadline_owned_failure` —
  `owned-failure` / `E_TIMER_CONFLICT`, conflicting unit never hijacked
  (no second create).
- **Callback intended-state-change / foreign-unchanged / dedup (checklist 4):**
  `test_callback_argv_has_db_and_exact_parser_two_dbs` — exact recorded argv
  carries `--db <intended>`; due action in the intended DB transitions
  (`handled:deadline:P6F:p6c-h1w == handled-acked`,
  `decision ∈ {interrupted, recovered}`, `dedup False`); foreign DB is
  kv-identical (`_kv_keys(db2)==before2`); twice-fired is `already-handled`
  with `dedup True` and no state delta; stale id → `no-op-not-armed`; early
  foreign DB callback → `no-op-early`.
- **Duplicate create / canonical identity:**
  `test_duplicate_create_rejects_and_reuse_no_second_call`,
  `test_unit_normalized_once`.

## Carried read-only findings (not re-executed here)

- **Checklist item 1 (old-fails on immutable parent):** the parent defects
  (reattach querying `timer-arm:deadline:<action>` vs persisted
  `timer-arm:<unit>`; doubled `.timer.timer`; callback argv omitting `--db`
  → `/tmp/p6h` fallback) were independently reproduced on the unmodified
  parent in `candidate-review-repair.md` (Check 1, PASS) and
  `candidate-review.md`. This pass did not re-run the immutable-parent
  reproduction because no source changed after `f1d7c86`; it is carried as a
  prior independent result.
- Earlier repair-2 blocking findings are resolved and re-confirmed: the
  `E_R3_DRIFT` gate (now `test_d4` green) and the observer hang (full 7/7
  green here).

## Omissions / residuals

1. **Whole-repository unrelated suite not run** — explicitly out of scope per
   this authorization ("no repository-wide unrelated research suite").
   Enumerated gate above is exactly the package's retained gates plus pinned
   contract regressions.
2. **Parent old-fails reproduction carried, not re-executed** (see above);
   bytes unchanged since its prior independent verification.
3. **Teardown cost** on the failing-path drill remains 2×60s emulator waits
   (test hygiene, unchanged, non-blocking; the passing gate completed in
   14m00s).

## Effect

The repair-3 candidate on frozen bytes `f1d7c86` / manifest `161afac5…`
**passes independent verification** of the complete retained gate and the
admitted amendment-2 checklist obligations. No required gate is missing,
failed or timed out; no live, prep, witness, service, timer or seat effect
occurred. Returned to Tern for candidate acceptance and the next live
decision under Brian's standing live authority. No automatic repair or
extension implied.
