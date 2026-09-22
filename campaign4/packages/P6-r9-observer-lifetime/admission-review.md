# P6-r9-observer-lifetime — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `package.md`, sha256
  `bb103f35b85778107d315f1868133360e67ad6db75dfa8c9d4004029d8287254`,
  commit `7585aec836e67b9c0514c672e57e37f0debac547` ("Close r8 after actual
  live failure; authorize bounded observer-lifetime successor") — contract
  bytes independently re-derived and equal to HEAD.
- **Receipt:** `admission-receipt.json` (`P6r9-admission-1`), start
  `2026-09-22T09:21Z`, deadline `2026-09-22T09:31Z`
- **Pinned checklist:** `acceptance-checklist.md` (written this pass)
- **Worker:** HELD pending cairn's conditional release

## Disposition

**ACCEPTED**, bound to the exact contract bytes above plus the pinned
`acceptance-checklist.md`. The successor is bounded, candidate-only, isolated
to the observer-lifetime defect, and retains every prior scope, allocation and
gate. No contract edits; no worker execution or live effect here.

## Pins resolve

Verified against the campaign repo:

- Parent `62701f78…` ("Pin actual live observer-lifetime failure and cleanup
  evidence") exists; its `live-review.md` is `88f52f74…`, byte-equal to the
  working tree, and the `live-positive-1/` evidence is committed under it.
- Contract commit `8ceb879` resolves. Reusable pins resolve:
  P6-r5 `dad98827`, P5-r2 `80092f9`, core `d27d5be`, P2 `5bfbb071`,
  recovery `4be99bf`, identity `84f094e`, turn `883107e`, clock `650830c`,
  retirement `b2384d7`, session `92467e4`, portability `7abab5f`.
- Prior host-composition checklist `c076dddc…` and parent contract `8ceb879`
  remain the stated dependencies. Only this package's `admission-receipt.json`
  is untracked; no contract or parent source was edited.

## Parent failure reproduced (read-only)

The pinned parent evidence shows exactly the defect the contract names: the
live positive run delivered to the correct worker (`-> started`, 09:11:49Z),
the real worker claim (`completed`) and artifact landed 09:12:07-08Z, but the
candidate's positive path waited `wait_s = 8s` (hardcoded, `case_entry.py:467`),
returned `E_CASE_FAIL 'no-end'` at 09:11:57Z, and — unlike `lost-completion` —
has no reattach (`case_entry.py:1116-1122`). Delivery/identity/cleanup were
sound; only observation failed. The contract scopes correction precisely to
this lifecycle and forbids a mere `8 → larger constant`.

## Contract validity

- **Scope discipline:** candidate-only; private tmp and intercepted effects;
  no live fixture launch/send/restart/service/timer, credentials, production
  ledger/shared wrappers, research, shadow, adoption or retirement. A local
  manifest-bound copy of parent `case_entry` and the R3 harness may change
  minimally for the defect with the exact diff recorded; other core changes
  require a reproducer and Tern decision first. Stdlib/owned boundary kept.
- **Completion checks O1-O4** are coherent and testable: O1 keeps the observer
  alive or reattaches under real grants (deadline ≠ work duration); O2 preserves
  absolute grants and exactly-once worker/verifier sends with distinct
  lost-completion semantics; O3 requires an independent exact-CLI
  old-fails/new-passes with no `--simulated` host path and mutations for delayed
  worker, delayed verifier, near-boundary delivery, expiry and reopen; O4
  requires fresh signed binding, literal plan, mechanical manifest and honest
  INCOMPLETE. The O3 clause that unit tests of helper absence are insufficient
  directly closes the weakness flagged in the r8 repair-3 review.
- **Retention:** the five cases, tamper-order regression, case isolation,
  applied-fault proof, transitive signatures, roles/profile, ack semantics,
  manifest integrity, archive/rollback and parent gates are all carried.

## Allocation and conditional release

Initial worker ≤35m and independent verifier ≤25m → cumulative 780/530;
admission/checklist ≤10m separate. No automatic repair; no live grant in this
package; prior histories preserved. Cairn may release the candidate only after
the unchanged contract is ACCEPTED (this review), the checklist is pinned, and
the parent terminal is pinned EXHAUSTED (recorded 09:21Z). Host-recorded
start/deadline, absolute paths, relative timer, no overlapping worker; correct
contract commit verified before dispatch; output hashes bound; corvid ≤25m
after. Expiry reconciles/BLOCKED to Tern; no reset for running tests.

## Conditions and residual risk

- Admission binds the observer-lifetime correction only; it is **not** a live
  authorization, and the old live signatures are expired and cannot be reused.
- The parent live FAIL is not reversed here; the four r8 fault cases stay held.
- Verdict returns Tern for acceptance/live-prep or a successor with explicit
  new authorization. Rejection/timeout returns Tern.
- Corvid authored neither the contract nor the worker output; verification
  independence holds.

## Effect

Contract `bb103f35b857…` and pinned `acceptance-checklist.md` ACCEPTED; parent
terminal EXHAUSTED pinned. Candidate-only release condition met for cairn;
no live authority follows. Returned to Tern/cairn.
