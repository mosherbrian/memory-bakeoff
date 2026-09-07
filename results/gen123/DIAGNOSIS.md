# Gen123 attempt1 — fixture 2 ran; 4 of 12 cores interpretable; no order effect visible

**Marker: `NON_EVIDENCE`. Nothing here may be cited.** The marker requires all
twelve cores to pass their controls; four did. The apparatus refused to publish,
correctly.

## What changed from Gen122

Fixture 2: ordinary-word values instead of invented ones, and a worked example in
the prompt. The success predicate, canonicalisation, ontology, conditions and
grader are byte-identical to fixture 1.

| | Gen122 (fixture 1) | Gen123 (fixture 2) |
|---|---|---|
| interpretable cores | 0 / 12 | **4 / 12** |
| exact-value answers | 0 / 48 | **24 / 48** |
| answers embedded in a sentence | 47 | 7 |
| distinguishing word only | 1 | 17 |

The dominant failure **shifted** rather than vanishing. Ordinary words removed the
sentence-wrapping; the reader now tends to drop the head noun instead - `harvest`
for `terrace harvest`. That is semantically reasonable: the question is "Harbour
office terrace", so repeating "terrace" reads as redundant. It is still a
violation of an instruction that forbids it by name.

## What the run shows about the actual question

`STALE_ONLY` appears in 8 cells, and **all 8 are `CLEAN_HISTORICAL_AS_OF`**, where
the stale value is the CORRECT answer. That is the reader answering a historical
question properly. It is not the effect under study, and reading it as such would
be a serious misreading - one nearly made while writing this.

The experimental conditions:

| condition | all 12 cores | the 4 interpretable cores |
|---|---|---|
| `CONFLICT_CURRENT_FIRST` | 5 current-with-history, 7 unsupported | 3 current-with-history, 1 unsupported |
| `CONFLICT_STALE_FIRST` | 5 current-with-history, 7 unsupported | 3 current-with-history, 1 unsupported |

**The two orders are identical, at both scopes.** Presenting the outdated record
first did not change what the reader selected. Gen114 claimed the opposite before
being retracted; this run points the other way, and cannot be cited either.

`INSUFFICIENT_CURRENT` is 12/12 correct for the second run running.

## Why iteration stops here

Tuning the fixture further to raise compliance would be fitting the stimulus to
outcomes already observed. Fixture 2's two changes were justified independently -
transcription fidelity is a nuisance variable, and the worked example was chosen
on measured evidence before this run - but a third round aimed at the head-noun
problem, chosen because this run failed that way, is the Gen114 error.

The remaining question is a control-plane one: an instruction the reader will not
follow, whose violation shape changes with the fixture. Options include naming the
head noun in the required output, restructuring the question so the head noun is
not already in it, or accepting that this reader cannot meet a verbatim-copy
predicate and measuring record selection alone under a differently-stated success
rule - decided BEFORE the next run, not after.

## Provenance

Sol's Gen123 instruction directed plan recovery and said NO READER RUN. Brian
directed this run. The authorisation was human. Everything else - frozen fixture,
frozen grader, sealed evidence, derived marker - is unchanged and verifiable.
