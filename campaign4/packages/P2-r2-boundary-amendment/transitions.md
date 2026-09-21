# Lifecycle transition table (frozen, revision r2.1)

**Freezes:** `ACCEPTED-ARCHITECTURE.md` §4, with receipt obligations from §5,
liveness ownership from `director-decisions.md`, and Brian's terminal-boundary
requirement (see `boundary-schema.md` for the machine-readable interface).
**Revision r2.1** amends live r2: it keeps all r2 closures (row 9a, CHECKING
return, precedence, no-silent-deadline) and adds the terminal boundary
declaration (rows 17–18, boundary section). R1 stays EXHAUSTED; r2 was
SUPERSEDED by the admitted amendment. This table is complete: an
implementation must be able to turn it into tests without further
interpretation. Terminal states have no outgoing execution transition.

## States and transitions

| # | State | Exit condition | Destination | Recorded |
|---|---|---|---|---|
| 1 | **DRAFT** | Reader accepts contract | ADMITTED | Acceptance + contract hash recorded |
| 2 | DRAFT | One bounded rejection (what is missing) | DRAFT (revised) | Rejection is bounded and owned; repair-certification bar applies |
| 3 | **ADMITTED** | Authorization + versioned contract recorded | REGISTERED | Authorization event, contract version/hash |
| 4 | **REGISTERED** | Controller records start (attempt identity bound, deadline declared) **before dispatch** | RUNNING | Start event with deadline; no execution precedes it |
| 5 | **RUNNING** | Required artifacts published | CHECKING | Artifact hashes; end event for the attempt |
| 6 | RUNNING | Interruption (deadline expiry, lost process, failed wake, host restart) | BLOCKED | Reason, evidence; attempt history preserved |
| 7 | **CHECKING** | Evidence satisfies contract (a valid negative finding completes here — it does not become exhaustion) | COMPLETE | Verification receipt + outcome finding (positive/negative) |
| 8 | CHECKING | Eligible implementation defect within budget | REPAIR_ALLOWED | Defect classed as repair (match registered rule), not amendment |
| 9 | CHECKING | Impediment (missing/mismatched artifact, invalid measurement, external block, verification-pass interruption) | BLOCKED | Owned integrity issue; BLOCKED record carries originating phase (CHECKING), attempt identity, and remaining allocation; claim blocked, nothing overwritten |
| 9a | CHECKING | Verification FAIL or director acceptance withheld **with no eligible attempt or repair allocation left** | EXHAUSTED | Owned recorded reason (`failed-verification-no-allocation` or `acceptance-withheld`); terminal for that revision; Tern decides the terminal disposition and whether a successor is warranted |
| 10 | **REPAIR_ALLOWED** | Repair allocation recorded and launched | RUNNING | New attempt number; cumulative spend carried, never reset |
| 11 | **BLOCKED** | Recorded resolution → return | Previous eligible stage (REGISTERED, RUNNING, **or CHECKING** — a resolved verification block returns to CHECKING under the same attempt identity with no worker launch and no new worker attempt) | Resolution event; history and spend preserved; verifier resumes inside the original verifier allocation |
| 12 | BLOCKED | Defer | BLOCKED (deferred, owned) | Owner + revisit condition; a shared pending-decision record if it gates others |
| 13 | BLOCKED | Terminate | TERMINATED | Reason; terminal for that revision |
| 14 | BLOCKED | Budget/question exhausted | EXHAUSTED | `why_ended` (disagreement / broken environment / never completed); terminal |
| 15 | Any nonterminal | Amendment (question, population, or acceptance criteria change) | Old revision → SUPERSEDED; new revision → DRAFT | Old evidence preserved and linked; cost history survives; no retroactive pass; budget continues under stable `question_id` |
| 16 | **COMPLETE / EXHAUSTED / TERMINATED / SUPERSEDED** | — (terminal) | None | Outcome finding stored separately from workflow status |
| 17 | Verdict recorded (row 7/9a/13/14), no boundary disposition yet | Bounded director-decision task in flight (default 10 min, owned by Tern) | Held at verdict stage (not legitimate rest) | Decision task id, owner, deadline; worker/verifier outputs are evidence, not authority |
| 18 | Director-decision task overdue, or terminal state found with no disposition | State fault | INVALID (flagged, owned by Tern) | Specific discrepancy + bounded resolution expectation; wakes Tern; launches no successor itself |

Notes:

- **Repair ≠ amendment.** Correcting the runner to match the registered rule
  is a repair (row 8). Changing population, metric or bar after seeing results
  is a new exploratory row via row 15, never a repair.
- **Resumption never resets.** Attempt count, cumulative spend and incident
  identity survive restarts, renames, reconciliations and amendments.
- **Row 6 vs expiry-spends-repair:** deadline expiry moves to BLOCKED; it
  does not consume the repair. Repair is spent only by a row-8 allocation.
- **Row 9 integrity rule:** on disagreement, do not overwrite one source with
  another (§5). Unreferenced post-crash artifacts are leftovers, not proof.
- **Row 9a vs row 7:** a valid negative finding (evidence satisfies the
  contract, bar missed) completes via row 7. Row 9a fires only when
  verification or acceptance *rejects* the evidence or the specification and
  no repair allocation remains. An implementation must not route one to the
  other's destination.
