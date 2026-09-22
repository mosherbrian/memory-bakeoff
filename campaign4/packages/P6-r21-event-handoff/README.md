# P6-r2.1 runtime-triggered closed handoffs — Stage A (SIMULATED; no live run)

Amendment implementing the turn-end handoff ruling on the archived r2 base
(P6-r2 source/tests copied; r2 originals immutable). New code is
`src/turn_handoff.py` (watcher, route-free claims, transactional handoff,
durable outbox) plus small adapter additions (`bound_artifacts`, outbox
methods, `drive_next` qid) and one additive dispatch-artifact binding in
the copied driver (no core semantic change). Read-only discovery of the
actual `acp-worker` producer captured the sidecar schema + source hash in
`host-inventory.json` (nothing executed, no credentials, runtime
unmodified). No live service/seat/wrapper/clock/Signal/pause effects, no
historical edits, no research, no script retirement; openwork stays live.

- Primary trigger: runtime turn-end subscription with persisted cursors
  and item/session/execution binding; duplicate/stale end, truncation,
  rotation/loss and restart reconcile against durable evidence and
  claims — never filenames, never mtime polling.
- Route-free atomic claims at the launch-assigned
  `<package>/completion-claims/<opaque execution>.json` (this package's
  own completion claim is written there on success); launcher owns
  routing/attribution; forged destinations and self-grants rejected.
- Connected entrypoint validates turn receipt + claim + artifacts +
  budget, declares transition + next intent atomically, commits the
  ledger step, and outboxes with ack-after-delivery (never clears before
  send). A production-path end causes the next authorized dispatch or an
  acknowledged bounded escalation through code. Missing/failed claims map
  to bounded recovery; valid no-successor terminal rest is quiet.
- Deadlines remain backstops for never-ended turns, failed capture and
  unacknowledged handoffs. New packages still need Tern's authorization.
- `fixture-plan.json` is PROPOSED ONLY (never executed here); Stage C
  needs candidate PASS + Tern-signed plan hash first.

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (130 tests, injected
effects only). Accepted core suite: 59 passed. Simulated evidence never
certifies live behavior.

## Sole repair (D1 + D2 + D3 + D4)

- D1: `harness.py` now implements `setup` (bound manifest IDs derived from
  the plan hash, never guessed) and `run-fixture` (dispatch → subscribed
  turn trigger → run_handoff → recovery) with failing exits; live mode
  verifies `--plan-hash` against the actual plan file bytes before
  enabling anything. `fixture-plan.json` setup/run/assertions/cleanup are
  executable with no placeholders; cleanup verifies each step before
  reporting success. A complete injected harness run was demonstrated
  (transition-committed + outbox identity, exit 0).
- D2: turns must be real ends of launcher-bound stream/item/current
  execution/step (stale/unbound/non-end rejected pre-mutation); claims
  load from the launch-assigned file path (never caller dicts);
  artifacts recomputed from actual files (mutation tested); worker
  completion cannot supply verifier PASS/disposition (verify closes only
  through manifest-authorized director dispositions; recovery bound comes
  from the manifest, never a fixed example).
- D3: seen+intent+done protocol — retries of declared-but-unfinished
  handoffs roll forward idempotently instead of false duplicates;
  outbox reconciles from persisted delivery evidence (delivered→ack,
  queued/sent→hold, only never-sent resends same identity); sends route
  by the contract-bound seat table; TypeError-catch retries removed;
  queued/started is never completion.
- D4: whole-file scans with a durable per-line seen set — partial tails
  held until complete, same-length replacement/truncation/rotation
  lossless; `notify()` labels producer-notified vs replay-fallback keys.
