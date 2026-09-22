# P6-r3 Stage-A implementation report (SIMULATED candidate — no live run)

## Commands
- `PYTHONPATH=src python3 -m pytest tests/ -q` → 150 passed (135 retained
  r2.1 regressions incl. D2/D3/D4 + atomic authority + 15 black-box CLI
  acceptance C1–C12, injected OS boundaries only).
- Accepted core suite from P3 package dir → 59 passed.
- AST check: no duplicated method bodies per class in new/changed code.
- Read-only discovery only; zero executions; zero credentials.

## Expected/observed (black-box CLI, injected boundaries)
- C1 live path constructs HostClock (receipt times equal host UTC, never
  a fake default); missing collaborators fail closed. Observed.
- C2 worker send on the shim call trace; ledger publish committed.
  Observed.
- C3 end appended after CLI start is subscribed and found. Observed.
- C4 setup without evidence args fails E_UNBOUND; manifest binds
  explicit session/stream. Observed.
- C5 no-end exits 3 with a latency failure sample. Observed.
- C6 latency rows carry real fields with uncertainty distinguished;
  gate math verified on generated fields. Observed.
- C7 ledger deadline equals trusted receipt + duration (no literal).
  Observed.
- C8 full graph: worker/verifier sends, both receipts, terminal with
  plan-authorized disposition, outbox acknowledged. Observed.
- C9 missing claim/failed turn recover without routing; duplicate ends
  add no ledger effect; torn stream fails owned. Observed.
- C10 cleanup executes verify-first with archive-before-delete; report
  appears only after verifies. Observed.
- C11 mismatched hash and non-allowlisted seats refused. Observed.
- C12 CLI reopen adds no ledger effect; outbox reconciles without dup.
  Observed.

## Limitations
Simulated/injected evidence only; shims stand in for host binaries;
reboot modeled as fresh process/epoch. Nothing authorizes cutover,
disablement or live effects.

## Readiness conclusion + blocking gaps
Live fixture is NOT yet runnable. Blocking gaps:
1. Candidate PASS by corvid (Stage B) outstanding.
2. Tern-signed fixture-plan hash (Stage C gate) absent by design here.
3. Host paths unwitnessed live against real binaries/producer.

## Sole-repair verification (D1 + D2 + D3 + D4)
- D1: setup creates per-seat stream surfaces and rejects reuse
  (E_BOUND_IN_USE); wake texts carry pinned instructions; per-seat
  streams separate worker/verifier ends. Observed.
- D2: configured `create_host` invoked with exact argv + candidate
  callback from the fixture path. Observed.
- D3: vacuous-only and unacked-escalation latency files fail;
  positive+failure files pass with denominators. Observed.
- D4: pending intents block rollback with no report; clean state yields
  a derived report plus a WAL-safe archive. Observed.
- Full suite: 156+ passed here (150 retained + 6 repair) + 59 core; no
  duplicated method bodies; Stage A effects remain disabled.
