# Pilot: does presentation order change what the reader reports as current?

**PILOT. EXPLORATORY. NOT EVIDENCE.** Crude scorer, unfrozen substrate, no
sealed contract. Half the items held back. Nothing here may be cited as a
result; it exists to decide whether a preregistered run is worth its cost.

## Design

Substrate: LongMemEval oracle, `knowledge-update`, sha256
`821a2034d219ab45846873dd14c14f12cfe7776e73527a483f9dac095d38620c`.
Each item: two conversations, the later revising a value stated in the earlier;
the question asks what is true now. Retrieval is perfect by construction.

Manipulation: the two conversations are shown in dataset order (`stale_first`)
or reversed (`current_first`). Nothing else differs.

Reader `qwen3.6-35b-vulkan-nothink`, temp 0, seed 0, stateless.
34 items, seeded split, the other 34 never passed to a reader.

## Results

As run, 34 items:

    dates shown      chronological 23/34   reversed 18/34   discordant  6 vs 1
    dates stripped   chronological 22/34   reversed  9/34   discordant 14 vs 1

After excluding, by the committed §2 rule, every item whose gold value is not
uniquely in the later session - 17 of the 34 in the pilot half - **17 items**:

    dates shown      chronological 15/17   reversed 12/17   discordant 3 vs 0
    dates stripped   chronological 14/17   reversed  5/17   discordant 9 vs 0

These are computed by `scripts/recompute_pilot.py` into
`research/pilot_ordering/PILOT_HEADLINE.json` and quoted from there, never typed.

**An earlier version of this block said "excluding 10 items ... 30 items ...
14 vs 0". No committed rule produces it.** It was the pre-rewrite crude,
turn-scoped cleaning, left standing through two scorer rewrites, and 34 - 10 is
not 30 - the arithmetic was wrong on its face and I never looked. Round 7 caught
it; sixth recurrence of the same class.

The single counter-directional item disappears on cleaning. Every discordant
item now runs the same way: right when the current conversation is last, wrong
when it is first.

## The failures are the superseded value, not scorer noise

Review found the crude scorer's false-negative rate (`four` scored against `4`)
is about 8 in 34, the same order as the dated arm's discordant count. That
objection first drew an impossibility argument from me - a scorer that cannot
read `four` misses in BOTH arms, so it cannot manufacture a direction.

**That argument is false and is withdrawn.** It assumes the model emits the same
answer string in both arms, which is the one assumption this experiment's thesis
denies. Counter-case: the earlier session writes "four", the later writes "4",
gold is "4"; a reader echoing the last-read form answers "four" under reversal -
semantically right, crude-scored MISS in one arm only. A manufactured discordant
pair. Substring false positives arm-correlate the same way.

What stands is the direct check, not the argument.

Checked on the 14 discordant items of the cleaned, date-stripped arm - is the
reversed-order answer present in the EARLIER, superseded conversation?

    12 of 14  yes

    $400,000 -> $350,000        Paris -> Hawaii         600 -> 500
    Friday -> Thursday          5 -> 4                  4 weeks -> 3 weeks
    Yes -> No  (x2)             132 points -> 124       6 ounces (stale value)
    Kansas City Masterpiece -> Sweet Baby Ray's
    Ford F-150 -> Ford Mustang Shelby GT350

The two exceptions (`3`->`2`, `Two`->`one`) are word/digit forms the substring
check could not locate; they are not counter-examples in the model's favour.

This is a directional, semantic pattern, and on THIS data no discordance is a
form artifact - review reproduced that independently at 0 of 15. That is an
empirical finding about these items, not a guarantee about crude scorers in
general. The preregistered run uses the normalised scorer, which removes the
class outright rather than arguing about it.

## What this does NOT establish

- **Position is not isolated.** Stripping the headers leaves month or year
  words inside the conversation text of 28 of the 34 pilot items, and both a
  month and a weekday in 10 of them - computed by `scripts/recompute_pilot.py`
  under a stated rule into `PILOT_HEADLINE.json`, not counted by eye. An earlier
  version said 17 of 34, which no rule produces.
  Worse, the instruction itself says "as of the most recent conversation", which
  is a recency cue no header-stripping can remove: with dates gone, a reader that
  assumes chronological presentation will read the LAST-shown session as the most
  recent, which in the reversed arm is the stale one. So the stripped arm measures
  position against residual textual chronology PLUS an ambiguous instruction. A
  clean isolation needs a neutral question and a stimulus with temporal language
  removed, neither of which exists yet.
- **No significance claim.** n=30, one reader, one temperature, one prompt.
- **No generalisation past this model.** The ceiling is model-dependent; a
  stronger reader may not show it, and that would itself be a finding.

## Contamination found, and what it cost

`scripts/verify_substrate.py` checked all 68 clean items instead of sampling:

    gold ONLY in the later session (as assumed)   31
    gold ONLY in the EARLIER session               8
    gold in BOTH                                  18
    not locatable by the matcher                  11

(An earlier version of this block read 47 / 8 / 2 / 11. Those were the
turn-scoped crude-matcher numbers, left standing after LEDGER 135 rewrote the
script to the session-scoped §4 rule underneath them. The current figures match
`SUBSTRATE_VERIFY.json` as committed.)

The 8 break the design assumption outright. One of them, `e66b632c`, was the
ONLY item in the whole pilot that favoured the reversed order - so the single
piece of evidence against the effect was an item where the design assumption
does not hold. It is excluded above, and the substrate document's claim that
this structure was "verified" is corrected.

The 11 unlocatable ones are a matcher limitation, not a dataset defect, and are
retained.

## The held-out half is not yet preregistered

Review is right that calling it "preregistered" was premature: no scorer, arms,
prompt or success rule are fixed for it, and its membership could still move
because the substrate is unfrozen. Until `research/pilot_ordering/PREREGISTRATION.md`
exists and names all of those, the held-out 34 are merely UNSPENT, which is a
weaker and honest word. They remain untouched.
