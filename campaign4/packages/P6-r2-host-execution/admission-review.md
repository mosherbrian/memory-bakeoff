# P6-r2-host-execution — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P6-r2-host-execution/package.md`,
  sha256 `97b6dff80cbbb4fa2942d90790042f098aa2540e44d794d79d7552d068c5ada0`,
  commit `582ae00bfba89337f127b5645ea976e1a48f6693` (re-derived; working tree
  matches)
- **Receipt:** `admission-receipt.json` (`7fae954c…`), start
  2026-09-22T00:09:40Z, deadline 2026-09-22T00:24:40Z

## Disposition

**ACCEPTED**, bound to the exact bytes above. The contract addresses the real,
recorded outstanding failures of the exhausted P6 candidate, its required
correction and evidence are complete and testable, pinned inputs resolve,
allocation arithmetic is correct, and Stage A is feasible under injected
effects with no live execution. This is admission only; no live effect or worker
execution occurs here.

## Outstanding failures accurately stated

The contract's failure list (lines 23–36) matches the recorded evidence:
`HostWakeTransport.send` passes invalid `timeout_s=None` to `subprocess.run`
(verified: not a valid parameter); queued wake exit3 is misclassified as failed
and the transport lacks `state()` that `HostAdapter.reconcile_send` calls; no
explicit campaign4 profile binding; `HostTimerService.create_host` returns argv
only with a `true` callback; fixture commands carry `<candidate>/<session>/
<execution>` placeholders, print timer argv and have prose cleanup; and the
observer tests fabricate `session_id`/`execution_id`/`outcome` rows rather than
establishing the real ACP producer schema. All are actual current-contract
failures, not new scope.

## Pinned inputs resolve

- Parent `campaign4/packages/P6-live-recovery` at
  `22c130892c0e433cd46b2975c8b1903cb0aa3243` — resolves; rejected `host_adapter`
  `6525eb1b…` and repair verdict `49967a93…` match the cited values.
- Accepted P5-r2 source `80092f9…` and acceptance `e69e2f4…` — resolve.
- Core `d27d5be…`; P2 spec `5bfbb071…`; rulings retirement `b2384d7…`,
  recovery `4be99bf…`, identity `84f094e…`, deployment `f858729…`, clock
  `650830c…` — all resolve. Short commits to be expanded in the receipt; no
  moving HEAD.

## Contract validity

- **Required correction** (lines 38–79) is complete and testable:
  1. One runnable entrypoint composing trusted ingress, durable intents,
     transport, actual source capture, timers and lifecycle reconciliation;
     live effects only under an explicit bound plan/allowlist; injected
     collaborators execute the **same production branches** in Stage A; no fake
     defaults in live mode; no manual director reconstruction as recovery.
  2. Bounded production subprocess/transport tests validate real API kwargs and
     the campaign4 environment, with **exit0 started / exit3 queued / other
     failure / timeout / malformed receipts** (independently confirmed against
     the inventoried `wake` script: `raise SystemExit(0 if status=="started"
     else 3 if "queued" in status else 1)`); stable persisted
     action/execution/message identity supports `state`/reconciliation across
     fresh instances; queued is delivery ack, never completion or redispatch
     permission.
  3. Actual timer create/cancel/reconcile through a bounded injected runner with
     unique fixture units, remaining authorized duration, an executable
     candidate callback and durable current-action checks; printing argv or a
     `true` callback fails; cancelled/stale/early/repeated callbacks and restart
     do not repeat effects; unit-name identity matches cancel/query.
  4. Establish the real ACP source schema from read-only captured records
     (sanitized content/credentials, field structure and provenance retained);
     bounded incremental observation with persisted cursor, explicit
     source-session→execution binding and artifact verification; tests for
     actual-format completion, failed turn, partial record,
     truncation/rotation/restart, unavailable source, stale execution and lost
     notification; completion must drive the next bounded action through code;
     escalation needs actual acknowledgement evidence, not an owner string.
  5. `fixture-plan.json` with executable setup/run/assertions/cleanup invoking the
     bound candidate, no unresolved angle-bracket placeholders (runtime IDs from
     an exact setup command's bound manifest, never guessed), isolated campaign4
     `p6-fixture` seats only, worker→verifier→director receipts,
     suppressed-notification recovery, unavailable receiver, timers, restart,
     quiet rest and rollback, all latency samples per the parent gates
     (30 s/180 s/60 s) with failures and false positives; exact host
     paths/units/callers/allowlists; no four-seat stop/repurposing, global
     wrappers, real Signal/all-seat pause, host reboot or clock change; Stage A
     must not execute it.
  6. Retain 107+59 regression semantics and D2 atomicity/D3 trusted capture/D4
     durable handled checks; corvid independently tests enabled host paths with
     injected runners of real signatures and captured host schemas, plus a
     complete harness run under injected effects, reviewing actual component
     connection rather than method existence or command text; pin source and
     plan hashes; report any accepted semantic change before implementing.
- **Outputs/stage ownership** (lines 81–90): only this directory's
  `src/tests/fixtures` and the named docs; stdlib; Stage A read-only discovery
  plus injected implementation/tests; Stage B independent candidate verification
  with no live effects; Stage C cairn once after Tern's signed exact-plan
  release with corvid witnessing; no cutover or retirement. Matches the parent
  contract and rulings.
- **Conditional release** (lines 102–109): Stage A only after ACCEPTED unchanged
  contract, recorded admission, and a pinned parent `EXHAUSTED` disposition;
  trusted start/deadline before wake; relative timer; bound completion before
  verifier; preserve initial before the sole repair; missing wake reconciled
  from session/hashes; real expiry BLOCKED+wake Tern; controller recovery ≤5m
  inside the grant; no second automatic repair or live rerun.

## Allocation

Worker initial ≤30m + sole repair ≤15m = **45m**; candidate verifier ≤20m per
pass × 2 = **40m**. Prior P6 60/55 plus 45/40 = cumulative **105 worker / 95
verifier minutes** — arithmetic correct; prior worker 60 and candidate verifier
40 spent, no reset. The existing unspent 15m live witness and 15m cairn fixture
are explicitly reassigned to this revision, not duplicated or increased, and
remain **HELD** for Tern release.

## Non-blocking observations

- The parent's `EXHAUSTED` disposition must be pinned by cairn, together with
  the recorded admission, before Stage A; the directory currently lists neither
  a disposition artifact nor a director admission record besides the receipt.
- Item 4's "real ACP schema" is a discovery risk, but the contract correctly
  bounds it to read-only captured records with sanitization and provenance and
  requires the worker to report infeasibility inside the bound rather than
  substitute a fabricated fixture.

## Effect

Bound to contract bytes
`97b6dff80cbbb4fa2942d90790042f098aa2540e44d794d79d7552d068c5ada0` at commit
`582ae00bfba89337f127b5645ea976e1a48f6693`. Cairn may release Stage A only
under the recorded conditional release once admission is recorded and the pinned
parent terminal disposition is present; Stage C additionally requires corvid
candidate PASS and Tern's signed exact-fixture-plan release. No live effects,
service installation, script retirement or host-clock change.
