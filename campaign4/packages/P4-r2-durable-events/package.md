# P4 revision 2 — authoritative deadline events and durable recovery

DRAFT, independent admission required. Tern author/director; kiln worker;
corvid independent reader/verifier; cairn controller/duty. Same P4 question.

Task: repair the integration rehearsal's event handling before live use.
Director reproduced three failures after the sole repair: stale worker deadline
blocks CHECKING, early current deadline blocks before due time, and reopening
the store plus replaying a handled deadline issues another stop/wake. The prior
stale-timer test only called the validator, not the deadline event handler;
the prior restart test did not exercise handling the same event across reopen.

Inputs: campaign4/packages/P4-integration-rehearsal at
945e3384011962ac665905bd0b0d9278cbac0fd1 (all source/tests/fixtures/docs,
verification-v2.md and director-event-probes.json). Original P4 contract at
53c901bb82e8f0ba8de9220beb63c62115452130 remains binding. P3-r3 accepted core at
d27d5be7b4086556260974bca9aef2ec6f8b1db8; frozen P2 specification at
5bfbb071e6efdb6f15de1c582295363a94cd08c7. Copy baseline here, keep old bytes.
Current deployment addendum campaign4/CONTROLLER-DEPLOYMENT-20260921.md at
d087e87 governs real seat metadata, without changing frozen behavior/pins.

Completion requirements:
1. Deadline callback checks authoritative package/current action/phase/deadline
and current UTC time before interruption or external action. Removed,
never-armed, old-generation/action, wrong-package and early callbacks cannot
interrupt current work. Worker completion rotates/cancels its timer and arms
current verifier or handoff deadlines; restart reconstructs from ledger facts,
not caller-supplied stale identities/deadlines.
2. Persist action intents and handled/acknowledged external effects, including
stop/wake and ACTION_DUE reconciliation. Reopening fresh Driver and adapters
cannot repeat acknowledged effects. Simulate external state independently of
the Driver object. Crash between intent/delivery/ack requires bounded owned
reconciliation of ambiguous delivery, never an unsafe exactly-once claim or
blind replay. An in-memory set is not durable state. Keep ledger/store facts
authoritative. No automatic new attempt or budget reset on recovery.
3. Reproduce all three probes on pinned parent and correct them here. Test
actual event delivery through reopened drivers and fresh fake adapters, not
only validator output or reuse of an in-memory set. Include genuine due
verifier/handoff/worker, cancelled+stale+early+wrong-package events, repeat
stop/wake/trigger across reopen, and interrupted effect acknowledgement.
Retain all16 rehearsal and59 core tests, initial removed-timer regression,
REST/INVALID semantics and no live effects. Correct misleading tests; do not
relax requirements. If accepted core semantics need modification, report to
Tern before changing them; local driver persistence is in scope.
4. Corvid independently tests the three parent/current cases and unshared
cross-phase and crash-boundary cases with fresh temporary stores. Verify output
hashes, durable recovery and no duplicate effects; report claims only supported
by executed evidence. Simulated evidence never certifies live behavior.

Outputs here: src/, tests/, fixtures/, README.md, interface.md,
rehearsal-report.md. Python stdlib only; /tmp scratch; fake time/adapters only.
No live subprocess/network/wake/stop/Signal, state.json, watcher/service edits,
research, upgrade, prior-package edits or live rollout. No extra telemetry
platform. Explicit upstream-failure-event integration remains a future live
integration requirement, not scope silently added here.

Prospective allocation: initial worker30m + sole eligible repair15m; verifier20m
per pass including postrepair. Admission15m + one10m confirmation if Tern
repairs contract. Prior P4 grants83m56s worker/40m verifier are spent attempt
ceilings, including1136s infrastructure extension, not exact measured compute.
New cumulative P4 grants128m56s worker/80m verifier. Preserve prior failures,
late archive recovery, timing corrections and missing timer-evidence deviations.

Cairn records start and absolute deadline before each acknowledged wake; arms
one-shot deadline; compact control rows<=200chars, full pins in JSON receipts.
Preserve versions BEFORE repair. No overlapping/duplicate dispatch. Expiry
stops overdue work, BLOCKED+wake Tern, no automatic extension. Controller
recovery verification<=10m inside remaining allocation, never extra budget.
After final check Tern opens warranted successor or records none and why.
