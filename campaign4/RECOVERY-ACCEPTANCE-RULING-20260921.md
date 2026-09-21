# Campaign acceptance: bounded progress or escalation

Tern ruling, 2026-09-21, adopting Brian's criterion. Recoverable interruptions
are expected. Success is timely detection followed by evidenced recovery or
bounded owned escalation, not stall-freedom and not guaranteed task completion.
Correct work in progress and legitimate terminal rest are not faults.

## Acceptance bounds for P6

These are prospective acceptance targets, not claims about today's performance.
On a healthy host with functioning local clock/storage and event transport:

- Explicit completion/failure or injected lost-handoff evidence: detection
  <=30 seconds from the source event becoming observable to the host.
- Suspected never-started/idle-open dispatch without an explicit outcome:
  owned suspicion <=180 seconds from trusted dispatch receipt. This includes
  startup grace; do not start the measurement only after grace expires.
- From either detection: <=60 seconds to evidenced recovery OR acknowledged,
  durable escalation with an owner, next action and absolute response deadline.
  Thus explicit cases have <=90 seconds total; suspicion cases <=240 seconds.
  These bounds supersede the retirement ruling's provisional <=10s proposal.

Recovery means the missing transition is committed and the next authorized
operation is acknowledged, or reconciliation establishes correct terminal rest.
A wake attempt, TSV append, queued message alone, or merely naming an owner is
not recovery. Record recovered and escalated as separate outcomes. An escalation
is an acknowledged bounded duty task; if its receiver is unavailable, the
independent backstop must reach the next owner. Repeated escalations do not count
as successful recoveries or satisfy the positive recovery demonstration.
A provider/model task may take longer; initiating and acknowledging the correct
bounded operation is the endpoint, not waiting for that task to finish. Global
host outage is outside these wall-time guarantees, must be reported explicitly,
and requires reconciliation at restart; it is not a passing latency sample.

P6 must put these bounds in its independently admitted contract and measure
source->detection, detection->recovery/escalation and end-to-end per action ID.
Include successful automatic recovery, actual failure and unavailable receiver,
lost/queued wake, never-started work, delayed startup, duplicate/reordered events,
controller restart, and quiet legitimate rest. Declare fixture counts, retain
all outcomes and violations, report maxima and distribution; no cherry-picked
fast sample or universal proof from a finite suite. Correctness, authorization,
no duplicate dispatch and trusted evidence remain necessary acceptance gates.
No permission to redispatch solely because a latency threshold expired.

## P5 is the instrument; P6 proves the behavior

P5's trusted recorded_at at ingress, persisted across reopen, is necessary
instrumentation for this criterion. It measures receipt, not remote occurrence.
Use trusted source capture as the start, explicitly separate claimed occurred_at,
and correlate every endpoint to action identity and committed evidence. Use
monotonic elapsed time within an epoch; cross-epoch UTC requires continuity
checks and explicit uncertainty. Quarantined clocks produce an unmeasurable
sample/owned fault, never an invented passing latency.

This is a purpose/acceptance interpretation addendum to P5 and P5-r2, not a
change to their frozen hashes, allocations or worker completion checks. Their
existing clock guarantees remain the instrument contract; no mid-flight
re-admission is needed for this context. P6 pins this ruling and exercises the
instrument end to end. P5 acceptance alone cannot demonstrate live recovery.

## Interim evidence

Brian's reported 16:32:39 artifact write ->16:33:03 openwork escalation is a
24-second detection proxy, not a detect-to-recover measurement. It has not been
independently reconstructed in this ruling. The earlier 9/13-minute intervals
are likewise reported observations, not a complete latency dataset.
Filesystem mtime and host journal timestamps are useful interim independent
clock observations, but package/TSV mtimes are mutable aggregate times: an
unrelated append can move them, and a file write does not prove recovery.
Capture the action-specific before/after record and observed mtime contemporaneously
and label this a proxy. Do not treat the current TSV mtime as the recovery time
for an older row, or count all activity as progress. Prefer host journal/capture
receipts tied to exact action IDs and hashes. Human corrections remain visible.

## Openwork ownership and retirement

Cairn owns openwork duty: findings, bounded reconciliation, operational health
and escalation to Tern. Tern owns policy/threshold changes and retirement.
This assigns ownership now; no change to the live script or timer is made here.
The 90-second grace is provisional, not a measured startup quantile. A suspicion
must reconcile session state, artifacts and delivery before any new execution.
Collect trusted dispatch->started observations including never-started/censored
cases and false alarms before replacing the grace; retain the independent hard
bound on reaching an owned disposition. Slow startup is not proof of failure.

Read-only inspection found openwork.timer OnUnitActiveSec=2min, AccuracySec=15s;
openwork measures grace from first observed idle-open state. Sampling, grace and
command duration can exceed the proposed P6 detection target. Today's isolated
24s observation therefore establishes neither a worst-case bound nor acceptance.
The script can log a failed seat read without waking, and it distinguishes wake
exit 0 from other statuses; P6 must test unavailable observation and queued
receipt handling rather than assume healthy monitoring from a running timer.

Openwork does NOT retire when P5 lands. Add it to P6's exact script/unit/caller
inventory and effect-ownership matrix. During candidate shadow it remains the
existing active work-state check. At a verified cutover, retire its duplicate
TSV/idle work-state policy and timer only when the replacement has passed the
latency/failure/quiet-rest gates. Keep an independent controller-health check
outside the controlled process; that requirement need not retain this particular
script. There must be one live authority for each recovery effect, not two
active redispatchers. Rollback disables candidate effects before restoring old
ownership. campaign4-pause, wake and lane wrappers remain per retirement ruling.
No script retirement, live cutover, new worker allocation or research is granted
by this ruling. P5-r2 continues under its existing admitted contract.
