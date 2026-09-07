# LongMemEval oracle as the substrate for the ordering experiment

Measured 2026-09-06 against `xiaowu0162/longmemeval-cleaned`,
`longmemeval_oracle.json`, 15.4 MB, 500 items, not gated.

## Why the oracle split

The oracle split contains ONLY the sessions that carry the answer. Retrieval is
perfect by construction. That is the perfect-records condition, already built,
on real questions - the thing Gen118-123 was hand-writing fixtures to create.

## The knowledge-update subset is the experiment

    question_type == 'knowledge-update'   78 items
      of which abstention variants (_abs)  6
      main items                          72
      main items with exactly one          68
        answer-bearing turn per session

Structure, verified over all 78:

- every item has EXACTLY 2 sessions
- every item lists them in chronological order (78/78)
- the earlier session states the superseded value
- the later session states the current value
- `answer` is the current value
- `has_answer` marks the exact turn in each session

Worked example, `945e3d21`:

    Q: How often do I attend yoga classes to help with my anxiety?
    GOLD: Three times a week.
    [2023/08/11] answer_6a4f8626_1: "...I've been doing yoga twice a week..."
    [2023/11/30] answer_6a4f8626_2: (states three times a week)

That is a core. Two records, one superseded, one current, a question whose
correct answer is the current one - built by someone else, at 68x our count.

## The manipulation is free

`haystack_sessions` is an ordered list. Presenting it as given is
chronological (stale first). Reversing the two sessions is current-first. Same
tokens, same content, only the order changes. That is the reader-interference
manipulation, applied to real items, with nothing hand-written.

## What is NOT yet verified

- A crude numeric matcher located the gold value in the later session for 32 of
  the 68, in the earlier for 4, both for 1, neither for 2, and could not extract
  a numeric key for the rest (answers like "Three times a week"). The 32/4 split
  is consistent with stale-earlier/current-later but the matcher is too weak to
  call it confirmed. A proper check needs the closed-pool treatment: extract BOTH
  values per item and verify they differ.
- The 4 items where the gold value appears only in the EARLIER session need
  reading individually before the set is frozen. They may be mislabelled, or the
  later session may restate the same value.
- The 10 main items without a clean one-marked-turn-per-session shape are
  excluded until read.

## What this replaces

Fixture 3 does not need to be written. The apparatus - runner, sealing, closed-
pool grading, freeze gates - points at this instead. The hand-written cores are
retired.

Source: https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned
