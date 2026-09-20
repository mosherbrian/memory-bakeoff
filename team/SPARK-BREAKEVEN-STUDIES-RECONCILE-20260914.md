# muse-drafter: the two break-even studies do not agree — pin the cost axes (spark pulse 2026-09-14)

Follows `SPARK-CONTRADICTION-FANOUT-20260914.md` #2 ("check for
convergences/conflicts with the existing study"). We already hold a cost study
(`2608.11879`, Assay-receipted in `ASSAY-DIRECTIVE-REMAINING-VERIFY.md`); the
fan-out found a second (`2603.04814`). Read side by side, their headline
break-even numbers **differ by more than an order of magnitude**, and the reason
is the cost model, not the systems. No score import.

## The two studies

| | `2603.04814` (Mar 2026) | `2608.11879` (12 Aug 2026, our known study) |
|---|---|---|
| Comparators | **Mem0-style fact memory vs long-context** (GPT-5-mini; GPT-OSS-120B) | **Mem0 + Hindsight + Mastra** (system-vs-system) |
| Data | LongMemEval, LoCoMo, PersonaMem v2 | LoCoMo (665 q, ≤400 turns) |
| Accuracy | memory 57.68 / 49.00 / 62.48 vs LC 92.85 / 82.40 / 69.75 (memory beats GPT-OSS-120B on PersonaMem, 62.48 vs 60.50) | acc spans **21–54%** |
| Cost model | **prompt caching included** (cached input at 10%); per-turn charge still grows with context length | serving/ingest cost of the three systems |
| Break-even | **~10 turns at 100k**; 13 @30k, 9 @200k, 9 @500k | "first tens of turns" → **never within 400 turns** |
| Headline | memory cheaper after ~10 turns at 100k, with a modest accuracy trade-off | *no system wins on both axes* |

## What actually diverges

- **Not a contradiction of findings.** Both agree on the direction: long context
  is accuracy-strong, memory does not dominate cost *and* accuracy, and
  break-even is **dependent on architecture/backbone**. Our long-context null
  and the directive's "no universal winner" both survive.
- **The number is a function of the cost model.** `2603` is a two-point
  architecture comparison at a *specified* context length with a *90% prompt-cache
  discount*, so its per-turn long-context cost collapses and the cross-over comes
  early (~10 turns). `2608` compares **three systems with their own write/reflect
  and serving costs** across up to 400 turns with a different backbone, and the
  fixed ingest/reflection costs push break-even out to tens-of-turns-or-never.
- **The "10 vs >400" gap is therefore likely accounting, not measurement
  conflict:** cache assumption + which fixed costs are included + whether the
  baseline is raw LC or a memory system. Neither paper contradicts the other on
  its own terms; they are not comparable as stated.

## Consequence for any break-even number we cite

A break-even value is meaningless without five pins, which these two papers set
differently:

1. **comparator set** (LC vs a specific memory system vs several systems);
2. **context length L** (and whether it is fixed or growing);
3. **caching assumption** (cached-input discount, if any);
4. **fixed costs included** (write/ingest + reflection, not just read);
5. **backbone + turn definition**.

Until a study pins all five, "break-even" should be quoted as
`break-even ≈ N turns at L, with/without cache, for system X vs LC on dataset Y`,
exactly as we require for every other metric. The existing Assay receipt and the
`RESEARCH-INTELLIGENCE-DIRECTIVE.md` line ("range from tens of turns to beyond
400") are compatible; the fan-out note's "~10 turns" is the other end of the same
model-dependent range.

## Net

Ranking unchanged: the two cost studies **corroborate the negative** and jointly
argue that any single break-even headline is not portable. `2603.04814` is worth
one card *only* as a second cost-model datum, not as a rival to `2608.11879`.
Recommend the cost/break-even thread (directive thread pool item 6) adopt the
five-pin template above. No import.

$0, web reads + our own receipt, no Muse batching. — muse-drafter (Spark)
