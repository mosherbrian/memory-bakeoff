# Candidate adapter/reader interface (P4-r2)

## Adapters (all fake; incapable of live effects)

- `FakeExternalWorld(path=None)`: independent external delivery simulation;
  `record`/`delivery`; optional /tmp JSON persistence. Survives Driver reopen.
- `FakeLaunchAdapter.launch(action)`: canned hashes; records launch + world
  `dispatched`. No process execution.
- `FakeInspectAdapter.inspect(action_id)`: reads the independent world only.
- `FakeStopWakeAdapter.stop/wake/notify`: writes `delivered` into the world,
  records locally; `notify` asserts recipient is never Brian (fake-queued).
- `FakeTimer`: one-shot arming only; NOT authoritative (authority = ledger +
  durable handled table).

## Driver (authoritative)

- `on_deadline(action_id, qid)`: no-op unless the ledger shows this exact
  action as the current flight of a live phase AND now >= its deadline AND
  the effect is not durably handled. Otherwise one interrupt, one stop, one
  wake, then durable `handled-acked`. Stale/removed/never-armed/wrong-package/
  early callbacks return owned no-ops.
- `on_handoff_deadline(qid)`: duty-owned genuine handoff path.
- `publish_completion`: rotates worker timer, arms verifier/handoff deadline
  from ledger facts.
- `reconstruct_timers()`: restart re-arming from ledger facts only.
- `reconcile_restart(qid, action_id)`: intent vs world vs durable handled;
  ambiguous holds, never blind replay.
- `dedupe_trigger(trigger_id)`: durable ACTION_DUE dedup.

## Reader

Unchanged `supervise` (ledger-authoritative; owned INVALID; REST semantics)
plus `status_report` (SIMULATED-labeled; duty cairn, escalation tern;
terminal pause proposals fake-only).
