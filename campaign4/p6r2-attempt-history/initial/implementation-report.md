# P6-r2 Stage-A implementation report (SIMULATED candidate — no live run)

## Commands
- `PYTHONPATH=src python3 -m pytest tests/ -q` → 118 passed (107 retained
  P5/P6 regressions incl. D2 atomicity, D3 trusted capture, D4 durable
  handled + 11 new connected-correction).
- Accepted core suite from P3 package dir → 59 passed.
- AST check: no duplicated method bodies per class (sole shared name is
  the `FakeClock.now` property pair).
- Read-only discovery only; zero executions; zero credentials.

## Expected/observed (connected matrix, injected runners)
- Entrypoint live gate fails closed (no plan/allowlist; fake-in-live);
  injected `run_step` executes production branches end to end (dispatch,
  send, capture, arm, reconcile-hold). Observed.
- Transport: exit 0 sent / exit 3 queued / exit 1 failed / timeout +
  malformed ambiguous, with real kwargs asserted (incl. campaign4 env and
  int timeout); message state stable across fresh instances; queued holds
  without redispatch. Observed.
- Timers: exact systemd-run argv with executable candidate callback (no
  `true`); cancel/query share unit identity; ActiveState parsed; handled
  repeats rejected in-process and after restart. Observed.
- ACP: real-schema completion/failed observed, message rows skipped,
  incremental cursor dedups, truncation resets, rotation unavailable;
  binding mismatch goes stale-only; verified completion publishes the
  verifier flight through code; escalation pending until
  transport-delivered ack. Observed.
- Fixture plan: no angle-bracket placeholders; executable commands bound
  to candidate paths; setup manifest supplies runtime IDs; isolated
  p6-fixture seats; latency/false-positive capture; cleanup + rollback.
  Plan NOT executed (Stage A prohibition). Observed statically + partially
  (harness CLI parsing, command builders) under injection.

## Limitations
Simulated evidence only; injected runners; reboot modeled as fresh
process/epoch. Nothing here authorizes cutover, disablement, or live
effects. `HostClock.now` read-only view added to the copied ingress for
driver clock compatibility (no semantic change).

## Readiness conclusion + blocking gaps
Live fixture is NOT yet runnable. Blocking gaps:
1. Candidate PASS by corvid (Stage B) outstanding.
2. Tern-signed fixture-plan hash (Stage C gate) absent by design here.
3. All observations simulated/injected; host transport/timer paths
   unwitnessed live.
