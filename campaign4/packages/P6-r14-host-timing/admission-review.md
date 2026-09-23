# P6-r14-host-timing — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r14-admission-1`, start `23:17Z`, deadline `23:37Z`
- **Brief:** `P6-r14-host-timing/package.md` sha256
  `4bf7e38df5ce1d1b43de0abac3bd1d61cd8d0b300c91c2dd7f34127ff2253078`
- **Director release:** `director-release.txt` + `director-release-receipt.json`
- **Scope:** read-only admission + pinned executable checklist. No source edit.

## Verdict

**ACCEPTED (bounded).** The contract is the already-recorded host-timing
successor to accepted R13, all pins resolve, the authorized surface
(`harness.py`, `host_adapter.py`, `case_entry.py`) is sufficient, and the T1–T4
outcomes are executable with injected host boundaries. Four bounded obligations
are pinned: **(a)** establish executable old-fails for T2/T3 before fitting
repairs (both were source-only in R12); **(b)** identify and *retain* old
assertions that depend on the superseded 8 s terminal-failure / false-metrics
behavior and specify replacements — no blanket deletion; **(c)** run the full
composed 59 + retained 83 + 59 on the actual new modules with paths/hashes and
resolved module-origin checks; **(d)** accurate acyclic manifests and an R3
descriptor with correct `identical` flags, no self-hash.

## Pin resolution

- Parent R13 candidate commit `5410332b1d61…`; outer manifest file sha256
  `e307fa3de458…` = `candidate/manifest.json` on disk; review `7f91da44…` =
  `candidate-review-completion-3.md`. R13 `acceptance.json` present
  (`ACCEPTED_SCOPED_CANDIDATE`, `source_commit 5410332b…`, manifest
  `e307fa3d…`, verification `7f91da44…`) — co-pinned.
- R13 `R3_REVISION.json` `81789c98…` (descriptor corrected, `identical` flags
  match copy-vs-parent equality).
- Inputs: `CODE-REVIEW-DISPOSITION-20260922.md @abb0f90`;
  `code-review-regressions/matrix.md @bccd688`; `CODE-REVIEW @197be51` (findings
  1/3/4/8/9). Governing rulings `4be99bf` (recovery), `650830c` (clock),
  `84f094e` (action identity), `883107e` (turn-end), `f7b0cce` (shadow-time),
  `5fefb0f` (executable completion commands) — all resolve.

## Pinned checklist (executable; full detail in `admission-checklist.md`)

**T1 timer authority (#1).** Every create/callback carries the ledger-selected
DB, qid, action, execution; bound to the persisted action, not callback
self-assertion; omitted/mismatched identity fails closed. Exact-CLI callback
tests with two qids in one DB, foreign DB, wrong execution, stale action, early
and genuine overdue; due current action interrupts once, owner wakes once,
others untouched; reopen/repeat preserves dedupe/cancellation. Injected host
boundaries only.

**T2 verifier grant (#3).** `verify_window_s` starts at the contract-authorized
verifier dispatch/handoff and is persisted once; worker elapsed cannot consume
it; reattach/reopen cannot restart/extend it; `escalation_window_s` is not a
substitute; global `live_stop_utc` remains the stricter cap; inadequate time →
truthful bounded result with reason. Tests: slow worker beyond the old escalation
window, full separate verifier window, expiry, restart. Record chosen dispatch
instant and effective `min(verifier deadline, outer stop)`.

**T3 normal observation (#8/#9).** Direct `run-fixture` (not only the case
wrapper) observes valid work to authorized end or returns an explicit
NONTERMINAL owned continuation; an 8 s slice cannot terminate authorized work as
`no-end`; notification-backed waiting + bounded reconnect/attach with original
identity/deadlines and one send; trusted/injected time for continuation and outer
stop, not `datetime.now`. Tests: direct CLI and wrapper beyond 8 s, real expiry
`no-end`, outer-stop-before-deadline, clock discontinuity, restart-during-wait,
continuation with no resend. Any nonterminal-yield adoption must show executable
owned continuation, not a hopeful flag.

**T4 honest metrics (#4).** Normal slice/continuation/success are ONE normal
execution with no fabricated `no-end-failure` row; real failed/expired history
preserved; tests inspect actual latency records/counts across repeat/restart;
synthetic controls separately labelled and excluded; missing onset/timing →
INCOMPLETE.

**Gate.** Existing composed 59 + retained 83 + 59 run against the actual new
modules with recorded paths/hashes and resolved module-origin checks; new
exact-CLI tests exercise production branches with injected collaborators, not
import-only stubs. R13 behavioral protections (authenticated rejection, causal
routing, A–E core) retained.

## Obligation (b) — superseded assertions to reconcile (not delete)

The following existing assertions may depend on the explicitly superseded 8 s
terminal-failure / false-metrics behavior; worker must classify each, **retain
the old failure evidence**, and specify the replacement before editing. Any
genuine semantic conflict returns Tern; no blanket deletion/weakening:

- `tests/test_r3_lifetimes.py`: `no-end`/`verifier-no-end` from the short
  `wait_s` slice while the grant is open (≈ lines 152, 160, 224, 296, 315).
- `tests/test_amendment2_reconcile.py`: `no-end`/`owned-failure` rows
  (≈ lines 196, 215, 236, 253, 265, 270) — classify slice-induced vs
  genuine-expiry; expiry-legitimate assertions stay.
- `tests/test_observer_lifetime.py`: the R8 **parent** old-fails test
  (≈ lines 198-208) is immutable-parent evidence — retain unchanged.
- No existing test was found asserting a synthetic `no-end-failure` row by name;
  worker must add real latency-row/count assertions for T4.

## Scope and exclusions

Changes only in local `src/r3harness/harness.py`, `host_adapter.py`,
`src/case_entry.py` + tests/plans/docs/mechanical manifests/descriptors; all
accepted core Python (`driver/ingress/store/lifecycle/validator/turn_handoff`)
byte-identical; any need to alter them returns Tern first. No new deps, polling
supervision, role/config migration, extraction, Go port, or old-package edits.
Late-recorded-work recognition, shadow-time retried/cancelled-action semantics,
and the lost/queued live controls remain **out of scope**; no unproved
`occurred_at`, no weakening of ingress recorded-time. Live remains held.

## Bounds

Reader 20 m (this) separate; ONE worker ≤60 m and ONE independent verifier ≤40 m;
no automatic repair. Ceilings `1125worker/895verifier` → `1185/935`. Full suite is
14–24 m — never fit into a 120 s probe, never claim unrun as pass. Honest
FAIL/INCOMPLETE returns Tern; timers never extend for running tests. Worker is
conditionally released only on unchanged ACCEPTED contract, pinned checklist,
pinned R13 acceptance/source, and no active prior writer. Every dispatch/receipt
carries an executable completion command (explicit campaign4, absolute wake path,
validated session id, action, absolute claim/verdict path).

## Effect

Admission **ACCEPTED (bounded)** with obligations (a)–(d). No implementation or
release conferred by this review. Returned to cairn/Tern.
