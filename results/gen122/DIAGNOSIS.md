# Gen122 attempt1 — the run happened, and the ruler is what failed

**Marker: `NON_EVIDENCE`. Nothing here may be cited as a result.** The frozen
success predicate was not met on 48 of 60 cells, so the apparatus refused to
publish, which is exactly what it should have done. This document explains what
the run showed, and does not repair anything.

## What ran

60 cases, once each, against the pinned reader `qwen3.6-35b-vulkan-nothink`,
106.2 seconds. The execution contract was written at 21:20:03, two seconds before
the first response was captured at 21:20:05 - the contract provably predates the
data, which a reviewer verified independently. Every case returned HTTP 200. All 60 responses were journalled
byte-for-byte and fsynced before any decode. Closure complete, seal agrees across
journal, manifest and disk, marker derived from observation and written last.

The apparatus behaved correctly in every respect, including the most important
one: it declined to call a broken measurement evidence.

## What the reader did

| | |
|---|---|
| cells | 60 |
| cases with a correct record to find | 48 |
| reader selected the **correct** record | **48** |
| reader selected a wrong record | **0** |
| `INSUFFICIENT` cases answered correctly | **12 of 12** |
| cells meeting the frozen success predicate | 12 of 60 |

The reader chose the right record in every case that had one, **including both
conflict orders** - current-first and stale-first alike - and correctly refused
to answer all twelve cases where the requested revision did not exist.

## Why 48 cells scored `UNSUPPORTED_VALUE`

The success predicate requires the selected value to match the expected value
exactly, after casefolding and whitespace collapse. The reader returned the
sentence containing the value instead of the value phrase:

```
EXPECTED value : 'bay tolliver'
READER value   : 'The Ambergris terminal berths at bay tolliver.'
EXPECTED record: REC-6C69462DEB
READER record  : REC-6C69462DEB      <- correct
```

In **47 of the 48**, the expected value appears verbatim inside the returned
string. The reader is not wrong about the fact. It is answering in a different
shape than the matcher accepts.

## CORRECTED: this is a reader finding, not a protocol defect

**The first version of this document was wrong, and wrong in the exact way this
project keeps having to retract.** It claimed the prompt and the matcher disagree
about what a value is. They do not. The frozen prompt says, verbatim:

> copy the ENTIRE value phrase exactly as written in the selected record. Do not
> abbreviate it, omit a word, **return only the distinguishing word**, paraphrase
> it, or **place it inside a sentence**.

Both observed failure shapes are named and forbidden by the instruction itself.
47 answers placed the value inside a sentence. One returned only the
distinguishing word. The prompt and the matcher agree completely.

**The honest finding is therefore about the reader:** given an explicit,
unambiguous instruction not to do two specific things, this reader did one or the
other in 48 of 48 cells - while selecting the correct record in every one of
them.

That is a far more interesting observation than a formatting mismatch. It
separates two capabilities that are usually measured together: this reader
identified the right record under every condition, including both conflict
orders, and could not comply with a simple output-shape constraint.

**Why the original framing was dangerous.** It invited "reconciling" the prompt
with the matcher, and the only available reconciliation is accepting sentence-form
answers - an acceptance class suggested by these very failures. Gen118's option-3
ruling refused precisely that, on the grounds that a class suggested by observed
failures may not be adopted after seeing them. I reproduced the Gen114 error
inside a document warning against it. Caught by glm-5.3-flash, which called the
original framing a decision trap.

## What must not happen next

**The grader must not be adjusted to accept these answers.** Loosening a matcher
after seeing the results it rejected is repair-after-exposure, and it is how
Gen114's headline came to be retracted. This attempt is sealed as NON_EVIDENCE
and stays that way whatever is decided.

Any repair belongs in a **new freeze with a new schedule**, because these 60
prompts have now been exposed to the reader and the schedule is valid once.

## Provenance, stated plainly

The Gen122 control-plane instruction said **NO READER RUN**; it directed a
plan-recovery and field-refresh generation instead. Brian, the project principal,
directed that the run proceed, over that instruction, on 2026-09-06 after the
apparatus was demonstrated working end-to-end against the live reader.

That is recorded here so nobody has to discover it later. The run's authorisation
was human, not control-plane. Everything else about it - frozen schedule, frozen
prompts, frozen grader, sealed evidence - is unchanged and verifiable.
