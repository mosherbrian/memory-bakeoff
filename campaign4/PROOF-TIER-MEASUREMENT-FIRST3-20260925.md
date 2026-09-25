# First three packages: proof-tier measurement

Tern, 2026-09-25. Small descriptive sample; no causal claim. Sources: each R1/R2/R3 metrics.json and timing-events.json. The original postmortem numbers are approximate and do not supply actual-time or round-overhead baselines.

| Package | Tier/result | Observed author elapsed min | Independent review elapsed min | (review+admission+signature)/author rounds | Initial→final ceilings |
|---|---|---:|---:|---|---|
| R1 synthesis | 1, accepted with local table normalization | 8.35 | 6.03 | (3+1+3)/2 = 3.5 | 185→185 |
| R2 design | 1, exhausted/not accepted | 9.53 | 3.87 | (3+1+3)/2 = 3.5 | 110→110 |
| R3 view | 4, accepted with local link correction | 1.90 | 0.92 | (1+0+2)/1 = 3.0 | 35→35 |

These are actual observed ledger intervals, not granted ceilings, but include dispatch/observation latency: **active effort is not yet measurable from these receipts**. Admission/director active time is unknown, not zero; no live execution occurred. Thus the requested complete active-minute accounting remains incomplete. Future receipts should capture host start/end at task execution where available, without another maintained recorder. Do not manufacture precise active time from message gaps.

Tier1 pooled ratio is14/4=3.5; tier4 is3/1=3.0. Tier2/3 have no observations. Counts include separate director substantive reviews and substantive release/acceptance gates; ordinary tool calls excluded. R3 skipped independent admission and did not open another round for its broken link, but the failed delegated close still brought it back to Tern. **There is not yet a clear demonstrated tier2–4 overhead reduction.** Only one tier4 package exists; no historical comparable ratio exists. We cannot call the tiers a success from this sample.

Comparable independent non-PASS review outcomes: 4, of which 2 format-only (R1 column mapping; R3 relative link), and 2 mixed substance (R2 search/provenance and unresolved configuration). That is2/4 versus approximately14/39 in the campaign baseline—no improvement demonstrated, with far too few cases for trend inference. Including director substance-withheld findings gives6 non-PASS dispositions,2 format-only; that denominator is different and must not be substituted. Director source omissions caused the R1 coverage repair; this is a real avoidable overhead, not the worker's research failure. Failed source pinning is not always formatting: missing selected configuration or unjustified feasibility remains substance.

Zero rounds ended INCOMPLETE because of time box or usage (all four independent INCOMPLETE verdicts were delivered within bounds). Baseline about9 box-limited rounds lacks a reliable total-round denominator; report counts, not a rate improvement. No ceiling growth, compared with baseline P12 260→1430 and P13 180→865; these are allocations, not measured spend, and task sizes differ drastically.

What worked: R1 scientific record reconciled; R2 did not trigger an unsupported experiment; R3 supplies a readable source-linked view. What did not: every package returned at least one non-PASS, and format/provenance defects still generated director intervention. Maintain the adopted low-tier path: local deterministic link/table reconciliation when independent substance is already checked; no new admission/review package for those errors. Do not down-tier research design or waive task-outcome validity to improve the metric. Continue the same lightweight terminal metrics; revisit after additional tier2–4 work if independently warranted, not by inventing work to populate the sample.
