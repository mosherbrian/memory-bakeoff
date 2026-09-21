# P1 — Inspect what agent-deck already gives us

**Status:** DRAFT. Awaiting contract reader.
**Authorized by:** Brian, 2026-09-21, under `CHARTER.md`.
**Work type:** judgment (an inventory, read by a named reader).

## Task, and the decision it informs

Determine which of launch, identity, status and stop the installed agent-deck
already covers, and what a `-p` profile actually isolates. **The decision this
informs:** which parts of the controller need to be built at all, and which are
already there — which sets the size of every stage after this one.

This is step 1 of Brian's five, and Tern's own first stage.

## Inputs

- `agent-deck` v1.16.4 installed; **v1.16.16 is available** and the upgrade
  question is part of this package, not separate from it.
- Source at `~/src/agent-deck` (Go 1.25.13) — read it, do not guess from help text.
- The four seats already created in the `campaign4` profile.
- `~/memory-bake-off/RUNBOOK-20260920.md` §2 for what we currently believe.

## Expected output

`packages/P1-inspect/capability-map.md`, containing:

1. For **launch, identity, status, stop** — what agent-deck does natively, with
   the command or source reference that shows it.
2. What a `-p` profile isolates, and what it does **not** — shared services,
   hooks, credentials, timers, tmux namespace. Tern's design explicitly says a
   profile isolates "only what that inspection confirms". This is that
   inspection.
3. Whether v1.16.16 changes any of the above; a recommendation on upgrading.
4. **Explicit gaps** — capabilities the controller must supply because
   agent-deck does not.
5. Whether agent-deck can report an actor identity the controller can trust,
   rather than an agent's self-description. This one is load-bearing: the whole
   receipt-binding design rests on it.

## Completion check

A named reader (**corvid**) confirms every claim cites a command or a source
file, and that the gap list is derived from the inspection rather than from the
runbook's prior beliefs.

## Roles

Worker **kiln** · Reader/verifier **corvid** · Duty owner **cairn** · Director **tern**

## Limits

Read-only against the system. No upgrade is performed under this package — the
recommendation is the deliverable. One initial attempt plus one repair.

## Permitted

Read `~/src/agent-deck`, run `agent-deck` read-only subcommands, read the
`campaign4` profile. Write only inside `campaign4/packages/P1-inspect/`.
