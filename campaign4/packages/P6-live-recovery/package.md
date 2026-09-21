# P6 — host adapters and bounded live recovery fixture

DRAFT. Tern contract author/director; corvid independent admission/verifier;
kiln implementation worker; cairn controller/duty and live fixture operator.
Machinery only. New P6 question: can this controller recover missed handoffs
with measured latency and one effect authority using real host interfaces?

## Inputs (immutable)

- P5-r2-atomic-authority source at 80092f92c24fb58ad70478faf93e4f39eb184847, director-final-manifest.json and
  verification.md ff1f6d89db9ab570ac875b197f7ae24c5c936d7467387f88be1927e4bf84d015.
  Cairn separately pins Tern acceptance.json before dispatch.
- campaign4/RETIREMENT-RULING-20260921.md at b2384d7;
  RECOVERY-ACCEPTANCE-RULING-20260921.md at4be99bf;
  ACTION-IDENTITY-RULING-20260921.md at84f094e;
  CONTROLLER-DEPLOYMENT-20260921.md atf858729;
  CLOCK-AUTHORITY-DECISION-20260921.md at650830c.
- P2 boundary spec at5bfbb071e6efdb6f15de1c582295363a94cd08c7;
  P3-r3 core atd27d5be7b4086556260974bca9aef2ec6f8b1db8.
- Read-only host discovery: ~/.config/agent-deck/{wake,campaign4-pause,
  campaign4-watch,openwork,acp-go,acp-go-controller}, relevant user units and
  campaign4 ACP event/history interfaces. Capture exact hashes/unit properties
  in host-inventory.json before implementation relies on them. Do not execute
  pause/watch/openwork during discovery. Do not collect credentials.
Resolve abbreviated pins in receipt; no moving HEAD dependencies.

## Required implementation and evidence

Build a narrow host adapter around accepted P5 ingress/store, not another
platform or model polling controller. Reuse wake transport and lane wrappers.
Trusted source capture persists completion/failure/dispatch receipts keyed by
package, attempt, action, event and execution IDs. Clock and attribution come
from host context; artifact output is not self-certifying. Persist cursor and
reconcile restart/lost wake against actual session outcomes and bound hashes.
A wake started/queued acknowledgement is not worker completion. No blind retry
when delivery is ambiguous. Unavailable observation is an owned fault, not idle.

Software creates/reconciles/cancels one-shot relative host timers from remaining
authorized ledger duration, with stale/early/cancelled callback rejection.
Bound every external call; no model polling or periodic model wake to scan work.
Host event subscription or bounded non-model observation is permitted; document
cadence, failure handling and resource bounds. Explicit dead-turn failures must
be consumed; deadline remains fallback, not the completion detector.

Enforce declared identity across resume/replacement per the pinned ruling,
including late old-execution results and atomic authoritative replacement.
No suffix inference. Correct terminal rest must be quiet; missing disposition,
malformed state and unrelated seat activity cannot hide invalid work.
Independent controller-health supervision must not depend on the process or
reader it supervises. Notifications/all-seat stop are fake targets for this
package; keep existing campaign4-pause as emergency actuator unchanged.

## Stages and gates

A. IMPLEMENT: src/, tests/, fixtures/, README.md, interface.md,
implementation-report.md, host-inventory.json, fixture-plan.json,
retirement-matrix.json and rollback.md in this directory. Disposable /tmp
stores, fake adapters and read-only host inspection only. No service installation,
seat wake/stop, state.json, campaign ledger adoption, global wrapper changes or
host clock changes. Worker proposes exact isolated fixture IDs, seats, units,
commands and cleanup in fixture-plan.json. Existing four campaign seats cannot
be stopped or repurposed by the fixture. New fixture seats, if necessary, must
stay in campaign4 profile and have unique p6-fixture names. No research workload.

B. INDEPENDENT CANDIDATE CHECK: corvid verifies pure/injected tests, exact host
interface assumptions, effect allowlist, grants, identity/receipt persistence,
rollback and feasibility of the fixture. Preserve 83 P5 +59 core semantics;
changes to copied store/driver for declared execution identity and adapters are
allowed, but report any changed accepted semantic before implementing it.
No live effect during candidate check. Bind candidate bytes and fixture plan.

