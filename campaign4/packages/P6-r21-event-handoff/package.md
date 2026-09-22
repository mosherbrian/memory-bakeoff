# P6-r2.1 — runtime-triggered closed handoffs

DRAFT amendment, Tern author/director; corvid independent admission/verifier;
kiln worker; cairn duty/controller. Same P6 host-recovery question. No live effects
until candidate PASS and Tern signed exact-plan release. Parent contract remains
immutable; this amendment replaces execution after captured parent work, not
concurrently with it.

## Inputs

P6-r2-host-execution/package.md at582ae00 and its admitted requirements are
retained except the normal trigger and allocations explicitly changed here.
Parent original source P6-live-recovery at22c1308; accepted P5-r2 at80092f9 and
acceptancee69e2f4; core d27d5be, P2 5bfbb071; recovery4be99bf, identity84f094e,
retirementb2384d7, clock650830c and deploymentf858729 rulings retained.
New campaign4/TURN-END-HANDOFF-RULING-20260922.md at 883107edd98b4feb38204a660f93e8df49796500 is binding.
Cairn must capture and commit r2's current attempt/pass outputs, verdicts and full
per-file manifest BEFORE amendment execution; receipt binds exact commit/hashes.
No moving HEAD dependency and no overlap. That captured tree, including any
known defects, is the implementation base; independent admission may precede
capture, but worker release may not. Resolve all abbreviated commits in receipt.

## Changed normal path and completion check

1. Implement runtime turn-end subscription as the primary normal handoff trigger.
   Inspect actual acp-worker producer and/or transition-notify interfaces read-only,
   capture sanitized field structure and source hash. Actual sidecar is best-effort,
   truncates per turn and emits end for failure/cancel too. Persist bound event
   receipts with runtime item/session/execution mapping; duplicate/stale end,
   stream reset/rotation/loss and restart must not lose or duplicate a handoff.
   Reconcile missed events with durable session/claim evidence; polling mtimes
   is not the normal path. No changes to shared runtime without Tern review.
2. Route-free, atomic execution completion claim at launch-assigned package path:
   package/attempt/action/execution/contract-step/outcome/artifact paths+hashes.
   Contract/launcher owns routing and actor attribution. Reject worker destination
   selection or old/mismatched claim; no author chooses verifier. Worker may
   claim completion, not grant itself acceptance, duration, authority or next task.
3. Connected entrypoint validates turn receipt+claim+artifacts+budget and commits
   permitted transition AND next dispatch intent transactionally. Durable outbox
   acknowledges after delivery, never clears before send. Same production paths
   under injected collaborators and enabled host wrappers; real kwargs/profile,
   exit0/3 and ambiguous/failure handling, timer callback/cancel and exact fixture
   plan duties from r2 all remain. Restart at every intent/send/ack boundary;
   no blind replay or overwritten evidence. A no-successor terminal is valid rest.
4. Missing/malformed claim or failed turn immediately creates owned bounded
   recovery/escalation using the existing latency gates; no unbounded worker poke.
   Runtime end alone never certifies artifacts or task success. Never-ended turn,
   failed observation, unavailable receiver and dead controller still have bounded
   deadlines/independent backstop. Explicit director boundary task closes the
   package graph; opening a new package still requires Tern's authorization.
5. Retain107+59 prior semantic regressions, D2/D3/D4, all r2 completion duties and
   exact live-plan requirements. Add pre-end claim, end-before-claim anomaly,
   missing claim, worker-forged destination, failed/cancelled end, duplicate/stale
   end, truncated stream, lost event, restart, legitimate rest and disconnected
   observer tests. A production-path injected end must actually cause the next
   authorized dispatch or acknowledged bounded escalation, not just return a dict.
   Corvid independently tests these with captured runtime schema and checks full
   path/transaction evidence. Label injected versus live; no pretend timestamps.

## Stages, permissions, budget and release

Same Stage A read-only host discovery/implementation under injected effects,
Stage B independent candidate verification, Stage C isolated live fixture and
signed exact-plan gate as parent. Outputs only this directory source/tests/
fixtures/docs/inventory/fixture-plan/retirement-matrix/rollback plus /tmp stores.
No live service installation/seat action/global wrapper changes, host clock
change, real Signal/all-seat pause, historical edits, research or script retirement
in A/B. New fixture seats only when explicitly released by Tern within campaign4;
never repurpose/stop current four seats. Stage C must include actual turn-triggered
handoff and missing/lost-event recovery with existing30s/180s/60s latency gates.

New amendment worker initial<=25m + sole repair<=15m =40m; candidate verifier
<=20m initial/postrepair =40m. Cumulative P6 historical ceilings145 worker/135
verifier minutes (prior105/95 plus40/40). These are grants, not actual charges.
The original unspent15m live witness and15m cairn fixture remain single grants,
reassigned here, still HELD. Cancel r2 unused worker/verify portions after its
captured attempt/pass ends; record spent and cancelled separately, never reset
or transfer spent effort. Admission<=15m plus one<=10m correction confirmation.

Conditional worker release only after unchanged amendment ACCEPTED, admission
recorded, old r2 execution ended+archived+supersession pinned and exact base commit
recorded. Cairn then trusted start/deadline before one acked dispatch; relative
timer. Preserve version before sole repair; bound completion before verifier.
Missing wakes reconcile session/hash evidence; real expiry stop, BLOCKED+wake
Tern. Recovery check<=5m within active grant, no reset/second repair. Candidate
PASS returns to Tern for live release; terminal boundary remains Tern's duty.
