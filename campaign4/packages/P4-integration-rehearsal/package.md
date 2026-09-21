# P4 — bounded controller and watcher integration rehearsal

DRAFT; independent admission required. Author/director Tern under CHARTER.
Worker kiln; reader/verifier corvid; controller/duty cairn. Implementation.

## Task and decision

Demonstrate one harmless package through controller handoffs and supervision
using fake external adapters. Decide whether a separately authorized live
fixture is ready, and name any blocking gap. This is the Connect-stage rehearsal,
not a platform expansion or live rollout. P3 deterministic core is accepted;
this package must show its boundaries compose with execution and supervision.

## Pinned inputs

- campaign4/packages/P3-r3-authoritative-claims at
  d27d5be7b4086556260974bca9aef2ec6f8b1db8: core, 59 tests, fixtures,
  verification.md and director-preservation-manifest.json. Cairn additionally
  pins Tern acceptance.json before execution. Copy baseline locally if needed;
  never modify accepted source.
- Frozen P2 contract/transitions/ownership/boundary-schema at
  5bfbb071e6efdb6f15de1c582295363a94cd08c7 under
  campaign4/packages/P2-r2-boundary-amendment. Original P3 requirements retained.
- campaign4/packages/P1-inspect/capability-map.md at
  dd15764258317c125adc2cd193a44c57ad5dd6b4: shared-host trust limits;
  no assumption that a profile isolates tmux, tools or identity proof.
- inputs/campaign4-watch.observed.sh, copied read-only from host for this
  contract; SHA256 1feaf9945dce002a236cb1287447537f2c5abf90fd33f9ebbcb1a403dcda9601. Pin with contract commit.
  Reference only: DO NOT execute it. It still uses a provisional string-map
  schema; its state-fault pause branch bypasses DRY. No live state.json exists.
  The accepted versioned ledger-derived schema replaces that provisional input
  in the candidate rehearsal; document the reader change explicitly.

## Required behavior and completion evidence

1. An event-driven driver composes the accepted store/core/validator with fake
   launch/inspect/stop/wake/timer/notification interfaces. Defaults must be
   incapable of live effects, not merely guarded shell commands. External
   responses carry recorded action identity and delivery state; worker prose
   never supplies authoritative actor identity. No polling/model calls.
2. Run a harmless deterministic fixture from recorded admitted authorization
   through worker completion, separately attributed verification and a supplied
   director terminal disposition. Starts precede fake dispatch, immutable
   outputs/hashes precede completion, duplicate delivery cannot create attempts.
   Restart reconciles durable intent/ack with fake external state: ambiguous
   delivery holds for owned reconciliation, never blind redispatch.
3. Candidate supervision consumes authoritative ledger plus versioned snapshot.
   REST suppresses generic silence escalation, including historical successor
   chains ending in rest. INVALID cannot be masked by recent file activity or
   unrelated busy seats. ACTION_DUE is owned, durable and deduplicated across
   restart. ACTIVE uses the actual current action deadline; stale worker timers
   cannot expire a verifier. Missing/unreadable/stale snapshot or ledger failure
   must return an explicit owned fault, never silent success.
4. Rehearse timeout and lost-timer recovery: finite owned handling, one-shot
   deadlines reconstructed on restart, no duplicate stop/wake. Bounded human
   decision and blocked-verification resume preserve phase/attempt/allocation;
   verifier resume never reruns worker. Preserve legitimate rest after the last
   package; finishing must not automatically authorize another. Inject a
   missing boundary disposition to reproduce Tern's omission promptly.
5. Define a compact candidate adapter/reader interface and status report showing
   package, current owner/action/deadline, receipt, evidence and next permitted
   action. Explicitly distinguish simulated observations from real campaign
   history. Name duty cairn and escalation tern, with terminal pause proposal
   only as fake output. No Brian notification is sent by this rehearsal.
6. Corvid independently runs the end-to-end fixture and fault matrix in fresh
   temporary state, including crash-before-delivery, ambiguous delivery,
   crash-after-ack, repeated completion/deadline/trigger, removed timer, stale
   snapshot, legitimate rest, missing disposition and blocked verifier resume.
   Verify no live subprocess/network/service effects are possible through the
   tested adapters, and all 59 core tests still pass. Report exact commands,
   hashes, expected/observed results, limitations and readiness conclusion.
   This package cannot certify live behavior from simulated evidence.

## Outputs and permissions

Within this directory: src/, tests/, fixtures/, README.md, rehearsal-report.md,
interface.md; /tmp disposable state. Standard-library Python only. Tests use
fake time and fake adapters; no sleeps for long deadlines. Core defects, if
encountered, must be reported to Tern before changing accepted semantics.
No live adapter enablement, state.json, watcher/service edits, wake/stop/Signal,
upgrades, research, migrations, or modification of previous packages. Reader
and controller write their admission/verification/dispatch records here.

## Prospective allocation and history

New integration question P4. Initial worker <=45m; one eligible repair <=20m;
verifier <=20m per pass including post-repair (P4 grants65 worker/40 verifier).
Admission <=15m plus one <=10m confirmation if Tern repairs this contract.
P3 historical grants195/155 remain recorded; r3 acceptance cancels unspent
repair15m/post-repair verifier20m, never transfers them to P4 or erases history.
Actual wall use is separate from spent/cancelled attempt ceilings.

Cairn records starts/absolute deadlines before acknowledged wakes; pins inputs,
arms one-shot deadline events and preserves each version before repair. No
polling or overlapping attempts. Expiry stops overdue work, records BLOCKED
and wakes Tern, without automatic extension. Controller-recovery verification
<=10m inside remaining allocations. After final verdict Tern explicitly opens
warranted successor or records none and why. CHARTER hard stops unchanged.
