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
    the gold value is locatable in the LATER session and NOT in the earlier one

The last clause excludes 10 items (8 gold-only-earlier, 2 gold-in-both). It is a
property of the dataset, checkable without running anything, and was applied
because the assumption it tests was found false - not because of how any item
scored. `research/pilot_ordering/SUBSTRATE_VERIFY.json` records the full
partition.

11 items whose gold the matcher cannot locate at all (string answers like "Yes")
are RETAINED. Their eligibility is decided by the normalised matcher in §4, not
by the crude one that produced that list.

## 3. Split, unchanged

`SPLIT_SEED = 20260907`, the original seed, over the original sorted id list.
The seed is NOT re-drawn. Re-splitting after seeing pilot outcomes would let the
split be chosen; keeping it means the unspent set is whatever it already was,
minus any item §2 excludes.

## 3a. The unspent set, enumerated

Applying §2 to the §3 split leaves **28 items**. Six are excluded from the
unspent half by the eligibility rule: 07741c44, 0977f2af, 0ddfec37, 10e09553,
50635ada, 9bbe84a2.

The 28 are not listed here by id on purpose - the ids are derivable from §§1-3
by anyone with the pinned file, and writing them out invites reading them.

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

## 10. What this run still cannot establish

One reader, one temperature, one prompt, one dataset, ~30 items. It cannot
establish a ceiling for any other model, cannot generalise past this substrate,
and cannot separate position from residual textual chronology. It can only say
whether, on these items and this reader, order changes what is reported as
current.
