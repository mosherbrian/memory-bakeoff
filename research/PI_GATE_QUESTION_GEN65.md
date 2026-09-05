# Gen65: closing the gate question — useful evidence, not an unattended gate

This generation runs no model, no GPU and no new filter. It reads the committed
outcomes of Gen60 through Gen64 and states what they collectively support.

## The question

Can a model, given only a task's visible instruction and the code as shipped,
write tests good enough to decide automatically whether someone's implementation
is correct?

## The answer

**Not demonstrated, for this pinned model and this generator configuration.**
The generated tests are genuinely useful — they catch wrong implementations that
the project's own tests approve — but nothing we tried made them safe to run
unattended, and we now understand why.

The supported use is **surfacing suspicious cases for a human reviewer**. The
unsupported use is **automatically deciding correctness**.

## The decisive arc

| | change | unsafe banks | retention | caught | removal precision |
|---|---|---|---|---|---|
| Gen60 | unchanged generator, repaired corpus | 4 of 8 | — | 12/12 | — |
| Gen61 | each test must quote its requirement | 4 of 8 | — | 12/12 | — |
| Gen62 | delete anything not entailed | 0 of 7 | 0.000–0.333 | 18/21 | 0.101 |
| Gen63 | screen repaired (retention floor) | Gen62 re-scored UNEVALUABLE | | | |
| Gen64 | delete only with a named extra condition | 4 of 8 | 0.821–0.964 | 12/12 | 0.267 |

Read down the "unsafe banks" column: **4, 4, (0 by destruction), 4.** Three
distinct interventions, no movement.

- **Gen61 — provenance made no difference**, because the false accusations
  already had provenance. All 223 citations were genuine; the filter deleted
  nothing because there was nothing ungrounded to delete.
- **Gen62 — entailment removed everything.** 158 of 188 tests deleted at
  precision 0.101; 142 sound tests destroyed to remove 16 bad ones. Every bank
  became "safe" because almost no bank was left.
- **Gen64 — a justified deletion removed almost nothing, and the wrong almost
  nothing.** 15 removals, precision 0.267, and it kept 12 of the 16 tests that
  actually reject correct code. The unsafe rate returned to 4 of 8 — the same
  four tasks as Gen61.

## Why every filter failed

The two error classes are indistinguishable from the information the checker is
given. A test that overreaches — demanding a Windows drive letter be rejected
because the sentence says "absolute paths must raise ValueError" — and a test
that reasons soundly — asserting `position_mm(0) == 0` when the sentence only
mentions 80 steps — look identical when all you can see is one requirement
sentence and one test.

Gen64's own justifications make this concrete: it deleted the sound inference
about zero and kept all six of the `pathsafe` false accusations, because the
false ones are *phrased* as direct readings of the sentence.

Separating them needs the repository. That is not a prompt change — it removes
the information barrier that makes a generated test independent evidence in the
first place, and a checker that reads the implementation is on its way to
agreeing with it.

## What we are retiring

**PASSED is no longer the headline for this research question.** The frozen
screen returned PASSED for a run with half its banks unusable (Gen60), for a run
that changed nothing (Gen61), and for a run that had deleted 84% of its tests
(Gen62). A verdict that survives all three tracks nothing we care about.

Gate suitability is now reported directly, with no threshold and no summary word:
the **unsafe bank rate**, the **retention range**, and **detection losses named
individually**. `gate-suitability-report-v1` produces exactly that and reaches no
verdict. The screen still exists and still runs; its output is recorded as
secondary.

## A correction to the Gen62 report

I wrote that Gen62 lost three previously-caught wrongs:
`culvert/shared_constant_breaks_telemetry`, `tally/reset_only_on_next_add` and
`tally/add_multiplies`. Gen61 did flag all three — but in `culvert` and `tally`,
whose banks Gen61 had already marked UNSAFE_AS_GATE, and whose verdicts
therefore carry no weight under our own rule. Restricted to the tasks both runs
actually scored, **Gen62's detection losses were zero.**

The Gen62 conclusion is unaffected — it was condemned by its removal precision of
0.101, not by those three — but the claim as I phrased it credited an unusable
bank with a catch. Cross-run detection comparisons are now restricted to the
shared scored population in code, so the mistake cannot recur.

## Scope

One pinned model. One generator contract. One corpus of eight tasks. One run per
condition. This is a bounded result about a specific configuration, not a general
claim that model-written tests cannot gate code. A different model, a larger
corpus, or repeated runs could all move it.

What the result does support is a practical recommendation: use these tests to
tell a reviewer where to look. On that job they are good — 12 of 12, including
wrongs that pass the shipped suite.

## What would open the question again

A **repository-informed checker** is the untested variable: it changes what the
checker can see rather than how it is instructed, and it is the only remaining
route to separating the two error classes. It belongs in a new experimental
branch, with its own independence analysis, because trading away the information
barrier is the whole design question rather than an incremental fix.

## Artifacts

- `results/pi_gate_question_gen65/gate_question.json` - every figure, derived from committed outcomes
- `src/memory_bakeoff/evidence_ruler/gate_suitability.py` - the report that reaches no verdict
- `scripts/run_gen65_synthesis.py` - reads results files only; no model, no re-run