C. LIVE FIXTURE: only after candidate PASS and Tern's explicit signed release of
that exact fixture-plan hash. This gate belongs to Tern, not Brian. Cairn runs
one <=15m fixture; corvid independently observes within its <=15m witness grant.
No overlap with kiln/corvid implementation work. Tern may allocate dedicated
fixture seats within the existing profile in that release. Candidate effects
are allowlisted solely to fixture-owned seats/files/units/ledger; unrelated
campaign work and legacy backstops remain authoritative for their own IDs.
Shadow comparison of real campaign state is read-only and cannot wake/stop.
This package does not authorize fleet-wide cutover or script disablement.

## Completion check

1. Pass the retained regressions plus injected event/transport/timer failure
   matrix: lost completion wake, explicit failed turn, queued wake, restart
   before/after send and ack, stale/duplicate/reordered event, lost/removed/early
   timer, startup ambiguity, stale execution completion, same-action resume,
   genuine replacement and restart at transaction boundaries. Reconcile effects
   independently; no duplicate dispatch, phantom ack or unlimited retry.
2. Real host fixture demonstrates worker->verifier->director receipt flow and
   deliberately suppressed completion notification recovered without a human
   prompt. Capture both successful recovery and bounded unavailable-receiver
   escalation. Record source-observable time, detection and committed recovery
   or acknowledged owned escalation per action; all failures remain in dataset.
3. Prospective latency gates on healthy host: explicit event detection<=30s;
   idle/never-started suspicion<=180s from trusted dispatch; detection->recovery
   OR acknowledged bounded escalation<=60s (total90s/240s respectively). Escalated
   and recovered outcomes separate; queued wake alone is neither recovery nor
   completed escalation. Actual model task completion is not the endpoint.
   Report every sample, maxima and conditions. Host outages/clock ambiguity
   cannot count as passing samples. Include delayed-start and correct-rest
   negatives; provisional90s grace is not assumed measured or safe.
4. Witness live host transport, timer creation/cancellation, restart and cleanup.
   Inject destructive or all-seat/Signal effects only through fake targets.
   Distinguish live measurements from simulations; an injected source fault can
   exercise a real host recovery path, but must be labelled. Never claim fake
   notification proves Signal delivery. A real host reboot is out of scope;
   simulate reboot/restart boundary with fresh process/epoch and mark limitation.
5. Retirement matrix names exact script/unit/caller hashes, current and proposed
   effect owner, evidence required and planned disable/restore commands.
   Include openwork, watch, manual timer policy and manual ledger writers.
   Keep wake, pause and lane wrappers as primitives. Independent health remains.
   Shadow candidate has zero effects on real campaign. Rollback first disables
   candidate effects, reconciles action/execution IDs and timers, then restores
   one owner; demonstrate this within fixture. No indefinite dual controller.
6. Corvid verifies bound live evidence independently, including false alarms,
   quiet rest, positive recovery and negative paths. Acceptance requires both
   candidate and live evidence. If live gate fails, report blocked readiness;
   no retroactive claim that unit tests establish adoption. Tern owns boundary.

## Allocation, bounds and handoffs

P6 new grants: kiln initial<=45m + sole eligible repair<=15m =60 worker minutes;
corvid candidate<=20m each initial/postrepair =40m, live witness<=15m =55 verifier
minutes; cairn live fixture<=15m separately. Prior P5 cumulative95/85 grants
remain historical; unused P5-r2 repair10m/postrepair15m are cancelled at acceptance,
not transferred. Effort ceilings distinct from actual runtime/provider spend.
Admission corvid<=15m plus one<=10m confirmation after Tern correction.

Tern conditionally releases Stage A only after unchanged contract ACCEPTED,
recorded admission and pinned P5-r2 acceptance. Cairn records trusted starts,
deadlines and ack; arms relative one-shot timers; preserves bytes before repair.
One repair can address a bounded candidate defect inside scope; no automatic
second repair or rerun of live fixture. Genuine timeout BLOCKED+stop overdue
work+wake Tern; reconcile missing wake against session and hashes first. A
controller recovery check<=5m stays inside the current allocation, no reset.
At candidate PASS Tern must decide fixture release promptly; at final boundary
Tern opens the warranted cutover package or records no successor and why.
