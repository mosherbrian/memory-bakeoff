# P6 Stage-A implementation report (SIMULATED candidate — no live run)

## Commands
- `PYTHONPATH=src python3 -m pytest tests/ -q` → 97 passed (83 retained P5
  regressions incl. D1/D2/D3 + atomic authority + 14 new host-recovery
  matrix).
- Accepted core suite from P3 package dir → 59 passed.
- AST check: no duplicated method bodies per class in new code.
- Read-only discovery: `sha256sum`/`file`/`systemctl list-units`/`ls`
  only; zero executions; zero credentials.

## Expected/observed (injected matrix, all fake)
- Lost completion wake → hold-for-receipt, no retry sent; queued wake is
  neither recovery nor escalation; explicit failed turn → owned-failure
  with deadline fallback; ambiguous → hold, call log unchanged. Observed.
- Restart before send / after ack reconciles against persisted outcomes;
  startup with no receipts claims nothing. Observed.
- Unavailable receiver → bounded owned escalation (owner/next/deadline,
  durable). Observed.
- Receipts keyed 5-tuple; cursor persisted; stale/duplicate/reordered
  lookups behave. Observed.
- Timers: remaining-duration arming; early/stale/cancelled rejected;
  expired arming is an owned fault. Observed.
- Identity: stale execution retained-not-applied (no suffix inference);
  resume keeps IDs with resume relationship; replacement atomic with
  supersedes note; late old results cannot touch successors. Observed.
- Transaction-boundary restart preserves cursor/identity/receipts.
  Bounded subscription drains once; absence is no-evidence. Observed.
- No-bypass source scan passes on the new module. Observed.

## Stage gates (not run)
- Stage B: corvid candidate check (no live effect). Stage C: ONLY after
  candidate PASS + Tern-signed exact `fixture-plan.json` hash; cairn runs
  one ≤15 m fixture, corvid witnesses ≤15 m. Latency gates and
  recovered/escalated separation per the recovery ruling; all failures
  retained; no outage/clock-ambiguity samples counted.

## Limitations
Simulated evidence only; fake transports/timers; reboot boundary modeled
as fresh process/epoch (real reboot out of scope). Nothing here authorizes
cutover, disablement, or any live effect.

## Readiness conclusion + blocking gaps
Live fixture is NOT yet runnable. Blocking gaps:
1. Candidate PASS by corvid (Stage B) outstanding.
2. Tern-signed fixture-plan hash (Stage C gate) absent by design here.
3. All observations simulated; host transport/timer paths unwitnessed.

## Sole-repair verification (D1 + D2 + D3 + D4)
- D1: exact `command_for` argv verified against fixture-plan IDs/seats;
  production transports fail closed when disabled (zero calls); observed
  dead-turn → owned-failure, missing observation → owned E_UNAVAILABLE;
  `trail()` shows the full dispatch→artifacts→outcome chain. Observed.
- D2: injected crash mid-`replace_action` leaves old=current, new=None
  (projection refreshed, DB rolled back) — the exact prior partial shape
  cannot recur; receipt+cursor survive restart together with resume
  intact. Observed.
- D3: caller 2099 occurrence quarantined with nothing persisted (prior
  code persisted it); conflict → E_CONFLICT with identity kept, identical
  → dedup; escalation + queued transport still holds (never settled).
  Observed.
- D4: double fire → already-handled in-process and after fresh-process
  restart with zero new effects; durable cancellation survives restart;
  `arm_current` binds the ledger deadline, not caller input. Observed.
- Full suite: 107 passed here (97 retained + 10 repair) + 59 core; no
  duplicated method bodies; Stage A effects remain disabled throughout.
