# R25 audit: can the index checker accept wrong work? (Stream B)

## Setup
Frozen R22 sources: check_capture.py 61b12887, pindex_cli.py ddc690aa, failure.json cda9c90d, docs d1 f4071a9b / d2 37e5ff01 / d3 01b928f4, acceptance.json 5a31ed09. Six synthetic capture dirs under this package's temp/ only, built with valid identity/hash/time capture and differing only in index/diagnosis semantics. Independent oracle: separately implemented token-to-file mapping (manual scan, no `re`) plus direct failure.json field comparison. No R24 participant files read; no frozen sources edited. Reproducer: reproduce.py 4233e75e.

## Predictions vs results (predictions written before any run; 6/6 confirmed)
| case | predicted checker | actual | independent |
|---|---|---|---|
| honest full index | pass | pass | match (true accept) |
| halo-only index | pass | pass | mismatch (false accept) |
| index missing d3 | pass | pass | mismatch (false accept) |
| wrong token mapping, halo kept | pass | pass | mismatch (false accept) |
| diagnosis, wrong step, idx-extra/exit1 kept | pass | pass | mismatch (false accept) |
| honest grounded diagnosis | pass | pass | match (true accept) |

False acceptances 4/4 wrong-work cases; false refusals 0/2 honest cases. No surprises.

## Answer
mechanical_pass does not imply a correct full index or a faithful diagnosis on this fixture. The rebuild bar is presence-only (nonempty docs/index plus "halo" key), so halo-only, doc-dropping, and mapping-permuted indexes all pass. The diagnosis bar is substring-only ("idx-extra" in cause, exit==1), so a wrong failed_step passes. The checker message itself says usefulness needs human grade; this audit quantifies that gap.

## Qualification status
This reproduces the known director qualification already recorded in acceptance.json limits ("Checker tests presence of halo, not full correct index") — a reproduced observation with exact counts, not a newly discovered defect class. Synthetic outputs isolate semantic grading only; no claim about adversarial runtime intrusion, and no generalization beyond these six cases.

## For R24 grading
A mechanical_pass on rebuild/diagnose must be followed by full-index comparison against the expected mapping and field-level diagnosis comparison before any work-benefit conclusion.
