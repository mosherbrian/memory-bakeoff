# Candidate adapter/reader interface (P4 rehearsal)

## Adapters (all fake; incapable of live effects)

- `FakeLaunchAdapter.launch(action) -> artifacts`: canned hashes keyed by
  action_id; records `launches`. No process execution.
- `FakeInspectAdapter.inspect(action_id, external_state) -> {action_id, delivery}`:
  reports recorded delivery state; never touches live systems.
- `FakeStopWakeAdapter.stop/wake/notify`: records stop/wake; `notify` asserts
  recipient is never Brian and only fake-queues. Terminal pause proposals are
  fake output strings, never sent.
- `FakeTimer.arm/remove/fire/due`: one-shot deadlines on a fake clock;
  restart reconstructs arming from durable intent/ack; fired ids never refire.

## Reader

`supervise(snapshot, ledger, now, triggers_fired, file_activity, busy_seats)`:
ledger determines inventory/phase/disposition/action/owner/deadline/receipt;
snapshot is compared claim-by-claim. Missing/unreadable/stale snapshot or
ledger failure returns owned INVALID (`cairn`/`tern`), never silent success.
`file_activity`/`busy_seats` are informational and never mask INVALID.
`dedupe_action_due(seen, verdict)`: ACTION_DUE deduplicated across restart.

## Status report

`status_report(package_id, ledger_packages, snapshot, verdict)` returns
package, simulated flag (always true here), owner, action, deadline, receipt,
evidence, phase, next permitted action, supervision verdict, duty (`cairn`),
escalation (`tern`). Simulated observations are labeled; no real campaign
history is claimed.
