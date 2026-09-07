# The "~32.9% of the bank" figure: unreproducible as published

Both independent accountants (2026-09-07, glm-5.3 and glm-5.3-flash), auditing
this repository blind to each other, flagged the same figure: `~32.9%` of the
bank opened, cited in four documents, with no artifact supporting it. Neither
could reproduce it. **They were right, and the audit is worse than they knew.**

## What I found

The only `scan_fraction` artifacts in the tree are in
`results/membukkit_gen40_intended_model/{offline,online}.json`:

    0.333333  0.316667  0.316667  0.316667  0.3  0.3  0.3  0.316667

    mean = 0.3125  ->  31.3%

**Not 32.9%.** And 31.3% is a Gen40 intended-model measurement.

## Why that is two errors, not one

1. **The number does not match any artifact.** 31.3% is what the tree supports;
   32.9% appears nowhere. It may come from a subset, an earlier run, or nothing.
2. **It is attributed to the wrong run.** `RESULTS.md`, `STATUS_AND_FINDINGS.md`,
   `AGENTS.md` and `CODEX_HANDOFF.md` attach it to the Gen7/Gen8 shared-LSA
   bucket-routing row, whose linked evidence is `results/membukkit_stress_lsa`
   and `results/membukkit_core`. **Neither directory contains any scan or bank
   figure at all** - I checked every file in both.

So a figure measured in one generation was carried into a claim about a
different one, and then drifted.

## Disposition

**RETRACTED.** Not corrected to 31.3%, because that would repeat the original
error - attaching a Gen40 measurement to a Gen7 claim. The bucket-routing rows
now state the recall figures they can support and say the scan fraction was not
measured for that configuration.

If the routing claim matters, it needs a scan fraction measured on the
configuration it describes, persisted as an artifact. Until then the honest
statement is that shared-LSA bucket routing matched dense-scan recall and we do
not know what fraction of the bank it opened.

## What this says about the wider record

The figure survived in four first-read documents across roughly a hundred
generations. It is the same class as the six non-reproducible-number findings
already in `reviews/LEDGER.md` (47, 69, 74, 115, 141, 147, 151) - and unlike
those, it was caught by outside auditors rather than internally.
