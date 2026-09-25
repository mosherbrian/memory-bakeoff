# R11-recheck-1 — independent repair recheck

- **Reviewer:** corvid-dsh. Read-only; **no install, production notification,
  seat or Signal.** Within bound.
- **Intake:** recheck-receipt `6ea05c8f…`; **seven hashes recomputed and match**
  (`candidate/research-gap-check` `518581b9…`, test `dc156726…`, mutants
  `92afabc3…`, results files). Initial archive
  `attempt-history/initial/research-gap-check` = `349a9780…` matches the
  original manifest; service/timer unchanged.
- **Verdict: PASS — D1 resolved; retained behavior holds; exact-byte readiness
  for the held witness/install step.** Original INCOMPLETE stays on record.

## D1 — quiet-stream removal no longer hides coverage — resolved

Reproduced against the repaired candidate: registry A,B active; B quiet on a
valid rest (no incident); **B removed** from the registry. Next tick now reports
`Q-B: ok (rest to …)` — B is still watched — and when B's rest later expires a
new gap opens (`GAP-Q-B-…`). The new `state['watched']` set preserves any
question that was ever an active stream through removal, inactivity, rest
expiry, package completion and restart, until an explicit `retired` record
drops only that question. The prior silent-disappearance hole is closed.

## Retained behavior (independently re-run)

- Candidate suite: **42 tests, OK** (claim says 41/41 — a one-count discrepancy
  in the prose, all pass; note for exact tally).
- Planted faults: **29/29 caught**.
- My sandbox: wrong/cross `stream_id` binding cannot quiet (`Q-A` still gaps);
  explicit retirement of B resolves only B while A's incident stays.

## Migration / top-question coverage (steering)

`qs = open gaps + watched (+ top question only when no registry is in use)`. So
under registry mode, a prior **R5 open gap** is preserved (open gaps remain in
`qs`), and every stream that was ever active stays watched — no unresolved
incident or quiet stream is silently dropped on migration. A top question that
is neither registered nor has an open gap is no longer watched once the explicit
registry is adopted; that is the intended shift to explicit registration, and
the proposed registry registers `A = Q-WORK-BENEFIT` (the current top), with
`B` inactive. This is an accepted design point, not a regression.

## Limits

- No calendar-timer witness, install, rollback or production notification
  performed (held). `B` stays inactive; reviewer grants no install authority and
  does not authorize Stream B.

*Reviewed: `recheck-receipt.json`, `repair-claim.json`, `candidate/*` (hashes
recomputed), `attempt-history/initial/research-gap-check`, `repair-test-results.txt`,
`repair-mutants-results.txt`, `verification.md` (preserved); independent `/tmp`
sandbox probes.*
