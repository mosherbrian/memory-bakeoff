# Gen61: making the tests cite the spec changed nothing, and showed us why

## The question

Gen60 found the generator catches every wrong implementation it is allowed to
judge, and also rejects known-correct code in four of eight tasks. The detection
half is good; the false-alarm half is what makes it unusable unattended.

The obvious hypothesis was that the false alarms are *invented* requirements -
things the model supposed rather than read. So Gen61 made the smallest change
that would test that: **every generated test must quote, word for word, the
sentence of the visible instruction it claims to check, and any test whose quote
is not in that instruction is deleted before the bank runs.**

Nothing else moved. Same pinned model, sampling, three repetitions, Gen59
corpus, frozen task order, and the same `b694f7b8` screen applied unmodified.
No critic and no second model, exactly as directed.

## The result: a clean null

| | Gen60 | Gen61 |
|---|---|---|
| UNSAFE_AS_GATE (primary false-alarm metric) | **4 of 8** | **4 of 8** |
| sensitivity | 1.000 (12/12) | 1.000 (12/12) |
| accepted outputs | 24 of 24 | 24 of 24 |
| tests deleted for a bad citation | n/a | **0 of 223** |

Grounding did not reduce the false-alarm rate at all. Three of the four failing
tasks are the same ones (`culvert`, `ledger`, `pathsafe`); `manifest` became safe
and `tally` became unsafe, which at eight tasks is noise, not signal.

## Why it could not have worked

The filter deleted nothing because there was nothing to delete: the model cited
correctly 223 times out of 223. And every single false alarm came from a test
carrying a **genuine, verbatim citation**. 16 distinct tests raised 27 false
assertions across the four unsafe tasks, and all of them quote the instruction
accurately.

What they get wrong is the *scope* of a requirement they quoted correctly:

- `pathsafe` cites "A name that is absolute, or that escapes the depot with
  `..`, must be refused by raising `ValueError`" and then demands that a Windows
  drive-letter path be refused. Real sentence, invented reach.
- `culvert` cites "The control room's telemetry frames must keep reporting the
  SAME number of steps" and then asserts 80 steps for 10 mm - when keeping the
  same number means 40.
- `tally` cites "Calling total() after close() must report 0 until something new
  is added" and then constrains what happens to accumulation afterwards.

So the failure was never ungrounded invention. **The model invents the extent of
a real requirement, not the requirement itself.** Provenance checking cannot see
that, because provenance is exactly what these tests have.

The citations are also broad: 223 quotes but only 45 distinct, several of them
whole sentences up to 40 words, reused across many tests. A sentence-level
citation simply does not constrain an assertion-level claim.

## What we can and cannot conclude

We can say the hypothesis is wrong in its stated form: requiring provenance
against the visible instruction does not reduce false alarms, because the false
alarms already have provenance.

We cannot say grounding is worthless in general, and we cannot resolve a small
effect. Eight tasks and one run per condition cannot separate "no effect" from
"an effect smaller than this design can see". The 4-of-8 to 4-of-8 comparison is
a single observation on each side.

The verdict line still reads PASSED, because sensitivity remained 1.000 and the
validity gate keeps specificity at zero by construction. That PASSED carries no
new information: as recorded in Gen60, specificity cannot fail once the gate has
run, so UNSAFE_AS_GATE remains the only false-alarm number worth reading.

## An honest note on the first attempt

The first Gen61 generation was discarded and re-run. My prompt said each test
"must begin with a docstring whose first line is `REQUIREMENT: ...`", and the
model wrote that line as a bare statement instead of a string - a syntax error,
which killed 8 of 24 outputs in the inherited sanitizer. That would have
measured my prompt's clarity, not spec grounding.

The whole attempt is kept under
`results/pi_spec_grounded_gen61/superseded_attempt_1/` with its own README. The
repair changed the formatting instruction and added a worked example; the
grounding rule itself is byte-for-byte identical. No bank had been run against
any candidate when the decision was made, so no outcome could have informed it.

## What comes next

The measured mechanism points at assertion-level scope, not sentence-level
provenance. Options, in the order I would rank them:

1. **Require the citation to license the exact assertion** - the quoted words
   must state the specific value or behaviour asserted, not merely the topic.
   This is still mechanical and still needs no second model.
2. **A critic pass** asking whether each test's assertion is entailed by its
   quote. This is the first change that adds a model, and should be measured
   against Gen61's 4-of-8, not Gen60's.
3. **Accept the generator as a reviewer's aid rather than a gate**, which is what
   the two runs so far actually support.

## Artifacts

- `results/pi_spec_grounded_gen61/generation_contract.json` - frozen before the first attempt-2 call
- `results/pi_spec_grounded_gen61/generation_log.json` - 24 calls, per-test citations kept and dropped
- `results/pi_spec_grounded_gen61/raw_banks/`, `grounded/` - what the model wrote, and what survived
- `results/pi_spec_grounded_gen61/screen_result.json` - every candidate outcome
- `results/pi_spec_grounded_gen61/superseded_attempt_1/` - the discarded attempt, kept in full
- `src/memory_bakeoff/evidence_ruler/spec_grounded.py` - prompt, filter and contract
