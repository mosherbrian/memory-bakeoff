# P6-r4 — notification wait, enforced timer, delivered-outbox drain

DRAFT. Tern author/director; corvid independent admission/verifier; kiln worker;
cairn controller/duty. Narrow successor, same P6 question. No live seat/service
execution before candidate PASS and Tern's signed exact fixture plan.

## Base and unchanged requirements

Copy campaign4/packages/P6-r3-cli-recovery at 4b02d0aa14d711b3d5673892ce760deb601f3ce5, full manifest and
candidate-review-recovery.md. Verdict SHA256
3cc00b9ea7b6bbf9cbd95774b14d4b64309426ea56f97118f3e2ed098e1b3680.
Parent contract a35eace and preregistered CLI cases atf87810b remain binding;
D1/D3/D4 improvements are retained, not presumed acceptance of all host behavior.
Read parent director repair decision d925834 and allocation extension643d1ae.
Rulings turn883107e/recovery4be99bf/identity84f094e/retirementb2384d7,
clock650830c/deploymentf858729/context54b6087+92467e4 remain binding. Accepted
P5-r2 80092f9, core d27d5be, P2 5bfbb071; resolve short pins in receipt.
Original bytes/history immutable. Full source pin, not moving HEAD.

## Three concrete defects and observable gates

N — _wait_end currently calls poll+sleep; notify has no producer caller.
Implement actual notification-backed wait using the available runtime or OS file
notification primitive. Persisted event reading is the drain, NOT a periodic
primary trigger. Attach before initial drain to close the subscribe/read race;
handle startup-existing event, partial record, truncation/rotation, overflow/loss,
restart and timeout with bounded owned reconciliation. No busy/model polling.
Evidence: instantiate the production notification class on private /tmp files;
append an actual-format runtime end after the wait starts and demonstrate wake
without periodic time.sleep scanning. This private-file OS notification test is
explicitly allowed in Stage A (no agent-deck effects, no live seats/services).
Also exercise the SAME exact CLI with injected runtime producers on distinct
worker/verifier streams. Prove bounded wait timeout, cancelled watcher and file
descriptor cleanup; injection must not bypass the production subscription path.

T — CLI constructs deadline:<action> but plan allowlists another timer unit;
E_DISABLED is swallowed and no host timer exists. Declare a stable action->unit
mapping in bound plan/manifest used consistently for create/query/cancel/callback.
Missing allowlist or failed systemd creation returns owned failure, prevents
claiming successful supervised dispatch, and reconciles any already-delivered
work; never treat in-memory create as a real timer. Production subprocess runner
is injected for candidate checks. Evidence: exact CLI trace contains required
systemd-run relative timer with remaining authorized duration and executable
candidate callback, followed by correct query/cancel; callback deadline authority
and duplicate/stale/early/cancelled behavior hold after reopen. Test rejected
allowlist and failed runner and assert no false backstop/success claim.

O — terminal-rest currently leaves verifier-dispatch outbox pending, blocking
rollback. Do not remove the rollback guard. Correlate transport acknowledgements
and actual verifier start/outcome evidence to the exact action/execution/message;
settle the matching durable intent after proof, not merely because phase is
terminal. Preserve queued/ambiguous handling, no blind resend or premature clear.
Evidence: exact positive CLI -> verifier receipt -> terminal -> restart -> rollback
has zero unresolved delivered intents, no second send, verified unit cleanup and
consistent archived ledger. Negative ambiguous delivery leaves intent pending
and rollback BLOCKED; terminal phase alone must not forge acknowledgement.
Crash before/after external delivery/local ack must reconcile the same identity.

Corvid must grade all three as BLOCKING. Before worker dispatch its admission
record supplies a short three-case expected-call/output checklist, including
positive and negative outcomes. This fixes observables, not implementation.
Parent C1-C12 and156+59 semantics retained. Changes confined to these connected
paths and supporting plan/tests/docs; no broad rewrite, new research or silent
weakening. Independent verification executes exact shipped CLI plus production
notification private-file test, not disconnected helpers or faked PASS counters.
Both repaired source and exact fixture plan hashes bound. If a gate is not
implemented, report FAIL/incomplete rather than forward-item/nonblocking.

## Stage limits and allocation

Outputs only this directory source/tests/fixtures/docs/plan/inventory/rollback
and /tmp tests. Stdlib implementation; read-only host discovery. No host services,
seat actions, runtime-wrapper edits, real Signal, clock change or script retirement
in A/B. Private temporary-file notification is permitted as above. Other OS
commands are intercepted at runner boundaries. The inherited Stage C isolated
fixture remains held until Tern signs exact plan after candidate PASS.

New worker initial<=30m + sole repair<=10m=40m; candidate verifier<=15m each
pass=30m. Historical cumulative P6 grants245worker/205verifier (prior205/175
plus40/30). The recovery verdict's185/175 was stale: extension643d1ae added20
worker minutes. Parent r3 worker60 and candidate40 spent; no reset. Existing
single live witness15 and cairn fixture15 remain unspent/reassigned HELD, not
added again. Admission including three-case checklist<=15m plus one<=10m
confirmation if Tern amends. Actual runtime/cost distinct from grant ceilings.

Release only after independent ACCEPTED unchanged contract + checklist pinned,
director admission recorded and parent EXHAUSTED pinned. Cairn checks no overlap,
records trusted start/deadline before wake, relative timer; preserves version
before sole repair. Bound output before corvid. Real expiry stops work,
BLOCKED+wake Tern after session/hash reconciliation; no reset/second repair.
Recovery check<=5m inside current grant. Candidate PASS returns to Tern for
live signature; every terminal boundary requires Tern's explicit disposition.
