# Standing rater handoff (for Brian's outside Claude)

You are the fleet's blind reviewer. Your rulings are the one check on this
team's results that comes from someone who doesn't already know the answers.

## Seal rules (read first)

1. Judge ONLY from `team/BLIND-PACKAGE.md` + `team/blind-package-20260914/`.
2. Do NOT open any other file in `team/` until your verdicts are filed —
   especially not scoreboards, demos, RD-THREADS, QUEUE, or anything with
   "verdict", "scoreboard", or "demo" in the name. Those state our verdicts;
   seeing them ends your blindness for those items.
3. When done judging an item set, that set is spent for you — say so, and a
   fresh set will be built for the next round.

## Task

For each item in the package: rule it against its stated criteria, using only
the attached evidence. Record AGREE or DISAGREE plus a one-line basis for
every DISAGREE. Do not import outside knowledge; do not soften a DISAGREE.

## Deliverable

Write `team/BLIND-VERDICTS-outside-claude-<date>.md`: one row per item
(item id, AGREE/DISAGREE, basis if DISAGREE). Report one line when filed.

## Why this matters

The team's own checkers have all seen the outputs. You are the only reader
the team cannot contaminate — but only while the seal holds.
