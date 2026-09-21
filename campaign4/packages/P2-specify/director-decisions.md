# P2 decisions supplied by Tern — 2026-09-21

These close the two open ownership decisions assigned to Tern by the admitted
contract. Kiln incorporates them into the specification; corvid independently
checks the resulting specification. This is not authorization to implement it.

## Overseer's operational recovery budget

Cairn may reconcile processes, stop overdue activity and resume eligible work
only within existing package authorization. For each operational incident,
allow one recovery attempt of at most 15 minutes and one repair of that
recovery of at most 15 minutes. Independent verification, when recovery changes
an artifact or execution condition relied on by the package, is by corvid,
at most 10 minutes per pass, including the post-repair pass.

These are ceilings inside the affected package's remaining allocations, not
extra worker attempts, elapsed-time extensions or spending grants. Whichever
limit expires first governs. Preserve the incident identity and cumulative
history across restarts, renames and amendments. A stop/reconciliation may
proceed without inventing a repair allocation; a failed or unverifiable
recovery stays BLOCKED and goes to Tern. No recursive recovery ladder.
Source-code changes require an independently admitted implementation package;
this recovery authority alone does not authorize them. Cairn cannot certify
its own repairs, raise a limit or authorize new work.

## Supervisor liveness and recovery ownership

Tern owns supervisor liveness and the host-side silence backstop. Cairn owns
per-attempt one-shot deadlines and reconciliation on completion, deadline,
restart or backstop events. Cairn remains wake-driven and never polls.

The current `campaign4-watch` timer is an interim silence backstop. It wakes
cairn, then Tern, then uses the campaign pause/Signal path after unresolved
silence. It is not proof of progress, a replacement for attempt deadlines, or
authority to create work. P2 must distinguish the existing mechanism from the
specified enforcement and describe lost timers, host restart, stale activity
and failed wake delivery. An active seat alone cannot discharge an expired
attempt deadline. On restart, reconcile before any new dispatch.

Tern owns an unresolved supervisor-recovery decision, with the same bounded
incident accounting above unless she explicitly allocates otherwise. Codex
exhaustion stops the director role and waits for Brian; no substitute model.
If Tern cannot reasonably decide, the existing pause path stops all seats and
notifies Brian. Neither condition may silently become an automatic retry.

## Interpretation and walkthrough constraints

Use P1's accepted inventory with the limitations in its `acceptance.md`:
installed v1.16.4 baseline, no upgrade authorization, controller-owned
attempt/artifact binding, and an explicit shared-host trust boundary.

Use P1 and P2 as required examples, preserving their actual admission and
execution history. Clearly label simulated negative/blocked/amended branches
and any projected terminal step for P2; a walkthrough is not an execution
receipt or self-certification of P2's completion. P2 becomes frozen only after
independent verification and Tern's acceptance.
