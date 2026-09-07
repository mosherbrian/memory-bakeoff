# Preregistration: the unspent 34

Written BEFORE the unspent items are passed to any reader, and before any
outcome on them is known. Everything below is fixed here. If any of it changes
after a run, that run is exploratory and must say so.

Authorised by: nobody yet. This document does not authorise the run. It only
fixes what the run would be, so that the control plane can approve or reject a
specific thing rather than an intention.

## 1. Substrate, pinned

`xiaowu0162/longmemeval-cleaned`, `longmemeval_oracle.json`
sha256 `821a2034d219ab45846873dd14c14f12cfe7776e73527a483f9dac095d38620c`
15,388,478 bytes, snapshot `98d7416c24c778c2fee6e6f3006e7a073259d48f`.

A run against any other bytes is a different experiment.

## 2. Eligibility, by a rule about the DATA and never about an outcome

An item is eligible iff ALL hold:

    question_type == 'knowledge-update'
    question_id does not end with '_abs'
    exactly two sessions
    exactly one has_answer turn in each session
    hit(gold, ALL TEXT OF THE LATER SESSION) is True
    hit(gold, ALL TEXT OF THE EARLIER SESSION) is False

where `hit` is exactly `memory_bakeoff.ordering_scorer.hit` from §4, and "all
text of a session" is every turn's `content` in that session joined by single
spaces, both roles, not only the `has_answer` turn.

**This wording is precise because the previous wording was not, and the
imprecision was load-bearing.** Round-3 review found that "locatable in the
later session" admitted two readings, and that the committed
`scripts/verify_substrate.py` silently used the narrower one - it checked only
the single `has_answer`-marked TURN. Measured, on the pinned file:

    rule                                   eligible  unspent  discordant
    crude matcher, turn scope                  47       24      12 vs 0
    §4 hit, turn scope                         47       23      11 vs 0
    §4 hit, session scope  (ADOPTED)           31       14       9 vs 0
      - as measured before the §4 unit fix:     23       11       8 vs 0

    the ORIGINAL §2 wording as frozen at bb93785
    (crude, turn, PLUS retaining 11 unlocatable) 58       28      14 vs 0

Under single consistent rules the frozen sets differ by 10 items (24 -> 14); the
original wording, which was not a single rule, gives 28. (Before the §4 unit fix
logged in §11 the adopted row was 11, and the spread was 13.)

**The first version of this table was itself a defect of the class it
documents.** It paired the crude+turn rule's `eligible` (47) with the ORIGINAL
rule's `unspent` and `discordant` (28, 14 vs 0), producing a row no single rule
generates, and drew "17 items" from that mixture. Round-4 review reproduced every
correct row and caught it. That is the fourth recurrence of the
non-reproducible-number class in this repo (LEDGER 47, 69, 74, 115), and it
occurred inside the passage whose subject is that a sentence must determine its
own membership.

Every row above is now the output of one stated rule, and each is reproducible
from the pinned file. The adopted rule, its membership, and the direction were
unaffected by the error. (Membership was 11 when that error was found and is 14
after the §4 unit fix logged below; the table error touched neither.)

**The strictest reading is adopted: §4 hit, session scope, 14 unspent items.**
Not because it is convenient - it is by far the most expensive, costing 17 of
28 items - but because it is the only reading under which "the earlier session
does not contain the answer" is actually true, and because adopting the loose
reading after seeing that it preserves more of the effect is the precise move
this document exists to forbid.

The direction is unchanged under all three readings (14 vs 0, 11 vs 0, 8 vs 0).
That is reassurance about the finding, not a defence of the sentence.

With 14 pairs and a preregistered direction, McNemar exact two-sided reaches
p = 0.00012 if all 14 run one way, and p = 0.03125 at 6 discordant pairs, so the
reduced set can still resolve the question. (An earlier draft said 0.0078, which
is 2 x 2^-8 - the pilot's OBSERVED 8 discordances, not the pair count.
Conservative, and still wrong.) If fewer than 6 discordant pairs appear the run is
underpowered and will say so rather than report a null as evidence of absence.

No item is retained by a deferred rule. Every eligibility decision above is
computable from the pinned file and §4 alone.

## 3. Split, unchanged

`SPLIT_SEED = 20260907`, the original seed, over the original sorted id list.
The seed is NOT re-drawn. Re-splitting after seeing pilot outcomes would let the
split be chosen; keeping it means the unspent set is whatever it already was,
minus any item §2 excludes.

## 3a. The unspent set

Applying §2 as now worded to the §3 split leaves **14 items**. They are not
listed by id here - they are computable from §§1-4 and the pinned file by
anyone, and writing them out invites reading them.

## 4. Scorer, fixed here

Normalised containment against the gold value:

    casefold; strip terminal punctuation
    map spelled numbers zero..twenty and their ordinals to digits, both ways
    strip currency symbols and thousands separators for numeric comparison
    HIT iff the normalised gold occurs in the normalised answer AT WORD
        BOUNDARIES, or every numeric token of the gold appears in the answer

Amended before any unspent item was run, after the scorer's own negative control
caught plain substring containment scoring gold `one` against "I spent the
money". This repo has shipped that bug before - a bare `sol` matching inside
`resolver` - so the boundary is the known failure mode of this operation, not a
refinement. The amendment removes a FALSE-POSITIVE class and was made without
reference to any outcome.

