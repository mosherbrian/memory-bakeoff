# P6-r2 connected host execution — Stage A (SIMULATED candidate; no live run)

Connected correction of the exhausted P6 candidate: one runnable entrypoint
composing trusted ingress, durable intents, transport, actual source
capture, timers and lifecycle reconciliation (`src/harness.py` +
rewritten `src/host_adapter.py`; P5-r2 baseline otherwise preserved).
Read-only host inventory refreshed and hash-pinned (nothing executed, no
credentials). No live state, seat actions, service installation, model
calls, host clock changes, or prior-package edits.

- Transport runs real subprocess branches under injected runners: real API
  kwargs (`argv/capture_output/text/int timeout/campaign4 env`), exit 0
  sent / exit 3 queued / other failed / timeout-malformed ambiguous;
  message identity persisted (stable `state()` across fresh instances);
  queued is delivery ack, never completion or redispatch permission.
- Timers run through a bounded injected runner with unique fixture units,
  remaining authorized duration, executable candidate callback argv
  (`harness timer-callback`, never `true`), durable handled/cancelled
  checks, and shared create/cancel/query unit identity.
- Observer implements the real ACP turn schema captured read-only
  (`fixtures/acp-schema-sample.jsonl`, content redacted, structure kept):
  bounded incremental scans with persisted cursor, explicit
  session→execution binding, artifact verification; verified completion
  drives the next bounded action through code (`drive_next`); escalation
  needs actual transport-delivered ack evidence.
- `fixture-plan.json` carries executable setup/run/assertions/cleanup with
  no placeholders (runtime IDs via the setup manifest) — PROPOSED ONLY,
  never executed here. `retirement-matrix.json` + `rollback.md` retained.
- `src/fake.py` is INTERNAL test-only (never a write path, never live).

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (118 tests, injected
effects only). Accepted core suite: 59 passed. Simulated evidence never
certifies live behavior; Stage C needs candidate PASS + Tern-signed plan
hash first.
