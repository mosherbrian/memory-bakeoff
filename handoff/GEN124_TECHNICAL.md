# Gen124 technical

## Substrate

`xiaowu0162/longmemeval-cleaned`, `longmemeval_oracle.json`, 500 items, not gated.
Local snapshot `98d7416c24c778c2fee6e6f3006e7a073259d48f`. NOT content-pinned -
finding 125, carried.

`question_type == 'knowledge-update'`: 78 items, 6 `_abs` variants excluded, 72
main, 68 with exactly one `has_answer` turn per session. All 78 have exactly two
sessions listed in chronological order. Earlier session superseded, later session
current, `answer` is the current value - the last two SAMPLED, not verified
item by item (finding 121).

## Design

Independent unit: the item. 34 items, seeded split `SPLIT_SEED = 20260907`, the
other 34 held out and never passed to a reader. Two orders per item:
`stale_first` (as shipped) and `current_first` (two sessions reversed).

Reader `qwen3.6-35b-vulkan-nothink`, temperature 0, seed 0, max_tokens 128,
stateless, `http://strix-halo.local:8080/v1/chat/completions`.

NOT a sealed evidence run. No contract, no freeze, no manifest, no `EV` journal
binding. Raw responses are appended per call to `journal.jsonl` and flushed, but
this is exploratory apparatus and is labelled so in the script docstring, in
`SUMMARY.json` and in `COMBINED.json`.

## Result, dated arm

    n_items 34
    stale_first_hits 23
    current_first_hits 18
    discordant_stale_first_only 6
    discordant_current_first_only 1

Discordant items: 852ce960, 9ea5eabc, 0f05491a, b6019101, 6071bd76, 7401057b
(chronological only); e66b632c (reversed only). In all six, the `current_first`
answer is the superseded value.

## Result, date-stripped arm

    n_items 34
    stale_first_hits 22      (dated arm: 23)
    current_first_hits 9     (dated arm: 18)
    discordant_stale_first_only 14   (dated arm: 6)
    discordant_current_first_only 1  (dated arm: 1)

Removing the header dates left the chronological arm unchanged within noise and
halved the reversed arm. The discordant count more than doubled.

It must NOT be read as "the model follows position rather than dates". The
stripped arm does not isolate position: month and weekday words remain in most
items, and the pilot's own question ended "as of the most recent conversation",
which points at transcript POSITION rather than at time. What the arm supports
is that order changes the answer, and that removing the header dates makes the
change larger. Separating position from residual chronology and from the
instruction is not done. See PILOT_ORDERING_RESULT.md, "What this does NOT
establish", and PREREGISTRATION.md §6.

`research/pilot_ordering/COMBINED.json` carries both arms.

## Contamination, and the cleaned result

`scripts/verify_substrate.py` over all 68 clean items, under the §2 rule it now
implements (ordering_scorer.hit, whole session, both roles): gold only in the
later session 31, only in the EARLIER session 8, in both 18, unlocatable 11 -
matching `research/pilot_ordering/SUBSTRATE_VERIFY.json` exactly.

An earlier version of this paragraph reported 47 / 8 / 2 / 11. Those were the
turn-scoped crude-matcher numbers from before the ledger-135 rewrite, left
standing after the script was changed under them. The 8 break the design assumption; e66b632c is among them and was
the pilot's only reversed-favouring item.

Excluding the 10 (8 + 2 ambiguous), n=30:

    dates shown      chrono 22  reversed 16   discordant  6 vs 0
    dates stripped   chrono 21  reversed  7   discordant 14 vs 0

Directionality check on the 14: 12 of the reversed answers contain the
superseded value.

The claim that "scorer crudeness produces concordant misses and cannot generate
a direction" is WITHDRAWN - it is false. Counter-case (review, round 3): earlier
session writes "four", later writes "4", gold "4"; a reader echoing the
last-read form answers "four" under reversal, which is semantically correct and
crude-scored MISS in exactly one arm. Substring false positives arm-correlate
too. The result rests on the direct semantic check above, which review
independently reproduced at 0 of 15 discordances being form artifacts - not on
an impossibility argument.

## Preregistration

`research/pilot_ordering/PREREGISTRATION.md` fixes substrate hash, eligibility,
split seed (not re-drawn), normalised scorer, two arms (dated condition
deliberately excluded), verbatim prompt with the recency-cue instruction
removed, reader, and a McNemar exact test on the discordant pair. 14 unspent
items after eligibility. It does not authorise the run.
Header dates replaced with `=== conversation N ===` and the lead sentence
changed from "in the order they happened" - false under `current_first` - to a
neutral one. Date words remain in the conversation text of 29 of 34 items;
the strip is partial (finding 118).

## Scorer

`hit()`: case-folded substring of the gold, or all numeric tokens of the gold
present. Marks `4` wrong against gold `four`. Crude by declaration, not by
oversight - the frozen v6 grader cannot run here (finding 123).

## Review

glm-5.3 `DEFECTS_BLOCKING`, decision `FIX FIRST`. Findings 118-125 in
`reviews/LEDGER.md`, 118-122 and 126 fixed, 123-125 carried with owners. A
re-review naming all five prior findings is queued behind the run.

## Prior art, corrected

ConflictQA arXiv:2604.11209, `github.com/Tianzhe26/ConflictQA`, runs the
before/after ordering manipulation on contradictory RAG evidence and releases
code. Position bias: 15.7pt first-position lift across 36 models, 41.3% flip rate
on swapped pairs. Our niche is supersession ordering in a memory setting, which
is narrower than what was claimed twice tonight (finding 119).
