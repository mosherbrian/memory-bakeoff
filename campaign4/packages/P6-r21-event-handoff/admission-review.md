# P6-r2.1-event-handoff — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P6-r21-event-handoff/package.md`,
  sha256 `71b455c299175e8863e799d65b59662b8733cfadcb463dc0016370ba066f91e8`,
  commit `e9993e7f3f91b5738a2c500b3a91d8a0869cc7b4` (re-derived; working tree
  matches)
- **Ruling:** `campaign4/TURN-END-HANDOFF-RULING-20260922.md` @
  `883107edd98b4feb38204a660f93e8df49796500`
- **Receipt:** `admission-receipt.json` (`076723fd…`), start
  2026-09-22T00:19:36Z, deadline 2026-09-22T00:34:36Z
- **No overlap:** I am not currently verifying the r2 pass, so this admission
  proceeds; its clock is not reset.

## Disposition

**ACCEPTED**, bound to the exact bytes above. The amendment replaces only the
normal trigger and allocations, retains the admitted r2 requirements, and
implements the new ruling's event-driven turn-end normal path, route-free
completion claim, transactional intent plus durable outbox, and deadline
backstops. Inputs resolve and allocation arithmetic is correct. No live effect
occurs here.

## Ruling alignment

The contract faithfully encodes `TURN-END-HANDOFF-RULING-20260922.md`:

- **Normal path is event-driven** (contract §1, §3): consume runtime turn-end
  notifications/stream append events as the primary handoff trigger; inspect the
  actual `acp-worker`/transition-notify producer read-only and capture sanitized
  field structure + source hash; the sidecar is best-effort, truncates per turn
  and emits end for failure/cancel, so counts/current contents are not a durable
  journal; persist bound turn receipts with runtime item/session/execution
  mapping; correlate by declared identity, not filenames/suffixes; reconcile
  loss/truncation/coalescing/duplicate-end/restart against durable evidence;
  polling mtimes is not the normal path; deadlines remain for never-ended turns,
  failed capture, unacknowledged handoffs and bounded recovery.
- **Route-free atomic completion claim** (contract §2): the worker publishes an
  execution-scoped claim at the launch-assigned
  `<package>/completion-claims/<opaque execution id>.json` with
  package/attempt/action/execution/contract-step/outcome/artifact paths+hashes;
  no routing fields; launcher/contract owns routing and actor attribution;
  unknown destination overrides rejected; the worker cannot nominate a verifier,
  grant acceptance/duration/authority/next task; reported occurrence is
  untrusted while host ingress records receipt time and launcher attribution.
- **Transactional commit + durable outbox** (contract §3): the connected
  entrypoint validates turn receipt + claim + artifacts + budget and commits the
  permitted transition **and** next dispatch intent transactionally; the outbox
  acknowledges after delivery and never clears before send; restart at every
  intent/send/ack boundary reconciles ambiguous delivery without blind replay or
  overwritten evidence; valid no-successor terminal rest is allowed.
- **Owned bounded failure** (contract §4): missing/malformed claim or failed turn
  immediately creates owned bounded recovery/escalation under the existing
  latency gates; runtime end never certifies artifacts or success; never-ended
  turn, failed observation, unavailable receiver and dead controller retain
  deadlines and an independent backstop; a new package still needs Tern's
  authorization as a bounded director task.
- **Openwork stays live** (ruling): the contract retires nothing and keeps
  independent controller-health supervision; cutover is a separate authorized
  decision.

## Pinned inputs and base capture

- Parent `P6-r2-host-execution/package.md` at `582ae00…` and its admitted
  requirements are retained except the normal trigger and allocations; parent
  original `P6-live-recovery` at `22c1308…`; accepted P5-r2 `80092f9…` /
  acceptance `e69e2f4…`; core `d27d5be…`; P2 `5bfbb071…`; rulings recovery
  `4be99bf…`, identity `84f094e…`, retirement `b2384d7…`, clock `650830c…`,
  deployment `f858729…` — all resolve. Abbreviated commits to be expanded in the
  receipt; no moving HEAD.
- **Required base ordering** (lines 16–21): cairn must capture and commit r2's
  current attempt/pass outputs, verdicts and full per-file manifest **before**
  amendment execution; that captured tree (including known defects) is the
  implementation base; independent admission may precede capture but worker
  release may not. This correctly prevents overlap with the running r2 attempt
  and supersedes it explicitly rather than silently appending requirements.

## Completion check

Items 1–5 (lines 23–58) are complete and testable, including the added anomalies
(pre-end claim, end-before-claim, missing claim, worker-forged destination,
failed/cancelled end, duplicate/stale end, truncated stream, lost event,
restart, legitimate rest, disconnected observer) and the requirement that a
production-path injected end actually cause the next authorized dispatch or an
acknowledged bounded escalation rather than returning a descriptive dict.
Corvid independently tests with the captured runtime schema and checks full
path/transaction evidence, labelling injected versus live and forbidding pretend
timestamps. All r2 duties (real kwargs/profile, exit0/3, ambiguous/failure,
timer callback/cancel, exact fixture plan) and 107+59, D2/D3/D4 are retained.

## Allocation

Worker initial ≤25m + sole repair ≤15m = **40m**; candidate verifier ≤20m × 2 =
**40m**. Prior P6 105/95 plus 40/40 = cumulative **145 worker / 135 verifier
minutes** — arithmetic correct. The original unspent 15m live witness and 15m
cairn fixture remain single grants reassigned here and still **HELD**. r2's
unused worker/verify portions are cancelled after its captured attempt/pass ends
and recorded separately; spent effort is never reset or transferred.

## Release conditions

Conditional worker release only after unchanged amendment ACCEPTED, admission
recorded, old r2 execution ended + archived + supersession pinned, and the exact
base commit recorded; then cairn records trusted start/deadline before one
acknowledged dispatch with a relative timer. Version preserved before the sole
repair; bound completion before verifier; missing wakes reconciled from
session/hash evidence; real expiry stops overdue work and wakes Tern; recovery
check ≤5m inside the active grant; no second automatic repair. Candidate PASS
returns to Tern for the signed exact-plan live release.

## Non-blocking observations

- The old r2 capture archive and pinned `EXHAUSTED`/supersession disposition are
  not yet present in the amendment directory; cairn must produce them before
  worker release, as lines 16–21 and 80–82 require.
- The contract's runtime-schema discovery is read-only and sanitized; if the
  actual producer cannot be correlated to declared execution/session identity,
  the worker must report that inside the bound rather than infer identity from
  filenames.

## Effect

Bound to contract bytes
`71b455c299175e8863e799d65b59662b8733cfadcb463dc0016370ba066f91e8` at commit
`e9993e7f3f91b5738a2c500b3a91d8a0869cc7b4`. Cairn may release the amendment
only after the recorded admission and the captured/pinned r2 base and
supersession exist; changed bytes require independent confirmation. No live
effects, service installation, seat action, global wrapper change, host clock
change, historical edit or script retirement.
