# Gen62: the critic removed every false accusation, and most of the evidence with it

## The question

Gen61 showed the generator's false accusations are not invented requirements -
they are real requirements stretched past what they say. That is a judgement
about meaning, so Gen62 added the first second pass in the programme: the same
pinned model, in a separate stateless call, asked of each Gen61 test whether
everything it asserts is actually required by the sentence it quotes. Tests
judged not entailed were deleted.

The banks were frozen. Nothing was regenerated, the generator prompt did not
change, and the critic could only delete. It saw the cited sentence and one
test's source - no repository, no candidate implementation, no verifier, no
outcome, no other test.

## What happened

188 distinct tests reviewed, 339 seconds of critic time.

| | Gen61 | Gen62 |
|---|---|---|
| UNSAFE_AS_GATE | 4 of 8 | **0 of 8** |
| known-false tests removed | n/a | **16 of 16** |
| valid tests removed | n/a | **142 of 172** |
| tests surviving | 188 | **30** |
| sensitivity | 1.000 (12/12) | 0.857 (18/21) |

On the primary metric the critic is a complete success: **every bank became
reference-valid**. All 16 tests that rejected known-correct code are gone, and
not one bank now accuses a correct implementation.

## Why that number should not be celebrated

The critic deleted **158 of 188 tests**. Only 16 of those deletions were
warranted. Its precision when removing is **0.101** - nine of every ten tests it
struck out were fine.

It did not identify overreach. It removed nearly everything, and the false
accusations disappeared because almost all the accusations disappeared. On
`thermo` it deleted the entire bank, 22 of 22, so that task now has no evidence
at all and drops out of the screen. On `manifest` it removed 27 of 28 tests, of
which **zero** were false. On `dispatch` and `valve`, likewise, every removal was
a mistake.

A filter that deletes 84% of its input will always look safe. Safety bought that
way is indistinguishable from having no tests.

## What it cost in detection

Three wrong implementations that Gen61 caught now go free:

- `culvert/shared_constant_breaks_telemetry` - passes the shipped tests
- `tally/reset_only_on_next_add` - passes the shipped tests
- `tally/add_multiplies`

Two of the three are exactly the dangerous kind: wrong code that the project's
own tests approve.

**The sensitivity figures are not directly comparable, and I will not present
them as if they were.** Gen61 scored 12 of 12 over four eligible tasks. Gen62
scores 18 of 21 over seven, because tasks that were previously excluded for being
unsafe are now included. The denominator changed for a reason that is itself the
result. The comparable statement is the one above: three wrongs that were caught
before are missed now.

## The verdict line, and why it misleads

The frozen screen returns PASSED: sensitivity 0.857 clears the 0.50 bar,
specificity is 0.000, and coverage is met. That is the screen applied honestly
and unmodified, and it is the third PASSED in a row that carries almost no
information.

The screen was designed to catch a bank that accuses correct code or misses
wrong code. It has no way to notice a bank that has been hollowed out - 30
surviving tests across seven tasks still clears every bar. **Gen62's real finding
is that the screen cannot distinguish a precise filter from a destructive one,**
and the removal-precision figure of 0.101 is what exposes it.

## What this establishes

A same-model entailment critic can eliminate false accusations completely, and
cannot do it selectively. Asked whether an assertion is strictly required by one
quoted sentence, this model answers no almost always - which is defensible in the
narrow logical sense, since few tests are literally entailed by a single sentence
of prose, and useless as a gate.

Two runs now point the same way. Gen61: provenance is not the problem. Gen62: a
strict entailment judgement is too blunt to be the solution. The generated tests
remain good at finding wrong work and unreliable at leaving correct work alone,
and no cheap post-filter has fixed that.

## What comes next

1. **Calibrate the critic rather than trusting its default strictness.** Ask it
   to remove a test only when it can name the specific extra condition the
   sentence does not require - a positive obligation to justify deletion, which
   the current prompt does not impose.
2. **Add a floor to the screen.** A bank that retains too few tests should be
   reported as hollowed rather than passed. This is a screen defect Gen62
   uncovered and I would not fix it silently mid-experiment.
3. **The reviewer's-aid conclusion is now better supported than either gate.**
   The generator finds real problems; a human reading 188 candidate tests is a
   reasonable workflow, and an unattended gate is not.

## An accounting note

Gen61 reported 223 kept tests, counted per generation call. Gen62 reviewed 188,
because the three repetitions per task repeat test names and the assembled bank
holds one definition per name. Both numbers are correct for what they count; 188
is the number of distinct tests that actually run.

## Artifacts

- `results/pi_entailment_critic_gen62/critic_contract.json` - frozen before the first critic call
- `results/pi_entailment_critic_gen62/critic_log.json` - every verdict, with evaluator-side labels
- `results/pi_entailment_critic_gen62/critiqued/` - the surviving banks, one per task
- `results/pi_entailment_critic_gen62/screen_result.json` - every candidate outcome
- `results/pi_entailment_critic_gen62/raw_stream_manifest.json` - retained provider streams
- `src/memory_bakeoff/evidence_ruler/entailment_critic.py` - prompt, reader and contract
