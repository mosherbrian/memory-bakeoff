# Normal handoff is event-driven; deadlines are backstops

Tern ruling, 2026-09-22 UTC. Brian's closed handoff graph is the intended normal
path. The accepted architecture assigns software handoffs and state+event
transitions, but I failed to specify and enforce the runtime trigger through
the packages. Deadline-led/manual advancement was an implementation omission
under my direction, not a deliberate requirement. I own that omission.

## Authority and handoff protocol

The admitted contract names allowed next steps, roles/seats and branch conditions.
The worker cannot nominate its verifier or destination. It atomically publishes
an execution-scoped completion claim at the path assigned in its launch manifest:
<package>/completion-claims/<opaque execution id>.json. Claim fields: package,
attempt, action, execution, contract step, outcome claim and artifact paths/hashes.
No routing fields; unknown destination overrides reject. Reported occurrence
is untrusted; host ingress records receipt time and launcher attribution.
The claim is evidence to check, not a trusted ledger write or a second queue.
Verifier/other seats publish their own step claims under the same separation.

A bound runtime turn-end event wakes deterministic reconciliation. Software
checks the matching claim, artifacts, execution identity, budget and admitted
transition. In one transaction it records the source receipt, current step
result and authorized next dispatch intent. A durable outbox delivers that
intent with stable action identity, bounded calls and receipt reconciliation.
Do NOT clear a target then call: a crash between those operations loses work.
Keep pending intent until acknowledged; restart reconciles ambiguous delivery,
never blindly duplicates a call. No universal exactly-once transport claim.

Valid terminal rest has an explicit disposition and needs no successor. Turn-end
without required claim, with failed/cancelled outcome or with invalid evidence
creates an owned bounded recovery/escalation, not an invented success. A worker
poke requires an explicit recovery grant; missing claim does not authorize an
unbounded retry. A package boundary still needs Tern's next-package decision,
represented as a bounded director task, never worker-created routing.

## Runtime signal and durability

Read-only inspection of ~/.config/agent-deck/acp-worker confirms emit writes
{"t": kind, "item": self.item}; start/end use this item. End is emitted on
normal completion, stall and cancellation paths. emit is best-effort and swallows
write failure; stream_reset truncates the sidecar at every new turn. Paths are
runtime-keyed, not reliably seat-name files. Therefore counts or current contents
alone are not a durable completion journal and cannot prove success.

Primary path consumes runtime notifications/stream append events, persists bound
turn receipts and reacts promptly. Correlate runtime key/item with the declared
execution/session; do not infer identity from filenames/suffixes. Stream loss,
truncation, coalescing, duplicate end and process restart require reconciliation
against durable session evidence and completion claims. Running->waiting notify
may be an observation trigger, not a substitute for matching execution/outcome.
Choose and test the actual producer interface; don't assume it is lossless.
Host receipt clock measures observation, not unrecorded source occurrence. Any
latency measurement with inferred source time must report its uncertainty.

Deadlines REMAIN for turns that never end, failed event capture, unacknowledged
handoffs and bounded recovery. Independent supervisor-health detection remains
outside the controlled process. No model polling. Bounded host reconciliation
is a fallback, not the normal mtime-driven handoff path.

## Package action and openwork

Amend P6 now via separately admitted P6-r2.1 event-handoff revision. Preserve
current r2 work/results; don't mutate its frozen contract or silently append
requirements to its running attempt. Cairn holds subsequent dispatches, lets any
already authorized attempt/pass resolve inside its original bound, archives it,
and prevents overlap. New amendment has explicit fresh effort; old spent history
survives, unused replaced allocations are cancelled with a receipt.

Openwork stays live during construction and shadow. P6 acceptance alone retires
nothing. At a separately authorized, evidenced cutover, retire its duplicate
open-dispatch/idle/mtime policy after event-driven missing-claim recovery,
loss/restart reconciliation and quiet-rest negatives pass the latency gates.
Keep independent controller-health supervision, not two normal work dispatchers.
The existing retirement and recovery-latency rulings otherwise stand.
