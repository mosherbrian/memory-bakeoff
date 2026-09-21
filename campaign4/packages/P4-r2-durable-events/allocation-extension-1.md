# Prospective allocation extension 1 — duplicate-only cleanup

Tern decision, 2026-09-21. Initial and sole repair are spent; the FAIL remains.
Independent AST inspection confirms19 identical _maybe_crash definitions,
18 cancel_deadline,18 is_cancelled in944-line driver.py, hash b285bc7f... .
Behavioural D1/D2 verification passed; duplication is a correctable artifact
integrity defect. Rejected repair + FAIL preserved before cleanup in
campaign4/p4r2-attempt-history/repair-rejected/ with full16-file manifest.

Explicit new grant: kiln one cleanup <=5 minutes; corvid one independent
post-cleanup verification <=5 minutes. This is additional allocation, not reuse
of spent repair or controller-recovery allowance. P4 cumulative worker ceiling
becomes133m56s; verifier85m. Historical grants/failures/actual use stay distinct.
No second cleanup or further execution automatic.

Worker may change ONLY src/driver.py: retain one copy of each byte-identical
method (preserve effective last-definition semantics), remove duplicate actor
mapping comments. No other refactor, formatting sweep, logic/test/core change.
Record cleanup rationale and before/after hashes in a separate cleanup receipt
(evidence, not another product output). Do not iterate edits or regenerate file.

Corvid: independently check effective AST equivalence to rejected repair
(collapse class methods by Python last-definition semantics), unique method
names, only redundant definitions/comments removed, all other15 worker outputs
byte-identical. Run36 local+59 core tests; full manifest, exact commands/results.
Write verification-cleanup.md; do not overwrite prior verdicts. No live effects.

Cairn records start/deadline BEFORE each acknowledged wake, arms one-shot timers,
preserves receipt hashes and uses compact event rows. No overlapping attempt.
On timeout stop overdue work, BLOCKED+wake Tern; no fresh clock or extra grant.
Tern accepts or disposes at boundary. Clock-authority successor requirement
remains pending and must precede live adoption. Current cleanup does not add it.
