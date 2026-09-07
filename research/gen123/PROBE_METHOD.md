# The prompt-variant probe — method and results

Both Gen123 reviewers flagged that the numbers justifying the worked example
(1/8 -> 8/8, 12/60 -> 53/60) had **no artifact**: live reader calls with no
journal, no seal, no authorisation record, vouched for only by code comments.
That is the third time this project has made a measurement and kept nothing.
These are the files.

## What was done

`prompt_variant_probe.py` drove the pinned reader against 8 exposed fixture-1
cases with four instruction variants, requiring exact value match:

| variant | exact | correct record |
|---|---|---|
| V1 — the frozen rule alone | 1/8 | 8/8 |
| **V2 — rule + one worked example** | **8/8** | 8/8 |
| V3 — rule + prose description of the value span | 4/8 | 8/8 |
| V4 — rule + description + example | 5/8 | 8/8 |

`prompt_variant_v2_all60.txt` is V2 across all 60 exposed cases: 60/60 correct
record, 53/60 exact value, with the 7 misses listed - and those misses are what
revealed the transcription problem (`farrowly` -> `farroly`).

## Status of these numbers

**Diagnostic only, and they are NOT sealed evidence.** They were taken on
already-exposed material, deliberately, to choose an instruction before writing a
fresh fixture. Gen122's sealed diagnosis pre-authorised exactly this: iterating on
the prompt to diagnose is legitimate, and a confirmatory result needs cases whose
outcomes did not inform the rule.

They were run outside the evidence apparatus, so they carry no manifest and no
seal. That was a mistake of process, not of reasoning: there is no reason a
diagnostic probe could not have been journalled. Recorded here so the claim can be
checked and re-run rather than taken on trust.

## The fixture search

`fixture2_search_result.json` holds the generator's output: the 12 cores and the
chosen salt. glm-5.3 observed that under the naive enumeration `s1..sN` the first
salt satisfying the three stated constraints is **s3, not the chosen s5** - so the
search as described does not reproduce the choice. The generator also filtered
against the burned set, which differed at the time it ran, and it drew subjects
and words with a seeded shuffle before searching salts. Either way, the honest
position is that the recorded constraints do not uniquely determine s5, and the
script that produced it was not committed at the time. It is here now.
