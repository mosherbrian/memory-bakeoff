# Suggestion: the inactivity clock resets on words, not on work

**2026-09-15, ~14:20 PDT. A SUGGESTION, not a change.** Nothing has been
applied to `fleet-poller.sh`. A working patch exists and is described below,
but the mechanism is the team's call — if you have a better design, take the
measurements and discard the patch.

Brian's question was why the seats appear to nap. The answer is not that they
are idle. It is that the supervision layer cannot tell activity from progress,
and neither could I until I measured it.

---

## MEASURED — the fleet is busy and almost nothing moves

Last 3 hours, from `opencode.db` and the worker transcripts.

- 312 ACP turns across the fleet, 104/hour. Most recent: seconds ago.
  (`opencode.db` counts 753 for the same window — it counts every model call
  including each tool step. Different unit, not a contradiction.)
- 71% of turns call a tool. 465 bash calls.

Where the 186 write operations went:

| file | writes | what it is |
|---|---|---|
| task-log.md | 72 | bookkeeping |
| RD-THREADS.md | 34 | talking to each other |
| QUEUE.md | 15 | board admin |
| poller.log | 14 | logging |
| fleet-poller.sh | 13 | editing the poller |
| **benchmark_adapters.py** | **3** | the product |

40% of bash calls are queue/board admin. The most frequent commands are all
the same shape: `ls -lt team/`, `tail -2 RD-THREADS.md`,
`agent-deck session output cairn-pi | tail -6`, `grep claimed: QUEUE.md`.

Per seat, and this is the part that matters. Two lanes should be discounted
before reading it: **conductor-glm** is the seat whose job is watching, and
**cairn-pi** has its own independent heartbeat, so neither is evidence about
fleet productivity. Brian made that point and he is right.

| seat | turns, 3h | last turn | last write outside bookkeeping |
|---|---|---|---|
| conductor-glm | 96 | 3m | 264m |
| cairn-pi | 58 | 0m | 111m |
| aletheia-dsh | 40 | 64m | 84m |
| fsync-claude | 35 | 1m | **291m** |
| ledger-claude | 34 | 16m | **424m** |
| assay-dsh | 17 | 109m | 113m |
| builder-claude | 12 | 63m | 70m |
| kiln-flash | 8 | 15m | 38m |
| corvid-dsh | 7 | 18m | 109m |
| verity-flash | 5 | 84m | **952m** |

Zero turns in 3h: anvil-oai, conductor-claude, inferx-rd, palimpsest-muse,
stratum-glm.

The four build seats managed **37 turns between them** and three had been dark
over an hour. Discounting the conductor and cairn, the other eight seats did
158 turns in three hours — overwhelmingly to describe the state of the work
rather than to change it.

## MEASURED — why the 10/20 timer cannot catch this

The timer is wired and firing (10 inactivity events in the last hour). It has
**never escalated once.** From its own log: 9 of the 12 inactivity events ever
recorded read `posted reason, clock reset`.

There are three independent ways to reset the clock without moving any work:

1. **Any status-text edit** restarts it from now — the `$SM` comparison in the
   claimed branch.
2. **A posted reason** restarts it, with no cap. RD-THREADS.md takes 34 edits
   in 3 hours, about one post every 5 minutes, so this condition is
   continuously satisfied by ordinary chatter.
3. **The darkness test uses the owner's transcript mtime** (`OHT`), which any
   turn refreshes — including the one-line reply to the nudge itself. Answering
   "still working on it" buys another 20 minutes.

Every one of those is satisfiable by typing. A seat can hold a row forever by
describing why it has not moved, which is precisely the behaviour the switch
exists to catch.

Separately: `10min unclaimed but no eligible seat resolves (seats:
worker-glm-2)`. Rows name seats that are not agent-deck session titles, so
`seat_id_for` returns nothing, the poller writes a log line, and no seat is
ever woken. The row is then marked fired. Same shape as this morning's
numeric row-matcher bug: it looks like it ran.

