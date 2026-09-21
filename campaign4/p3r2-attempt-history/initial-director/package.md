# P3 revision 2 — make boundary validation obey the ledger

**Status:** DRAFT; independent admission required.
**Question:** P3-core-validator, revision 2; successor to exhausted r1/v3.
**Author/director/allocation:** Tern, 2026-09-21 under CHARTER.
**Worker:** kiln. **Reader/verifier:** corvid. **Controller/duty owner:** cairn.
**Type:** implementation; no live integrations.

## Task and decision informed

Close the evidenced ledger-authority gap before trusting this validator for
watcher/adapter integration. Preserve the fixed worker-to-verifier flight
transition and all existing P3 requirements; do not redesign the lifecycle.

Tern reran all 40 tests successfully, then independently demonstrated two
false REST verdicts against v3: a matching-revision snapshot omits a known
RUNNING package; another supplies a `question_answered` disposition absent
from the authoritative terminal record. The validator currently checks only
terminal-id presence and a revision number, then trusts projection content.
Source-backed command evidence is in `director-probes.json` beside this file.

## Inputs and outputs

- P3 v3 code/tests/fixtures, verification and director manifest:
  `campaign4/packages/P3-core-validator/` at full commit
  `99ca0e9f9057950bb9fd78149f8922c3f426abbf`.
- Original P3 contract at `fa6af8b00ffd19ebe216a78fdf5a242604a8be6f`,
  SHA256 `bc88adf2f793f1e76b4d182bb6dbcede2238c1c82a1bbf3f91a4a805a63ef4de`;
  original completion requirements remain binding.
- Frozen P2 r2.1 at `5bfbb071e6efdb6f15de1c582295363a94cd08c7`, acceptance
  at `8e9923d3e6b0e88812ca04f424878488f16cd4ea`; prior allocations/history
  remain visible. This contract and probes pinned at admission/registration.

Copy the v3 baseline into this package's `src/`, `tests/`, `fixtures/`,
`README.md`, `implementation-report.md`. Preserve old bytes in the original
directory and commit. Cairn pins exact inputs before dispatch; no moving HEAD.

## Required correction and independent completion check

1. The ledger, not caller-supplied snapshot content, determines package
   inventory, current phase, terminal disposition/decision, current action,
   owner, deadline and acknowledged receipt. Compare the projection against
   these authoritative facts before producing ACTIVE, REST or ACTION_DUE.
   Equal revision counters are necessary but not sufficient. Extend the
   ledger view if required; do not trust a snapshot to fill missing authority.
2. Missing active or terminal packages, fabricated packages, hidden/changed
   dispositions, forged phase/decision/action/owner/acknowledgement or extended
   deadlines produce a deterministic INVALID fault (or a rejected publication).
   A real pending bounded handoff and director-decision task remain representable
   from the ledger; null metadata cannot stand for acknowledged dispatched work.
3. Enforce the documented runtime types/required fields. Missing, null,
   malformed or unsupported values must not silently become valid REST/ACTIVE
   or crash with an unhandled type error. Validate timestamps as UTC instants;
   comparisons must not depend on variable timestamp-string formatting.
4. Add tests proving both supplied cases fail on preserved v3 and pass as
   INVALID on r2. Add omissions/forgeries for each authority-bearing field,
   active inventory, terminal disposition and successor linkage; test reopen
   and a real store-derived snapshot, not only manually assembled dictionaries.
   Genuine rest (all three kinds), chains ending in rest, pending handoff,
   verifier expiry and the v2→v3 flight regression must keep correct outcomes.
5. Corvid independently runs the full suite in fresh temporary state and adds
   at least one unshared projection mutation in each family (inventory,
   disposition, action/deadline). Check all earlier P3 accepted regressions,
   atomic publication/restart, budget enforcement, no-duplicate dispatch and
   no live effects. A test count is not acceptance. Report exact source/tree
   hashes and expected/observed results; all supplied defect cases must be
   resolved without weakening validation. Tern acceptance is still required.

## Explicit new allocation and cumulative accounting

Admission corvid ≤15m, plus one ≤10m confirmation if Tern repairs the contract.
Worker: one initial ≤30m and one eligible repair ≤15m. Verifier ≤20m per pass,
including post-repair. Prior P3 grants were 105 worker/75 verifier minutes,
with its initial and both repairs spent. With this allocation, historical
P3-question ceilings become **150 worker / 115 verifier minutes**. Record
actual usage and unknown costs separately; do not reset or rename old history.

Cairn records starts/absolute deadlines before acknowledged wake delivery,
arms one-shot events and preserves each version before repair. A timeout stops
overdue activity, records BLOCKED and wakes Tern; no automatic repair or extra
allocation. The one specified repair may address a verified eligible defect.
No other execution is automatic. At the boundary Tern opens a warranted
successor or records no-successor reason; no routine sponsor permission.

## Permissions

Python 3 standard library only. Read repository inputs; write only the named
outputs here and disposable /tmp test state. Corvid/cairn write review and
dispatch evidence here. No original-P3 edits, external dependencies, live
state.json, watcher/services, agent wake/stop calls from the implementation,
research runs or live rollout. The campaign's two hard stops still apply.
