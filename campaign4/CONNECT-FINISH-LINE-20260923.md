# Connect finish line — director decision
Tern, 2026-09-23. Brian requested a finite end to Connect and prioritised Expose.

Connect is CLOSED as a demonstrated integration stage, NOT accepted for general
unattended adoption. Its architecture criterion was a harmless fixture completing
unattended; R9 live-review-3 proves that on its pinned historical bytes. R18 is the
latest accepted candidate, not a new live PASS. We do not relabel failed timing
reviews or transfer the historical witness to untested later bytes.

I let Connect accumulate product safety, host instrumentation, fixture tooling,
and strict latency qualification without a stage-level stopping rule. These were
real defects but they did not all justify keeping Connect open. That was my scope
control failure. Further P6 expansion stops now. R19's already finished admission
is retained; preparation/live and unused grants are cancelled, no retry successor.
This is an ordinary budget/scope decision, not campaign-wide pause.

## Eight pre-unattended-use checks
| Check | Evidence now | Disposition |
|---|---|---|
| Restart cannot duplicate execution | retained P5 test_rehearsal.py crash-before/after-ack, ambiguous-delivery-holds; test_durable_events.py reopen effects. R9 live-review-3 saw 1+1 sends and duplicate timer no-op, NOT live crash during uncertain delivery. | Test-proven, deployed-host restart qualification open. P8. |
| Hung attempt gets enforced owned disposition | R14 candidate-review-repair.md due registered callback interrupts once, missing authority rejects; retained due-worker/verifier/handoff tests. Manual Cairn stops aren't software proof. | Test-proven; current host stop+owned escalation witness open. P8. |
| Worker cannot self-verify | R13 candidate-review-repair.md public-ingress same-principal PASS/FAIL with atomic decide reject E_SELF_VERIFY with zero changes; unknown producer rejects, reopen preserves identity. Final full gate candidate-review-completion-3.md; unchanged through R18. | Proven for trusted runtime/ingress authority boundary; no new package required. |
| Changed inputs invalidate affected registrations | P6 signature gate rejects changed tool/plan/config/binding; test_host_composition.py drift negative. This is NOT general dependency-registration invalidation; core AUTHORIZE merely registers phase. | Partial. P8 must prove or implement revalidation before dispatch for every declared input; no automatic amended input reuse. |
| Repair exhaustion stops automatic attempts | retained P3 test_lifecycle.py repair_then_exhausted_no_allocation and fail_without_repair_budget_exhausts_directly; terminal execution rejects; independent full retained gates. Later rounds were new director allocations, not autonomous retries. | Proven at core allocation boundary. Freeze policy in P8 smoke, no new repair mechanism. |
| Pending judgments visibly block dependents | core decision_task and authoritative validator tests establish owned pending decision; no unified exposed view and no demonstrated general dependent scheduling gate. | Partial. P7 owns visibility; P8 owns no-dispatch enforcement, together explicitly qualified by P8. |
| Evidence recoverable after interruption | R13 rollback/seen-event tests, retained SQLite reopen/atomic and outbox tests; preserved real failed runs/claims/reviews. Historical TSV in-place edits and late archives remain limitations. | Core recovery proven; current deployed ledger+artifact interrupted recovery drill open. P8. No claim of historically immutable TSV. |
| Routine handoffs don't need Brian | R9 live-review-3 independently confirmed real automatic worker->verifier->terminal-rest, 1+1 sends; R17 live-review-failed-1 confirmed genuine rejection/no COMPLETE (timing INCOMPLETE). | Proven for bounded happy handoff/rejection paths, not all host faults or broad adoption. |

Thus three checks met at their stated boundary (#3,#5,#8); five remain partial,
not zero progress and not eight live proofs. Tests are appropriate for deterministic
core invariants. We will not demand a live demonstration of every arithmetic rule.

## Fixed remaining work, no P6-r20 chain
P7-expose-status: one read-only status view + pending-decision list, owner, next
action, source links, freshness, accepted/current source map, limitations, costs
and missing cost evidence explicit. Injected blocked decision appears; unknown data
is unknown, never green. No redesign/host service. <=100m total allocated work
including admission/one repair/verification. Release admission now.

P8-unattended-qualification: ONE finite package owns all remaining adoption checks
#1,#2,#4,#6,#7. Before worker, pin test cases: uncertain-delivery restart cannot resend;
real hung fixture is stopped with owned disposition; declared input mutation blocks
registered dispatch; unresolved judgment blocks dependent dispatch; interrupted DB+
artifact publication recovers or blocks truthfully. Normal terminal rest stays quiet.
Use production control path, not a new parallel simulator. A bound source/clock is
needed to establish ordering and allocated deadline, NOT a new exact latency campaign.
Known late completion may stop for duty reconciliation instead of backdated acceptance.
Candidate qualification and live drills split within this ONE contract; at most one
repair, total <=4h when prospectively allocated. If a check fails at cap, report
NOT READY and stop. No successor by default. Do not claim this is guaranteed to pass.

P9-reusable-release: ONE extraction/package/docs job, <=2h when allocated. Normal
src/tests layout in separately authorized repository, pinned origin, one documented
entrypoint, one-project config, stdlib core/adapter seam, install/run/status/stop/
restore instructions, known limits. No history rewrite, new Go port, simultaneous
multi-project feature, broad framework or compactor. It may ship a supervised
preview if P8 fails; it may not label that unattended-ready. Code relocation is
byte-preserving before optional mechanical import adjustments and smoke tests.

This is a fixed work list, not a promise no unknown defect exists. New work beyond
it requires a visible budget/scope decision after demonstrating the result; it is
not automatically manufactured from each new verifier observation. P8/P9 are roadmap,
not allocations released by this record. P7 is the only new execution authorization.

## Value and done state
P7 is reusable product capability, not host-proof polish. P8 is portable safety
behavior plus one host-adapter acceptance record. P9 is reuse/distribution, not more
qualification on this machine. R18's reusable idea is trusted runtime end-time
provenance and consumer schema; its copied acp-worker and lane wrappers are an
agent-deck/ACP-specific adapter/instrument, NOT the portable core and NOT required
on a different runtime that already provides trustworthy events.

Defer exact source-to-recovery latency recertification, repeated failed-verifier
witness, exhaustive queue-fault variants, and observer-cycle tuning as independent
projects unless an actual safety gate fails. Keep safe defaults: ambiguous delivery
blocks, overdue work stops, missing evidence blocks, pending judgments don't dispatch.
No script retires without explicit ownership transfer; current Cairn/coax/backstops
remain until qualification and a bounded cutover. No indefinite dual effect owners.

Done v0.1: runnable navigable release + one status/decisions view + known limits;
explicit supervised mode if qualification absent. Done unattended v1: same release
plus all eight gates evidenced for one declared supported adapter configuration,
real stop/owner/restart path and documented recovery. Not every host/runtime or
multi-project support. Expected route is Expose in one bounded session, then one
focused qualification/release day if checks pass, not an estimated round count.

## Budget ruling
YES, P6 has reached its engineering decision boundary. No claim that Brian's
charter expired: he explicitly extended continuation. Nevertheless 26h/17 revisions
is enough to demonstrate available capability and stop expanding Connect. I should
have applied this boundary earlier. Close Connect now; move to Expose. Retain the
actual unattended blockers, but remove non-safety proof refinement from its critical
path. The fixed allocations above cannot silently renew themselves.
