# P6-r14-host-timing — pinned executable checklist

Pinned by corvid-dsh at `P6r14-admission-1`. Brief `4bf7e38df5ce…`; parent R13
candidate commit `5410332b…`, outer manifest `e307fa3d…`, review `7f91da44…`,
R13 acceptance co-pinned. Authorized surface: local `src/r3harness/harness.py`,
`host_adapter.py`, `src/case_entry.py` + tests/plans/docs/mechanical
manifests/descriptors; core Python byte-identical. Injected host boundaries only.

## T1 — timer authority (#1)
- Every timer create/callback carries the ledger-selected DB, qid, action,
  execution; identity bound to the persisted action, not callback
  self-assertion; omitted/mismatched → fail closed (no `P6F` default for `P6C`).
- Exact-CLI callback tests: two qids in one DB; foreign DB; wrong execution;
  stale action; early callback; genuine overdue. Due current action interrupts
  once, intended owner wakes once, others untouched.
- Reopen/repeat preserves dedupe and declared cancellation; adapter
  receipt/ambiguous rules retained.

## T2 — verifier grant (#3)
- `verify_window_s` bounds verification, starting at the contract-authorized
  verifier dispatch/handoff, persisted once; worker elapsed cannot consume it;
  reattach/reopen cannot restart/extend; `escalation_window_s` is not a
  substitute; global `live_stop_utc` is the stricter cap; inadequate time →
  truthful bounded result with reason (no free grant while queued).
- Record chosen dispatch instant and effective `min(verifier deadline, outer
  stop)` in durable evidence.
- Tests: slow worker beyond the old escalation window; full separate verifier
  window; expiry; restart.
- Old-fails established on the immutable R13 parent before repair (T2 was
  source-only in R12).

## T3 — normal observation (#8/#9)
- Direct `run-fixture` (not only the wrapper) observes valid work to the
  authorized end or returns an explicit NONTERMINAL owned continuation; an 8 s
  slice cannot terminate authorized work as `no-end`.
- Notification-backed waiting, bounded reconnect/attach, original
  identity/deadlines, one send; trusted/injected time for continuation and
  outer stop, not `datetime.now`.
- Tests: direct CLI and wrapper with work >8 s; `no-end` through real expiry;
  outer-stop-before-deadline; clock discontinuity; restart during waiting;
  successful continuation with no resend.
- Nonterminal-yield adoption must demonstrate executable owned continuation.
- Explicit fault drills require applied control + independent causal evidence.

## T4 — honest metrics (#4)
- Normal slice/continuation/success are ONE normal execution; no fabricated
  `no-end-failure` row; real failed/expired history preserved; no truncation or
  retrospective rewrite.
- Tests inspect actual latency records/counts across repeat/restart, not only
  final rc; synthetic controls separately labelled and excluded; missing
  onset/timing → INCOMPLETE.

## Superseded assertions to reconcile (retain evidence; specify replacement)
- `tests/test_r3_lifetimes.py` open-grant slice `no-end`/`verifier-no-end`
  (≈152,160,224,296,315).
- `tests/test_amendment2_reconcile.py` `no-end`/`owned-failure` rows
  (≈196,215,236,253,265,270) — classify slice-induced vs genuine expiry.
- `tests/test_observer_lifetime.py` R8-parent old-fails (≈198-208) retained.
- Add real T4 latency-row/count assertions (none currently assert the synthetic
  row by name).
No blanket deletion/weakening; any semantic conflict returns Tern.

## Gate / deliverables
- Composed 59 + retained P5 83 + P3 59 on the actual new modules; record paths,
  hashes, resolved module-origin checks, commands, rc, elapsed; no historical
  source substitute or focused-gate replacement.
- Accurate acyclic manifests; R3 descriptor with correct `identical` flags; no
  self-hash; changes.md mapping T1–T4 to exact changes/evidence; NEW claim;
  logs. R13 behavioral protections (authenticated rejection, causal routing,
  A–E) retained.
- Out of scope: late-recorded-work recognition, shadow-time action
  reconciliation, lost/queued live controls; no `occurred_at` invention or
  ingress recorded-time weakening. Live stays held.
- Bounds: reader 20 m; worker ≤60 m; verifier ≤40 m; ceilings 1125/895 →
  1185/935; no automatic repair; timer never extends for running tests; honest
  FAIL/INCOMPLETE returns Tern. Every dispatch includes an executable completion
  command (explicit campaign4, absolute wake path, validated session id, action,
  absolute claim/verdict path).
