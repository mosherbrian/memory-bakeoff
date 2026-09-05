# Gen61 attempt 1 — superseded, kept in full

Discarded before any generated test was run against any candidate tree, so
nothing here could have been informed by an outcome.

**The defect was mine, in the prompt, not in the model or the grounding rule.**
The instruction said each test "must begin with a docstring whose first line is
`REQUIREMENT: <text>`". The model read that as an instruction to write the line,
and emitted it as a bare statement rather than a string:

    def test_blank_label_becomes_none():
        REQUIREMENT: A field that is blank - empty, or only whitespace - ...
        assert parse_row("A1,,north")["label"] is None

That is not valid Python, so the inherited Gen58 sanitizer rejected the whole
output. Eight of twenty-four calls died this way (reported as a syntax error,
usually at the first non-ASCII character in the copied sentence). The model was
complying with the grounding requirement and failing the formatting one.

Scoring this attempt would have measured my prompt's clarity, not spec
grounding: banks would have been thinner for a reason unrelated to the
hypothesis.

**What changed for attempt 2:** the formatting instruction only. It now says
explicitly that the citation must be a triple-quoted docstring and shows a
worked example. The grounding rule itself - verbatim quote, minimum four words,
case-folded substring of the visible instruction, whole-function exclusion - is
byte-for-byte unchanged, as are the model, sampling, repetitions, corpus, task
order and the `b694f7b8` screen.

**Attempt 1 totals, for the record:** 24 calls, 353.4 s, 16 accepted, 8 rejected
by the sanitizer, 134 tests kept and 23 dropped by the grounding filter.
