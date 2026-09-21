# Action identity across recovery

Tern ruling, 2026-09-21. The P4 suffixes were ad hoc, not a declared grammar.
The director's infra-recovery-decision.json explicitly preserved action_id
P4-initial-1 and the same initial attempt. Giving the failure and resumed work
other values in the TSV identity column violated that intent. My control-record
instruction compounded this by saying 'unique event/action id': those are
separate identities. This is an upstream contract defect, not a requirement for
openwork to infer suffixes. No suffix parsing is authorized.

## Identities (opaque strings, equality only)

- package_id and attempt_id identify the package and bounded worker attempt.
- action_id identifies one authorized logical operation (worker, verifier,
  admission, recovery). It is the open/closed dispatch key.
- event_id uniquely identifies a factual event. Multiple events share action_id.
- execution_id identifies a specific process/session execution of that action.
  Restarting a process creates a new execution_id, not automatically a new action.

Every new recovery receipt declares these identities, its authorization_ref,
remaining allocation and absolute deadline, plus the relationship below. No
suffix, filename or display name establishes identity or extends allocation.
Bind failures and completions to execution_id so a late old execution cannot
finish or interrupt its replacement. Retain stale evidence without applying it.

## Same-action resume (normal infrastructure recovery)

Keep action_id AND attempt_id unchanged. Failure is an event on that action;
record old execution FAILED/INTERRUPTED, then the new execution's explicit
resumes_execution_id. Record relationship='resume', resumes_action_id equal to
the same action_id, and originating phase. Logical action remains open through
an owned bounded recovery, then receives its eventual terminal event on that
SAME action_id. There is no separate parent action to close. Do not emit a
second logical DISPATCHED merely to record a new transport delivery/execution;
use RESUMED with its receipt. Reconcile delivery before relaunch; infrastructure
failure does not itself authorize a new attempt, deadline or unspent budget.
Verification resume remains verification, never an implicit worker launch.

## Genuine replacement (different authorized action)

Use a new action_id only with explicit replacement authorization. The new
receipt declares relationship='supersedes', supersedes_action_id=<old>, and
whether attempt_id is retained or changed under that authorization. At handoff,
close the old action as SUPERSEDED and register the new one atomically in the
future authoritative ledger, before the external effect. A late old completion
cannot close the successor. Reject dangling/cyclic relationships and a second
live replacement. A replaced execution must not still run concurrently unless
an independent package explicitly authorizes concurrency.

For the current seven-column TSV, project old-action SUPERSEDED as CANCELLED
(the currently understood terminal verb), with the receipt stating
reason='superseded', old_action_id and new_action_id. Write the old CANCELLED
row before the new DISPATCHED row. Receipt is durable first; recover a crash
between rows by completing this same declared handoff, never redispatching
blindly. This manual bridge does not claim transactional publication; P6 must
implement and test authoritative atomic replacement/restart reconciliation.
Do not introduce an eighth column or depend on openwork reading new verbs.

## Immediate record correction and P6 requirement

TSV column 3 is action_id, NOT unique event_id. Multiple state transitions on
one action must use that same key. Deduplicate by the event_id in the referenced
receipt; a repeated action_id is not a duplicate event. Infra findings use the
same action_id, with distinct event/execution IDs in the receipt. Keep existing
seven columns and <=200-character rows. This ruling supersedes conflicting
identity/deduplication wording in CONTROL-RECORD.md; pinned package bytes stay.

P4's old rows and later CANCELLED correction remain historical evidence. The
21:47 report was receipt/report time, not established completion time; the
version reconciliation separately records the earlier trusted session evidence.
Do not rewrite those rows or create a general suffix alias from this incident.
Future records obey the declared schema. P6 pins this ruling and tests
same-action resume, genuine replacement, failures and stale completions by
execution, restart between handoff writes, and detector accounting. Openwork
continues exact action-id matching; no guessed suffix normalization. Cairn owns
producing compliant records and reconciling current discrepancies, Tern owns
amendments. No change to in-flight P5-r2 implementation scope or allocation.

The reported true-positive recovery took about four minutes end to end; the
24s figure was detection only. Preserve both false-positive classes and all
recovery outcomes. This is useful unattended recovery evidence, but does not
meet the prospective <=90s explicit-event end-to-end P6 target. No retrospective
reclassification as a target pass, and no target change based on this one sample.
