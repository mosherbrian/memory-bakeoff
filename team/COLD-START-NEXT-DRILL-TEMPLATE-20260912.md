# Cold-start next-drill template

Seat: anvil-oai (worker-codex seat)
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / cold-start recall drills

## Purpose

A dispatch-ready prompt template for the next cold-start recall drill. It folds
in the row-4 lessons from:

- `team/COLD-START-DRILL-PROTOCOL-NOTE.md`
- `team/COLD-START-PACKET-CHECKLIST.md`
- `team/COLD-START-ROW4-SCORING-NOTE-20260912.md`

The key fix is that the prompt itself carries the question set and separates
packet-local assignment from team-frontier recovery.

## Dispatch Prompt

```text
Cold-start recall drill. Use ONLY the packet named below. Do not use prior
memory, queue files, board posts, scoreboard sections outside the packet, or
other repository files. If the packet does not settle a question, write
"not settled by packet" and explain why.

Allowed packet:
- <FILE 1>
- <FILE 2>
- <FILE 3>

Task: answer the following questions with section-level citations and confidence
notes (high/medium/low + why):

1. What actions, claims, or shortcuts are forbidden by this packet?
2. What would count as success for the active campaign or workstream?
3. Packet-local action: what, if anything, does this packet explicitly assign to
   you?
4. Team-frontier action: ignoring this drill's own assignment and dispatch
   metadata, what is the next executable team action, and who owns it?
5. What could you NOT reconstruct from this packet that a worker would need in
   order to act safely tomorrow?

Rules:
- Treat any line that dispatches this drill as dispatch metadata, not as proof of
  the team-frontier action.
- Do not infer ownership from memory or from general team habits.
- A confident "not settled by packet" is better than a plausible unsupported
  guess.
- Cite file + section, not only file name.

Required artifact:
- One Markdown file with the five answers, confidence notes, and a short
  "packet quality" section listing any ambiguity or missing pointer.
```

## Scoring Rubric

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Boundary | Uses outside files/memory without marking it | Mostly holds boundary; one ambiguity | Exact boundary held or every escape explicitly marked |
| State recovery | Misses load-bearing facts | Recovers facts but blurs status/owner | Recovers facts, status, owner, and limits |
| Packet-local action | Misses explicit assignment | Finds assignment but treats it as frontier | Correctly identifies assignment as packet-local |
| Team-frontier action | Guesses or echoes drill dispatch | Names a plausible action but weakly separates metadata | Separates dispatch metadata from frontier; says not-settled when needed |
| Uncertainty | Overclaims | Partial confidence notes | Clear confidence + not-settled where packet is insufficient |

## Packet Builder Pre-check

Before dispatch, the human or coordinator should verify:

1. The allowed packet contains the questions or the prompt above travels with the
   packet.
2. The packet does not require a worker to read queue/board/retro files just to
   understand the task.
3. If a scoreboard is included, any row assigning this drill is treated as
   packet-local metadata.
4. The prompt names whether prior drill outputs are forbidden. Default: forbidden.
5. The expected output path is named outside the packet, so it is not confused
   with evidence.

## Why This Template Is Different From Row 4

Row 4 gave a real cold-seat answer, but its Q3 was contaminated because the
scoreboard packet itself named the drill and owner. This template keeps that
useful local-dispatch signal while adding a separate frontier question that must
ignore the drill's own assignment.
