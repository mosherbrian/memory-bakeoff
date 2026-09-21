# P4 rehearsal report (SIMULATED — cannot certify live behavior)

## Commands
- `PYTHONPATH=src python3 -m pytest tests/test_rehearsal.py -q` → 14 passed.
- Accepted core suite from P3 package dir → 59 passed.
- No sleeps, no network, no subprocess; fake clock + fake adapters only.

## Expected/observed
- Happy path authz→start→dispatch→publish→verify→decide: REST. Observed REST.
- Duplicate delivery: same action, attempt stays 1. Observed.
- Crash-before-delivery / ambiguous delivery: hold-for-reconciliation, no
  blind redispatch, no duplicate launch. Observed.
- Crash-after-ack: settled-acknowledged. Observed.
- Repeated completion rejected; deadline one-shot; single stop/wake. Observed.
- Lost-timer restart: reconstructed one-shot, one stop + one wake. Observed.
- Blocked-verifier resume: CHECKING, same attempt, no worker rerun. Observed.
- Rest after last package: REST, no auto-authorize (no r2). Observed.
- Missing boundary disposition: prompt E_MISSING_DISPOSITION (Tern omission
  reproduced). Observed.
- Supervision: missing/stale snapshot and ledger failure → owned INVALID;
  forged owner still INVALID under file-activity/busy-seat noise. Observed.
- Stale worker timer cannot expire verifier: ACTIVE on verifier deadline.
  Observed.
- ACTION_DUE durable/deduped across restart; status report SIMULATED-labeled;
  duty cairn / escalation tern; terminal pause fake-only; zero notifications.
  Observed.
- Source scan: no live-effect imports/calls in `src/driver.py`. Observed.

## Limitations
Simulated evidence only; fake adapters prove composition boundaries, not live
launch/inspect/stop/wake behavior. One harmless fixture package; single
question id.

## Readiness conclusion + blocking gaps
A separately authorized live fixture is NOT yet ready. Blocking gaps:
1. No live adapter implementation reviewed or enabled (by design excluded).
2. No real campaign-history validation; all observations simulated.
3. Director live authorization for any live fixture is absent and out of scope.
