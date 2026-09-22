# P6-r5-launch-binding — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P6-r5-launch-binding/package.md`,
  sha256 `40fce2e2e81f826366412adff82f9b58e68f4eb47c3d3aafc6bd5d15b311c399`,
  commit `e40ce397797a0d1e5cf5e74ded66a307a1f50108` (re-derived; working tree
  matches)
- **Dispatch/receipt:** `admission-dispatch.json` (`e5485a12…`), recorded
  `2026-09-22T02:28:40Z`, deadline `2026-09-22T02:43:40Z`
- **Pinned checklist:** `launch-acceptance-checklist.md` (written this pass)

## Disposition

**ACCEPTED**, bound to the exact bytes above plus the pinned
`launch-acceptance-checklist.md`. The contract correctly targets the parent's
live-readiness defects as blocking (L1–L4), keeps all inherited pins and
regressions, and is feasible under injected boundaries with read-only host
discovery. Worker release remains HELD; no worker execution occurs here.

## Parent defect reproduced (L1)

Running the parent `director-readiness-probe.py` against `P6-r4` @ `efc3f827`
reproduces the reported failure exactly:

```json
{"decision":"terminal-rest","expected":1,"rc":0,"verifier_send_count":2,
 "verifier_sends":[
   "CALL wake p6-fixture-verifier {\"kind\": \"verifier-dispatch\", \"action\": \"p6h-v1\"}",
   "CALL wake p6-fixture-verifier TASK-V run p6h-v1"]}
```

Two verifier wakes for one authorized verifier action (the outbox send plus the
harness send), and the CLI still returns `terminal-rest` rc0. This is the L1
duplicate-sender defect, and it is a live-readiness gap, not a rewrite of the
prior N/T/O candidate PASS (which the contract preserves for its tested scope).

L2–L4 are confirmed against the parent `director-readiness-findings.json`
(`WITHHOLD_STAGE_C`) and the read-only `host-inventory.json`: the plan reads a
nonexistent launcher-evidence file and fabricates derived stream keys (L2); task
texts omit execution/step/claim schema/artifact/check and tests fabricate claims
from undispatched manifest variables (L3); and the inventoried `acp-worker`
`emit(end)` carries **no `at` timestamp**, so latency source time cannot be
measured from actual-format events (L4; `acp-history` outcome rows carry `at`,
but the stream end does not).

## Pinned inputs resolve

- Parent `P6-r4-notify-timer-drain` at
  `efc3f827c91f45d1faf37eaf9c401528ffd4fa2a` — resolves; its `package.md`
  recomputes to `c5725d29…`, and `terminal-disposition.json` records
  `EXHAUSTED`, successor `P6-r5-launch-binding`, Stage C HELD.
- Parent package `214e73c…`, three-case checklist, repair decision,
  `candidate-review-repair.md` (`3ca2ac57…`) and readiness findings/probe are
  named.
- Rulings recovery `4be99bf…`, identity `84f094e…`, turn `883107e…`, retirement
  `b2384d7…`, session `92467e4…`; P5-r2 `80092f9…`; P3-r3 `d27d5be…`; P2
  `5bfbb071…` — all resolve. Short pins to be expanded in the receipt.

## Contract validity

The question is bounded and testable: can the exact live entrypoint launch ONE
fully specified worker step, consume its actual runtime end, launch ONE
independent verifier step, and measure/archive the result without test helpers
filling protocol gaps? The four completion checks are complete and blocking:
one durable sender with the full task/pinned-brief pointer and identity-stable
reopen (L1); executable allowlisted launcher binding from read-only discovery,
no key inference/fabrication/truncation, missing binding fails before wake (L2);
dispatch-sufficient task/claim schema with a fresh producer seeing only the
outgoing message and named files, positive **and** negative verdicts, no
worker-chosen routing or director authority (L3); and honest timing on
actual-format timestamp-free events with host-stamped observation, provenance,
uncertainty, and explicit statement of which intervals are establishable (L4).
The exact plan must cover preparation, launch/observer attachment, bounded
waits, positive fixture plus retained faults, owned recovery, timer
query/cancel, rollback and archival before deletion, executable from declared
preconditions with no invented evidence or placeholders; both plan and produced
binding manifest are signed before Stage C sends. Verification executes the
exact shipped CLI with injected boundaries and private `/tmp` notification only,
reproducing L1 on the parent and checking the single-send trace, failed
verification, stale streams, ambiguous delivery and restart, while retaining
N/T/O and 172+59.

## Allocation

Worker initial ≤30m + sole repair ≤20m = **50m**; candidate verifier ≤20m
initial + ≤20m post-repair = **40m**. Prior cumulative 245/205 plus 50/40 =
**295 worker / 245 verifier** — arithmetic correct; parent r4 worker 30+10 and
candidate 15+15 are spent, no reset. The single live witness 15 and cairn fixture
15 remain unspent, reassigned and HELD, not added again. Admission ≤15m + one
≤10m confirmation only if Tern amends. The prospective repair-20 is a judgment
allocation, not a p95 estimate; running tests never silently extends a deadline.

## Release conditions

Release only after independent ACCEPTED unchanged contract + checklist pinned,
director admission recorded and the parent `EXHAUSTED` disposition pinned; cairn
verifies no overlap, host-stamps action/attempt/execution receipt and absolute
deadline before wake, arms a relative timer, preserves outputs before repair,
and binds full output hashes before independent review. No second repair,
automatic extension or next package; candidate verdict returns to Tern.

## Non-blocking observations

- The parent's `terminal-disposition.json` (`EXHAUSTED`, successor
  `P6-r5-launch-binding`) is present; cairn must pin it together with the
  director admission record before worker release.
- The private `/tmp` notification test and read-only discovery are the only
  host-touching allowed operations in candidate work; preparation requiring host
  mutations needs explicit Tern release.

## Effect

Bound to contract bytes
`40fce2e2e81f826366412adff82f9b58e68f4eb47c3d3aafc6bd5d15b311c399` at commit
`e40ce397797a0d1e5cf5e74ded66a307a1f50108` and to
`launch-acceptance-checklist.md`. Worker release HELD. No live seat/service,
Signal, main-seat reset, wrapper edit, clock change or retirement occurred.