This is fixed to remove the known false-negative class (`four` vs `4`) that the
pilot's crude scorer produced. It is NOT an LLM judge and adds no component.
Raw answers are journalled so a stricter scorer can be applied later without
re-running.

Known and accepted limitation: an answer that states BOTH values ("it was
$350,000, now $400,000") scores HIT. The pilot saw none, but it is not excluded.

## 5. Arms, fixed here

Two, and only two:

    chronological   the two sessions in dataset order, current one last
    reversed        the two sessions swapped, current one first

Both arms run with dates stripped: headers rendered `=== conversation N ===`.
The dated condition is NOT part of this run - it was measured in the pilot and
adding it here would be a third arm chosen after seeing that it mattered.

## 6. Prompt, fixed here verbatim

    Below are past conversations between a user and an assistant.

    === conversation 1 ===
    <turns>

    === conversation 2 ===
    <turns>

    === question ===
    <the item's question>

    Answer with the value that is currently true. Reply with the value only.

The pilot's final line said "as of the most recent conversation", which points
at conversation POSITION and is therefore a recency cue the reversal cannot
remove. It is deleted. "Currently true" refers to the world, not to the
transcript.

Residual confound, stated and NOT fixed: month, weekday and year words remain
inside the conversation text of most items. This run measures position against
residual textual chronology. It does not isolate position, and its result may
not be described as if it does.

## 7. Reader, fixed here

`qwen3.6-35b-vulkan-nothink`, temperature 0, seed 0, max_tokens 128, stateless,
one call per (item, arm), no retry on any decodable response.

## 8. What counts as the result

The independent unit is the ITEM. The two arms of one item are paired, never
pooled as independent observations.

Primary: the count of items HIT in chronological but not reversed, against the
count HIT in reversed but not chronological. A McNemar exact test on that
discordant pair, two-sided, alpha 0.05.

Preregistered direction: chronological > reversed. The pilot showed 14 vs 0 on
30 items, so the discordant pair is the whole test; if the effect is real this run should reproduce it, and if it does not
that null is the result and will be published as one.

Secondary, descriptive only, no test: of the items HIT in chronological and
missed in reversed, how many reversed answers contain the superseded value.

## 9. What would make this run void

- any change to §§1-8 after the run starts
- any reader call against an unspent item before this document is authorised
- resuming a partially completed run
- **any amendment to this document that is not recorded in §11 before
  authorisation**

Round-3 review found the original list bound only "after the run starts", so a
pre-run edit - including a convenient clarification made after another look at
pilot-adjacent data - would leave the run fully preregistered. A document whose
whole purpose is to make post-hoc choice impossible permitted exactly that. §11
closes it: every amendment is dated, given a reason, and states whether any
outcome was known when it was made.

## 11. Amendment log

Amendments before authorisation are legitimate; unrecorded ones are not.

**2026-09-07, §4.** Word-boundary containment replaced plain substring
containment. Reason: the scorer's own negative control caught gold `one`
matching inside "money". Removes a false-positive class. No outcome consulted.

**2026-09-07, §2 and §3a.** Eligibility rewritten from "locatable in the LATER
session" to an exact `hit`-and-scope statement, and the strictest of the three
readings adopted, reducing the unspent set from 28 to 11. Reason: round-3 review
found the sentence admitted three readings differing by 17 items. Pilot-arm
discordance under each reading WAS known when this was written and is recorded
above; the strictest reading was adopted despite being the one that discards the
most evidence.

**2026-09-07, §9 and §11.** Added the pre-run amendment binding and this log.
Reason: round-3 review, defect 3. No outcome consulted.

**2026-09-07, §4 - WITH A MEMBERSHIP CONSEQUENCE, DISCLOSED.** The numeric
fallback now fires only for a gold that is purely numeric.

This change made `hit` STRICTER, which made fewer items "ambiguous", which
RAISED the unspent set from 11 to 14 - a change in my favour, so it is stated
first. It was made because round-4 review found `hit("4 weeks", "4 days")` was
True, a defect about units that has nothing to do with which items survive; the
membership effect was discovered afterwards, when the runner's own gate test
failed on the item count. The pilot-arm discordance under the new rule is 9 vs 0
(was 8 vs 0). The reason for the change came from a reviewer, not from me, and
the direction of the effect is unchanged. Reason: round-4 review, defect 4 - it dropped units, so
`hit("4 weeks", "4 days")` was True. A unit mismatch can arm-correlate exactly
the way the retracted crude-scorer argument assumed it could not, and this
scorer is the run's primary endpoint. Removes a false-positive class. Five
negative controls added. No outcome consulted.

**2026-09-07, §2 table and §8 p-value.** Corrected, not amended in substance:
the justification table mixed two rules into one row, and the power sentence
quoted 2^-8 where 2^-11 was meant. Reason: round-4 review, defects 1 and 3.
Neither touches the adopted rule, the membership, or the test.

## 10. What this run still cannot establish

One reader, one temperature, one prompt, one dataset, ~30 items. It cannot
establish a ceiling for any other model, cannot generalise past this substrate,
and cannot separate position from residual textual chronology. It can only say
whether, on these items and this reader, order changes what is reported as
current.
