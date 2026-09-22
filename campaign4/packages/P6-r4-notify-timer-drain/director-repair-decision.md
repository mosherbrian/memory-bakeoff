# Existing O repair released; Stage C held

Tern, 2026-09-22. Candidate FAIL932f548f81c354042c8d3ef98dc1d1aae5bb882a0dd8872e562b90466f9e1e0d
confirmed. Initial bytes/verdict preserved under
campaign4/p6r4-attempt-history/initial/archive-manifest.json before edits.
Host transport emits sent/queued/ambiguous/failed; settlement requires delivered,
so production intent remains pending and rollback blocks. This is one bounded
correlation/settlement defect inside O, not a new question.

Authorize existing sole <=10m worker repair, then remaining <=15m independent
candidate recheck. No new grant; historical245worker/205verifier unchanged.
This is narrower than the prior four-family repair. If it cannot complete
within the allowance, report incomplete; running tests alone do not extend it.
Live witness15/cairnfixture15 remain HELD. Preserve candidate-review.md and write
candidate-review-repair.md for the recheck.

Required correction: settle the intent using valid production transport receipt
plus authoritative evidence that the intended verifier action/execution actually
started or produced its bound outcome. Match package/revision/action/execution/
message/destination; reject malformed receipt, wrong seat, unrelated or stale
execution, reused/colliding message identity, missing proof and conflict. Preserve
receipt history. Initial queued alone is not proof of execution, but matching
later runtime evidence may resolve it. Do not globally relabel sent/queued as
completed/delivered; retain the distinction between transport ack and outcome.

Current _ledger_evidence_for accepts any matching flight (even other package)
or any terminal disposition in qid. Neither alone proves this verifier ran.
Replace that loose evidence test as part of O. Terminal state must not clear an
unrelated pending intent. A flight is intent, not runtime delivery. Keep ambiguous
cases pending and rollback BLOCKED until sufficient bound evidence exists.
Settlement and pending-clear atomic/durable; reopen/crash before and after ack
must not replay a delivered dispatch. Message counters restarting at1 cannot
overwrite prior receipt identity. No blind retries, no guard deletion.

Evidence: independently reproduce initial terminal-rest+pending+rollbackFAIL;
exact repaired CLI with injected production runner and two real-format runtime
sources -> matched verifier receipt -> terminal -> new process rollback succeeds,
zero unresolved delivered intents and no second send. Negative cases above stay
pending/BLOCKED; crash boundaries reconcile the same identity. Test both genuine
started and initially-queued then proved-started paths. Retain165+59 semantics.
Do not manufacture fake delivered state to make production settlement pass.

Corvid must execute the EXACT shipped setup/run/check/cleanup sequence under
injected OS boundaries, including systemctl query/cancel of the mapped unit;
prior T review did not run cleanup. Existing N private-file notification evidence
retained; no live seats/services permitted. Gate remains N/T/O plus inherited
C1-C12. Bind source and plan, report all unmet requirements as FAIL/incomplete.

Cairn: compare archive hashes; confirm previous attempt ended; trusted start/
deadline before one acknowledged repair dispatch, relative timer. Bound output
before verifier. Missing wake: session/hash reconciliation; genuine expiry stops
work, BLOCKED+wake Tern. No reset, automatic second repair or live release.
