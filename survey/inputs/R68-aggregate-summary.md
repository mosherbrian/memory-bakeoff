# R68 aggregate: saved preference across fresh sessions (repaired measurement)

8 rows, 14 Max calls (claude-sonnet-5, Claude Code 2.1.283, claude.ai firstParty Max), frozen R62 order 12288-I, 24576-R, D-24576, 12288-N, 24576-I, 12288-R, 24576-N, D-12288. Each arm once, no retry; 14 distinct sessions, every child and wrapper exit 0, every R51 scan rc 0 clean. Archive = native bytes; 250 claimed-file checks (archive and native) + dependency pins, 0 drift. Numbers: aggregate-table.json.

## Final endpoint (R63 candidate + R67 finalizer, after bound corvid receipt)
| | 12288 | 24576 | final primary |
|---|---|---|---|
| R (relevant note saved) | FINAL primary | FINAL primary | 2/2 |
| I (irrelevant note saved) | FINAL non-primary (ask) | FINAL non-primary (ask) | 0/2 |
| N (no note) | FINAL non-primary (ask) | NOT_FINALIZED_INTEGRITY_HOLD | 0/2 = 1 finalized non-primary + 1 held |
| D (note in prompt) | FINAL primary | FINAL primary | 2/2 |
Seven terminals (4 primary, 3 valid non-primary) plus one held N. Primary within-target R-I: +1 at 12288 and +1 at 24576. N and D descriptive. 24576-N is not a valid finalized negative and its status is not inferred.

## Raw vs final vs semantic (kept separate)
Raw candidates: candidate_primary 4 (R2, D2), asked_no_run 4 (I2, N2). Semantic: 4 correct target runs, 4 relevant clarification asks (24576-N ask judged legitimate by the reviewer, but the row stays HOLD). No guessing, no contradiction, no wrong-context run. External-trace questions: 0 (the R61 confound disappeared after the uniform disclosure; descriptive only).

## Memory
N saved 0/2 (host EMPTY_DIR is not survival). I and R saved and survived 2/2 each (after-s1 = before-s2 = after-s2). No successful s2 memory read in any row. N: 12288-N failed Read of absent MEMORY.md; 24576-N compound own-memory `ls ... && cat .../MEMORY.md` (empty dir, cat failed) - a single-command instruction deviation and an events-classifier coverage gap (unsupported_shell) -> integrity HOLD; no contamination observed; permission mechanism unverified. R: value used with no read call; delivery by index injection inferred (target appears in the saved MEMORY.md index). I: delivery indeterminate. D: direct template, observed; the report's "saved note" wording is not persistence.

## Interpretation (narrow)
On one synthetic task, one model/host, two targets, n=1 per cell: a relevant preference saved in one fresh Claude Code session led to autonomous preference-compliant completion in the next fresh session (2/2), as direct delivery did (2/2); irrelevant or no memory led to clarification. Not evidence of broad real-work benefit, harm reduction, real throughput, or proven memory causality. R68 changed task disclosure and endpoint vs R61, so cross-cohort differences are not attributable to memory alone; no pooling with R61/R53/R65.

## Limits and accounting
Same reviewer (corvid) across R61-R68 and same user runs all seats: independence operational only. Seat-minutes not measured (unknown). Provider cost-equivalent per transcript not summed here. Go review pool at freeze: see execution-claim.json.