**So shortening 10/20 makes things worse, not better** — more nudges into a
fleet already spending its turns answering nudges. Brian's instinct that the
interval is "pokey" is understandable and, I think, the wrong lever.

## Brian's framing: a different approach entirely is welcome

He asked for this to be a suggestion so the team can tackle it its own way,
and said plainly: *"maybe they'll want to tackle it a different way entirely."*
So treat the patch below as the least interesting part of this document. The
measurements are the contribution; the mechanism is yours.

Directions that are NOT what I proposed, and may well be better, since the
deeper finding is that the fleet spends its turns on self-description rather
than on work:

- **Fix the protocol, not the watchdog.** If claiming, posting and
  acknowledging did not each cost a turn, there would be far less to
  supervise. A row could carry its own state transitions without a seat
  narrating them.
- **Make claims expire.** A claim with a deadline needs no darkness test: it
  either completes or it lapses and returns to the pool.
- **Stop the conductors polling.** 40% of bash calls are conductors checking
  whether files changed. A file-watch, or seats reporting on completion, would
  delete that whole category rather than time it.
- **Measure the row, not the seat.** Rows have ages and statuses already; a
  scoreboard of row age may make per-seat liveness tests unnecessary.
- **Decide that this needs no watchdog at all** and say why. If the honest
  answer is that the work is genuinely blocked on something upstream, then a
  timer is the wrong instrument and naming the blocker is the right one.

If one of those is the real fix, discard the patch and say so. A better
diagnosis is also a valid answer — my measurement could be wrong, and the
weaknesses I list at the end are the places I would look first.

## What any fix has to achieve

Offered as acceptance criteria so an alternative design can be judged against
the same bar:

1. The clock cannot be reset by text alone. Words buy at most one grace
   period per claim, not unlimited ones.
2. "Owner is alive" must mean the owner changed something, not that the owner
   spoke.
3. A row whose eligible seats resolve to no session raises a fault a person
   sees, not a log line.
4. No new token cost. Local file reads only.

## One implementation, if you want it

`inact-artifact-clock.py`, beside this file. Anchored and idempotent; refuses
to write a partial patch if the file has drifted, so it fails loudly rather
than half-applying. Verified against
`fleet-poller.sh` sha256 `06134936a73d4fb1`: all six edits apply, `bash -n`
passes, second run is a clean no-op. `inact.diff` is the resulting 95-line
diff.

    python3 inact-artifact-clock.py --check <file>   # report only
    python3 inact-artifact-clock.py --apply <file>

What it does:

- Adds `art_ts()`: given a seat's history file, returns the epoch of its newest
  `kind="edit"` tool record whose paths are not bookkeeping. Pure local read.
- Claimed clock restarts only on a genuinely new claim (different owner), not
  on any status-text change.
- Posted-reason reset capped at one per claim, recorded in field 6 of the state
  file (old 5-field state files still parse; the counter defaults to 0).
- Darkness test uses `OAT` (last real write) instead of `OHT` (last turn).
- An unroutable row wakes Ledger once with the seat names that failed to
  resolve.

## Known weakness in my own proposal

The bookkeeping exclusion list treats QUEUE / BOARD / RD-THREADS / task-log as
non-work. **For a conductor, writing those IS the work.** So this yardstick is
correct for build seats and wrong for conductors as written — it would nudge a
conductor for doing its job. Options, none of which I have picked for you:
exempt conductor seats from the 20-min branch; give them a different artifact
set; or judge them on whether the rows they steward move rather than on their
own writes. This is the part I would most like someone to beat.

Second weakness: `art_ts` depends on adapters reporting `kind="edit"` with
paths. Measured across the fleet's transcripts: 9,293 edit records carry it,
so it works today on every lane that writes — but a future adapter that
reports writes differently would read as permanently dark, and the failure
direction is a false alarm rather than silence, which is the right way round
but still noise.
