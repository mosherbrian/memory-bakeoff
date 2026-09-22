# P6-r9-observer-lifetime — pinned acceptance checklist

Pinned by corvid at admission before any worker run. Contract: `package.md`
sha256 `bb103f35b85778107d315f1868133360e67ad6db75dfa8c9d4004029d8287254`
(commit `7585aec`). Any contract edit invalidates this checklist. All checks are
candidate-only, private tmp, intercepted external boundaries; no live effect.

## Reproduce the parent failure first (old-fails, no `--simulated` host path)

- [ ] Failure is reproduced against the unchanged parent entry on the exact
      production deadline/notification path: positive-handoff `wait_s = 8`
      (`case_entry.py:467`) sees no end while the real first-turn completes at
      `~18-20s`; positive path has no reattach (`:1116-1122`) → terminal
      `E_CASE_FAIL 'reason': 'no-end'`. The failure must be shown with measured
      delay or a controlled equivalent through the SAME path — not a unit test
      that merely calls a missing helper.
- [ ] Capture the parent bytes/hash used and the exact observed error.

## O1 — normal positive path observes worker AND verifier

- [ ] Notification-backed positive run reaches worker **and** verifier
      completion (or real authorized expiry/owned escalation) without a short
      slice causing terminal `no-end`.
- [ ] Observer is kept alive or explicitly reattaches the same
      action/execution; no model polling loop; attach before drain; persist
      correlation/cursor.
- [ ] Deadlines derive from signed grants; detect/recover latency is separate
      from normal work duration. **No mere `8 → larger constant`.**
- [ ] Delayed worker (≥ measured 18-20s, or controlled equivalent) commits and
      the verifier is dispatched once and observed to completion.

## O2 — grant and identity preservation on reopen/reattach

- [ ] Original absolute grants preserved on reopen/reattach; no silent
      extension, no fresh execution identity.
- [ ] Late valid worker handoff → **exactly one** verifier send; delayed
      verifier outcome observed **exactly once**.
- [ ] No repeated worker send; no duplicate verifier send (assert actual send
      counts from durable transport receipts, not rc0).
- [ ] Delay verifier beyond 8s → still observed once.
- [ ] Deliver near the actual grant boundary → observed once.
- [ ] Grant expiry → bounded owned failure/escalation; absent/invalid evidence
      never success.
- [ ] Abnormal `lost-completion` semantics remain distinct from a normally slow
      model turn; normal delayed completions are not reclassified as recoveries.
- [ ] Respect any stricter signed outer live stop/cleanup bound; report owned
      INCOMPLETE rather than accept if the bound prevents completion.

## O3 — independent exact-CLI regression, NO `--simulated` host path

- [ ] Old-fails/new-passes on the exact CLI sequence with only external
      runtime/model/service effects intercepted; controlled delay through the
      SAME production deadline and notification path.
- [ ] Mutations exercised: delayed worker, delayed verifier, deliver near grant
      boundary, grant expiry, and reopen/restart during each phase.
- [ ] Assert the complete worker→verifier outcome, evidence and send counts —
      not rc0 alone.
- [ ] Retain and re-run: tamper-order regression, all five cases, case
      isolation, applied-fault proof, transitive signatures, explicit
      roles/profile, true ack semantics, manifest integrity, archive/rollback
      and parent gates; changed-entry regressions, not unchanged-parent tests
      alone.
- [ ] No forged runtime/receipt/clock facts; no weakened assertion; no
      retry-until-green; no timeout inflation.

## O4 — inventory, manifest, honest reporting

- [ ] Deliver code, tests, complete execution inventory, minimal diff/rationale
      and exact proposed live plan (literal commands, grants compatible with
      observer/subprocess lifetimes).
- [ ] Fresh runtime binding/config values explicitly filled and signed before
      any future live release; **no reuse of stopped r8p1 IDs**, no runtime
      fabrication.
- [ ] Manifest hashes generated mechanically (transitive executables, no
      self-hash); claims enumerate every known flake/residual; CLI reports
      incomplete/failure honestly; evidence labelled injected until an actual
      run.

## Admission-state preconditions (for cairn's conditional release)

- [ ] Contract `bb103f35b857…` independently ACCEPTED (this review).
- [ ] This checklist pinned before worker dispatch.
- [ ] Parent terminal pinned EXHAUSTED (recorded 09:21Z).
- [ ] Host-recorded start/deadline, absolute cwd/claim/receipt paths, relative
      timer, no overlapping worker; correct contract commit verified before
      dispatch; output hashes bound; corvid ≤25m after.

## Verdict rule

PASS only if the positive worker→verifier path completes/reattaches under real
latency and all mutations preserve grants, single sends and honest failure.
Missing timing evidence or an unobserved bound → owned INCOMPLETE; any
fabricated success, duplicate send, silent extension or weakened test → FAIL.
