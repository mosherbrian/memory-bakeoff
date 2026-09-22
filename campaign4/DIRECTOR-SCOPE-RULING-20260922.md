# Director context: campaign memory in records, bounded conversational carry

Tern decision, 2026-09-22. Extends SESSION-SCOPE-RULING-20260922.md to the
director. Operator reports 116.7M input tokens across three Codex sessions;
this is supplied telemetry, not independently audited here, a price calculation,
or a measure of unique context length. The policy does not depend on its exact size.

## What the director carries

Carry a small campaign brief: current charter and authority limits; research
priority; current frontier and explicit next action; active owners, action IDs,
deadlines and remaining grants; unresolved decisions and contradictory evidence;
a compact decision index with reasons and links. Retain cross-package invariants
and failure patterns that guide judgment, including the reasons for rejected
alternatives. Carry references to evidence, not all previous verdicts, raw tool
output, routine acknowledgments, logs or package conversations.

Unlike a worker, the director's scope is campaign-wide. That means access to the
whole durable record, not automatic inclusion of that record in every prompt.
A closed package may still be a necessary dependency or counterexample. Never
filter retrieval solely by package age or terminal status.

## What is re-read

Before authorizing an action, read its governing charter/ruling, current contract,
allocation and release/dispatch records. Before acceptance, read the bound primary
artifacts and independent verdict, relevant prior failures and version differences.
Before changing a cross-package decision, retrieve its rationale and contrary
evidence. Verify path+commit+full hash; an index, short hash or previous conclusion
is a navigation aid, not authority. Do not assume a summary can certify evidence.

Decision records should contain decision, authority, scope, evidence pins, rationale,
material alternatives/rejection reasons, uncertainties, and what could reopen the
question. Missing consequential reasoning is a record defect: add a dated supplement
from available evidence, with uncertainty labelled. Do not reconstruct an invented
rationale from confidence or fill gaps with the old conversation by default.
Historical transcripts remain available for targeted forensic retrieval.

## Safe session boundary

Use a fresh director conversation at a reconciled package/revision boundary,
with a versioned director packet and explicit inbox handoff. Do not reset on every
routine message, and do not wait for involuntary context exhaustion as the strategy.
Before cutover: record the frontier and next action, reconcile pending deliveries,
verify duty/deadline coverage, bind old/new session identity, and ensure exactly one
director can authorize work. New session first re-reads the packet's sources and
confirms the active frontier; an archived conversation is not replayed wholesale.
No allocation, clock or incident identity resets. Do not substitute another model
if Codex usage is exhausted: the charter's hard stop still applies.

This ruling authorizes the policy, not an untested session switch during P6-r8.
At its next reconciled boundary Tern owns assessing the available handoff mechanism
and doing the smallest safe cutover, or recording the concrete missing capability
and a bounded next action. Brian is not the routine scheduler. No new framework,
compactor, dependency, background summarizer or worker allocation is created here.

## Packet size and proof

Target <=2,000 words for the director packet, excluding linked authoritative files.
This is an editorial target, not permission to omit an unresolved obligation. If it
does not fit, index evidence and reduce narrative; disclose any necessary exception.
Update on decisions/boundaries, not every receipt. Store historical packet versions
in git. Brief + decision index + active frontier is enough to start reconstruction;
it has not yet been shown sufficient for an actual director handoff.

At cutover, demonstrate recovery of authority, every active action/deadline/grant,
the next decision, and at least one relevant historical contradiction solely from
the packet and linked records. Missing facts block cutover until the record is fixed;
missing reasoning that affects the current decision must be recovered before acting.
Measure actual input/cache/output, latency and missed obligations after the switch;
no claim that a fresh context preserves caches or guarantees a particular saving.
Bank released context and budget by default. Do not spend it automatically on more
packages, deeper review, concurrency or a larger director prompt.
