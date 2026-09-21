# P2 — Freeze the contract, the transition table and the ownership map

**Status:** DRAFT. Awaiting contract reader.
**Authorized by:** Brian, 2026-09-21, under `CHARTER.md`.
**Work type:** judgment (a specification, read by a named reader).
**Depends on:** P1 — the ownership map cannot be settled without knowing what
agent-deck already enforces.

## Task, and the decision it informs

Produce the frozen versions of the three things Tern named as the first
deliverable: the **work-package contract**, the **lifecycle transition table**,
and the **ownership map**. **The decision this informs:** whether the controller
is a finite implementation task with a testable boundary. Until these are
frozen, stage 3 cannot start.

This is steps 2, 4 and most of 5 of Brian's five.

## Inputs

- Tern's architecture, sections 2–5, as the source. **It is the specification;
  this package freezes it, it does not redesign it.**
- `campaign4/CONTRACT-TEMPLATE.md` — a transcription of Tern's §3, provisional.
  **P2 replaces it.**
- `../../LOOP-REQUIREMENTS-20260920.md` and Tern's three reviews in
  `../../team/.director-*.md` for what was already settled and withdrawn.
- P1's capability map.

## Expected output

1. `contract.md` — the frozen author-facing contract, plus the four work-type
   extensions. It must stay compact. Tern's line governs: *"There is no bespoke
   schema or gate-authoring exercise for each package."*
2. `transitions.md` — every state, every exit condition, every destination,
   including BLOCKED's exits, the amendment path via SUPERSEDED, and the
   terminal states. Complete enough to be turned into a table of tests without
   further interpretation.
3. `ownership.md` — who holds each role, what each may and may not do, and the
   independence rules. **Two things are still open and must be closed here:**
   the overseer's own repair budget, and who is responsible for the
   supervisor's liveness. Tern wrote "detection alone is not enforcement" and
   left it unassigned.
4. `walkthrough.md` — Tern's own acceptance evidence: walk a **successful**, a
   **negative**, a **blocked** and an **amended** example through the table and
   record where it binds. **P1 and P2 themselves are two of those examples**;
   use them rather than inventing fixtures.

## Completion check

**Corvid** confirms: the transition table has no state without an exit; the
amendment path exists and does not reset budgets; every role's "may not" is
stated; and the walkthrough reaches a terminal state for all four examples
without a step that is not in the table.

## Roles

Worker **kiln** · Reader/verifier **corvid** · Duty owner **cairn** · Director **tern**

## Limits

No controller code. One initial attempt plus one repair. If the contract cannot
be kept compact, that is a finding to report, not a reason to expand it.

## Permitted

Read anything in `memory-bake-off`. Write only inside
`campaign4/packages/P2-specify/`.
