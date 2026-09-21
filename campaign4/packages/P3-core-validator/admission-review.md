# P3-core-validator — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P3-core-validator/package.md`,
  sha256 `bc88adf2f793f1e76b4d182bb6dbcede2238c1c82a1bbf3f91a4a805a63ef4de`,
  commit `fa6af8b00ffd19ebe216a78fdf5a242604a8be6f` (both re-derived; working
  tree matches)
- **Dispatch:** `admission-dispatch.md` (`9c2a8324…`); receipt
  `admission-receipt.json`
- **Pass bound:** one 15-minute admission pass; absolute deadline
  2026-09-21T17:38:42+00:00

## Disposition

**ACCEPTED**, bound to the exact bytes above. The contract measures the
intended question, its inputs resolve against the frozen P2 specification, the
required behavior and adversarial tests are adequate, scope is honestly
bounded, and the allocation is explicit. This is admission of an implementation
to be built under a separate execution pass — not a verification of code that
does not yet exist.

## Dependency and pinned inputs resolve

- P2 r2.1 frozen spec at commit
  `5bfbb071e6efdb6f15de1c582295363a94cd08c7`: independently recomputed hashes
  for all six artifacts and `verification.md`; every value matches the
  verification record (`contract 87435405…`, `transitions 3afedd35…`,
  `ownership cd198c0b…`, `walkthrough 12348310…`, `changes c081291c…`,
  `boundary-schema ec6daf09…`, `verification 93263e9a…`). The pinned commit
  contains each named input; no moving-HEAD dependency.
- Freeze record present and attributable: `P2-r2-boundary-amendment/acceptance.json`
  records `state COMPLETE`, `decided_by tern`, `decision_ref
  P2-r21-freeze-20260921`, disposition `successor_opened → P3-core-validator`,
  and points at the P3 admission receipt. The P3 dependency ("freeze decision
  recorded before execution") is satisfiable; cairn must pin the freeze record
  by hash before dispatch.
- CHARTER governs; P1's shared-host trust qualification is carried as binding.

## Required core behavior (P2 spec → P3 mapping)

Items 1–7 cover the accepted semantics without redesign: explicit
events/states/roles/phase-attempt identity/question-level allocations/absolute
deadlines/artifact hashes with fail-closed rejection and start-before-dispatch;
the transition semantics including repair exhaustion, valid negatives,
phase-preserving blocked verification, expired allocations, amendment/history,
and the row 7/9a/13/14/15 rule that terminal closure requires an attributed
director disposition (with INVALID a fault, not a terminal or a dispatch
permission); idempotent action IDs with replay-safe fake dispatch and crash
reconciliation distinguishing acknowledged from intended delivery; one durable
authoritative store with terminal state + disposition in one transaction plus
an atomically published derived snapshot; validator enforcement of the
versioned shape, four kinds, required fields/types/ownership/receipts and
ledger completeness (matching the authoritative revision/inventory, not a
last-seen counter), with malformed/absent/dangling/cyclic/overdue states unable
to produce REST; historical successor-chain resolution to acknowledged work or
a valid rest leaf, with a due blocker yielding exactly one bounded
owner-reconciliation action per trigger id; and a fixture-driven CLI emitting
structured verdict/action data without calling wake/stop/Signal or
manufacturing human judgment. This tracks the pinned `transitions.md` and
`boundary-schema.md` validation rules.

## Adversarial tests

Adequate and requirement-driven, not count-driven. The contract names, at
minimum: missing disposition despite fresh activity; claimed successor without
acknowledged work; unrelated busy package; each rest kind; empty/stale/malformed
projection against a known ledger; two completed successors ending in rest;
cycles; pending director decision and its expiry; blocked trigger becoming due;
the actual P2 repair-exhaustion acceptance case; blocked verification resuming
the same attempt without dispatch; expired verification without a fresh grant;
valid negative completion; exhausted repair stopping; duplicate
completion/event delivery; duplicate launch requests; crash before/after
dispatch acknowledgement; interrupted snapshot publication; changed
artifacts/registration; unauthorized reviewer; and stale deadline events after
completion — with a fake clock. Corvid must independently derive expected
outcomes, run in fresh temporary state, add adversarial REST-vs-INVALID and
no-duplicate-dispatch cases, reproduce the actual P2 director omission as an
invalid boundary on a fixture, and confirm legitimate rest returns REST without
proposing an alarm.

## Honest scope and budgets

- **Scope:** Python 3 standard library only, no network; a replaceable
  prototype core explicitly not a live-adapter language commitment; no model
  calls in the transition engine; no live agent dispatch, stop, Signal, timer
  modification, `state.json`, watcher/service changes, upgrades, research runs,
  or other-package execution. Outputs are bounded to `src/`, `tests/`,
  `fixtures/`, `README.md`, `implementation-report.md`; the report must state
  hashes, commands, results, limitations and operational deviations.
- **Budgets:** admission 15 min + one 10-min confirmation; worker one 60-min
  initial attempt + one eligible 30-min repair; verifier 30 min per pass
  including post-repair. New question `P3-core-validator`; P2's spent history
  stays separately visible and is never relabelled as unused P3 budget. Timeout
  stops overdue work, records BLOCKED and wakes Tern with no automatic repair;
  controller-recovery verification keeps its ≤10-min ceiling inside remaining
  allocations. Consistent with the charter and director-decisions.

## Roles, independence, permissions

Author/director/allocation Tern; reader/verifier corvid; worker kiln;
controller/duty owner cairn. Worker ≠ verifier; author ≠ validity reviewer;
corvid did not author or materially repair this contract, and a rejection is
one bounded disposition. Tern acceptance is required before live integration.
Permissions are bounded and consistent with the admitted P2 approvals.

## Non-blocking observations

- `acceptance.json` is an untracked working-tree record; the dispatch requires
  cairn to pin it (full commit/hash) before dispatch — accounted for, but it
  must actually be pinned or committed, since it is the dependency the P3
  release rests on.
- `acceptance.json`'s limitation "Archive recheck budget deviation recorded
  separately; not retroactively authorized" has no separate artifact on disk;
  the deviation is disclosed only in that limitations array. Worth Tern/cairn
  making the separate record explicit before freeze is treated as final, but it
  does not change the P2 spec bytes P3 builds against.
- The pinned-input list names six docs and omits `changes.md`; the commit pins
  the whole directory, so no input is unresolved.

## Effect

Bound to contract bytes
`bc88adf2f793f1e76b4d182bb6dbcede2238c1c82a1bbf3f91a4a805a63ef4de` at commit
`fa6af8b00ffd19ebe216a78fdf5a242604a8be6f`. Cairn may register and dispatch
this exact contract under the dispatch's conditional authorization once the P2
r2.1 freeze record is pinned and admission is recorded; changed bytes require
independent confirmation. No code or live state changes before both hold.
