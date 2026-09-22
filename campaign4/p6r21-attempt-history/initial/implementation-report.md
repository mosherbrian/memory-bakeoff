# P6-r2.1 Stage-A implementation report (SIMULATED candidate — no live run)

## Commands
- `PYTHONPATH=src python3 -m pytest tests/ -q` → 130 passed (118 retained
  r2 regressions incl. D2/D3/D4 + atomic authority + 12 new event-handoff).
- Accepted core suite from P3 package dir → 59 passed.
- AST check: no duplicated method bodies per class in new/changed code.
- Read-only discovery only (sidecar/producer source viewed, never run);
  zero executions; zero credentials; runtime unmodified.

## Expected/observed (event matrix, injected effects)
- Sidecar poll yields normalized turn events; second poll dedups;
  truncation resets with the new turn intact; missing files report
  rotation. Observed.
- Route-free writer/validator round-trips; forged destinations, verifier
  nominations, self-granted duration/deadline, gaps and manifest
  mismatches rejected with exact codes. Observed.
- Injected end causes the next dispatch committed in-ledger (verifier
  flight) plus a pending outbox entry; duplicate end never redispatches;
  stale old-item results never apply. Observed.
- Failed end creates owned recovery with no fake success; missing/
  malformed claims hold without pokes; pre-end claims wait; end-before-
  claim holds; legitimate terminal rest closes quietly with disposition.
  Observed.
- Outbox acks only after delivery; restart resends under the same
  identity; disconnected observer is an owned fault. Observed.
- Fixture plan has no angle-bracket placeholders and binds candidate
  paths/IDs; NOT executed (Stage-A prohibition); retirement matrix keeps
  openwork live; rollback ordered disable→reconcile→restore-one.

## Limitations
Simulated/injected evidence only; reboot modeled as fresh process/epoch;
sidecar subscription wired for injection (production notification binding
is a Stage-C integration detail). Nothing authorizes cutover, disablement
or live effects.

## Readiness conclusion + blocking gaps
Live fixture is NOT yet runnable. Blocking gaps:
1. Candidate PASS by corvid (Stage B) outstanding.
2. Tern-signed fixture-plan hash (Stage C gate) absent by design here.
3. Turn-end path unwitnessed live against the real producer.
