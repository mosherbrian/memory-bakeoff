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

## Repair additions (D1–D4)

- D1: `harness setup` (plan-hash-bound manifest IDs) and `harness
  run-fixture` (dispatch → subscribed end → run_handoff → recovery,
  failing exits); live mode verifies `--plan-hash` against the plan file
  bytes plus a non-empty allowlist before enabling anything.
- D2: `run_handoff(adapter, qid, turn, claims_dir, launch, verify_spec?)`
  loads the atomically published claim file; turn authority (real end of
  bound stream/item/current execution/step) checked pre-mutation;
  artifacts recomputed from disk; verify closes only via
  manifest-authorized director dispositions; recovery bound from manifest.
  `bind_turn` / `turn_binding` launcher bindings.
- D3: seen+intent+done protocol with idempotent roll-forward;
  `reconcile_outbox` from persisted delivery evidence (acked / hold /
  same-identity resend only when never sent); `bind_route` /
  `route_for` contract-bound seats; queued/started never completion.
- D4: watcher whole-file scans with durable per-line seen predicates;
  partial tails held; `notify()` labels notified vs replay-fallback.
