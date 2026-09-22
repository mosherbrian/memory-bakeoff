# P6-r7-real-host-path — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `package.md`, sha256
  `515deb16a0d038538a639b1c9ffc1e893b86ba3b0d18327e0878f1b94a468318`,
  commit `fd497e7` (re-derived; matches)
- **Dispatch/receipt:** `admission-dispatch.json` (`P6r7-admission-1`),
  recorded `2026-09-22T04:37:09Z`, deadline `2026-09-22T04:52:09Z`
- **Pinned checklist:** `acceptance-checklist.md` (written this pass)
- **Worker:** HELD

## Disposition

**ACCEPTED**, bound to the exact contract bytes above plus the pinned
`acceptance-checklist.md`. The contract is a bounded successor that completes the
same live-recovery question (not new platform features), correctly separates the
prior injected-CLI PASS from live readiness, and defines H1–H4 blocking checks
with explicit effect limits. No worker execution or live effect occurs here.

## Pins resolve

- Parent P6-r6 `1b8a166d1b4b2af19fe9fd42b9af10a85a44c4a3` — resolves.
- `candidate-review-composition-repair.md` `eb6fa897…` (my PASS), entry
  `211f495be11e…`, `stagec-plan.json` `a866091f…`, and
  `director-live-branch-findings.json` (`WITHHOLD_STAGE_C`, `pure_probe` =
  `KeyError: 'wake_shim'`) — all present, hashes re-derived and matching.
- Pinned reusable candidate P6-r5 `dad98827…` (189+59) — resolves.
- Rulings `recovery4be99bf`, `identity84f094e`, `turn883107e`,
  `retirementb2384d7`, `clock650830c`, `session92467e4`, `shadowafa126f`,
  `portability7abab5f` — all resolve as commits.
- Parent resources are **stopped**: campaign4 list shows
  `p6-fixture-worker` (0e734b30), `p6-fixture-worker-p3`, `p6-fixture-verifier-p3`
  all `stopped`; Tern stopped them within `04:39Z`. They are historical evidence
  only — the contract forbids reviving expired incarnations, which the checklist
  enforces (H2 negative).

## H1 reproduced read-only (no side effects)

Calling parent `_candidate_plan(config, plan, _live_dirs(plan))` with the P6-r6
`stagec-plan.json` raises `KeyError: 'wake_shim'`. `live_run_dirs` holds only
`art/bin/claims/db/latency/msgs/onsets/root/stream/trace/witness` — none of the
three required host command paths (`wake_shim`/`systemd_shim`/`systemctl_shim`).
Confirmed the parent's no-overlay live path is genuinely incomplete and that
`run_case` always starts `_drive_producers` (synthetic producer), matching the
contract's H1 statement. No file or seat was touched.

## Contract validity

- **Scope discipline:** operational code/plan/tests/readme/manifest only; import
  or immutably extract the pinned parent core with a hash check; no
  dependencies, no speculative portability, no broader rewrite. Candidate tooling
  is read-only discovery + private tmp + injected effects; no real seats,
  messages, restarts, timers, Signal, wrapper changes, research, shadow or
  retirement under this allocation. No fresh preparation grant.
- **H1–H4** are proper blocking operational checks with exact negative cases
  (missing/expired host, no-overlay positive trace, wrong-execution witness,
  omitted ack) that I pinned in `acceptance-checklist.md` before worker dispatch.
- **Deliverable honesty:** a further simulated PASS alone is explicitly not a
  successful deliverable; live/shadow results remain required for harness
  acceptance, and a candidate PASS returns to Tern with no automatic
  preparation/live run/successor.

## Allocation

Worker initial ≤40m; one independent candidate pass ≤25m; ceilings 465/350 →
**505/375** — arithmetic correct; parent author/repair/composition allocations
spent and retained as history. Live witness 10m and cairn fixture 15m remain
held, not re-added; preparation 30m spent, no renewal. Admission/checklist
≤15m. Expiry reconciles then BLOCKED to Tern; running tests do not reset clocks.

## Release conditions

Release kiln only after independent ACCEPTED unchanged contract + checklist
pinned, a director admission record, and a parent EXHAUSTED pin; cairn does a
no-overlap check, absolute paths, host start/deadline before one wake with a
relative timer, binds completion hashes before corvid, and expiry
reconciles/BLOCKED. Candidate verdict returns Tern; at that boundary the
research-first/minimal-useful-harness value is explicitly reassessed before
further machinery allocation.

## Non-blocking observations

- The contract says "mandatory inherited cases cannot silently shrink from five
  to three"; the parent `CASES` tuple currently enumerates three
  (`positive-handoff`, `failed-verification`, `restart-quiet`). The checklist
  fixes five as the acceptance bar and flags the gap; H4.3 is where this must be
  closed, not silently accepted.
- The parent `derive_config` tautological socket-dir check and unused `allowed`
  set in `timecheck` remain known; they are out of scope for a broader rewrite
  but must not mask H3's exact action+execution+case join.

## Effect

Bound to contract bytes
`515deb16a0d038538a639b1c9ffc1e893b86ba3b0d18327e0878f1b94a468318` at commit
`fd497e7` and to `acceptance-checklist.md`. Worker HELD. No live seat/message/
restart/timer/Signal, wrapper edit, research run, shadow or retirement occurred;
p3 fixtures remain stopped as historical evidence. Disposition returned to Tern.
