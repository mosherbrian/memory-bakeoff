# Overnight sponsor scope and supervisor-liveness ruling
Tern, 2026-09-23T05:35:10.862635+00:00. Brian's instructions relayed by Claude.

## Go Expose
Sponsor-authorized redo in the Go binary AFTER the current P8 frozen-pin work
finishes. Use P7's existing contract/checklist as requirements, not its failed
implementation or an inherited acceptance. Add section8 overhead counts derived
from the loop ledger: dispatches, repairs, timeouts, blocks, director decisions,
step durations. Event meaning determines counts, not action-name suffixes or
conversation. Show unknown/incomplete durations honestly; allocations aren't cost
or elapsed work. Costs remain outside the binary; an external UI can join session
identities/times to go-budget. No cost-service/runtime dependency introduced here.

Include status and pending decisions, owner, next action, source/evidence links,
as-of/freshness, UNKNOWN never green and injected blocked judgment. Corvid reviews
against those checks; Tern decides acceptance. Historical Python P7 stays EXHAUSTED.
This is sponsor-authorized Go work, not a silent reset of P7's spent fleet repair.
No Go Expose build or installed-binary replacement during current P8 live witness.
Review allocation/immutable candidate pins will be explicit after P8; none spent now.

## Supervisor liveness belongs to P8 safety qualification
Architecture section6 explicitly requires ownership of the supervisor's own
liveness; an unobserved dead run process can strand the loop. Therefore liveness
is required before P8 can certify unattended use. It is not merely presentation
or packaging. P9 ships the tested unit/check configuration and instructions.
A Stage C observation under a bounded test runner does NOT prove durable service
supervision; preserve that distinction rather than quietly transferring evidence.

Target: systemd user service Restart=always plus an independent deterministic
staleness check. Cairn is operational duty owner; Tern escalation owner. The
outside check must remain active if run exits/hangs/restart-loops. Check evidence
of the control loop servicing work, not merely process existence or an unrelated
heartbeat thread. Planned stop/legitimate rest must be explicitly distinguishable
from failure: idle work queues don't imply stale supervisor; intentional shutdown
must not alarm forever or be undone by automatic restart. Define normal stop,
crash restart, failure/escalation semantics and interaction with agent-loop stop.

Bound restart and outside detection/escalation; use the existing recovery ruling
as acceptance policy rather than a new timing campaign. Capture actual endpoints
and owner acknowledgement; sending a queued wake alone isn't recovered. Test
crash recovery without resend; hung run flagged by independent check; systemd
restart-limit/backoff leads to owned escalation; intentional stopped/rest state
quiet. Existing per-action deadline timers must still enforce their own bounds.
Qualification uses isolated fixture units/resources; no main service adoption,
account-wide user/linger change, script retirement or cutover.

## Work sequencing and budget
Current Go4a00d675 / binary8cc149bf is frozen until live driver ends AND evidence
is archived. No moving target. Claude may prepare a read-only liveness design/
unit/check proposal now and send its exact proposed patch/test surface to Tern.
Do not edit/install/restart the candidate or fixture environment yet. On the live
result Tern consolidates any observed Go defects and liveness implementation into
at most P8's ONE scoped repair, using the existing30m repair+20m recheck grant;
Claude may be repair author instead of kiln under Brian's instruction. No double
allocation, overlapping authors, or reset of history. Cairn records actual author.
If liveness cannot fit that scope/cap or cannot be demonstrated within P8, final
result is NOT READY with this named blocker; no P8-r2 or automatic extra grant.
No resource is consumed from the unallocated60m reserve without an explicit decision.

## Requalification after Go Expose
A genuinely read-only addition need not repeat all live P8. Corvid checks exact
source diff and independent status/decision/count/freshness negatives, proves no
control-state/receipt/dispatch mutation, and runs existing core/host/loop regressions
on the new pinned binary. Bind results to its actual hash, not only P8's old hash.
If the patch alters shared DB/store semantics, lifecycle, routing, timers, watcher,
startup/shutdown or supervision, repeat the affected P8 cases including affected
live observations. A read-only label does not decide this; the diff and evidence do.

## Communication
Brian explicitly authorized direct notices to Claude via notify-claude tern.
Tern uses that path for actionable findings/rulings/questions and retains delivery
receipts. No extra fleet dispatch or live release follows from this record.
