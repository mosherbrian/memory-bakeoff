# P6-r14 — connected host timing and truthful observation

Tern author; corvid independent reader/verifier; kiln worker; cairn duty.
DRAFT for admission. No live/preparation/adoption/retirement. Parent R13 candidate
5410332b1d614823ca29d343b051ab471c4bacb3 at ../P6-r13-core-record-integrity/candidate/;
outer manifest e307fa3de458e5926a40a4f18f310d7b014e770219e1fb05f468f7a9982cb322,
review 7f91da44e04d81a6233cad69bd9f468dcfdfc4f707973834463e65a2f3beffc4.
R13 acceptance.json is co-pinned with this contract. Additional inputs: repo-root
campaign4/CODE-REVIEW-DISPOSITION-20260922.md @abb0f90;
campaign4/code-review-regressions/matrix.md @bccd688; findings1/3/4/8/9 in
campaign4/CODE-REVIEW-20260922.md @197be51 (resolve historical blob, do not infer).
Recovery4be99bf, clock650830c, action84f094e, turn-end883107e, shadow-time f7b0cce,
notification5fefb0f remain governing rulings. Corvid resolves pins before admission.

## Scope and required outcomes
Copy the accepted R13 candidate locally. Production changes allowed only local
src/r3harness/harness.py, host_adapter.py, and src/case_entry.py, plus tests,
plans/docs and mechanical manifests/descriptors. All accepted core Python including
driver/ingress/store/lifecycle/validator/turn_handoff remains byte-identical. Return
any demonstrated need to alter these before doing so. No new dependencies, polling
supervision, role/config migration, extraction, Go port, or old-package edits.

T1 timer authority (#1): every timer creation/callback carries the ledger-selected
DB, qid, action and execution identity. No silent P6F default for P6C; omitted or
mismatched identity fails closed. Bind to actual persisted action, not merely callback
self-assertion. Callback exact CLI tested with two qids in one DB, foreign DB,
wrong execution, stale action, early and genuine overdue callbacks. Due current
action interrupts once, intended owner wakes once; others untouched. Reopen/repeat
preserves dedupe and declared cancellation behavior. Use injected host boundaries,
no real systemd/seat operations. Existing adapter receipt/ambiguous rules retained.

T2 verifier grant (#3): verify_window_s bounds verification, beginning at its
contract-authorized dispatch/handoff, persisted once. Worker elapsed time cannot
consume it. Reattach/reopen cannot restart or extend it. escalation_window_s is
recovery/escalation allowance, not a substitute verification budget. Receipt/ack
uncertainty retains owned bounded recovery; no free grant while queued. Preserve
explicit global live_stop_utc as stricter cap; inadequate time => truthful bounded
result with reason, not extra budget. Test slow worker beyond old escalation window,
full separate verifier window, expiry and restart. Record chosen dispatch instant
and actual effective min(verifier deadline, outer stop) in durable evidence.

T3 normal observation (#8/#9): direct run-fixture, not just case wrapper, must
observe valid normal work until authorized end or return explicit NONTERMINAL
owned continuation. An eight-second slice cannot terminate authorized work as
no-end failure. Keep notification-backed waiting and bounded reconnect/reattach,
original identity/deadlines and one send. Use trusted/injected time consistently
when deciding continuation and outer stop, not an unrelated datetime.now shortcut.
Test direct exact CLI and case wrapper with work completing beyond eight seconds,
no-end through real expiry, outer-stop-before-deadline, clock discontinuity,
restart during waiting and successful continuation with no resend. If adopting
nonterminal yield, demonstrate executable owned continuation, not a hopeful flag.
Explicit fault drills require applied control plus independent causal evidence.

T4 honest metrics (#4): normal observation slice/continuation/success is ONE
normal execution, no fabricated no-end-failure row. Real failed/expired executions
remain in history; no truncation or retrospective rewrite. Tests inspect actual
latency records and counts across repeat/restart, not only final rc. Synthetic
negative controls separately labelled and excluded from production denominators.
Missing onset/timing yields INCOMPLETE, not manufactured zero-latency recovery.

Late-recorded work recognition, retried/cancelled-action reconciliation from the
shadow-time ruling remain separately scoped: do not weaken ingress recorded-time
or introduce unproved occurred_at to pass these tests. Lost/queued live controls
remain outstanding. This package does not authorize all remaining recovery work.

## Admission, checks and deliverables
Corvid <=20m independent admission and executable acceptance checklist BEFORE
worker dispatch. Reproduce supplied failures on immutable parent where possible;
#3/#9 were source-only in R12, so establish executable old-fails for target behavior
before fitting repairs. Distinguish test fixture limitation from public behavior.
If any requirement cannot be satisfied within allowed modules, return scope defect.
Independent unshared mutation per T family required at final review. Preserve all
R13 behavioral protections, authenticated rejection and causal routing errors.

Deliver candidate/, changes.md mapping T1-T4 to exact source changes/evidence,
accurate acyclic manifests and R3 descriptor (correct identical flags), NEW claim,
and commands/logs. All existing 59 composed tests + retained83+59 must run against
new actual composed modules with paths/hashes recorded. If an old assertion depends
on the explicitly superseded eight-second terminal-failure/false-metrics behavior,
corvid must identify it in the pre-worker checklist, retain old failure evidence,
and specify replacement before edit. No blanket test deletion/weakening; any newly
found conflict returns Tern. New exact-CLI tests must exercise production branches
with injected collaborators, not import-only stubs. Retained core byte comparison
and import check block acceptance. No self-hash or stale provenance descriptors.

## Prospective bounds and release
New ONE worker <=60m and ONE independent verifier <=40m; no automatic repair.
Prior cumulative1125/895 ->1185 worker/935 verifier ceiling minutes. Reader20m is
separate admission allocation. Full suite recently took14-24m; do not fit it into
a120s probe or claim unrun as pass. Honest INCOMPLETE/FAIL returns Tern. Timers never
extend because tests are running. Preserve all spent history and cancelled grants.

Tern releases admission now through cairn. Worker is conditionally released ONLY
when corvid ACCEPTS unchanged contract, checklist/review are pinned, R13 acceptance
and exact source are pinned, and no prior writer is active. Cairn records admission
and sends exactly once with host-read clocks/one-shot timers and bound identity.
Any proposed scope/test-semantic amendment returns Tern before worker release.

Every dispatch/receipt includes an actual executable completion command per
COMPLETION-NOTIFICATION-RULING (explicit campaign4, wake absolute path, validated
exact destination session ID, actual action and absolute claim/verdict path).
No reliance on prior context, no inline socket sender, no ledger edits. Notification
failure is owned reconciliation, not rerunning completed work. PASS returns Tern;
live remains held until separately reviewed/released. At next boundary Tern opens
warranted recovery work or records why none is warranted.
