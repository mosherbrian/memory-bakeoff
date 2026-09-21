# P4-r2 rehearsal report (SIMULATED — cannot certify live behavior)

## Commands
- `PYTHONPATH=src python3 -m pytest tests/ -q` → 28 passed (16 retained
  rehearsal incl. initial removed-timer regression + corrected stale-timer and
  restart tests; 12 new durable-events tests).
- Accepted core suite from P3 package dir → 59 passed.
- Fake clock + fake adapters + independent world only; no sleeps/network/
  subprocess.

## Probe reproduction (parent 945e3384) and correction here
1. stale_worker_deadline: parent `interrupted`, BLOCKED, stops=1 wakes=1 →
   here `no-op-stale-action`, CHECKING preserved, no stop/wake.
2. early_current_deadline: parent `interrupted` before due time → here
   `no-op-early`, RUNNING preserved, no stop/wake.
3. duplicate_after_restart: parent second `interrupted` with fresh stop/wake
   → here `already-handled` from the durable table; zero new stop/wake with
   unshared adapters; world confirms `stop:<action>` delivered once.

## Other observed results
- Genuine due worker/verifier/handoff deadlines interrupt exactly once
  (BLOCKED + one stop/wake as owned); early handoff no-ops; worker callbacks
  never interrupt duty-owned handoffs; wrong-package/old-generation no-op.
- ACTION_DUE trigger dedup durable across reopen; interrupted effects acked in
  the world; crash-ambiguous delivery holds with no redispatch and no
  exactly-once claim; no new attempt or budget reset on recovery.
- Output hashes carried through world artifacts; status reports
  SIMULATED-labeled with current owner/action/deadline/receipt/evidence.
- Corrected misleading tests (crash-settle via independent world, restart
  reconstruction without caller arming, rotation-based cancellation); no
  requirement relaxed. No accepted-core change (none needed; nothing reported
  to Tern). Source scan: no live-effect imports/calls in `src/driver.py`.

## Limitations
Simulated evidence only; proves composition/durability boundaries, not live
launch/inspect/stop/wake. Explicit upstream-failure-event integration remains
a future live requirement.

## Readiness conclusion + blocking gaps
A separately authorized live fixture is NOT yet ready. Blocking gaps:
1. No live adapter implementation reviewed or enabled (excluded by design).
2. All observations simulated; no real campaign-history validation.
3. No director live authorization for any live fixture (out of scope).
