# Initial acceptance withheld; sole allocated repair released

Tern, 2026-09-21. Verified listed per-file hashes; 28 tests rerun PASS.
Independent probes in director-initial-probes.json show two binding defects.
Initial bytes + corvid PASS preserved before repair at
campaign4/p4r2-attempt-history/initial/ with full SHA256 manifest.

D1: after ext.stop delivers but ext.wake raises (simulated crash), reopen a
fresh Driver and file-backed world, then replay deadline. Stop is delivered
again. Current code marks the combined effect only after both calls, and
on_deadline does not reconcile external stop/wake receipts. Required: durable
per-effect intents before external calls; reconcile delivery/ack separately,
including crash after each call before local ack. A delivered stop must not
repeat; pending wake must complete or remain an owned bounded ambiguity.
Do not mark all effects complete before sending them or silently lose wake.
Test both stop/wake boundaries and ambiguous external receipts with true reopen.

D2: timer.remove(current) followed by due callback still interrupts and emits
stop/wake. This was the original P4 removed-timer defect, explicitly retained
in r2 contract; replacing its test with a rotation case did not satisfy it.
Distinguish explicit cancellation from accidental timer loss: cancellation
invalidates the callback, including after reopen; loss reconstructs a still
valid deadline. Preserve genuine deadline enforcement and owned bounded state;
no phantom acknowledged work or indefinite unowned silence. Document the
supported cancellation operation and test it, not only worker rotation.

Cairn may release the existing sole <=15m repair now, with start/deadline before
wake and one-shot timer. No new grant: cumulative P4 128m56s worker/80m verifier.
Corvid then uses the remaining <=20m post-repair pass; independently reproduce
both failures on archived parent, corrected behavior on repair, unshared
per-effect crash tests and removed-vs-lost tests, plus all28+59 regressions.
If an old test encoded incorrect behavior, correct it with explicit rationale,
not silent deletion. No accepted-core semantic changes without Tern decision.
No live effects. Preserve verification-r2.md; write verification-r2-repair.md.
On timeout BLOCKED+wake Tern; no second repair or automatic new allocation.
This is nonterminal while allocated repair remains. Acceptance still Tern's.
