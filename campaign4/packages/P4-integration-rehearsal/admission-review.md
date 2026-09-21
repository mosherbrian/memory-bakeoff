# P4-integration-rehearsal — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P4-integration-rehearsal/package.md`,
  sha256 `c0f31dd0c61b1598c87b30cfc9a6bfeffcbf5ce326c9f0a1ef5ef39309e04463`,
  commit `53c901bb82e8f0ba8de9220beb63c62115452130` (re-derived; working tree
  matches)
- **Receipt:** `admission-receipt.json` (`ddccf01f…`), start
  2026-09-21T19:52:45Z, deadline 2026-09-21T20:07:45Z

## Disposition

**ACCEPTED**, bound to the exact bytes above. Scope is a bounded fake-adapter
rehearsal over the accepted P3 core; pinned inputs resolve; the required
behavior and independent completion checks are adequate; the no-live-effects
and no-execute boundaries are explicit; and the allocation arithmetic is
correct. This is admission, not execution verification.

## Pinned inputs resolve

- P3-r3 core at `d27d5be7b4086556260974bca9aef2ec6f8b1db8`: confirmed to contain
  the accepted r3 tree (`src/validator.py dcecfc1d…`), 59 tests, fixtures,
  `verification.md`, `director-preservation-manifest.json` and
  `admission-confirmation.md`; the accepted source is never to be modified.
- Frozen P2 contract/transitions/ownership/boundary-schema at `5bfbb071…` —
  resolves.
- P1 `capability-map.md` at `dd157642…` — resolves; shared-host trust limits
  retained.
- `inputs/campaign4-watch.observed.sh` recomputes to
  `1feaf9945dce002a236cb1287447537f2c5abf90fd33f9ebbcb1a403dcda9601` — matches
  the contract. I read it without executing it and confirmed the described
  properties: a provisional string-map `state.json` schema
  (`in_flight`/`terminal` string values) and a state-fault pause branch that
  bypasses `DRY` (line 74 calls `campaign4-pause` unguarded). The contract's
  instruction to treat it as reference-only and not execute it is warranted.

## Contract validity

- **Task/decision** (lines 6–12): one harmless package through controller
  handoffs and supervision using fake external adapters; decide readiness for a
  separately authorized live fixture and name blocking gaps. Bounded Connect-stage
  rehearsal, not a platform expansion or rollout.
- **Required behavior** (lines 34–72) is complete and testable: an event-driven
  driver composes the accepted store/core/validator with **fake**
  launch/inspect/stop/wake/timer/notification interfaces whose **defaults are
  incapable of live effects**, not merely guarded commands; external responses
  carry recorded action identity and delivery state and worker prose never
  supplies authoritative identity; no polling or model calls. A deterministic
  fixture runs from admitted authorization through worker completion, separately
  attributed verification and a supplied director disposition, with
  start-before-dispatch, hashes-before-completion and duplicate-delivery
  non-duplication; restart reconciles durable intent/ack against fake external
  state and ambiguous delivery holds for owned reconciliation rather than blind
  redispatch. Candidate supervision consumes the authoritative ledger plus the
  versioned snapshot: REST (including historical successor chains ending in
  rest) suppresses generic silence escalation; INVALID cannot be masked by fresh
  activity or unrelated busy seats; ACTION_DUE is owned, durable and deduplicated
  across restart; ACTIVE uses the actual current action deadline so stale worker
  timers cannot expire a verifier; missing/unreadable/stale snapshot or ledger
  failure returns an explicit owned fault. Timeout/lost-timer recovery,
  one-shot deadlines reconstructed on restart, no duplicate stop/wake,
  phase/attempt/allocation-preserving blocked-verifier resume, no automatic
  successor after the last package, and an injected missing disposition to
  reproduce the Tern omission are all required. A compact candidate
  adapter/reader interface and status report must distinguish simulated
  observations from real campaign history, name duty cairn and escalation tern,
  and emit any terminal pause proposal only as fake output with no Brian
  notification.
- **Independent completion check** (lines 65–72): corvid runs the end-to-end
  fixture and fault matrix in fresh temporary state — crash-before-delivery,
  ambiguous delivery, crash-after-ack, repeated completion/deadline/trigger,
  removed timer, stale snapshot, legitimate rest, missing disposition and
  blocked-verifier resume — verifies no live subprocess/network/service effect
  is possible through the tested adapters, all 59 core tests still pass, and
  reports commands, hashes, expected/observed results, limitations and a
  readiness conclusion, without certifying live behavior from simulation.
- **Outputs/permissions** (lines 74–82): `src/`, `tests/`, `fixtures/`,
  `README.md`, `rehearsal-report.md`, `interface.md` here plus `/tmp`; stdlib
  only; fake time and adapters, no long sleeps; core defects reported to Tern
  before changing accepted semantics; no live adapter enablement, `state.json`,
  watcher/service edits, wake/stop/Signal, upgrades, research, migrations or
  modification of previous packages.
- **Independence** holds: author/director Tern, reader/verifier corvid, worker
  kiln, controller/duty cairn; the reader did not author or repair this contract.

## Boundary constraints honored in the contract

- The copied watcher reference is marked **reference only — DO NOT execute**
  (lines 27–32), and the candidate supervision must use the accepted
  ledger-derived schema with the reader change documented. This matches the
  dispatcher's instruction that the watcher's state-fault DRY bypass is out of
  execution scope; the contract does not require running it.
- No live effects: adapters are fake and default-incapable; only fake output may
  propose a pause; no Brian notification.

## Allocation

New integration question P4: worker initial ≤45m + one eligible repair ≤20m =
**65 worker**; verifier ≤20m per pass including post-repair = **40 verifier**;
admission ≤15m + one ≤10m confirmation tracked separately. P3 historical grants
195/155 remain recorded; r3 acceptance cancels the unspent r3 repair (15m) and
post-repair verifier (20m) and never transfers them to P4 or erases history —
arithmetic and history handling correct.

## Non-blocking observations

- Tern's P3-r3 `acceptance.json` is not yet present in the pinned r3 tree; the
  dispatch requires cairn to pin it before execution. That is cairn's release
  step, not a contract defect.
- `admission-receipt.json` records `dispatch_receipt:"intended"`; delivery in
  fact occurred (this pass is running), but cairn should reconcile the receipt
  convention when recording admission.

## Effect

Bound to contract bytes
`c0f31dd0c61b1598c87b30cfc9a6bfeffcbf5ce326c9f0a1ef5ef39309e04463` at commit
`53c901bb82e8f0ba8de9220beb63c62115452130`. Cairn may execute under the
recorded conditional release once admission is recorded and Tern's P3-r3
acceptance is pinned; changed bytes require independent confirmation. No live
integration.
