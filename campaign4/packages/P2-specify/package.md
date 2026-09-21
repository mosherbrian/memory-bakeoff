# P2 — Freeze the contract, the transition table and the ownership map

**Status:** DRAFT, corrected after one bounded rejection. Awaiting corvid's
confirmation of the repaired contract; execution also requires accepted P1 output.
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

- Repository-root `campaign4/ACCEPTED-ARCHITECTURE.md`, sections 2–5, as the
  source; SHA256 `cf390ce0d79bf404c166c59ca0b2548a57e6f239b5e380d88aec569ad11c2b5c`,
  commit `a4c143be903c26dea5cb82efcca015d0a671052d`.
  **It is the specification; this package freezes it, it does not redesign it.**
  `campaign4/ARCHITECTURE-PROVENANCE.md` records the exact extraction and the
  later charter's precedence on today's scope. Sections 6–7 supply the liveness
  obligation and walkthrough context; they do not authorize controller code.
- `campaign4/CONTRACT-TEMPLATE.md` — a transcription of Tern's §3, provisional.
  **P2 replaces it.**
- Repository-root `LOOP-REQUIREMENTS-20260920.md` and the relevant historical
  reviews `team/.director-decisions-review.md`, `team/.director-loop-review.md`
  and `team/.director-loop-review-rev2.md` for what was settled and withdrawn.
- P1's independently accepted `campaign4/packages/P1-inspect/capability-map.md`;
  cairn must record its accepted version and hash before P2 starts.

All repository-root paths above resolve from `/home/bmosher/memory-bake-off`,
not from this package directory or an implementer checkout.

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

**Corvid** confirms: every nonterminal state has an exit, and terminal states
have no outgoing execution transition; the
amendment path exists and does not reset budgets; every role's "may not" is
stated; and the walkthrough reaches a terminal state for all four examples
without a step that is not in the table.

## Roles

Worker **kiln** · Reader/verifier **corvid** · Duty owner **cairn** · Director **tern**

## Limits

No controller code. One initial attempt plus one repair. If the contract cannot
be kept compact, that is a finding to report, not a reason to expand it.

At most 60 minutes for the initial worker attempt and 30 minutes for its sole
repair; at most 30 minutes for each verifier pass, including post-repair
verification. Cairn records start/deadline, owns stopping overdue work and
recording BLOCKED, and wakes Tern with evidence. Deadline handling must be
event-driven; this does not authorize cairn to poll. Expiry does not
automatically spend a repair. The campaign's end-of-day boundary still applies.
P1's output must be independently accepted before P2 execution starts.
The two ownership questions are for Tern to decide within the accepted
architecture; kiln must not redesign it.

## Permitted

Read anything in `memory-bake-off`. Write only inside
`campaign4/packages/P2-specify/`.