- **Event precedence at CHECKING.** When several conditions hold, apply in
  this order: (1) deadline expiry of the verification pass → BLOCKED (row 9),
  never a silent fresh deadline (see below); (2) integrity mismatch
  (missing artifact / hash mismatch) → BLOCKED (row 9); (3) invalid
  measurement → BLOCKED (row 9); (4) eligible repair with budget left →
  REPAIR_ALLOWED (row 8); (5) repair budget spent or defect ineligible →
  EXHAUSTED via row 9a (fail/acceptance-withheld, no allocation) or row 14.
  At RUNNING: deadline expiry → BLOCKED (row 6) outranks late artifact
  arrival; artifacts published after expiry are leftovers, not completions.
- **Expired verification gets no silent fresh deadline.** A verification pass
  past its deadline is BLOCKED (row 9) with remaining allocation zero. Return
  to CHECKING (row 11) requires either remaining verifier allocation from the
  original grant or an explicit, recorded new allocation by Tern (a new
  allocation, not an automatic retry). Termination (row 13) or exhaustion
  (row 14 / 9a) are the only other exits.

## Terminal boundary declaration (r2.1)

- **Atomic commit rule.** A revision leaves the lifecycle only when terminal
  state and boundary disposition commit together in one ledger transaction:
  `(state, disposition{kind, links}, decided_by, decision_ref, reason +
  evidence)`. A result may publish before the closure decision; until the
  decision commits, row 17 holds the package at its verdict stage. This is
  not legitimate rest.
- **Enumerable kinds only** (exact shapes in `boundary-schema.md`):
  `successor_opened` (names the specific successor with acknowledged bounded
  work and a finite deadline), `question_answered`, `budget_spent`, `blocked`
  (blocker id, owner, machine-readable wake trigger: event id and/or revisit
  timestamp). No free-text kind; no "idle means done" inference; fresh file
  activity and active seats are checked *after* faults, never as rest
  evidence.
- **Missing disposition is a state fault** (row 18) regardless of fresh file
  activity or an active seat. A historical terminal without a disposition is
  flagged INVALID immediately; intention is never inferred. Missing,
  unreadable, malformed, unsupported-version, or ledger-incomplete state never
  silently passes as rest.
- **Lifecycle BLOCKED ≠ blocked disposition.** Lifecycle BLOCKED is an active
  package awaiting resumption (phase, remaining allocations, trigger — rows
  6/9/11). A `blocked` boundary disposition parks the *question* at a
  terminal revision; it never mutates a terminal back into lifecycle BLOCKED.
- **Successor chains resolve, then rest.** `successor_opened` is validated by
  following links through terminal successors to real in-flight work or a
  legitimate rest leaf; completed chains reach valid rest without permanent
  alarms; cycles and dangling/broken links are invalid. No automatic
  successor is required or authorized for the rest kinds — legitimate
  completion without invented work must remain possible.
- **One authoritative location, atomic publication.** The controller event
  ledger is canonical; the versioned state projection has one sole writer
  (cairn until the controller takes over): temp file, flush, atomic rename,
  ledger transaction precedes publication. On interruption rebuild from the
  ledger; an old snapshot authorizes no dispatch and hides no closure.
  Validation runs immediately after each terminal decision/handoff, on
  startup/recovery, and at backstop invocation.

## Liveness and supervision (from director-decisions.md)

- **Cairn** owns per-attempt one-shot deadlines and reconciliation on
  completion, deadline, restart, or backstop events. Cairn is wake-driven and
  never polls. An active seat alone cannot discharge an expired deadline.
- **Tern** owns supervisor liveness and the host-side silence backstop. The
  current `campaign4-watch` timer is an **interim** backstop (wakes cairn,
  then Tern, then the pause/Signal path after unresolved silence) — it is not
  proof of progress, not a replacement for attempt deadlines, not authority to
  create work. The specified enforcement (per-attempt deadlines + named
  blocked-marker) must be distinguished from this mechanism.
- **Specified failure coverage:** lost timers, host restart, stale activity,
  failed wake delivery. On restart, reconcile recorded attempts against actual
  processes **before** any new dispatch; idempotent action IDs make redelivery
  safe. Restart cannot duplicate execution.
- **Overseer recovery budget (per operational incident):** one recovery
  attempt ≤15 min + one repair of that recovery ≤15 min; corvid verification
  ≤10 min per pass when recovery touches a relied-on artifact or condition.
  Ceilings inside the affected package's remaining allocations — never extra
  attempts, extensions, or spending grants; whichever limit expires first
  governs. Failed/unverifiable recovery stays BLOCKED → Tern. No recursive
  ladder. Cairn cannot certify its own repairs, raise a limit, or authorize
  new work; source changes need an admitted implementation package.
- **Director-role exhaustion:** Codex exhaustion stops the director role and
  waits for Brian — no substitute model. If Tern cannot reasonably decide,
  the pause path stops all seats and notifies Brian. Neither becomes an
  automatic retry.

## Pre-unattended demonstrations (§7 gate, for stage-3+ reference)

Restart cannot duplicate execution · hung attempt reaches an enforced, owned
disposition · workers cannot verify their own artifacts · input changes
invalidate affected registrations · repair exhaustion stops further automatic
attempts · pending judgments visibly block dependent work · evidence
recoverable after interruption · routine handoffs do not require Brian.
