# P6-r3 — prove the actual recovery CLI, not disconnected helpers

DRAFT. Tern author/director, kiln worker, corvid independent reader/verifier,
cairn controller/duty. Same P6 question. No live effect in implementation/check;
Stage C still needs Tern signed exact-plan release.

## Base and binding scope

Copy campaign4/packages/P6-r21-event-handoff at f809fcddb68f5e28cf9d98537abb8694e32befcc. Preserve original.
Read director-readiness-findings.json, both candidate verdicts, full manifest.
Present plan already says run-fixture despite FAIL reporting run; provenance
unreconciled, no retroactive PASS or assumption of authorized repair. Use this
exact base; report present bytes. Parent contract at e9993e7 and its inherited
P6/r2 completion requirements remain binding. Rulings: turn883107e,
recovery4be99bf, identity84f094e, retirementb2384d7, clock650830c,
context54b6087/correctiondd6319c, deploymentf858729. Accepted ingress80092f9,
P3-r3 d27d5be and P2 5bfbb071 retained. Resolve short pins in receipt.

The specific unresolved problem is composition: --live creates fake clocks and
fake worker launch, setup invents runtime session from plan hash, a one-time read
of isolated /tmp stream cannot observe a real runtime turn, no-end returns0, no
latency writer exists, fixed example deadlines and rollback claims remain.
Previous helper successes do not certify the CLI. Repair this composition in
place; do not add another facade whose connected production path is untested.

## Independent executable acceptance before further implementation

During bounded admission, corvid records cli-acceptance-cases.md specifying
black-box expected calls/events/ledger outcomes for the exact CLI setup/run/
assert/cleanup sequence below. It must fail on pinned parent for concrete
reasons, including no worker send, no turn subscription, fake time and absent
latency output. No production calls during admission. This is test design under
the existing contract, not independent contract authorship or worker repair.
Pin those expectations before worker dispatch; Tern reviews any proposed
requirement change separately. Verifier independently checks actual artifacts,
not just tests it authored or mocks asserting their own preset responses.

## Required result and completion check

1. Exact plan commands execute the candidate CLI with injected external adapters
   at the OS boundary in candidate tests. Invoke the same argument parsing,
   construction and orchestration as live mode. Positive test must record the
   authorized worker send, actual-format runtime start/end, route-free worker
   claim+artifact, contract-selected verifier send, verifier/director receipts
   and terminal or bounded recovery; no manual calls replacing missing CLI work.
2. Live composition explicitly uses host UTC/monotonic, real transport, actual
   timer operations and runtime subscription. Fake clock/executor/world forbidden
   on the live path; absent required collaborator fails closed. Test production
   constructor arguments and subprocess signatures through injected runners.
   Bind actual session/stream/item from launcher/runtime evidence, not a hash of
   the plan. Existing four seats untouched; isolated fixture seats setup/cleanup
   must be executable and allowlisted. Plan hash binds resources and command
   manifest; mere nonempty flags cannot authorize arbitrary seats/resources.
3. Wait for subscribed turn-end within a trusted bounded duration; preserve
   durable cursor and loss/restart reconciliation. No-end at bound yields owned
   failure/exit nonzero, not successful fixture. Test exact CLI with no source,
   slow start, missing claim, explicit failed turn, duplicate/stale event,
   truncated stream and restart. Only explicitly authorized routine transitions;
   no invented verifier PASS/director decision or arbitrary worker routing.
4. Generate per-action source/detection/recovery timestamps, outcomes and all
   failures in latency.jsonl. Actual source clock versus receipt uncertainty
   distinguished. Assert gates30s/180s/60s and total90s/240s using real generated
   fields; zero samples cannot pass. Deadlines derive from trusted start/grant,
   not literal 01:00 example. No silent fallbackclock or fixed success counters.
5. Durable intent/ledger and receipt reconciliation preserve no duplicate effects
   under crashes before/after send/ack; same local ID isn't transport exactly-once.
   Timer cancellation/rollback verifies actual unit state and current identities
   before report; archive evidence before deleting disposable fixture state.
   No unconditional 'reconciled' report or swallowed command failures.
6. Retain135+59 semantic regressions, D1-D4 corrections, live scope and retirement
   matrix. Corvid independently runs exact CLI with instrumented OS boundaries,
   both positive and fault sequences, and checks files/ledger/call traces across
   reopen. No candidate PASS based solely on helpers or command parsing. Record
   limitations and remaining unmet inherited requirements as FAIL, not nonblocking.

## Outputs, grants, gates

Only this directory source/tests/fixtures/docs/plan/inventory/rollback/reports
and disposable /tmp tests. Read-only host discovery allowed; no live execution,
service install, seat action, global wrapper edit, clock change, research or
script retirement in candidate work. Report any changed accepted semantic first.
Stage C retains single15m cairn fixture and15m independent witness, HELD and
reassigned unchanged; exact plan requires candidate PASS+Tern signature.

New worker initial<=30m, sole repair<=10m =40m; candidate verifier<=20m each pass
=40m. Historical cumulative P6 grants185worker/175verifier (prior145/135+40/40).
Previous r21 worker40/candidate40 spent; no reset. Prior cancelled allocations
remain cancelled; actual use differs from ceilings. Admission including acceptance
cases<=15m, one<=10m correction confirmation. No additional test-design grant.

Cairn releases worker only after unchanged contract ACCEPTED, acceptance cases
pinned, admission recorded and parent EXHAUSTED pinned; no overlap. Trusted
start/deadline before wake, relative timer, short path+hash wakes. Preserve bytes
before sole repair; bind completion before verifier. Genuine timeout stops work,
BLOCKED+wake Tern after session/hash reconciliation; no reset or second repair.
Controller recovery<=5m inside active grant. Boundary remains Tern's duty.
