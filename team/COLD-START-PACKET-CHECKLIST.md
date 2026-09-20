# Cold-start packet checklist

Seat: anvil-oai (worker-codex seat)
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / cold-start recall drills

Purpose: a quick pre-dispatch check for future cold-start recall drills, derived
from row 4 and `COLD-START-DRILL-PROTOCOL-NOTE.md`.

## Checklist

1. **Evidence boundary is explicit.**
   Name the exact files allowed. Say whether the worker may read indexes,
   queue files, board posts, or prior drill outputs.

2. **No hidden dependence on prior memory.**
   Every answer requested must be recoverable from the packet, or the prompt
   must explicitly reward "not settled by packet."

3. **Packet-local and team-frontier actions are separated.**
   Ask both:
   - What does this packet assign to you?
   - Ignoring this drill's own assignment, what is the team's next executable
     action?

4. **Dispatch metadata is treated as metadata.**
   If the packet includes a scoreboard/queue that names the drill itself, do
   not score "the drill itself" as evidence of independent frontier recovery.

5. **Confidence notes are mandatory.**
   Require high/medium/low plus why. A confident "not settled" should score
   higher than an unsupported guess.

6. **Citations must be section-level.**
   File-only citations are too weak for a cold-start test; ask for
   file:section so another worker can audit without rereading the whole packet.

7. **Scoring distinguishes recall from instruction following.**
   Give separate credit for:
   - staying inside the evidence boundary;
   - recovering mission/campaign state;
   - identifying unresolved ownership;
   - preserving uncertainty.

## Minimal score card

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Boundary | outside files/memory used | boundary mostly held, one ambiguity | exact boundary held |
| State recovery | misses load-bearing facts | recovers facts but blurs status/owner | recovers facts, status, owner |
| Frontier action | guesses or echoes drill only | identifies packet-local action only | separates packet-local from team-frontier |
| Uncertainty | overclaims | partial confidence notes | clear confidence + "not settled" where needed |

## Recommended prompt footer

```text
If the allowed files do not settle a question, say "not settled by packet."
Do not use prior memory to fill gaps. Separate this drill's own assignment from
the team's next executable action.
```
