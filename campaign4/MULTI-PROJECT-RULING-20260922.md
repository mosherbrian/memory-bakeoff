# Independent project loops — director ruling

Tern, 2026-09-22. No interruption or scope change to active P6-r9 timer repair.
Two independent loops in one agent-deck are a portability/reuse goal. They are
not currently demonstrated or accepted. Research stays primary; this authorizes
a design direction and next-boundary planning, not an unbounded platform build.

## Findings and limits

P5-r2 Driver takes db_path and injected collaborators; this is a useful isolation
seam. Two databases alone do NOT establish independent loops. Checked current
P5-r2 sources: ingress trusted seats and status/supervisor owners are literals;
driver.py also embeds director/duty actors, default decided_by/owner, durable
wake keys and actual wake("tern",...) calls. So this is broader than four files
or eight literals, and the claim of no project identity in core is too strong.
Default fake collaborators also do not prove live isolation. No estimate of a
trivial migration is warranted before a complete inventory.

## Configuration and authority

Use one explicit, versioned per-project configuration as the deployment source,
validated by trusted bootstrap and injected into Driver/TrustedIngress/supervisor/
status as one immutable policy/context argument alongside db_path. The core does
not discover config by cwd, read globals/env implicitly, or know agent-deck syntax.
Host adapter translates that policy into verified runtime bindings. Stdlib/owned
core and replaceable adapter boundary remain binding.

Policy declares stable project/loop identity, authorized principals and their role
capabilities, duty owner and escalation target. A principal is not automatically
allowed every role merely because its name is in one list and role in another.
Ingress binds the authenticated host actor to this project's allowed role/action;
a worker-supplied actor, role or project string never grants authority. Unknown,
missing, ambiguous or cross-project identity fails owned and closed. No fallback
to tern/cairn in generic core. Campaign4's current cast belongs in its explicit
configuration; a compatibility adapter may load it deliberately, never silently.

Contracts pin the applicable policy revision and choose worker/verifier/researcher/
helper assignments from its authorized capabilities. A contract cannot enroll a
new trusted writer, redirect escalation outside its project, or relax independence
by declaring itself authorized. New roles are separately defined capabilities,
not unrestricted strings. Worker/verifier separation still applies. Runtime seat
names are labels, not role or project identity; bind actual session/incarnation.

Persist policy identity/version/hash with the ledger and relevant grants/receipts.
On reopen, mismatch is a controlled migration/reconciliation decision, not silent
reinterpretation. Historical events retain the policy and runtime identity under
which they occurred. Reconfiguration must drain/reconcile in-flight effects and
cannot revive expired grants or adopt another loop's work.

## Isolation beyond the database

Separate ledgers, artifacts, snapshots, receipts, outboxes, trigger dedupe state,
clock epochs and action/execution namespaces. Bind each host effect to its loop's
allowlist. Timer/service names must be collision-free across loops, including
identical local action IDs. Runtime subscriptions/cursors and cleanup ownership
must use declared project+execution bindings; cleanup for A cannot stop B.
No global fixed temporary database or fallback timer callback context.

Two loops can use the same agent-deck profile with distinct explicitly bound seats;
a separate profile is an optional host convention, not proof or a core requirement.
For the first acceptance test, workers/verifiers/duty seats are disjoint. Shared
seats or cross-project delegation are OUT of that initial scope: they need explicit
arbitration/authority rules rather than accidental sharing. Shared hardware/provider
quotas still couple performance; semantic isolation does not promise zero resource
contention. Do not invent a global scheduler to answer this question.

## Order and acceptance

Open a separately admitted, bounded successor at a reconciled P6 live-path boundary,
with this ruling as an input. Do not edit hash-pinned accepted cores or active r9
contracts. Tern owns deciding and allocating that successor; Brian need not say go
again. Inventory every core/adapter identity literal and fixed host resource before
implementation. Reuse the validated core and do the smallest policy-injection and
namespace change; no external framework or new dependency implied.

Acceptance must run two independent loops with deliberately identical local action
IDs and adversarial seat names. Prove A cannot submit a completion/actor/receipt to B,
B's faults route only to B's owners, both can progress, restart/dedupe remain separate,
and stopping/cleaning A leaves B running. Pin role capabilities and reject foreign
or forged authority. Reopen after policy drift must fail explicitly. Run actual
adapter integration with scoped effects before claiming same-agent-deck support;
unit tests and two SQLite files are insufficient. Retain a single-project regression
and make historical campaign4 configuration explicit.

No new worker grant, fixture, research run, migration or deployment is authorized
by this design ruling. It adds a concrete reuse acceptance obligation, not a reason
to postpone proving the current single-loop live path or prioritize a platform over
research. The two charter hard stops remain unchanged.
