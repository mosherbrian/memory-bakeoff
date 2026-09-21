# P4 integration rehearsal (SIMULATED)

Event-driven driver composing the accepted P3-r3 store/core/validator
(vendored verbatim in `src/` as `store.py`, `lifecycle.py`, `validator.py`,
`fake.py`; accepted source at `campaign4/packages/P3-r3-authoritative-claims`
@d27d5be never modified) with FAKE launch/inspect/stop/wake/timer/
notification interfaces (`src/driver.py`). Defaults are incapable of live
effects: no subprocess, socket, signal, network, or model calls exist.

- `src/supervisor.py`: ledger-authoritative supervision + owned faults.
- `src/status.py`: compact status report (SIMULATED-labeled).
- `fixtures/fixture.json`: deterministic harmless fixture.
- `inputs/campaign4-watch.observed.sh`: REFERENCE ONLY, never executed. Its
  provisional string-map schema is replaced here by the versioned
  ledger-derived snapshot (`Store.publish_snapshot`); the reader change is
  that supervision consumes ledger + snapshot and treats the shell map as
  non-authoritative documentation only.

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (14 tests, fake time only).
Accepted core suite: 59 passed (run from P3 package dir).
No Brian notification; duty cairn / escalation tern appear as fake output only.
