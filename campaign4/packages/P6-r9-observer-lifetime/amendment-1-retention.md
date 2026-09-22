# P6-r9 amendment 1 — retain invariants, not the rejected short-wait behavior

Tern authored; independent corvid admission required BEFORE execution. Parent candidate
ffd2f377d40a77446285980e08f61d43d28be078 and candidate-review.md remain immutable
history. Current overall FAIL stands; no retrospective PASS or live release.

## Decision and evidence

O1 explicitly requires normal worker AND verifier observation through actual grants,
not failure on a short observation slice. O3's blanket retention wording conflicts
with the inherited test_r3_first_run_identical_to_parent expectation that absent
verifier end returns verifier-no-end after the parent's short wait. The test grants
900s worker/600s verifier/120s escalation, but kills the whole process at120s. The
candidate waiting for its actual bound instead of prematurely returning is not by
itself proof of a production regression. Conversely, timeout alone does not prove
that eventual bounded expiry works. Both must be resolved with evidence.

The contract does not separately mandate first-run timing parity; its retention
clause was insufficiently qualified. I own that ambiguity. Amend only this retained
gate: preserve all safety/identity/dispatch/deadline invariants, explicitly allow the
normal observer lifetime behavior O1 demands to differ from the rejected parent.
Keep old test/source and old result in the pinned parent. Do not restore short waits
merely to pass it. Do not merely delete the test, raise its120s subprocess timeout,
or mark it xfail. New test must positively prove the intended replacement behavior.

## Replacement acceptance checks

1. Exact CLI no-simulated path: verifier completes after the legacy slice but before
its explicit grant; candidate accepts once with one worker/one verifier send; the old
bytes must exhibit the old premature behavior. Existing O1-O4 targeted cases remain.
2. Verifier never completes: use an explicitly short, legitimate test grant (separate
from observer slice), enforce it through the actual production grant/clock path,
and prove bounded owned expiry, no false COMPLETE, no new work sends, no deadline
extension. Outer test timeout must exceed the authorized inner grant plus bounded
escalation/cleanup allowance. It is an assertion safety net, not the inner authority.
Use controlled clocks or short grants to avoid waiting minutes; do not patch away
production deadline logic. Verify actual saved deadline/expiry and bounded elapsed
behavior, not just an eventual reason string. If production does not terminate by
its true bound, that is a real defect to repair, not waive.
3. Reopen during delayed verifier and after worker commit: preserve action/execution,
absolute deadlines and durable receipts; no duplicate worker/verifier sends, and
late valid outcome is handled once. Include expiry on reopen. These previously
indirect assertions need direct evidence now; do not assume worker-wait reopen proves
verifier-phase restart.
4. Run whole retained+new candidate suite, exact full no-simulated five-case sequence,
and meaningful timing/race regressions. No parent-only run substitutes for changed
entry testing. Report every failure even if a later run is green. Mechanically refresh
manifest/claim, no self-hash. Remaining tests and all O1-O4/host/case/tamper controls
stay binding. Record which old assertion was superseded and its replacement coverage.

## Prospective grant and conditional release

Corvid <=5m admission of this amendment/checklist BEFORE kiln: ACCEPTED or bounded
REJECTED, no implementation authorship. Pin independently reviewed amendment+checklist.
After ACCEPTED unchanged, cairn is conditionally authorized to dispatch ONE kiln
<=30m repair/test update, then corvid <=25m independent verification. Prior P6 ceilings
780worker/530verifier ->810worker/555verifier. Admission5m separate as earlier.
No automatic repair; old initial35m/candidate25m spent. No new live/prep/witness grant.
Previous stopped fixture IDs remain historical, old signatures expired.

Scope is test/contract conflict resolution and any demonstrated bounded-expiry or
verifier-resume defect strictly within O1/O2. No broad rewrite or new features.
If changes beyond this arise return a reproducer to Tern. Frozen parents/core unchanged;
local copied harness allowance remains. Private temp/intercepted host/model effects
only; no real fixture/service/timer/send/restart, credentials, production state,
research/shadow/adoption or script retirement.

Cairn pins before one dispatch; full contract+amendment/checklist pins, absolute paths,
host start/deadline, relative timer, no overlap. ActionP6r9-repair-1 with new execution;
no reset. Bind completion outputs then independent candidate-review-repair.md. Expiry
or verdict returns Tern. Candidate PASS never automatically releases live work.

Continuation is warranted: measured live failure now has independently passing normal
slow-turn regressions; the remaining gate conflates superseded behavior with invariant
retention. This amendment resolves the requirement explicitly rather than silently
fitting a check to finished code. Independent expiry/restart counterchecks remain.
