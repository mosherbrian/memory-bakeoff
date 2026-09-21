# P5-r2 implementation report (SIMULATED — cannot certify live behavior)

## Commands
- Parent breach reproduction (read-only, parent untouched):
  `PYTHONPATH=<parent>/src:<parent>/tests python3
  director-mixed-atomic-probe.py` → `ACCEPTED`, `mixed-d` persisted with
  `kiln/director`, `2099-01-01T00:00:00Z`, no receipt (evidence in
  `fixtures/probe-parent-evidence.json`).
- Candidate: same probe → `REJECTED E_MIXED_ATOMIC`, zero rows persisted.
- `PYTHONPATH=src python3 -m pytest tests/ -q` → 83 passed (77 retained P5
  regressions + 6 new atomic-authority).
- Accepted core suite from P3 package dir → 59 passed.
- AST check: no duplicated method bodies per class (sole shared name is the
  `FakeClock.now` property pair).

## Expected/observed (atomic matrix)
- Mixed hold+decide in both key orders, mixed with forged kiln/director
  actor and 2099 caller time → rejected pre-mutation; event counts
  unchanged; phase unchanged. Observed.
- Schema variants (empty, unknown keys, hold+unknown, non-dict string/list,
  malformed hold, grantless 2099 hold, non-dict decide, missing trusted
  actor) → deterministic rejection codes; no rows written. Observed.
- Forged sub receipt/time/actor → rejected; counts unchanged. Observed.
- Genuine bounded hold → verdict committed with owned decision task
  (snapshot DECISION entry, owner tern). Observed.
- Genuine decide via both `record_terminal` and `append(atomic=decide)` →
  COMPLETE + disposition together, both rows trusted-stamped at the shared
  instant, history preserved across reopen, replay dedups. Observed.
- Invalid/forged/non-terminal/mismatched pairs → both rows absent,
  lifecycle unchanged. Standalone decide from CHECKING still gated.
  Observed.

## Limitations
Simulated evidence only; fake clocks; no live ledger adoption. The boundary
does not protect against an actor rewriting SQLite outside it, nor prove
occurrence.

## Readiness conclusion + blocking gaps
Live ledger adoption is NOT yet ready. Blocking gaps:
1. No live deployment of this boundary reviewed or enabled (excluded).
2. All observations simulated with injected clocks.
3. No director live authorization for any live adoption (out of scope).
