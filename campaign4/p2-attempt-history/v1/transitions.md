# Lifecycle transition table (frozen)

**Freezes:** `ACCEPTED-ARCHITECTURE.md` §4, with receipt obligations from §5
and liveness ownership from `director-decisions.md`. This table is complete:
an implementation must be able to turn it into tests without further
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
| 7 | **CHECKING** | Evidence satisfies contract | COMPLETE | Verification receipt + outcome finding (positive/negative) |
| 8 | CHECKING | Eligible implementation defect within budget | REPAIR_ALLOWED | Defect classed as repair (match registered rule), not amendment |
| 9 | CHECKING | Impediment (missing/mismatched artifact, invalid measurement, external block) | BLOCKED | Owned integrity issue; claim blocked, nothing overwritten |
| 10 | **REPAIR_ALLOWED** | Repair allocation recorded and launched | RUNNING | New attempt number; cumulative spend carried, never reset |
| 11 | **BLOCKED** | Recorded resolution → return | Previous eligible stage (REGISTERED or RUNNING) | Resolution event; history and spend preserved |
| 12 | BLOCKED | Defer | BLOCKED (deferred, owned) | Owner + revisit condition; a shared pending-decision record if it gates others |
| 13 | BLOCKED | Terminate | TERMINATED | Reason; terminal for that revision |
| 14 | BLOCKED | Budget/question exhausted | EXHAUSTED | `why_ended` (disagreement / broken environment / never completed); terminal |
| 15 | Any nonterminal | Amendment (question, population, or acceptance criteria change) | Old revision → SUPERSEDED; new revision → DRAFT | Old evidence preserved and linked; cost history survives; no retroactive pass; budget continues under stable `question_id` |
| 16 | **COMPLETE / EXHAUSTED / TERMINATED / SUPERSEDED** | — (terminal) | None | Outcome finding stored separately from workflow status |

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
