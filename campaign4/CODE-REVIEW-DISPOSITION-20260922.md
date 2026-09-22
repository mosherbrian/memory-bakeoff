# Director disposition of the ten code-review findings

Tern; 2026-09-22T19:51:38.233043+00:00.
Intake CODE-REVIEW-20260922.md atc464709. Read all ten. Director inspected reported
store transaction, atomic-key parser, DECIDE, callback argv and verifier-clock paths;
the described source issues are present. Runtime impact still needs failing tests.
This is a scoped diff review, not assurance about unreviewed code. No fixes claimed.

## Immediate boundary and ownership

HOLD further live preparation/task releases, adoption and retirement until the
applicable confirmed blockers are fixed and independently verified. This is Tern's
ordinary evidence gate, not campaign-wide pause or a request for Brian approval.
Brian's durable live authority remains intact. Active r11 entrypoint-only routing
repair/verification may finish under its existing grant; it does not touch the
reviewed frozen core/harness and its PASS cannot override this gate. No parallel
writer modifies r11 or its parent. Cairn preserves cleanup duty and returns its
verdict normally. Review attribution and every historical result remain intact.

## Order and target semantics

First, durable-record correctness (#2,#5,#6,#7,#10), in one narrowly bounded core
successor after reproduction. SQLite rollback must also roll back any in-memory
seen/cache projection; retry in SAME store must equal reopen, exactly once. Atomic
forms must either apply every declared operation or reject before mutation: no
ignored decide/hold or grant_ref. A distinct second DECIDE cannot overwrite a closed
disposition; exact event replay retains idempotence. If later amendment of a decision
is ever needed it requires a separately specified explicit event, not overwrite.
Time comparisons must use validated UTC instants including offsets/fractions, not
lexicographic strings. Authentication/ingress checks cannot be bypassed to prove a
public path; separately show any internal invariant and its public reachability.

Second, connected host timing (#1,#3,#8,#9), once core revision is bound into a
candidate adapter. Callback must carry authoritative qid, action, execution and
exact DB, not a default unrelated package. Test same DB with TWO qids as well as
foreign DB; prove due owned action changes, early/stale/other package unchanged.
Verifier's execution grant starts at its authorized verifier dispatch/handoff and
is durably recorded once; worker runtime does not consume it. Reopen preserves that
absolute verifier deadline, not reset. Explicit global/outer stop still caps both;
insufficient remaining global time yields truthful bounded disposition, not invented
extra time. Resolve escalation vs verifier grants explicitly in the repair contract.

#8 ruling: normal run-fixture is a supported production path. Its short observation
slice can be an internal wait quantum or a resumable NONTERMINAL yield, but cannot
be a terminal owned-failure while authorized normal work remains. Either maintain
notification-driven observation or preserve bounded continuation identity/ownership;
no dependence on one particular case wrapper secretly fixing the semantics. Actual
lost-signal/delay drills require declared applied control and independent evidence.
Never manufacture a production failure merely to keep an old fault test passing.
#9 must respect trusted clock and stricter outer stop before reattach; preserve
causal reasons and original deadlines. Do not replace8 with a larger magic number.

Third, measurement correctness (#4), integrated with the observation change rather
than a dashboard patch. A normal slice followed by success is one normal execution,
not a synthetic failure plus success. Deliberate negative controls live in explicitly
labelled test evidence outside production denominators. Ledger records attempts,
observations and terminal dispositions without overwriting real failed history.
Prove this with actual latency-file rows/counts, not just final timecheck verdict.

## Effect on prior claims

R9 positive handoff still proves real1+1 delivery and a verified completion, not
correct overdue backstop enforcement. Its successful no-duplicate timer fire did
NOT prove the callback addressed P6C. Its review's description of the no-end row as
an intentional negative control is now DISPUTED by finding4: until reproduced,
do not use that row to certify honest production failure counts or zero-latency
recovery. Preserve review/acceptance unchanged and link this qualification.
R11 candidate passes, if any, remain scoped and not a release of these findings.

## Next authorized work: independent regression reproduction

ONE corvid<=40m read-only diagnostic pass, AFTER current r11 verification/review
finishes (no queueing over an active pass). New action C4-review-regressions-1.
Separate review allocation40m, not worker/core repair; P6 implementation ceilings
remain1025worker/765verifier. No implementation, source mutation, live action or
additional researcher/agent. Cairn dispatches at that boundary without another
Tern permission; explicit conditional release in this ruling is sufficient.

Create campaign4/code-review-regressions/ with a short executable failing case per
finding on pinned originals (P5-r2 80092f9 and P6-r9 f1d7c86). Record actual source
hashes and whether each byte appears in the current r11 local copy; do not assume
fixing the original source automatically changes copied deployment code. Start with
2,5,6,7,10, then1,3,8,9,4. Reports may group a shared causal reproduction but every
finding receives REPRODUCED / NOT REPRODUCED / UNTESTED with command, assertion,
actual output and exact pin. Old code must actually violate the target behavior;
not 'test passed because function exists'. Include same-store retry/reopen (#2),
post-state+row counts (#5/#6/#7), equivalent offset instants (#10), actual callback
argv on same-DB wrong-qid (#1), slow-worker verifier budget (#3), and first-slice
normal versus intentional-fault metrics (#8/#4). Intercept host effects only, no
real timers/sockets/services, no secrets or main-seat actions. No cherry-picked
success that changes the reviewed precondition. Preserve logs and source bytes.
If40m insufficient, report the remaining matrix honestly rather than claiming all
ten confirmed. Return one bounded report to Tern; corvid cannot certify its own
future fixes and writes no fixes in this pass. Admission of each later repair
contract remains independent. Tern authors the bounded implementation successor
from demonstrated failures and the ordering above, not blanket permission to edit.

Navigation: CODE-MAP.md records reviewed-but-unfixed blockers. Separate harness
repository and multi-project successor remain planned after live-path work; no
migration of in-flight pins as a remedy for correctness defects.
