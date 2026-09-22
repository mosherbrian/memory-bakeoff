# P6-r2 — connected host execution and recovery

DRAFT. Tern author/director; corvid independent admission/verifier; kiln worker;
cairn controller/duty. Same P6 question, new bounded revision. No live execution
until candidate PASS and Tern's signed exact fixture-plan release.

## Pinned inputs and carried requirements

Parent campaign4/packages/P6-live-recovery at 22c130892c0e433cd46b2975c8b1903cb0aa3243, including
package.md, director-final-manifest.json, director-repair-decision.md and both
candidate verdicts. Rejected host_adapter SHA256
6525eb1b5f22230ea410ad5c409131565b36a36122da80ca2c530954a4230a33;
repair verdict49967a93f8bd73671dd8773dcc370ebcf2f53928543fd2fe163647e2a474938a.
Copy parent source/tests here; originals immutable. Accepted P5-r2 source80092f9,
acceptancee69e2f4; core d27d5be; P2 spec5bfbb071. Retirement b2384d7,
recovery4be99bf, identity84f094e, deploymentf858729, clock650830c rulings retained.
Resolve short commits to full IDs in receipt. Parent contract's required
implementation, six completion conditions, live scope restrictions and latency
bounds remain binding except allocations replaced explicitly below. No moving
HEAD input. Read-only host interface inventory must be refreshed/hash-pinned;
never execute pause/watch/openwork or collect credentials during discovery.

## Actual outstanding failures

Parent send passes invalid timeout_s=None to subprocess.run. Even if removed,
queued wake exit3 is classified as failed; HostWakeTransport lacks state(),
which HostAdapter.reconcile_send calls. It does not explicitly bind campaign4
profile. HostTimerService.create_host returns argv only; callback is true, not
candidate reconciliation, and inherited create/cancel are fake operations.
Fixture commands contain <candidate>/<session>/<execution>, print timer argv,
and have prose cleanup; no connected recovery harness or seat setup exists.
Observer tests fabricate session_id/execution_id/outcome rows; they do not
establish that the actual ACP producer emits that schema or can correlate it.
D2/D3/D4 simulated improvements are retained, but cannot establish host recovery.
P6 initial45+repair15 worker and two20m candidate passes are spent. No live
fixture/witness ran. The director declines a one-line-only repair on this basis.

## Required correction and independent evidence

1. Implement one runnable entrypoint composing trusted ingress, durable intents,
   transport, actual source capture, timers and lifecycle reconciliation. Enable
   live effects only with explicit bound plan/allowlist; injected collaborators
   execute the SAME production branches in Stage A tests. No fake defaults in
   live mode. No manual director reconstruction masquerading as recovery.
2. Bounded production subprocess/transport tests validate real API kwargs and
   campaign4 environment, exit0 started/exit3 queued/other failure/timeout and
   malformed receipts. Stable persisted action/execution/message identity must
   support the adapter's state/reconciliation interface across fresh instances;
   queued is delivery ack, never completion or automatic redispatch permission.
3. Actual timer create/cancel/reconcile operations use bounded injected runner,
   unique fixture units, remaining authorized duration, executable candidate
   callback and durable current-action checks. Printing argv or callback true
   fails. Prove cancelled/stale/early/repeated callbacks and restart do not
   repeat effects; unit name identity must match cancel/query commands.
4. Establish real ACP source schema using read-only captured records (sanitize
   content/credentials, retain field structure and provenance). Implement bounded
   incremental observation with persisted cursor, explicit source-session to
   execution binding and artifact verification. Test actual-format completion,
   explicit failed turn, partial record, truncation/rotation/restart, unavailable
   source, stale execution and lost notification. A hand-invented outcome JSON
   fixture alone is insufficient. Completion must drive the next bounded action
   through code, not only return a descriptive dict. Escalation needs actual
   acknowledgement evidence, not an owner string written to KV.
5. Provide fixture-plan.json with executable setup/run/assertions/cleanup commands
   invoking bound candidate. No unresolved angle-bracket placeholders. Runtime
   IDs may be created by an exact setup command and consumed from its bound
   manifest; never guessed. Include isolated campaign4 p6-fixture seats only,
   actual worker->verifier->director receipts, suppressed-notification recovery,
   unavailable receiver, timers, restart, quiet rest and rollback. Capture all
   latency samples per parent gates30s/180s/60s, all failures and false positives.
   Exact host paths/units/callers and allowlists; no existing four-seat stop or
   repurposing, global wrappers, real Signal/all-seat pause, host reboot or clock
   change. Stage A must NOT execute this plan or enable live effects.
6. Retain107+59 regression semantics and D2 atomicity, D3 trusted capture and D4
   durable handled checks. Corvid independently tests enabled host paths using
   injected runners with real signatures and captured host schemas, plus a
   complete harness run under injected effects. Review actual connection of
   components, not just method existence or command text. Pin source and plan
   hashes. Report any accepted semantic change before implementation.

## Outputs and stage ownership

Only this directory src/tests/fixtures, README/interface/implementation-report,
host-inventory, fixture-plan, retirement-matrix and rollback documents; /tmp
stores for tests. Stdlib implementation. Copy baseline as needed. Stage A:
read-only host discovery plus implementation/test under injected effects.
Stage B: independent candidate verification, no live effects. Stage C: cairn
operates once only after Tern's signed exact-plan release; corvid independently
witnesses. No fleet-wide cutover or script retirement. Parent retirement and
independent-health requirements remain; candidate shadow cannot affect real work.

## Explicit allocation and release

New worker initial<=30m + one eligible repair<=15m =45m; candidate verifier<=20m
each pass =40m. Cumulative P6 grants105 worker/95 verifier minutes: prior60/55
plus45/40. Prior worker60 and candidate verifier40 spent, no reset. The existing
unspent15m live witness and15m cairn fixture are explicitly reassigned to this
revision, not duplicated or increased, and remain HELD for Tern release. Actual
runtime/provider charges distinct from ceilings. Admission<=15m, one<=10m
confirmation after Tern correction.

Conditional release Stage A only: corvid ACCEPTED unchanged contract, recorded
admission and pinned parent EXHAUSTED disposition. No overlap. Cairn generates
trusted start/deadline before wake; relative timer; bound completion before
verifier; preserve initial before sole repair. Missing wake: session/hash
reconciliation; real expiry stop overdue work, BLOCKED+wake Tern, no reset.
Controller recovery<=5m within current grant. No second automatic repair or
live rerun. Candidate PASS returns to Tern for exact-plan release; terminal
boundary Tern opens warranted successor or records why none, no sponsor scheduling.
