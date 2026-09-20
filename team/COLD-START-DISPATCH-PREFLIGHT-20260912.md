# Cold-start dispatch preflight

Seat: anvil-oai (worker-codex seat)
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / cold-start recall drills

## Purpose

A one-page preflight form for whoever dispatches the next cold-start recall
 drill. It turns `team/COLD-START-NEXT-DRILL-TEMPLATE-20260912.md` into a
 pass/fail gate before a cold seat is contacted.

## Fill Before Dispatch

| Field | Value |
|---|---|
| Drill id / row | `<row or drill id>` |
| Cold seat | `<seat name>` |
| Output artifact path | `team/<artifact>.md` |
| Allowed packet file 1 | `<path>` |
| Allowed packet file 2 | `<path>` |
| Allowed packet file 3 | `<path>` |
| May read QUEUE/BOARD? | `no` unless explicitly listed above |
| May read prior drill outputs? | `no` unless explicitly listed above |
| Packet-local assignment source | `<where the drill assignment appears, or none>` |
| Team-frontier source expected | `<section expected to settle it, or not settled>` |

## Pass/Fail Gate

Run these checks manually before dispatch:

| Check | PASS condition | FAIL condition |
|---|---|---|
| Prompt travels with packet | The dispatch text includes the five questions from the template | The seat must read another file to learn what to answer |
| Evidence boundary is closed | Every allowed file is named exactly | The prompt says vague things like "mission docs" or "current scoreboard" |
| Dispatch is not frontier evidence | Any line assigning this drill is labeled packet-local metadata | The only visible next action is the drill itself |
| Frontier can abstain | The prompt explicitly rewards `not settled by packet` | The prompt pressures a guess when ownership is absent |
| Output path is outside evidence | Artifact path is in the dispatch text, not treated as an allowed evidence file | The output path is implied by queue/scoreboard lookup |
| Citation granularity set | Requires file + section citations | File-only citations are accepted |

If any row fails, fix the packet before sending it. Do not rely on the worker to
infer the instrument design.

## Row-4 Regression Test

The row-4 packet would have failed two gates:

- **Prompt travels with packet:** FAIL. Corvid had to read `RETRO-1-worker-codex.md`
  and `QUEUE.md` to learn the question set; Anvil got the questions in dispatch,
  but the three-file corpus did not contain them.
- **Dispatch is not frontier evidence:** FAIL. `SCOREBOARD-20260912.md` named
  row 4 and anvil-oai, so Anvil's Q3 could be correct while only reading back
  the drill assignment.

The next drill should pass both gates before it is considered a valid cold-start
instrument.

## Minimal Dispatch Footer

```text
Use only the files listed in Allowed packet. The assignment of this drill is
packet-local metadata. For team-frontier ownership, ignore this drill's own row
and say "not settled by packet" if the packet does not settle it. Cite file +
section for every substantive answer.
```
