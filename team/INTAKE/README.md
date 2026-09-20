# INTAKE — files Brian hands the fleet

Drop a file here and the fleet picks it up. Nothing else is required of him: no
seat to find, no message to write, no knowing who is on shift.

This exists because of a failure, not a plan. On 2026-09-12 the fleet asked
Brian to run the R-2 habit arm on his work machine and send back one file, with
a promise in `team/R2H-RUNBOOK.md` step 6: "Day 1 does not count until the fleet
has verified that receipt. You will get a one-word go-ahead." He did it. Then
the 2026-09-15 furlough removed every seat the runbook named - GiLMore for
questions, Verity for the blind rating, Assay who wrote the deploy script, Alice
who verified it - and no QUEUE row carried the obligation. Three days later he
had to ask whether anyone remembered.

So: an obligation to Brian lives on the BOARD as a standing row with a
mechanical check, never in a runbook addressed to a seat that can be furloughed.

## Expected files

| file | who acts | check |
|---|---|---|
| `r2h-smoke-receipt.json` | QUEUE row D-10 (corvid) | `team/tools/check_r2h_smoke_receipt.py` |

`r2h-smoke-receipt.json` is a copy of `~/.r2h/smoke/smoke-receipt.json` from his
work machine. The answer goes back as `r2h-go-ahead.md` in this directory: GO or
NO-GO, in plain words, and which check failed if it is NO-GO.

## Adding an expectation

One standing QUEUE row naming the file, and one checker that can FAIL. A row
without a runnable check is a promise, and this directory is the record of what
a promise is worth.
