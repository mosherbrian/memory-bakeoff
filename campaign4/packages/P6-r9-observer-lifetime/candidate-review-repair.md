# P6-r9 repair 1 — independent candidate review (replacement checks 1–4)

- **Reviewer:** corvid (independent of author, worker and amendment)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-repairverify-1`, receipt `repair-1-receipt.json`, start
  `2026-09-22T10:41Z`, deadline `2026-09-22T11:06Z`
- **Amendment (authority):** `amendment-1-retention.md` `5c537bea9329…`
- **Admission:** `amendment-1-admission-review.md` `1f8a5503708a…`; replacement
  checklist = amendment §1–4
- **Claim:** `completion-claims/ex-p6r9-repair-1.json`
- **Bound manifest:** `composition-manifest.json`
  `673c723c11da5c2717ccf87ed350a8464bcf9a30ef1c0f8cc63d01bb1aa65ca4`
  (re-derived on disk, equals the claim's `manifest_sha256`)
- **Prior verdict:** `candidate-review.md` `6cbd608e0e54…` (FAIL, one retained
  R3 first-run parity gate) — preserved, not revised

## Verdict

**PASS** — the replacement checks 1–4 are met, the bound manifest is clean, and
the full retained+new suite is green under independent execution. The repair is
tests-only; every production file is byte-identical to the admitted candidate.
No live effect; no r8p1 reuse; old live signatures remain expired. Candidate
PASS does **not** release live work.

## Independent execution — whole retained+new suite

I ran the full candidate test directory myself (the worker's claim deferred the
~11m observer suite to this pass, marking check 4 PARTIAL):

```
PYTHONPATH=src python3 -m pytest -q tests/ -rf
27 passed in 594.56s (0:09:54)   EXIT=0   (10:42:57Z → 10:52:51Z)
```

That is 8 observer-lifetime cases, 5 R3 cases, and 14 retained
case-execution/host-composition/fault-ordering cases — all green, zero
failures, zero skips, no `--simulated` path.

## Manifest and scope — PASS

- 27/27 listed files hash-match on disk; **0** self-hash entries; manifest hash
  equals the claim's `manifest_sha256` (`673c723c…`).
- Diff vs the admitted candidate (`9e59378d…` @ `a85c402`) is exactly two files:
  `tests/test_r3_lifetimes.py` (`bb1f674e678b` → `aa267de5…`) and the manifest.
  **All `src/` production files are byte-identical** — `case_entry.py`
  `9a1bb23c…`, `r3harness/harness.py` `2a19f1b8…`, `R3_REVISION.json`
  `08ffab73…`, and the rest. "No prod-code change; frozen parents unchanged"
  holds. `test_observer_lifetime.py` is unchanged (`57560d72…`), so the
  O1–O4 targeted cases remain as admitted.

## Check 1 — old-fails / new-passes, exact CLI, no `--simulated` — PASS

- New: `test_r3_verifier_delayed_beyond_slice_completes_once` — exact CLI,
  worker staged, verifier staged at +5s (past the 2s `wait_s` slice, inside a
  30s legitimate esc grant). Result `transition-committed`/`terminal-rest`,
  exactly 2 msgs and 2 sends (one worker, one verifier). Green in the suite.
- Old: `test_r3_parent_bytes_premature_on_delayed_verifier` runs the pinned
  parent bytes and asserts `verifier-no-end`. I did **not** take the committed
  shape on faith, because it stages no verifier; I ran the same delayed-verifier
  shape against the parent bytes:

  ```
  {"parent_reason": "verifier-no-end", "parent_returned_at_s": 2.11,
   "verifier_staged_at_s": null, "rc": 0}
  ```

  The parent returns at ~2.1s — before the verifier end was even staged at 5s —
  proving the superseded premature behavior still exhibits on old bytes, on the
  same production deadline/notification path. This is the exact conflict the
  amendment resolved, not a post-hoc test fit.

## Check 2 — verifier never completes → bounded owned expiry — PASS

- Controlled-clock path: `test_r3_expiry_escalates_bounded_no_extension`
  (FakeClock, real `run_fixture` grant path, `duration_s=30`): first `no-end`,
  then `grant-expired` / `owned-recovery`, `calls_delta == 1` with
  `new_kinds == ["escalation"]` (zero fixture resends), `facts_same is True`
  (no extension), and the **strengthened** assertions pin the actual saved
  deadlines `verify_deadline == 2026-09-22T04:00:30Z` and
  `esc_deadline == 2026-09-22T04:02:00Z`.
- Verifier-phase expiry: `test_r3_late_verifier_reattach_once_no_resend` first
  run stages the worker and sends the verifier, then expires the verifier wait
  boundedly under a 25s esc grant → `verifier-no-end`, never accept.
- Real-time bounded expiry with no false COMPLETE:
  `test_expiry_owned_failure_not_success` (real 40s worker delay, `duration_s=15`)
  returns rc3 and asserts `"verdict": "accept"` is absent. Outer CLI/script
  timeouts (120s) exceed the inner grants (25–30s) plus escalation/cleanup, so
  the timeout is a safety net, not the authority.

## Check 3 — reopen during delayed verifier and after worker commit — PASS

- Verifier phase: `test_r3_late_verifier_reattach_once_no_resend` — first run
  expires honestly, late valid verifier outcome consumed once on reattach
  (`transition-committed`/`duplicate-end-ignored`), msg count stays 2, send map
  unchanged (`sent_before == sent_after`), and `r3:` facts unchanged (absolute
  deadlines preserved). This is direct evidence, replacing the previously
  indirect assertion.
- Worker phase: retained `test_r3_late_completion_once_no_resend` — late worker
  commit then reattach, same worker identity never resent, exactly one verifier
  send, claim `completed`.
- Reopen during the live worker wait: `test_reopen_worker_phase_same_execution`
  (concurrent reattach while the late end is in flight) settles 2 actions with
  `{worker:1, verifier:1}`. Green.

## Check 4 — full suite, manifest/claim, supersession recorded — PASS

- Whole retained+new suite green (above); the exact no-`--simulated` five-case
  sequence is present and green: delayed worker (`test_delayed_worker_commits_new`),
  delayed verifier (`test_delayed_verifier_observed_once`), near boundary
  (`test_near_boundary_small_grant`), expiry
  (`test_expiry_owned_failure_not_success`), reopen
  (`test_reopen_worker_phase_same_execution`), plus the parent old-fails and
  outer-stop cases.
- Manifest generated mechanically, no self-hash, hash-bound to the claim.
- Supersession recorded explicitly in the test module docstring and the claim:
  `test_r3_first_run_identical_to_parent` is retained in the pinned parent only
  and is replaced by `test_r3_verifier_delayed_beyond_slice_completes_once` +
  `test_r3_parent_bytes_premature_on_delayed_verifier` +
  `test_r3_late_verifier_reattach_once_no_resend` + the strengthened expiry
  deadline assertions.
- Claim honesty: check 4 was self-reported PARTIAL (observer suite deferred).
  I executed the deferred suite; it passed. No failure was concealed — the one
  reported disposition issue (`question_answered` kind) was fixed in test setup,
  not production.

## Non-blocking observations

- `tests/test_r3_lifetimes.py:232` contains a vacuous assertion
  (`... is None or True`). Harmless dead residue; the substantive deadline
  assertions on the following lines carry the check. No action required.
- The committed parent old-fails test stages no verifier; my probe supplies the
  matching delayed-verifier shape and confirms the same premature return, so the
  gap is closed by this review's independent evidence.

## Effect

Replacement checks 1–4 independently verified; manifest `673c723c…` 27/27
clean; whole suite 27/27 green in 9m54s. **PASS** on the bound repair candidate.
Returned to Tern for acceptance / live-prep decision; no live authority follows,
no r8p1 reuse, old live signatures expired.
