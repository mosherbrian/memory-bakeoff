# R14 repair 1 — absent execution authority fails closed

Tern; 2026-09-23T00:12:26.256188+00:00. Acceptance WITHHELD. Review
84b75ed1dbf624baa5b896e6be8f79910a6782c38edacbed530f274a6e53162d
is preserved as bounded PASS, not promoted to unconditional acceptance.
Director inspected harness.timer_callback: if current_exec is None the comparison
is skipped and on_deadline executes. T1 requires persisted authority, not callback
self-assertion. Normal registration order does not justify fail-open on missing
facts. This is completion of T1, no new architectural requirement or live permission.

Prospective ONE kiln<=15m repair + ONE corvid<=40m verification. Cumulative P6
candidate1185worker/935verifier ->1200/975. No automatic second repair. Old results,
infra cutoff and original deadlines remain recorded without retroactive changes.

Before dispatch cairn pins the commit containing current candidate/review and this
decision, retires finished timers and confirms runtime activation/no active writer.
Allowed production edit ONLY local candidate/src/r3harness/harness.py callback
identity guard; tests/docs/acyclic manifests and revision descriptors may follow.
Core/adapter/case-entry production frozen. Require nonempty valid persisted current
execution identity and equality to supplied identity before on_deadline or effects.
Missing/null/empty/malformed authoritative identity must deterministically reject;
never recover authority from callback argv alone or create registration on callback.
Keep distinct errors where useful; no public error-contract weakening needed.

Tests: reproduce old fail-open on pinned bytes with an otherwise valid due current
action but absent exec-current. Exact CLI on repaired candidate rejects with no
stop/wake, no deadline-state or ledger/KV mutation; reopen agrees. Include empty/
malformed identity and wrong identity controls, genuine registered due execution
still interrupts once, early/stale callbacks remain safe, repeat dedup retained.
Do not make tests pass by pre-registering the missing fact in the failure fixture.
Any need outside the guard/specified scope returns Tern first.

Worker runs focused checks then freezes NEW claim/manifest. Corvid independently
reproduces old-fails/new-rejects and unshared missing-fact variant, verifies authorized
diff and unchanged accepted core, then full existing69 composed +retained83+59 and
new regressions on actual final modules. Counts may rise with explained new tests,
never skip/delete inherited assertions. Accurate descriptors including identical
flags, no self-hash; all manifest entries match. Record commands/rc/module hashes.
Failure/timeout/unrun returns Tern with preserved evidence, no retry-until-green.

Explicit release now on preserved base; no new admission round for this narrow
existing-T1 correction. Cairn host-read start/deadline and one-shot timers, wake
exact profile/session; EVERY dispatch and receipt includes executable completion
command with actual action and absolute claim/verdict path per5fefb0f. New review
candidate-review-repair-1.md. No live/preparation/adoption. PASS returns director
for acceptance and warranted next package; not an idle terminal boundary.
