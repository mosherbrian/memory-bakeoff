# P5 implementation report (SIMULATED — cannot certify live behavior)

## Commands
- `PYTHONPATH=src python3 -m pytest tests/ -q` → 54 passed (36 ported P4-r2
  rehearsal/durable/repair regressions + 18 new ingress tests).
- Accepted core suite from P3 package dir → 59 passed.
- AST check: no duplicated method bodies per class (the single shared name
  `FakeClock.now` is a property getter/setter pair, not a duplicated body).

## Expected/observed (ingress matrix)
- Deadline derived from trusted start (12:00 + 3600 s = 13:00Z), receipt
  persisted with epoch. Observed as specified.
- Forged `recorded_at`/`receipt`/`_trusted` → `E_FORGED_RECEIPT`; caller
  start `deadline` → `E_DEADLINE_FORGE`. Observed.
- Minute-only/space-separated/non-time/naive/out-of-range occurrence →
  quarantined `E_BAD_OCCURRED` with cairn evidence; lifecycle untouched.
  (Naive instants pass the lower-level validator, so the ingress boundary
  explicitly requires a zone designator — documented strictness, not a core
  change.) Observed.
- +60 s future occurrence accepted; +32 min (observed-rows shape) →
  `E_SKEW_EXCEEDED` quarantine, phase preserved. Observed.
- Backdated/delayed receipt keeps both times; late completion still
  `E_DEADLINE_EXPIRED` (no retro-authorization). Observed.
- Far-future deadline inside pinned grant accepted (not skew); expired /
  unknown / mismatched grants, nonpositive/malformed/over-cap durations
  rejected with exact codes. Observed.
- Duplicate event_id append idempotent (no re-stamp, no new attempt).
  Restart a day later replays receipts byte-unchanged under a new epoch.
  Grants persist across restart. Observed.
- Forward/backward wall jumps → `E_DISCONTINUITY` quarantine; deadline
  unchanged (not reset/lengthened); `reconcile_clock` resumes writes in a
  new epoch. Observed.
- No-bypass source scan passes (only `ingress.py` calls store writes);
  `HostClock` returns valid UTC; no live-effect imports in driver/ingress.
  Observed.

## Schema (trusted receipt, persisted per event)
`receipt: {recorded_at, occurred_at|null, provenance, skew_s, epoch,
caller_at_ignored?}` + `_trusted: true`; start claims also persist
`duration_s` or `grant_ref` with the derived `deadline`.

## Limitations
Simulated evidence only; fake clocks; no live ledger adoption. Host UTC
proves receipt time, never occurrence; nothing here protects against an
actor rewriting SQLite outside the trusted boundary.

## Readiness conclusion + blocking gaps
Live ledger adoption is NOT yet ready. Blocking gaps:
1. No live deployment of this boundary reviewed or enabled (excluded).
2. All observations simulated with injected clocks.
3. No director live authorization for any live adoption (out of scope).

## Sole-repair verification (D1 + D2 + D3)
- D1: raw admit with caller `{kiln, reader}`, forged director decide, terminal
  subevent and atomic-decide caller actors all → `E_FORGED_ATTRIBUTION`;
  untrusted adapter contexts → `E_UNTRUSTED_ACTOR`; every public path persists
  the boundary-bound seat/role. Observed.
- D2: grantless 2099 verifier/handoff deadlines → `E_DEADLINE_UNAUTHORIZED`;
  CHECKING-phase grant for a RUNNING start → `E_GRANT_MISMATCH` from actual
  binding (no hints); start without duration/grant → `E_NO_AUTHORIZATION`;
  publish in the wrong actual phase → `E_PHASE_MISMATCH`; grant-covered
  distant deadlines accepted with persisted refs. Old tests encoding caller
  authority corrected with explicit rationale; lifecycle assertions preserved
  (rejections still reject, duplicates still dedup). Observed.
- D3: identical clock values across reopen → distinct epochs; backward UTC at
  reopen → `E_AMBIGUOUS_RESTART` until owned `reconcile_clock`, ledger
  deadline byte-identical before/after; wild cross-process mono values cause
  no spurious quarantine. Observed.
- Full suite: 69 passed here + 59 core; REST/INVALID semantics unchanged; no
  duplicated method bodies per class (sole shared name remains the
  `FakeClock.now` property pair).

## Repair-2 verification (atomic close ordering)
- Archived failure reproduced by code path (CHECKING verify_pass +
  question_answered via terminal_close previously raised E_PHASE_MISMATCH);
  now commits terminal state + disposition together via both supported forms
  (`record_terminal` and `append(atomic=decide)`), with both subevents
  trusted-stamped at the same receipt instant; state + disposition survive
  reopen; replays dedup without re-stamp.
- Invalid/forged dispositions, non-terminal pairs (repair-eligible fail),
  package/revision mismatches: rejected with both rows absent and lifecycle
  unchanged (no partial writes). Wrong actor, forged receipt, standalone
  decide from CHECKING still fail as documented.
- Full suite: 77 passed here (69 retained + 8 atomic) + 59 core; D1/D2/D3
  evidence retained; no duplicated method bodies (sole shared name remains
  the `FakeClock.now` property pair).
