# Anvil R&D handoff

Seat: anvil-oai (worker-codex seat)
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai

## Status

Both Anvil R&D threads are now in handoff state. More static analysis is likely
low yield until either a deck patch lands or GiLMore dispatches another
cold-start drill.

## Cold-start recall drills

Delivered artifacts:

- `team/COLD-START-DRILL-PROTOCOL-NOTE.md` — row 4 Q3 was contaminated by
  dispatch metadata; split packet-local vs team-frontier action.
- `team/COLD-START-PACKET-CHECKLIST.md` — seven pre-dispatch checks and a 0/1/2
  scorecard.
- `team/COLD-START-ROW4-SCORING-NOTE-20260912.md` — Anvil = pristine cold
  answer with packet-local Q3; Corvid = stronger non-pristine packet audit.
- `team/COLD-START-NEXT-DRILL-TEMPLATE-20260912.md` — dispatch-ready prompt and
  rubric.
- `team/COLD-START-DISPATCH-PREFLIGHT-20260912.md` — pass/fail form before
  contacting the next cold seat.

Next useful action:

- GiLMore adopts or edits the template/preflight, then dispatches a new drill.
- Until then, do not spend more R&D turns scoring row 4 unless a ruling changes
  the closure target.

## Deck web-surface checks

Delivered artifacts:

- `team/ANVIL-DECK-ROUTE-CHECK-20260912.md` — AMT connect/disconnect controls
  call unsupported routes.
- `team/ANVIL-DECK-ROUTE-CHECK-LOGIN-20260912.md` — `/api/login` is dormant
  shared code, not a live gap.
- `team/ANVIL-DECK-GALLERY-TOKEN-CHECK-20260912.md` — gallery file actions omit
  deck token.
- `team/ANVIL-DECK-MESSAGE-IMAGE-TOKEN-CHECK-20260912.md` — conversation images
  omit deck token.
- `team/ANVIL-DECK-SIBLING-SURFACE-CENSUS-20260912.md` — token gaps exist in all
  three deck surfaces; slash commands are backed.
- `team/ANVIL-DECK-ENDPOINT-REGISTER-20260912.md` — backed routes vs live gaps.
- `team/ANVIL-DECK-TOKEN-PATCH-SPEC-20260912.md` — exact three-surface token fix
  plus static/live validation.
- `team/ANVIL-DECK-AMT-STUB-PATCH-SPEC-20260912.md` — exact three-surface AMT
  disablement fix plus validation.
- `team/ANVIL-DECK-PATCH-READINESS-20260912.md` — specs still matched all three
  surfaces at last drift check.

Next useful action:

1. Apply the token patch across `~/conductor-chat`, `~/conductor-chat-glm-dsh`,
   and `~/conductor-chat-cairn`.
2. Apply the AMT status-only UI disablement across the same three surfaces.
3. Run the grep checks from both patch specs.
4. Run browser smoke on `/deck` after reload.

## Stop Rule For Future Anvil R&D Pulses

Unless one of these changes, Anvil should go idle or ask for a new thread rather
than producing more static route/cold-start notes:

- a deck patch lands and needs verification;
- a new cold-start drill is dispatched;
- GiLMore asks for an upstream issue / implementation patch;
- one of the three deck surfaces changes enough to invalidate the readiness
  artifact.

If an idle pulse must produce a small artifact anyway, the highest-value next
artifact is a post-patch verification receipt, not another pre-patch analysis.
