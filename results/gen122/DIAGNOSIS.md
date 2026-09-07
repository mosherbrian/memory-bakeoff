# Gen122 attempt1 — the run happened, and the ruler is what failed

**Marker: `NON_EVIDENCE`. Nothing here may be cited as a result.** The frozen
success predicate was not met on 48 of 60 cells, so the apparatus refused to
publish, which is exactly what it should have done. This document explains what
the run showed, and does not repair anything.

## What ran

60 cases, once each, against the pinned reader `qwen3.6-35b-vulkan-nothink`,
106.2 seconds. Every case returned HTTP 200. All 60 responses were journalled
byte-for-byte and fsynced before any decode. Closure complete, seal agrees across
journal, manifest and disk, marker derived from observation and written last.

The apparatus behaved correctly in every respect, including the most important
one: it declined to call a broken measurement evidence.

## What the reader did

| | |
|---|---|
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

## Why this is a protocol defect and not a reader finding

This is the Gen117 failure mode returning in a new form. Gen117 died on value
surface form; the control plane ruled option 3 in response, requiring the prompt
to demand the reader "copy the ENTIRE value phrase exactly as written". That
instruction is present in all 60 prompts and verified by the freeze audit.

What the run shows is that the instruction produces **complete sentences**, which
is a defensible reading of "the entire value phrase", and that the exact matcher
rejects them. The prompt and the matcher disagree about what a value is. Neither
is obviously wrong in isolation; together they cannot both be satisfied.

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
