# P6-r14 changes — connected host timing and truthful observation

(R13 record-integrity history in ../P6-r13-core-record-integrity/candidate/
changes.md; this file maps T1–T4 only.)

Parent: R13 candidate `5410332b` (`candidate/manifest.json e307fa3d` verified
on copy). Production changes ONLY `src/r3harness/harness.py` and
`src/case_entry.py`; `host_adapter.py` and all accepted core Python
(driver/ingress/store/lifecycle/validator/turn_handoff/...) byte-identical
(verified per-file). No new dependencies, no polling supervision, no
role/config migration. Injected effects only.

## T1 timer authority (#1) — harness.py
- `timer_callback` requires full identity (DB, `--timer`, `--qid-cb`,
  `--action`, `--execution`): omitted → `E_NO_IDENTITY`; unknown qid →
  `E_UNKNOWN_PACKAGE`; action ≠ persisted flight action → `E_ACTION_MISMATCH`
  (no silent flight fallback); `exec-current` present and ≠ → 
  `E_EXECUTION_MISMATCH`. No silent P6F default for P6C.
- `_arm_host_timer` embeds `--qid-cb` + `--execution` in every callback argv
  (qid/execution required params); CLI parser defaults removed.
- Evidence: new `test_r14_host_timing.py` T1 (two qids one DB isolation,
  foreign DB, wrong execution, omitted identity — zero writes each) +
  extended `test_amendment2_timer.py` (argv carries identity; stale action
  now owned `E_ACTION_MISMATCH`).

## T2 verifier grant (#3) — harness.py
- Verifier window starts at verifier dispatch (worker-end detection):
  `verify_deadline = dispatch + verify_window_s`,
  `esc = dispatch + verify_window_s + escalation_window_s`, persisted ONCE
  via keep-first (`r3v:<vaction>:<vexec>:`); reattach/reopen reuses, never
  restarts/extends. Worker elapsed cannot consume it.
- Effective bound `min(verifier deadline, live_stop_utc)` recorded in kv
  (`effective_deadline`) and result `verifier_window` (dispatch instant +
  effective); verifier wait bound = effective; escalation uses persisted esc.
- Inadequate time → truthful bounded owned-recovery with window evidence.
- Evidence: new T2 tests (window starts later than worker dispatch;
  dispatch instant + effective in evidence; expiry → bounded recovery;
  facts identical across reattach).

## T3 normal observation (#8/#9) — harness.py + case_entry.py
- Slice miss with the signed grant still open returns explicit
  `nonterminal-continuation` / `grant-open-continue` (owned continuation
  with resume facts), never terminal no-end failure. Zero latency rows for
  unconcluded executions. Genuine expiry (no remaining grant) keeps
  terminal `owned-failure`/`no-end`. Verifier wait runs to the persisted
  window bound (honest expiry → owned-recovery, unchanged).
- case_entry: reattach triggers accept the continuation outcome at the
  three normal-continuation sites; lost-completion first-miss accepts the
  honest continuation; `_grant_remaining_s` now derives from ledger
  receipt time (max `receipt_at_utc`), host-UTC fallback only when no
  ledger time exists (documented, never extends).
- Evidence: new T3 tests (direct CLI >8s work → continuation → reattach
  commits with no resend; genuine 1s-grant expiry stays terminal no-end);
  wrapper suites (observer/case/host) exercise continuation end-to-end.

## T4 honest metrics (#4) — harness.py
- Continuation path writes no row (one execution → rows only on conclusion).
- `_write_latency` empty-signal row is now `incomplete-unmeasured`, never
  `no-end-failure`; `check_latency` rejects fabricated `no-end-failure`
  rows with `E_BAD_SAMPLE`; missing onset → `unmeasurable-incomplete`.
- Evidence: new T4 tests (2 rows for one worker+verifier execution incl.
  across reattach; synthetic row → E_BAD_SAMPLE; missing onset →
  unmeasurable-incomplete, never zero).

## Reconciled superseded assertions (old evidence retained, replacements
specified; no blanket deletion)
- `test_r3_lifetimes.py` L152/L224: slice-miss `no-end` → 
  `nonterminal-continuation`/`grant-open-continue` (grant was open; old
  terminal verdict was the superseded behavior).
- `test_r3_lifetimes.py` L149/L307 + `test_amendment2_reconcile.py` L194/L214:
  plans gain explicit small `verify_window_s` (25/20s); the verifier wait
  is now bounded by the persisted window, not the t0-based escalation.
- `test_amendment2_reconcile.py` L196/L215/L236/L265: first-run `no-end` →
  `grant-open-continue`; conflict/query owned-failures unchanged (genuine).
- `test_amendment2_timer.py`: manifest gains `execution_id`; stale action →
  `E_ACTION_MISMATCH` owned failure (was silent no-op).
- `test_observer_lifetime.py` R8-parent old-fails test retained unchanged
  (immutable-parent evidence).
- `test_case_execution.py` lost-completion: first miss now the honest
  continuation (handled in case_entry, same recovery assertions).

## Out of scope (untouched)
Late-recorded-work recognition, shadow-time action reconciliation,
lost/queued live controls; no `occurred_at` invention; ingress
recorded-time untouched. Live remains held.

## Repair-1 (callback identity guard; harness.py only)
- `timer_callback`: absent/null/empty/malformed `exec-current` now rejects
  `E_NO_EXECUTION_AUTHORITY`; `SUPERSEDED->` marker rejects
  `E_SUPERSEDED_ACTION`. Guard never recovers authority from argv and never
  creates registration. Old fail-open (comparison skipped when None) closed.
- Tests: new `test_T1R_absent_execution_authority_rejects_no_effects_
  reopen_agrees` (due action, missing fact NOT pre-registered; empty/
  malformed/superseded controls; genuine registered execution still
  interrupts once + dedup); timer + T1-two-qid fixtures now register
  execution authority.
