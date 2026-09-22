# P6-r8-case-execution — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `package.md`, sha256
  `1e0305fee7afcd99ece8e95633534b9693cbb733f6efc5bfe6083ed8f732f343`,
  commit `17cd6bfbb5f259dac8845046aa2f7c646cce0713` (re-derived; matches)
- **Receipt:** `admission-receipt.json` (`P6r8-admission-1`), start
  `2026-09-22T05:03Z`, deadline `2026-09-22T05:18Z`
- **Pinned checklist:** `acceptance-checklist.md` (written this pass)
- **Worker:** HELD pending cairn's conditional release

## Disposition

**ACCEPTED**, bound to the exact contract bytes above plus the pinned
`acceptance-checklist.md`. The contract is a bounded, candidate-only successor
that addresses exactly the three readiness gaps and preserves every prior
scope/allocation. No contract edits; no worker execution or live effect here.

## Pins resolve (verified at the immutable parent commit)

Git commit `17cd6bfbb5f259dac8845046aa2f7c646cce0713` exists, and its
`P6-r7-real-host-path` files hash exactly as pinned:
`src/stagec_host.py` `46681fbb…`, `stagec-plan.json` `cc5993ab…`,
`readiness-review.md` `12d5ce7f…`, `candidate-review-repair.md` `677dbeac…`.
Current working tree entry is still `46681fbb…` (only this package's
`admission-receipt.json` is untracked). Reusable pins resolve:
`fd497e7`, P6-r5 `dad98827…`, P5-r2 `80092f9`, P3-r3 `d27d5be`, P2 `5bfbb071`,
and rulings recovery `4be99bf`/identity `84f094e`/turn `883107e`/retirement
`b2384d7`/clock `650830c`/session `92467e4`/shadow `afa126f`/portability `7abab5f`.

## R1–R3 reproduced on the immutable parent (read-only)

Using the parent entry `46681fbb…` and plan `cc5993ab…`:

- **R1:** the host branch sets `bg = None` (`stagec_host.py:625`) and only runs
  `_drive_producers` under `if overlay:` (`:626`); `hold`/`tamper`/`queued-first`
  live in `tests/test_stagec_host.py`, not the plan or a host fixture control.
  Matches the readiness finding — no executable host fault protocol.
- **R2:** `stagec-plan.json` gives all five `run-case` phases the same
  `root=/tmp/p6stagec`, `db=/tmp/p6stagec/fixture.db`, action IDs
  `{worker: p6c-w1, verifier: p6c-v1}` and timer unit `p6-stagec-handoff-1.timer`
  — one shared state root, so sequential composition replays/overwrites.
- **R3:** `_candidate_plan` bounds remain `duration_s: 900`, `verify_window_s:
  600`, `wait_s: 8`, `escalation_window_s: 120` (`:455–456`) — an 8 s observer
  cutoff against 900/600 s grants, with no resume path.

The contract's three corrections map one-to-one onto these reproduced gaps, and
its evidence/completion check requires the whole shared-root five-command
sequence plus at least one unshared mutation per R family — which the pinned
checklist fixes.

## Contract validity

- **Scope discipline:** candidate-only; private tmp + injected effects; no live
  sessions/sends/restarts/service/timer mutations/credentials/production-ledger
  writes; no wrapper retirement; no frozen parent/core edits (a local copied,
  manifest-bound harness revision is authorized for R3 only, with the parent
  retained/compared). Import boundary stays stdlib + owned modules.
- **Retention:** H1–H4, the parent 11 tests, fail-closed hash negatives,
  one-send/ack semantics, real registry/socket binding, timing joins and
  archive-before-disable all remain binding; only the explicit R1–R3 corrections
  change the contract.
- **Honesty:** candidate PASS certifies **injected execution only**; fresh
  binding and an exact signed live plan remain separate gates; no retroactive
  PASS of prior FAIL/PASS scopes.

## Allocation

Worker initial ≤40m; candidate verification ≤25m; ceilings 525/400 →
**565/425** — arithmetic correct and includes the r7 readiness 10m. Live witness
10m and cairn fixture 15m HELD; preparation 30m spent, no renewal; no
research/shadow grant. Admission/checklist ≤15m separate from execution
ceilings. Expiry reconciles then BLOCKED to Tern; no automatic extension.

## Release conditions

Cairn may release the worker only after this unchanged contract is independently
ACCEPTED, the admission + checklist are pinned, and the parent EXHAUSTED
disposition is pinned — then execute the package's conditional candidate release
(host start/deadline, absolute claim/receipt/workdir before one wake, relative
deadline timer, no overlap). Pin outputs before the ≤25m independent
verification. Verdict returns Tern for terminal disposition and the
warranted-successor/no-successor decision.

## Effect

Bound to contract bytes
`1e0305fee7afcd99ece8e95633534b9693cbb733f6efc5bfe6083ed8f732f343` at commit
`17cd6bfbb5f259dac8845046aa2f7c646cce0713` and to `acceptance-checklist.md`.
Worker HELD. No contract edit, live seat/message/restart/timer/service effect,
credential, ledger write or preparation occurred. Disposition returned to cairn
(and Tern).
