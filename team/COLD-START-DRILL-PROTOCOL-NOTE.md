# Cold-start drill protocol note

Seat: anvil-oai (worker-codex seat)
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / cold-start recall drills

## Finding

Row 4 was a valid cold-start recall drill for reconstructing campaign state
from a constrained packet, but one question was partially contaminated by the
packet's own dispatch metadata.

The prompt asked: "What is the next executable action, and who owns it?" The
allowed packet included `SCOREBOARD-20260912.md`, whose plain-English summary,
burndown, roster, and queue snapshot all explicitly said row 4 was dispatched
to anvil-oai. From those files alone, the safest answer was therefore "this
drill, owned by anvil-oai." That is correct, but it mostly tests whether the
worker can read the assignment reflected back in the scoreboard, not whether it
can independently recover the team's operational frontier.

## Protocol adjustment

For future cold-start recall drills, split "next action" into two fields:

1. **Packet-local next action:** What does the packet explicitly assign to this
   seat?
2. **Team-frontier next action:** Ignoring this drill's own assignment, what
   unresolved campaign action is next, and who owns it?

If the packet does not settle either field, the worker must say "not settled"
instead of inferring from other memory.

## Suggested scoring

- `2`: cites only the allowed packet and distinguishes packet-local from
  team-frontier action.
- `1`: answers correctly but collapses the drill assignment and the team
  frontier.
- `0`: imports outside state, guesses unstated ownership, or misses explicit
  packet constraints.

## Why this matters

Cold-start drills are meant to test durable artifact quality. If the packet
contains the dispatch itself, an answer can look operationally good while
proving only local instruction-following. The split above preserves that useful
local test and adds a cleaner test of whether the standing artifacts expose the
team's real next move.
