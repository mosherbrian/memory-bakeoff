# P6-r9 amendment 1 (retention) — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Amendment under review:** `amendment-1-retention.md`, sha256
  `5c537bea932956f627d0442b70d3aa71151157aa268fd6644a829793062b480e`
  (commit `a85c402`, byte-equal to HEAD working tree; re-derived)
- **Contract:** `package.md` `bb103f35b857…` @ commit `7585aec` (unchanged)
- **Parent checklist:** `acceptance-checklist.md` `f52a876fcae0…` (unchanged)
- **Parent candidate verdict:** `candidate-review.md` `6cbd608e0e54…` (FAIL,
  one retained R3 gate)
- **Receipt:** `amendment-1-admission-receipt.json` (`P6r9-amendment-1`),
  start `2026-09-22T10:18Z`, deadline `2026-09-22T10:23Z`
- **Worker:** HELD pending cairn's conditional release

## Disposition

**ACCEPTED**, bound to the exact amendment bytes above plus its embedded
**Replacement acceptance checks §1–4**, which are hereby the pinned
replacement checklist. The amendment is an explicit, bounded resolution of a
real contract-vs-retained-test conflict, and it does not weaken a check to fit
finished code. No implementation authorship; no live effect.

## The conflict is real, and independently confirmed

The candidate-review FAIL is caused by
`tests/test_r3_lifetimes.py::test_r3_first_run_identical_to_parent`, which runs
the parent harness and the candidate R3 harness on a plan granting
`duration_s=900`, `escalation_window_s=120`, `wait_s=2`, with no verifier end
staged and `subprocess timeout=120` (`test_r3_lifetimes.py:230–255`,
`write_plan:40–54`). I re-read the candidate harness to confirm the mechanism
rather than take the review's word:

- Verifier grant: `verify_deadline = base + duration_s` (900 s);
  escalation bound: `esc_deadline = base + escalation_window_s` (120 s)
  (`harness.py:515–519`).
- First-run verifier observation waits `_observe_until(manifest, esc_deadline)`
  — the signed escalation bound, not the `wait_s` slice (`harness.py:690–693`);
  `_observe_until` explicitly refuses to treat the slice as the bound
  (`harness.py:391–402`).
- Therefore the candidate returns at ~120 s while the test kills the process at
  exactly 120 s. The parent returns `verifier-no-end` after the 2 s slice.

So the amendment's three factual claims hold: the retained test conflates the
rejected premature return with the O1-mandated normal lifetime; the candidate
waiting to its true bound is not itself a production regression; and a timeout
at the bound proves neither bounded expiry nor acceptance. The contract's
retention clause ("parent gates") was indeed under-qualified, and the amendment
owns and narrows that ambiguity.

## The amendment does not fit a check to finished code

The replacement checks are stronger than the assertion they supersede:

- §1 keeps an old-fails/new-passes exact-CLI, no-`--simulated` proof: old bytes
  must still exhibit premature behavior while the verifier completes after the
  legacy slice but before its explicit grant, with one worker/one verifier send.
- §2 requires positive proof of *bounded owned expiry* through the real
  production grant/clock path, with the outer timeout explicitly larger than
  the authorized inner grant plus escalation/cleanup — i.e. it forbids using
  timeout inflation as the substitute for expiry evidence, and it names a
  failure to terminate by the true bound as a defect to repair, not waive.
- §3 requires *direct* evidence for reopen during the delayed-verifier and
  post-commit phases (previously only indirect), including expiry on reopen.
- §4 requires the whole retained+new suite, the full no-simulated five-case
  sequence, meaningful timing/race regressions, every failure reported, a
  mechanically refreshed manifest (no self-hash), and an explicit record of
  which old assertion was superseded and by what coverage.

It also keeps the explicit prohibitions: do not restore short waits to pass, do
not delete the test, do not raise the 120 s subprocess timeout, do not mark it
`xfail`. The superseded assertion stays in the pinned parent as immutable
history. That is contract-clarification discipline, not check-weakening.

## Scope, authority and allocation

- Scope stays test/contract conflict resolution plus any demonstrated
  bounded-expiry or verifier-resume defect strictly within O1/O2; broader
  changes require a reproducer back to Tern. Frozen parents/core unchanged;
  local copied-harness allowance retained; private tmp/intercepted effects only.
- No new live/prep/witness grant. Prior stopped fixture IDs stay historical and
  old signatures stay expired.
- Grant is prospective and conditional: after this ACCEPTED unchanged, cairn may
  dispatch **one** kiln ≤30 m repair/test update, then **one** corvid ≤25 m
  independent verification; ceilings 780/530 → 810/555, admission 5 m separate.
  No automatic repair; no reset. Expiry or verdict returns Tern; candidate PASS
  never releases live work.

## Independence

Tern authored the amendment; corvid only reviewed it and authored neither the
amendment nor any candidate code. Corvid's prior FAIL is preserved and not
retroactively revised. Independence holds.

## Non-blocking observations (for the worker, not conditions)

- The amendment says "900s worker/600s verifier"; the operative verifier
  observation bound is `esc_deadline = base + escalation_window_s` (120 s),
  while `duration_s` (900 s) is the verifier *grant*. The numbers do not change
  the required evidence, but §2 must pin the actual `esc_deadline` it exercises.
- §1 must be run against the parent bytes for the verifier phase specifically,
  since the candidate intentionally keeps the worker first-run slice unchanged
  (`harness.py:637–644`); only the verifier first-run path is the carve-out.

## Effect

Amendment `5c537bea9329…` and its Replacement acceptance checks §1–4 are
**ACCEPTED** as the pinned replacement checklist for the one bounded repair.
Cairn's conditional release condition is met for this amendment; no live
authority follows. Returned to Tern/cairn.
