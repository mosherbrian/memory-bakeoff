# P3-r3-authoritative-claims — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P3-r3-authoritative-claims/package.md`,
  sha256 `d6bb02602000cc6e993226c80585684a373a2dd58290882a5a128352ad8d7c88`,
  commit `7afd07525d27aebfae71ad4434d59d0bdc3b9f68` (re-derived; working tree
  matches)
- **Receipt:** `admission-receipt.json` (`fdf8b7e5…`), start
  2026-09-21T19:32:05Z, deadline 2026-09-21T19:47:05Z

## Disposition

**ACCEPTED**, bound to the exact bytes above. The contract closes a real,
independently reproduced authority gap without redesign; its required
correction, mutation matrix and completion checks are adequate; pinned inputs
resolve; and the allocation arithmetic is correct. This is admission, not
execution verification or acceptance.

## The two claimed failures are real (reproduced on pinned r2)

Against the r2 validator at the pinned commit (`src/validator.py 2e8f9e11…`,
matching `624dedcb…`):

- `invented_decision_reference` — snapshot entry carries
  `decision_ref:"invented-decision"` while the ledger disposition has no
  decision reference. Observed **REST**, expected **INVALID**.
- `forged_handoff_ack_satisfies_successor` — ledger `work` has a bounded handoff
  and **no** receipt; the snapshot claims `dispatch_receipt:"acknowledged"` and
  this satisfies `old`'s `successor_opened`. Observed **ACTIVE**, expected
  **INVALID** (or a bounded pending handoff that does not discharge the
  successor).

Both match the contract's evidence statement (lines 11–14).

## Contract validity

- **Task/decision** (lines 9–25): complete the existing ledger-authority
  requirement, no redesign; two supplied failures are actual contract failures.
  Inputs pinned to r2 at commit
  `624dedcb801f9bcd87cd1f4f7c28ffd5175c803c` — verified to contain the repaired
  r2 tree, `director-v2-manifest.json`, `verification.md` (`a9bf3919…`) and
  `director-postrepair-check.json`; original contract `fa6af8b0…`/`bc88adf2…`,
  r2 `package.md` `0b00ea3f…`, and frozen P2 `5bfbb071…` all remain binding.
  Baseline is copied; prior package and archives stay immutable.
- **Required correction** (lines 29–53) is complete: missing authoritative
  decision data cannot be supplied by the projection (no relaxation of
  comparisons; fixtures repaired to represent authoritative decisions with
  explicit invalid cases retained); **every** flight variant is checked
  (dispatched worker/verifier, bounded handoff, pending director decision,
  no-current-action); null/absent ledger receipt is not acknowledged dispatch
  and a forged handoff receipt cannot discharge `successor_opened`; a
  ledger-backed pending handoff stays `ACTIVE` without claiming dispatched work;
  correct DECISION entries remain representable and forged
  receipt/action/owner/deadline/phase or unsupported populated metadata faults.
  Both probes must reproduce false-valid on pinned r2 and INVALID on r3; a
  table-driven mutation matrix must cover variants/fields **including missing
  authoritative facts**, on real store-derived/reopened snapshots as well as
  focused dictionaries; all 54 prior regressions and five repaired probes are
  retained (true REST for all three kinds, genuine `ACTION_DUE` once, historical
  successor chains, verifier flight/expiry, bounded handoff, atomic/restart,
  allocations, no-duplicate execution, runtime types, UTC comparisons).
- **Independent completion check** (lines 49–53): corvid runs the suite and adds
  unshared missing-fact and receipt-forgery cases across handoff and DECISION
  plus a genuine store-backed terminal decision, compares r2/r3 probes, reports
  exact hashes and actual outcomes, and treats a test count as insufficient.
- **Independence** holds: author/director Tern, reader/verifier corvid, worker
  kiln, controller/duty cairn; the reader did not author or repair this contract.
- **Permissions/outputs** (lines 55–61): only `src/`, `tests/`, `fixtures/`,
  `README.md`, `implementation-report.md` here plus `/tmp`; stdlib only; no
  old-package edits, `state.json`, watcher/service changes, live wake/stop/Signal
  from code, research or rollout.

## Allocation

P3 prior ceilings 150 worker / 115 verifier; this adds worker 30+15 = 45 and
verifier 20+20 = 40, giving the stated cumulative **195 worker / 155 verifier
minutes** — arithmetic correct, prior spent history preserved, no reset by
revision name. Admission ≤15m (+ one ≤10m confirmation) is tracked separately.
Timeout stops overdue work, records BLOCKED and wakes Tern; controller-recovery
verification stays ≤10m inside remaining allocations; no further execution
after the spent repair without a prior Tern allocation.

## Non-blocking observations

- The dispatch requires the P3-r2 `EXHAUSTED`/`successor_opened` terminal
  disposition to be pinned before execution; cairn must record and pin it, as
  no discrete r2 disposition artifact is named in the contract's input list.
- `admission-receipt.json` records `dispatch_receipt:"intended"`, not
  "acknowledged"; delivery in fact occurred (this pass is running), but the
  receipt itself does not evidence acknowledgement — cairn should reconcile the
  receipt convention when recording admission.

## Effect

Bound to contract bytes
`d6bb02602000cc6e993226c80585684a373a2dd58290882a5a128352ad8d7c88` at commit
`7afd07525d27aebfae71ad4434d59d0bdc3b9f68`. Cairn may dispatch this exact
contract under the recorded conditional release once admission is recorded and
the pinned r2 terminal disposition is present; changed bytes require independent
confirmation. No live integration.
