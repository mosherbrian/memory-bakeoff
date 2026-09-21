# P6 live recovery — Stage A implement (SIMULATED candidate; no live run)

Narrow host adapter around the accepted P5 ingress/store (baseline copied
from P5-r2 `80092f9`; old bytes preserved; only addition is
`src/host_adapter.py` plus tests/docs). No live state, timers, seat
actions, model calls, host clock changes, research workload, or prior-
package edits. Read-only host discovery captured exact script hashes and
unit states in `host-inventory.json` (nothing executed, no credentials).

- Trusted source capture keyed by package/attempt/action/event/execution;
  host-context clock + attribution; artifacts never self-certifying.
- Declared execution identity (equality only, no suffix inference):
  same-action resume keeps IDs; genuine replacement declares supersedes
  atomically; late old results retained stale, never applied.
- One-shot relative timers from remaining authorized ledger duration with
  stale/early/cancelled rejection; every external call bounded; bounded
  non-model observation only (documented cadence/failure/resources).
- Persisted cursor + restart/lost-wake reconciliation: queued is not
  completion; ambiguous delivery never blind-retried; unavailable
  observation is an owned fault (bounded escalation, fake target).
- Dead-turn failures consumed; deadline stays fallback. Notifications and
  all-seat stop are fake targets; `campaign4-pause` unchanged.
- `fixture-plan.json` proposes exact fixture IDs/seats/units/commands/
  cleanup but NOTHING is run: Stage C needs candidate PASS + Tern-signed
  plan hash first. `retirement-matrix.json` + `rollback.md` are proposals.

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (97 tests, fakes only).
Accepted core suite: 59 passed. Simulated evidence never certifies live
behavior; no retroactive adoption claim from unit tests.
