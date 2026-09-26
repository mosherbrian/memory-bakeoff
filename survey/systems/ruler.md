# System card: RULER (benchmark facility, not runtime mechanism)

**kiln · 2026-09-26 · source: paper v3 full methods 2404.06654v3 (§§1–8). Pinned; no later replications merged. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Facility vs mechanism

RULER is a synthetic behavioral-check harness (13 tasks: retrieval variants, variable-tracing chains, word aggregation, QA-with-distractors; configurable length 4K–128K and complexity), open-sourced for model evaluation. It is not a runtime mechanism and ships no deployment guidance — no retriever, no composer, no host integration.

## Operational meaning of "effective length"

Threshold-graded against Llama2-7B@4K: models claiming 32K+ hold satisfactory performance at 32K only half the time, and nearly all fail before their claimed length. Critically task-dependent: vanilla retrieval holds longest; multi-hop tracing, aggregation, and distractor-heavy QA collapse sooner. "Effective context" is therefore not one number but a per-operation curve — the paper's own limitation section adds: no position control, unverified realistic-task correlation, no short-context calibration, no prompt-robustness verification.

## Borrowable diagnostic distinction

Test the operations separately: can the setup *find* X, *track* X through changes, *aggregate* X? Each failure implies a different fix (retrieve better, shorten/trace explicitly, pre-compute summaries). For Brian: budget injected context to the weakest needed operation, and distrust any single "context size" number — including our own loader caps — as a guarantee.

## Limits (fenced)

2024 models (best: Gemini-1.5-Pro, GPT-4; rest degrade), synthetic-only, no current-host extrapolation, no cost accounting. An effect about old models' curves mandates nothing except humility about long prompts.
