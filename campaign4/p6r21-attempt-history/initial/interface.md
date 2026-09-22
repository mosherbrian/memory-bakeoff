# Candidate adapter/reader interface (P6-r2.1 Stage A)

Inherits the P6-r2 connected boundary unchanged; new surface:

## Turn watcher (`TurnWatcher(stream_dir, reader=None)`)

- `poll(keys, cursors)` → `(events, cursors, notes)` with normalized
  `{stream_key, item, kind, extra}`; notes `ok/truncated-reset/
  rotated-missing/unavailable`; partial lines skipped. Reader injectable;
  production default reads the runtime sidecar read-only.

## Route-free claims (`write_claim` / `validate_claim`)

- Claim fields: package/attempt/action/execution/contract_step/outcome/
  artifacts(paths+hashes). Forbidden worker fields: verifier/destination/
  next_task/next_action/accept/duration/authority/grant/deadline/seat/
  actor/route. Mismatches vs the launch manifest → `E_CLAIM_MISMATCH`;
  routing fields → `E_FORGED_ROUTE`; gaps → `E_CLAIM_INCOMPLETE`.

## Handoff (`run_handoff`)

- Inputs: adapter, qid, turn event, claim, launch manifest, optional
  `verify_spec{action_id, deadline_utc}` or `terminal_disposition`.
- Duplicate end → `duplicate-end-ignored` (durable); failed/cancelled →
  `owned-recovery` (bounded escalation, no fake success); other outcomes
  → owned rejection; artifact mismatch → `E_ARTIFACT_MISMATCH`.
- Success declares intent atomically, commits the ledger step, outboxes
  the next dispatch (`dispatched-next`) or closes terminal rest
  (`terminal-rest`, quiet, no successor dispatch).

## Outbox (`outbox_send` / `outbox_ack` / `reconcile_outbox`)

- Pending intents persist with stable identity; resends reuse it (never
  new intents); ack only after delivery evidence; ambiguous holds.

## Reader

Unchanged ledger-authoritative supervision (REST/INVALID/ACTION_DUE) plus
SIMULATED-labeled status. Deadlines backstop never-ended turns, failed
capture and unacknowledged handoffs. Latency instrumentation per action
ID for the 30 s / 180 s / 60 s Stage-C gates.
