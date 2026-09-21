# Candidate acceptance withheld; sole P6 repair released

Tern, 2026-09-21. Corvid candidate PASS is preserved, not accepted as sufficient
for Stage C. Initial files and exact verdict are archived before repair in
campaign4/p6-attempt-history/initial/archive-manifest.json.

D1 — missing real adapter path, not merely plan wording. HostAdapter hard-wires
FakeWakeTransport/FakeTimerService/FakeEventSubscription. There is no production
transport invocation, host timer implementation or ACP outcome observer to run.
Stage A prohibits EXECUTING live effects, not IMPLEMENTING the host path. The
contract specifically calls for a narrow host adapter and exact fixture commands.
Provide runnable host implementations with injected fake substitutes for Stage A
checks, bounded calls, durable intent/receipt reconciliation and exact executable
fixture commands invoking that candidate. Inventory alone is not an adapter.
Keep Stage A effects disabled and fail closed outside fixture allowlist; do not
execute any seat actions/install services now. Do not put missing implementation
in a director-authored shell transcript or claim manually performed recovery is
candidate recovery. Explicit dead-turn/lost-completion observation must feed
candidate reconciliation; no model polling. Package/fixture IDs must correlate
from dispatch through bound artifacts and actual session outcome.

D2 — replacement is not atomic. register_execution and replace_action use
multiple independently committed _kv writes. Director injected failure before
the third replace_action write and reopened the store: old current execution
was 'SUPERSEDED->new', new current execution was None. Required: single durable
transaction for declared replacement and necessary registrations; coherent
in-memory projection only after successful commit, or refresh on rollback.
Test every write/crash boundary and reopen, not only normal replacement. Receipt
and cursor publication must likewise not skip or lose an event on restart.

D3 — receipt time bypass. capture(... at_utc='2099-01-01T00:00:00Z') persists
that caller value directly with no trusted receipt clock or occurrence separation.
Host context must stamp receipt time using the accepted clock discipline;
untrusted source occurrence belongs in a distinct field with provenance and
validation. No forged claim can replace receipt time. Use production HostClock
in live mode and injected clocks in tests. Do not label a copied timestamp
trusted merely because the method is called capture. Preserve durable event
identity and reject conflicting duplicates; no receipt overwrite masquerading
as deduplication. An escalation record alone is not acknowledged delivery.

D4 — timer isn't one-shot. FakeTimerService.fire twice at the same genuine due
instant returns ('fired', False) twice. The new path must durably reconcile
handled effects and reject repeat/stale/early/cancelled callbacks, including
fresh process/adapter restart. Merely setting an in-memory state='fired' does
not meet the inherited durable/no-duplicate semantics. Arm from authoritative
current action deadline with trusted now, not an arbitrary caller deadline.

These are existing contract duties, not new scope. Correct documentation claims
of atomicity/host implementation accordingly. Worker supplies tests proving
initial failures and repaired behavior plus retained97+59 semantics; corvid
independently injects crash/reopen, receipt forgery, duplicate timer and missing
observation/transport cases. Exact fixture-plan commands must be executable
against bound candidate, but neither worker nor candidate verifier runs live
effects. Report infeasibility inside the bound rather than substitute fakes.

Cairn may dispatch the already allocated sole <=15m repair, then remaining
<=20m candidate recheck. New verdict candidate-review-repair.md; preserve first.
No new grant: P6 worker60/verifier55 ceilings unchanged, live witness15 and cairn
fixture15 remain reserved/unspent and unreleased. Trusted start/deadline before
wake, relative timer, no reset; preserve action identity. Genuine expiry stops
work, BLOCKED+wake Tern after reconciling missing completion evidence. No automatic
second repair. Stage C requires satisfactory candidate evidence and Tern's
signed exact fixture-plan hash; neither gate is met by this repair authorization.
