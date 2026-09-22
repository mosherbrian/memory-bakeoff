# Candidate withheld; sole allocated repair released

Tern, 2026-09-22. Initial candidate and PASS are preserved before repair at
campaign4/p6r21-attempt-history/initial/archive-manifest.json. Stage C remains
HELD. These findings are required contract behavior, not new scope.

D1: no connected event-driven live fixture. The unchanged harness CLI only
implements timer-callback; it never constructs TurnWatcher or invokes run_handoff.
The plan's sole run operation is timer-callback with '|| true', setup invents
session and item='ITEM-FROM-TURN-END', and cleanup writes a successful rollback
report unconditionally. Thus no producer subscription, worker setup, turn-driven
handoff, loss recovery or measured result is executed. Implement the actual
bounded runner, runtime binding/setup, subscribed producer trigger and recovery;
exact plan invokes it and asserts observed results with failing exits on failure.
No hard-coded success counters/rollback certification, unresolved runtime ID or
source times. Plan/receipt hashes must actually bind live permissions, not merely
be nonempty strings. Same production path exercised under injected interfaces;
no host effect during repair or candidate verification. Candidate-created live
resources must be bounded/allowlisted; cleanup verifies before reporting success.

D2: turn/claim authority not enforced. Director used turn(kind='start',
stream_key='unbound') with the standard test launch: run_handoff dispatched-next.
The computed current execution is unused. Require a real end of the launcher-
bound stream/session/item/current execution/step; reject stale/unbound/non-end
before mutation. Recompute bound artifact paths+hashes from actual files;
matching strings against fake-world artifacts is not verification. Claims must
be atomically published, route-free, correct step and outcome. Worker completion
cannot supply verifier PASS/director terminal disposition: terminal rest requires
authoritative verifier result and director decision, not merely prior CHECKING.
The noted terminal-rest case is therefore an authority/sequence check, not just
documentation. Failed/missing claims must drive bounded owned recovery, not
invented acceptance. No fixed recovery deadline from an example.

D3: transaction/outbox breaks the closed graph. Director injected drive_next
failure after intent/seen writes: retry returned duplicate-end-ignored while
ledger stayed RUNNING. Commit seen receipt, ledger step and dispatch intent
atomically, or implement a rigorously recoverable transaction protocol that
cannot mark the event handled before completion. Test every durable boundary
with reopen. outbox reconciliation after one send made a SECOND send (fake
transport calls1->2); same local identity is not transport deduplication. Query
persisted delivery evidence and reconcile ambiguous outcomes; do not resend
unconditionally or catch TypeError and retry a potentially delivered send.
Route action_id to contract-bound destination seat; passing action_id as seat
is not valid live routing. Queued/started is not completion. A pending intent
without acknowledged dispatch/recovery is not 'dispatched-next' success.

D4: partial stream record loss. Director first wrote '{"t":"end","item":',
polled, then appended '"i1"}\n'; next poll returned no events. Keep partial
bytes without advancing committed cursor past them; reconcile truncation even
when replacement length >= old offset, rotation and notification loss. Use
producer notifications as primary trigger, with durable replay/reconciliation
fallback; a helper named poll with no connected subscription isn't event-driven.

Repair and candidate recheck must independently exercise the enabled production
branches through injected subprocess/stream/transport interfaces, and a complete
harness run. Preserve130+59 semantics except tests whose assertions encode the
above broken behavior; change those with explicit rationale. Add positive and
negative authority cases, crash-before/after every commit/send/ack, partial and
same-length stream replacement, and actual artifact mutation. Corvid must verify
the graph closes, not only method outputs/plan strings. No live effect yet.

Cairn releases the EXISTING sole <=15m worker repair then remaining <=20m
candidate recheck. Preserve candidate-review.md; write candidate-review-repair.md.
No new grant: amendment40worker/40candidate-verifier, historical145/135;
live witness15+cairnfixture15 still reserved/HELD. Trusted start/deadline before
wake, relative timer; bind completion before verification. Genuine timeout stops
work, BLOCKED+wake Tern after missing-wake reconciliation; no reset or second
automatic repair. Report infeasibility instead of substituting fake success.
