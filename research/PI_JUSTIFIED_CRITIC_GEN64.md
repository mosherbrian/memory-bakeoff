# Gen64: making the critic justify itself stopped the damage and fixed nothing

## The change

Gen62's critic was asked whether a test's assertions are *entailed* by the
sentence it quotes. Read strictly, almost nothing is, so it answered no to 158 of
188 tests and destroyed the evidence to earn a clean false-alarm score. Gen63
repaired the screen so that can no longer pass.

Gen64 changes the question. A deletion is now only honoured when the critic
**names the specific extra condition** the test imposes that the sentence does
not - a concrete value, case or behaviour. Vague refusals, missing
justifications, too-short answers and unreadable replies all keep the test. Doing
nothing leaves the bank intact; deleting requires work.

Everything else is Gen62's design unchanged: same pinned model, same frozen Gen61
banks, one stateless call per test, deletion only, and Gen63's guardrail in
force.

## What happened

| | Gen61 (no critic) | Gen62 (entailment) | Gen64 (justified) |
|---|---|---|---|
| tests removed | 0 | 158 of 188 | **15 of 188** |
| removal precision | n/a | 0.101 | **0.267** |
| known-false removed | 0 of 16 | 16 of 16 | **4 of 16** |
| valid removed | 0 of 172 | 142 of 172 | **11 of 172** |
| retention (worst bank) | 1.000 | 0.000 | **0.821** |
| UNSAFE_AS_GATE | 4 of 8 | 0 of 8 (hollow) | **4 of 8** |
| sensitivity | 1.000 (12/12) | 0.857 (18/21) | **1.000 (12/12)** |
| verdict under the guardrail | PASSED | UNEVALUABLE | PASSED |

The destruction is gone. Retention runs 0.821 to 0.964, nothing is hollowed, and
detection is fully restored at 12 of 12.

**And the primary metric did not move.** UNSAFE_AS_GATE is 4 of 8 - not merely
the same number as Gen61 but the same four tasks: `culvert`, `ledger`, `pathsafe`
and `tally`. On the measure we care about, Gen64 is indistinguishable from having
no critic at all.

## Why

The critic removed 15 tests and kept 12 of the 16 that actually reject correct
code. Its recall on false accusations is 0.250. Precision improved from 0.101 to
0.267, which sounds like progress and is not enough to matter: 11 of its 15
removals were still sound tests.

Reading the justifications shows a coherent, wrong bias. It deletes tests that
assert a value the sentence does not literally print:

- `culvert/test_position_mm_0_steps_is_0_mm` - removed because the sentence
  "only specifies the mapping for 80 steps". Zero maps to zero under any sane
  reading; the test was fine.
- `dispatch/test_empty_queue_raises_error` - removed because the sentence
  "only specifies" ordering, not the empty case.
- `ledger/test_returns_string` - removed for checking the return is a string,
  when the sentence says the function returns a decimal string.

Meanwhile it keeps the genuinely false ones, because they are *phrased* as direct
readings of the sentence. All six surviving `pathsafe` false accusations are of
the form "an absolute path must raise ValueError" - which is what the sentence
says, applied to a case the sentence never contemplated. The critic sees the
sentence, sees the assertion echoing it, and approves.

**The two error classes are not separable by the information the critic has.** A
test that overreaches by demanding a Windows drive letter be rejected and a test
that correctly infers zero maps to zero look identical from a single sentence and
a single test. Distinguishing them needs the repository - what a path actually
is, what the function actually returns - and the critic is deliberately denied
that, because giving it the repository is how a checker starts agreeing with the
implementation it is supposed to check.

## What the arc now establishes

Three generations have attacked the false-alarm rate and none has moved it:

- **Gen61** - require provenance. No effect; the false accusations already had
  provenance.
- **Gen62** - require entailment. Removed everything, including the evidence.
- **Gen64** - require a justified deletion. Removes almost nothing, and the wrong
  almost-nothing.

The false accusations are not a formatting failure, a sourcing failure, or a
strictness dial to be tuned. They come from the model reasoning past the text it
was given, and every filter tried so far can only see that same text.

I think the honest reading is that the reviewer's-aid conclusion is now the
supported one. The generator finds real problems - 12 of 12, including wrongs
that pass the shipped tests - and no cheap post-filter makes it safe to run
unattended. That is a useful tool, described accurately.

## What would actually test the remaining hypothesis

If the programme continues on the gate question, the untested variable is the
**information the checker sees**, not its instructions. A checker given the
repository and the spec, asked whether an assertion is consistent with what the
code can do, would at least have the material to separate the two error classes -
at the cost of the independence that makes generated tests worth having. That
tradeoff is the real question, and it is a design decision rather than a prompt
change.

## Artifacts

- `results/pi_justified_critic_gen64/critic_contract.json` - frozen before the first call
- `results/pi_justified_critic_gen64/critic_log.json` - every verdict with its named condition
- `results/pi_justified_critic_gen64/critiqued/` - surviving banks, one per task
- `results/pi_justified_critic_gen64/screen_result.json` - outcomes plus retention
- `src/memory_bakeoff/evidence_ruler/justified_critic.py` - prompt, reader, contract
