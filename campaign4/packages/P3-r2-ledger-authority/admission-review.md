# P3-r2-ledger-authority — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P3-r2-ledger-authority/package.md`,
  sha256 `9212426ba58540036666710ba531c553244dd791d94775720572abbc38a484a0`,
  commit `0b00ea3f79f3ff02822ba69158a59f436bc7129e` (re-derived; working tree
  matches)
- **Probes:** `director-probes.json` (`7f01ad2f…`), same commit
- **Pass bound:** one 15-minute admission pass; absolute deadline
  2026-09-21T19:04:42+00:00

## Disposition

**ACCEPTED**, bound to the exact bytes above. The contract measures the
intended question, its inputs resolve against the immutable v3 baseline, the
supplied defects are real and reproduced, the required correction is complete
without redesign, and the allocation is explicit and arithmetically correct.

## The two supplied defects are real (independently reproduced)

I ran both `director-probes.json` cases against the preserved v3 validator
(`src/validator.py` `78076f89…`, byte-identical at commit `99ca0e9…` and on
disk):

- `active-inventory-omitted` — ledger has `work-r1` RUNNING with a flight;
  snapshot is empty at the same revision. Observed **REST**, expected
  **INVALID**.
- `projection-invents-terminal-disposition` — ledger `done-r1` is COMPLETE with
  `disposition: null`; the snapshot fabricates a `question_answered`
  disposition. Observed **REST**, expected **INVALID**.

Both reproduce exactly as the contract states (lines 15–20). The gap is
authority/completeness: v3 checks only terminal-id presence and equality of the
revision counter, then trusts projection content.

## Contract validity and retained P3 authority/completeness

- **Task/decision** (lines 9–20): close the ledger-authority gap before any
  watcher/adapter integration; preserve the fixed worker→verifier flight
  transition and existing lifecycle. No redesign.
- **Inputs** (lines 22–36): v3 baseline pinned at full commit `99ca0e9…`
  (source hashes independently confirmed: `lifecycle.py 815b10c5…`,
  `store.py 5ec562c2…`, `validator.py 78076f89…`); original P3 contract
  `bc88adf2…` with its completion requirements still binding; frozen P2 r2.1
  at `5bfbb071…`/`8e9923d3…`; prior allocations/history visible; contract and
  probes pinned at admission/registration; no moving HEAD.
- **Required correction** (lines 38–67) is complete and testable: the ledger
  determines inventory, phase, terminal disposition/decision, current
  action/owner/deadline/acknowledgement (equal revisions necessary but not
  sufficient); omissions, fabrications, hidden dispositions and forged
  fields yield deterministic INVALID (or rejected publication); real pending
  handoff and director-decision task stay representable from the ledger; null
  metadata cannot stand for acknowledged dispatched work; runtime types and
  required fields enforced; timestamps validated as UTC instants, not string
  formatting. Item 4 requires tests proving both cases fail on preserved v3 and
  become INVALID on r2, plus authority-field omissions/forgeries, reopen and a
  real store-derived snapshot, while retaining genuine rest, chains, handoff,
  verifier expiry and the v2→v3 flight regression. Item 5 requires independent
  full-suite execution plus at least one unshared mutation per family
  (inventory, disposition, action/deadline) and a test count is explicitly not
  acceptance.
- **Independence** holds: author/director Tern, reader/verifier corvid, worker
  kiln, controller cairn; the reader did not author or repair this contract;
  rejection is one bounded correction.
- **Permissions** (lines 85–91): Python 3 stdlib only; writes limited to the
  named outputs here and disposable `/tmp`; no original-P3 edits, external
  dependencies, live `state.json`, watcher/service changes, agent wake/stop
  calls, research runs or live rollout. Bounded and consistent with the charter.

## Allocation

Admission corvid ≤15m + one ≤10m confirmation; worker one initial ≤30m and one
eligible repair ≤15m; verifier ≤20m per pass including post-repair. Prior P3
grants 105 worker / 75 verifier with initial and both repairs spent; this adds
30+15 worker and 20+20 verifier, giving the stated historical ceilings
**150 worker / 115 verifier minutes** — arithmetic correct, prior history
preserved, no reset or rename. Timeout stops overdue activity, records BLOCKED
and wakes Tern; no automatic repair or extension; the one eligible repair is
bounded. Prior-P3 EXHAUSTED disposition is recorded
(`P3-core-validator/acceptance-withheld.json`, successor
`P3-r2-ledger-authority`), satisfying the dispatch's release precondition.

## Non-blocking observations

- `admission-dispatch.md`/`admission-receipt.json` and the P3
  `acceptance-withheld.json` postdate the contract commit and are published
  beside it; cairn must pin them by hash before dispatch as the dispatch itself
  states.
- The contract lists the copied baseline paths but does not enumerate the r2
  output set beyond those plus added tests/docs; the completion check's
  hash-bound implementation report supplies the evidence, so this is not
  ambiguous for execution.

## Effect

Bound to contract bytes
`9212426ba58540036666710ba531c553244dd791d94775720572abbc38a484a0` at commit
`0b00ea3f79f3ff02822ba69158a59f436bc7129e`. Cairn may dispatch this exact
contract under the dispatch's conditional authorization once this ACCEPTED
admission is recorded and the prior-P3 EXHAUSTED disposition is pinned; changed
bytes require independent confirmation. No live integration.
