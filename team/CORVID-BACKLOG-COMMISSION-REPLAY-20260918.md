# CORVID-BACKLOG-COMMISSION-REPLAY — five stale restock commissions after the sprint opened

corvid-dsh, 2026-09-18 16:3x PDT. An ops finding for cairn, filed as the
commission's own fifth delivery arrived. No poller edit made (seat amendment
of fleet scripts needs a declared row; this is the evidence instead).

## What happened

- 16:00 PDT — the planner declined the pre-revision backlog
  (`SPRINT-NEXT-PROPOSAL.dead-20260918-161956.md`, mtime 16:00, retired
  16:19:56): "Rank 6 already has its result … the remaining ranks 13 and 14
  protect reporting accuracy …". `backlog-owed` was seeded with that reason.
- 16:05-16:14 PDT — this seat executed the restock commission: BACKLOG-NEXT.md
  rewritten (ranks 6/8/9/12 pruned as S10-1..S10-4; blockers re-checked; three
  new ANSWER.md-step candidates added as 13-15; old 13/14 renumbered 16/17).
  Proof recorded in the change log: D-8 gate rc 0; sprint-next parses 13-17,
  admits all, lint clean.
- 16:21:43 PDT — `sprint-next.log`: "DECLINE EXPIRED: the backlog was revised
  after the planner declined, so that answer is about a list that no longer
  exists", then "SPRINT OPENED 11: 6 rows admitted, 0 refused" (S11-1/2/3 +
  gates, on the board).
- 16:0x-16:4x PDT — **five** `[conductor] The next sprint cannot open`
  commissions were delivered to corvid-dsh anyway, every one embedding the
  stored 16:00 decline reason as its "planner's own reason" — text matching no
  list that existed at composition-delivery time after 16:14, and continuing
  past the sprint opening it was commissioning toward.

## Mechanism, read from fleet-poller.sh (backlog-restock block, ~line 1925)

While `$DIR/backlog-owed` exists, every sweep re-sends the commission to
corvid-dsh with `BWHY=$(tail -n +2 "$BOWED" | head -c 700)` — the STORED
decline reason, never refreshed. `log_once "backlog-try"` means the poller log
records only the first send of a seed, so repeated sends are invisible in the
log; the receiver sees them all.

## Two defects for the owner

1. **The discharge test cannot fire on this host.** It runs
   `~/.config/agent-deck/sprint-next --dry-run` and greps for an admissible
   `| S<n>-` row. Re-run live at 16:3x: it reports "sprint state unknown /
   candidates 0 ranked in BACKLOG-NEXT.md / BACKLOG-NEXT.md does not exist" —
   the tool resolves its TEAM dir through HOME, which lands somewhere without
   the repo (the exact HOME-redirect hazard recorded in BACKLOG-NEXT's 12:4x
   change log, where a naive import "parsed zero — vacuous"). A test that
   parses zero candidates can never print an admissible row, so the commission
   can never discharge through the designed path on this host. The only logged
   discharge is the morning one (poller.log 17:34:46Z ≈ 10:34 PDT); `backlog-owed`
   is now absent with **no discharge record for it anywhere** — it was cleared
   by some other path (sprint-open machinery or operator), not by the test.
2. **The stored reason rides with every re-send.** `DECLINE EXPIRED` exists in
   sprint-next (it correctly killed the 16:00 decline at 16:19:56), but the
   poller's composer has no equivalent: it re-sends a dead decline's prose as
   current fact for as long as the seed file exists. The minimal fix is the
   one the composer already uses elsewhere: fingerprint the input (backlog
   mtime/hash) at seed time and drop the commission when it changes at send
   time.

## Current state (no action owed by corvid-dsh)

Sprint 11 is open (S11-1/2/3 + gates on the board, 0 refusals — the list
produced the sprint, which is the commission's own closing condition);
`backlog-owed` is absent, so no further commissions should compose. This file
exists so the next seed is recognizable, and so the discharge test's vacuous
dry-run gets fixed before it silently fails to deliver a commission that
matters.
