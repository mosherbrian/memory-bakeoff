# Gen35 — agentmemory retirement ablation (controlled_core)

**Evidence class: `controlled_core`, modified-product ablation.** This is not a
`raw_product` result and does not replace Gen33, which remains the authoritative
unmodified agentmemory profile.

## What was varied

One runtime gate, in one function, in one file. `src/functions/remember.ts`
computes lexical Jaccard similarity against each candidate memory and, on
`similarity > 0.7`, assigns `supersededId`, `supersededVersion` and
`supersededMemory` before breaking out of the loop. Those three assignments are
what later drive versioning, parent links, retirement from the search indexes
and cascade update.

The patch wraps **only those three assignments** in a check of
`AGENTMEMORY_EXPERIMENT_DISABLE_AUTO_SUPERSESSION`. The candidate scan, the
threshold, the tokenizer, the loop `break`, memory creation, indexing,
embeddings, retrieval and service architecture are untouched.

| | |
|---|---|
| upstream commit | `e04ba88819c365c9acf9d6661ea802143e728bd6` (package 0.9.29) |
| pre-patch `remember.ts` | `e14b5c946d08843a68cd62fa10ed349a0398a84c2a87ec6d39a172b1934b6d40` |
| post-patch `remember.ts` | `a1e4d56aab1be354144bc85af12723253e147835c7ee4fca2c76b86e43ab3bc5` |
| patch artifact | `research/patches/agentmemory-gen35-retirement-flag.patch`, sha256 `1aee426efd2460f4f2b77094082b8442ec44bc0ec9017d06c2b3d9d417b57c6d` |
| build tree | `external/agentmemory-gen35` (both arms) |
| adapter contract | `a06482525d718dd…`, unchanged from Gen33 |
| fixture / scorer | `a5c67e7b2677dff…` / `1dd831e80b3769a…`, unchanged |

Both arms execute the same built artifact. Only the flag and the run identifiers
differ, and the runner fails if any other environment variable differs, or if
the flag never varies at all.

## Preflight, on unrelated synthetic content

Twelve checks, all passing, on a greenhouse/orchard corpus with no fixture
vocabulary:

- above-threshold pair: ON retires exactly one row; OFF retires nothing and
  leaves no `parentId`, no `supersedes`, version 1.
- ON on the patched build is row-for-row identical to the **unpatched** pinned
  build on the same pair — the patch does not change enabled behaviour.
- below-threshold pair: both arms retain both memories, with identical shape,
  identical ranking and identical scores.
- the OFF arm still writes, indexes and retrieves normally.
- no LLM credentials, local embeddings only, no GPU path.

## Manipulation and control gates

Both gates pass before any causal reading.

- **Manipulation.** Every ON repetition reproduces the Gen33 retirement pattern
  natively: two supersessions, `L001 -> L003` false and `L002 -> L004`
  legitimate, 14 live / 2 retired at CP16. Every OFF repetition has zero
  supersessions, zero retired rows, 16 live at CP16.
- **Control replication.** The fresh ON repetitions match the Gen33 leaf
  evidence on product lifecycle events and their classification, on case failure
  classes per case, on case totals, on lifecycle totals, and on the canonical
  returned-id ordering of all 20 cases. The patched enabled arm is a faithful
  control.

## Result

Counts are per repetition; all three repetitions in each arm are identical, so
the aggregate is exactly three times each figure.

| stream | class | ON | OFF | delta (OFF − ON) |
|---|---|---|---|---|
| lifecycle | `false_supersession` | 1 | **0** | −1 |
| case | `history_erasure` | 2 | **0** | −2 |
| case | `correction_failure` | 1 | **0** | −1 |
| case | `missing_required_truth` | 2 | 1 | −1 |
| case | `configuration_collapse` | 1 | 2 | +1 |
| case | `false_persistence` | 2 | 3 | +1 |
| case | `stale_persistence` | 4 | 5 | +1 |
| case | `belief_truth_confusion` | 2 | 2 | 0 |
| case | `scope_collapse` | 2 | 2 | 0 |
| case | `failed_procedure_adoption` | 1 | 1 | 0 |
| case | `late_history_corruption` | 1 | 1 | 0 |
| case | `unsupported_evidence` | 2 | 2 | 0 |

Case and lifecycle streams are scored separately. `false_supersession` is a
lifecycle class and is sourced only from the lifecycle scorer replay, reconciled
independently against the product's own retirement events.

## Hypotheses

- **H1 supported.** Disabling retirement removes the false supersession
  entirely: lifecycle `false_supersession` 3 → 0 in aggregate.
- **H2 supported in direction.** The Gen33 reductions were caused by retirement.
  With retirement off, `configuration_collapse` returns to 6 and
  `false_persistence` to 9 in aggregate — the same figures the three append-only
  engines produced. Retirement was buying those reductions.
- **H3 traced, not assumed.** `history_erasure` and `correction_failure` are
  present only in ON and fall to zero in OFF. Both trace case-by-case to `L001`
  and `L002` being unreachable after retirement.
- **H4 measured.** `stale_persistence` rises 4 → 5 per repetition; the other
  classes are reported as measured, not expected.
- **H5.** `belief_truth_confusion`, `scope_collapse`,
  `failed_procedure_adoption`, `late_history_corruption` and
  `unsupported_evidence` are unchanged across arms. On this evidence they are
  not attributable to retirement in this engine.

## Case-level difference trace

Thirteen of the twenty cases differ between arms in returned sequence or in
failure classification. **Every one is explained by the presence in OFF of
`L001` or `L002`** — the two records retirement removes. Zero possible
confounds.

The trade is visible case by case. In OFF, `LQ04` and `LQ06` stop failing,
because the corrected history is still reachable. In the same runs `LQ02`,
`LQ05` and `LQ07` start failing, because the superseded configuration and the
stale fact are still competing for the answer.

## What may be claimed

Within this pinned agentmemory system, with source, build, runtime, write
payload, query stream, ruler and adapter held constant and only the automatic
Jaccard retirement gate varying, toggling that gate caused the measured changes
above. That is the first within-engine causal evidence in the project.

It does not generalise to other memory systems. The broader append-versus-retire
conclusion remains cross-product evidence plus this one intervention.

The sharper reading: **retirement did not fix the append-only failures, it
traded them.** Every failure it removed from the current-state classes it
re-created in the history classes, at the same fixture, on the same ruler, in
the same engine. Similarity is not supersession, and a system that cannot tell
the difference will either keep what it should retire or destroy what it should
keep.

## Reproduction

```
scripts/preflight_agentmemory_gen35.py
scripts/run_agentmemory_gen35_ablation.py
scripts/build_agentmemory_gen35_ablation_report.py
```

Six leaf repetitions, `paired-derived.json`, `validation.json` and
`content-digest.txt` live in `results/agentmemory_gen35_retirement_ablation/`.
The report reads no `summary.json` and rebuilds every count from leaf evidence
under the Gen34 contract `round2-reporting-v1`. Re-running the builder on
unchanged leaf evidence reproduces content digest
`073baaab3ac3c6eaac084c3f96d264c37acc974c514d2aa8185f1725a9b81e52`.
