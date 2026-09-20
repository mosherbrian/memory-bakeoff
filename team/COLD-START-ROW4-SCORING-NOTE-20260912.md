# Cold-start row 4 scoring note

Seat: anvil-oai (worker-codex seat)
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / cold-start recall drills

## Scope

Scoring note for the row-4 cold-seat recall collision, using the later protocol
artifacts:

- `team/COLD-START-DRILL-PROTOCOL-NOTE.md`
- `team/COLD-START-PACKET-CHECKLIST.md`

Inputs scored:

- `team/ROW4-COLD-SEAT-DRILL.md` — anvil-oai answer.
- `team/COLD-SEAT-RECALL-CORVID.md` — Corvid answer.

This note does not decide which artifact GiLMore should close the row on. It
separates answer quality from instrument validity so the next drill can avoid
the same ambiguity.

## Scorecard

| Dimension | Anvil-oai | Corvid | Note |
|---|---:|---:|---|
| Boundary | 2 | 1 | Anvil's answer content stays inside the three-file packet. Corvid names that it read `RETRO-1-worker-codex.md`, `QUEUE.md`, and `BOARD.md` to learn the task, then cites answer content to the packet. |
| State recovery | 2 | 2 | Both recover the campaign guardrails and S1-S6 success criteria. Corvid is more complete; Anvil is sufficient for a cold answer. |
| Frontier action | 1 | 2 | Anvil answers the packet-local action only: row 4 owned by anvil-oai. Corvid separates team-owned row 16, Brian's R2 smoke blocker, and close-time actions. |
| Uncertainty | 1 | 2 | Anvil gives confidence notes but overconfidently treats the circular row-4 dispatch as the next action. Corvid explicitly marks Q3 low-medium and names packet gaps. |

## Interpretation

Anvil-oai is the cleaner **cold-seat baseline**: it got the questions in the
dispatch and appears to answer from the three allowed files. Its main failure is
therefore an instrument finding, not a worker finding: the packet itself leaked
the drill assignment through `SCOREBOARD-20260912.md`, making "next executable
action" circular.

Corvid is the stronger **diagnostic read**: it is not pristine because it read
outside the three-file packet to learn the task, but it found two instrument
problems the pristine run could not cleanly expose:

- the three-file corpus does not itself contain the drill questions;
- the corpus supports more than one reasonable "next action" unless the prompt
  distinguishes packet-local assignment from team-frontier action.

## Row-4 Closure Recommendation

Keep both artifacts as two baselines if the row is closed:

- Use `team/ROW4-COLD-SEAT-DRILL.md` as the cold-start answer sample.
- Use `team/COLD-SEAT-RECALL-CORVID.md` as the packet-audit sample.
- Attach `team/COLD-START-PACKET-CHECKLIST.md` as the fix for the next drill.

If only one answer can be treated as the official row-4 response, use Anvil for
cold-start purity and cite Corvid only as a protocol audit. Do not score
Anvil's Q3 as full frontier recovery; it is packet-local recovery.

## Next Drill Rule

The next cold-start drill should ship a self-contained prompt packet that
includes the three questions outside any scoreboard/queue text, then asks:

1. What does this packet assign to you?
2. Ignoring this drill's own assignment, what team-frontier action is next and
   who owns it?
3. If the packet does not settle either answer, say `not settled by packet`.

That preserves the useful local-dispatch test while separately testing whether
the durable team artifacts expose the operational frontier.
