# Gen60: on a ruler that can measure it, the generator caught every wrong answer

## What we were trying to settle

Gen58 asked a pinned local model to write extra tests from the visible
instruction alone, and then could not score the answer. Every wrong
implementation we had on record lived in a task whose generated tests rejected
known-correct code, and the two tasks where the generated tests were trustworthy
contained no wrong work at all. The screen came back UNEVALUABLE, not failed.

Gen59 fixed the measuring instrument rather than the model: eight tasks in which
right and wrong implementations sit side by side, with hidden checks the
generator never sees. Gen60 is the re-run. **The generator did not change** -
same contract `model-assisted-challenge-evidence-v1` (`5bad7bd7`), same prompt
template, same pinned model, same sampling, same three attempts per task. Only
the corpus changed. The question was whether Gen58's non-result was a fact about
the generator or an artefact of a broken ruler.

## What happened

Twenty-four generation calls, 425 seconds of model time, all twenty-four
accepted by the sanitizer. Banks ran from 8 to 42 tests.

Scored against the screen frozen at `b694f7b8` before the first call:

| | result | bar |
|---|---|---|
| sensitivity | **1.000** (12 of 12 wrong candidates flagged) | >= 0.50 |
| specificity | **0.000** (0 of 8 correct candidates rejected) | <= 0.25 |
| coverage | **4 eligible tasks** | >= 4 |
| verdict | **PASSED** | |

On the four tasks where the generated tests were trustworthy, they caught every
single wrong implementation - including three that pass the shipped tests.

## The other half of the result

Four of the eight tasks were marked UNSAFE_AS_GATE: `culvert`, `ledger`,
`manifest` and `pathsafe`. In each, the generated bank rejected a known-correct
implementation, so nothing it says about wrong code may be counted. That is the
same failure at the same rate as Gen58 - about half the banks.

So the honest reading is two findings, not one:

1. **Gen58's non-result was the ruler's fault.** Given a task it judges
   correctly, the generator is a strong detector - it missed nothing.
2. **The generator's reliability did not improve, because nothing about it
   changed.** It still invents a requirement roughly half the time. That is a
   fact about the generator, and it is unchanged by this generation.

The failures are near misses rather than nonsense: on the unsafe tasks the bank
rejects a correct tree over 2 to 12 assertions out of 30 to 80. It is mostly
right and confidently wrong at the edges - which is exactly what makes it
unusable as an unattended gate.

## Two caveats that limit the claim

**Specificity could not have failed.** A bank that rejects any correct tree is
removed from the population by the validity gate, so every surviving bank has a
specificity of zero by construction. The 0.000 above is implied by the design,
not measured independently. The real specificity signal is the UNSAFE_AS_GATE
count, which is 4 of 8.

**Flagged is not diagnosed.** The screen records that a bank fails on a wrong
tree. It does not establish that it failed for the requirement that tree
actually breaks. Sensitivity here means detection, not explanation.

One observation outside the screen: in `culvert`, the candidate that edited the
shipped test to agree with its own mistake was flagged, with 21 failures. That is
the Gen49 shape - the false assurance that no structural probe could see. It is
recorded as an observation only, because `culvert`'s bank is UNSAFE_AS_GATE and
therefore carries no weight.

## What this means

Model-written challenge tests are now demonstrably capable of catching wrong work
that the shipped tests miss, on this corpus. They are not yet safe to run
unattended, because half of them would reject a correct implementation. The next
question is no longer "can this produce evidence" - it can - but "can its false
alarms be brought down", and that is a generator question, which Gen60
deliberately did not touch.

## What comes next

A generator-side change is now measurable against a ruler that will not flatter
it: a critic pass, a cross-model check, or a rule that a bank must justify each
assertion against a quoted line of the instruction. Any of those can be run
against this same frozen screen and compared directly with 4-of-8 unsafe and
12-of-12 caught.

## Artifacts

- `results/pi_generated_evidence_gen60/generation_contract.json` - frozen before the first call
- `results/pi_generated_evidence_gen60/generation_log.json` - 24 calls, hashes, timings
- `results/pi_generated_evidence_gen60/generated/` - the 24 accepted banks as written
- `results/pi_generated_evidence_gen60/screen_result.json` - every candidate outcome
- `results/pi_generated_evidence_gen60/raw_stream_manifest.json` - retained provider streams
- `src/memory_bakeoff/evidence_ruler/gen60_screen.py` - the screen arithmetic, tested apart from the run
