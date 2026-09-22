# P6-r4 Stage-A implementation report (SIMULATED candidate — no live run)

## Commands
- `PYTHONPATH=src python3 -m pytest tests/ -q` → 165 passed (156 retained
  r3 regressions incl. C1–C12/D1–D4 + atomic authority + 9 N/T/O gates,
  injected OS boundaries only).
- Accepted core suite from P3 package dir → 59 passed.
- AST check: no duplicated method bodies per class (sole shared name is
  the `FakeClock.now` property pair).
- Read-only discovery only; zero executions; zero credentials.

## Expected/observed (N/T/O, production paths under injection)
- N: real `DirNotifier` wakes on an after-start append with no sleep on
  the path; startup-existing ends observed once; timeout bounded; fds
  really closed; missing dirs fail closed. Worker/verifier ends arrive
  on distinct streams through the same CLI. Observed.
- T: CLI trace carries systemd-run with the mapped unit, remaining
  duration and executable callback; cancel/query share the unit;
  reopen callback authority holds; non-allowlisted units and failed
  runners fail owned with no success claim; fake-only timers refused.
  Observed.
- O: positive CLI → verifier receipt → terminal → restart → rollback
  settles with zero pending, no resend, verified cleanup and a
  consistent archive; ambiguous delivery stays pending with rollback
  BLOCKED; crash boundaries reconcile the same identity. Observed.

## Limitations
Simulated/injected evidence only; shims stand in for host binaries;
reboot modeled as fresh process/epoch. Nothing authorizes cutover,
disablement or live effects.

## Readiness conclusion + blocking gaps
Live fixture is NOT yet runnable. Blocking gaps:
1. Candidate PASS by corvid (Stage B) outstanding.
2. Tern-signed fixture-plan hash (Stage C gate) absent by design here.
3. Host paths unwitnessed live against real binaries/producer.
