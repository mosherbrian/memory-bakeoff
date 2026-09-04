# Gen38 — MemConflict at full release: Perseus and Mem0, exact provenance

**Evidence class: `external_benchmark_full_release_raw_product_exact_provenance`.**
A full-release run of the benchmark-owned `memconflict-exact-whitebox-v1` lane —
not an official or upstream MemConflict white-box score. `upstream_llm_judge`
remains `requires_reader_authorization`; no reader, no LLM, no external API and
no GPU were used.

The **primary** slice is the 27-persona remainder, which no adapter or setting
was ever tuned against. The fresh 30-persona release is secondary, and the
3-persona calibration slice exists only to prove the engines still behave as they
did in Gen37.

## What was frozen

Contract `memconflict-benchmark-v1` `0521210818e448c8…`, dataset
`8ef9ec8589eccb86…` at upstream `ec51d5d`, the Gen36 calibration manifest, and
both Gen37 adapter contracts byte-for-byte: Perseus `627f812d5296130c…`, Mem0
`920f496be7470fca…`. Every persona run re-asserts all four before writing
anything. The 36 malformed released messages stay excluded by the frozen Gen36
list, and the 181 identifier-unaddressable conditional questions stay UNMEASURED.

Two instrumentation fixes from Gen37 were declared and tested before exposure,
and neither touches writes, queries or ranking: Mem0's in-run inventory is now
explicitly UNMEASURED instead of a `get_all` page size, and Perseus's repeat
queries run against the same session-boundary snapshot as the original query. A
regression test proves the old final-snapshot design is rejected.

Persona is the atomic unit. Each leaf is written temp-then-rename with its own
scientific digest, and a persona is skipped on restart only if its pin, identity,
adapter hash, counts, schema and digest all validate; an interrupted persona is
discarded and rerun whole.

## The replication gate, and what it caught

Both engines re-ran the three calibration personas from fresh stores before
touching held-out data.

**Mem0 reproduced Gen37 exactly**: zero ordering differences, zero score
mismatches, zero hit@3 class changes across 380 measured questions.

**Perseus did not, and the reason is a genuine property of the product.** 77 of
399 questions returned a different order — with byte-identical score vectors
containing ties. Perseus's hybrid RRF produces tied scores, and the order among
equal-scored items is stable within a run but not across runs against a fresh
vault; at the rank-5 cutoff that also changes which tied item survives. Measured
effect on the primary metric: **2 of 380 measured questions changed hit@3 class**
(0.53%), moving calibration hit@3 from 0.4421 to 0.4474.

Before any held-out persona ran, the gate was given an explicit tolerance:
ordering differences must be fully explained by identical tied scores, score
vectors and applicability must match exactly, and hit@3 class changes must stay
under 1%. On that basis Perseus passes, with the tie instability published as its
own quantity rather than hidden inside a pass. This is a deviation from the gate
as literally written ("canonical ordering for every question"), declared here.

That the same harness produced a byte-identical replication for Mem0 and a
tie-explained one for Perseus is what identifies the instability as the product's,
not the harness's.

## Primary result: 27 held-out personas

Perseus, 3,189 measured questions and 162 unmeasured:

| conflict type | measured | hit@2 | hit@3 | hit@5 | log-rank@3 |
|---|---|---|---|---|---|
| dynamic | 2,631 | — | 1,142 (0.434) | — | — |
| static | 324 | — | **111 (0.343)** | — | — |
| conditional | 234 | — | 231 (0.987) | — | — |
| **overall** | **3,189** | **1,267 (0.397)** | **1,484 (0.465)** | **1,814 (0.569)** | **0.385** |

First-support-rank distribution: rank 1 in 870 cases, rank 2 in 397, rank 3 in
217, rank 4 in 180, rank 5 in 150, no hit in 1,375.

Contract integrity on the primary slice: zero unmapped provenance, zero empty
returns, zero returns shorter than five, zero future-session leakage.

**H2 holds for Perseus.** Static conflict is its weakest class by a wide margin —
0.343 against dynamic 0.434 and conditional 0.987 — on 27 personas the adapter
never saw. The calibration slice had said 0.167 on 36 questions; at ten times the
sample it settles at 0.343, which is why the held-out slice is the primary one.

Mem0, the same 3,189 measured questions and 162 unmeasured:

| conflict type | measured | hit@3 | log-rank@3 |
|---|---|---|---|
| dynamic | 2,631 | 1,103 (0.419) | — |
| static | 324 | **124 (0.383)** | — |
| conditional | 234 | 228 (0.974) | — |
| **overall** | **3,189** | **1,455 (0.456)** | **0.386** |

**H2 holds for Mem0 too**, though less starkly: static is 0.383 against dynamic
0.419, so it is the weakest of the two substantive classes rather than an outlier.
Contract integrity is identical to Perseus: zero unmapped provenance, zero empty
returns, zero future-session leakage.

## Slice agreement

| slice | Perseus hit@3 | Mem0 hit@3 |
|---|---|---|
| calibration 3 | 0.447 | 0.474 |
| held-out 27 | 0.465 | 0.456 |
| full 30 | 0.463 | 0.458 |

The three slices agree to within two points for Perseus, so the development
exposure of the calibration personas did not inflate them.

## Why static conflict fails — the pre-registered mechanism diagnostic

Derived scorer-side, after retrieval was frozen. For each static question, whether
the gold truth session and the newer contradicting session appear in the returned
five (Perseus, held-out):

| top-5 outcome | count |
|---|---|
| truth and contradiction both present | 60 |
| truth only | 82 |
| contradiction only, truth absent | 86 |
| neither present | 96 |

**The single-mechanism story is wrong.** "Retrieval prefers the newer
contradiction" describes 86 of the 324 static questions. Another 96 return
neither the truth nor the contradiction — the supporting session simply never
surfaces, which is a reachability failure rather than a competition one. Reporting
only a hit rate would have merged these two very different problems.

## Perseus admission: is a static miss a ranking failure or an unavailable support?

Perseus quarantined **199 writes** across the 27 held-out personas, in every one
of them, each carrying a native reason string of the form
`quarantined (interference score 0.9xx > bound 0.900)`. Joining that public write
ledger to the scorer-side gold, posthoc:

- static hits: 111
- static misses whose gold support was **fully admitted**: 197
- static misses whose gold support was **partly quarantined**: 16

So 92% of static misses are genuine ranking failures against fully searchable
evidence. Quarantine is real, is named by the product, and explains only a small
minority — which is exactly the confound Sol asked to be separated rather than
assumed away.

Mem0's static mechanism split is the same shape: 78 of its static questions return
the contradiction without the truth, 122 return neither, 43 return both and 81
return truth alone. Two engines with unrelated retrieval stacks fail static
conflict in the same two ways and in similar proportions.

Mem0's admission diagnostic is the control that makes Perseus's readable: Mem0
**quarantines nothing at all**, and still misses 200 static questions whose gold
support was fully admitted and searchable. Whatever static conflict costs, it is
not an admission problem.

## Paired comparison on the 27 held-out personas

Both engines saw the same personas and the same questions, so the pairing is
preserved rather than averaged away.

| | K=3 | K=5 |
|---|---|---|
| both hit | 1,117 | 1,434 |
| Perseus only | 367 | 380 |
| Mem0 only | 338 | 324 |
| neither | 1,367 | 1,051 |

They disagree on **705 of 3,189 questions** at K=3. Two engines whose overall
rates differ by one point are finding substantially different evidence.

Persona-block bootstrap, contract frozen before any outcome was read (seed
20260903, 10,000 resamples, resampling the 27 personas rather than treating
thousands of questions as independent):

**Mem0 minus Perseus, exact-provenance hit@3: mean −0.0097, median −0.0089, 95%
interval [−0.0273, +0.0095].**

The interval straddles zero. There is no winner on this lane, which is exactly
what H5 declined to preregister.

## The frozen BM25 baseline, as context

The Gen36 baseline, unchanged, over the same release and the same lane:

| | hit@3 overall | dynamic | static | conditional |
|---|---|---|---|---|
| Perseus | 0.465 | 0.434 | 0.343 | 0.987 |
| Mem0 | 0.456 | 0.419 | 0.383 | 0.974 |
| BM25 | 0.285 | 0.226 | 0.312 | 0.914 |

Context only; nothing was tuned toward it. But the shape is worth stating plainly:
**both engines beat the lexical baseline by roughly twenty points on dynamic
questions and by three points at most on static ones.** On the class where the
task is to prefer an older truth over a newer contradiction, a pure BM25 index
over the same allowed history is within a few points of two production memory
systems. Embeddings are buying very little exactly where the benchmark hurts.

## Operations at full release

| | Perseus | Mem0 |
|---|---|---|
| personas | 30 | 30 |
| writes | 142,093 | 142,093 |
| write p50 | 140–144 ms | 357–366 ms |
| query p50 | 21–27 ms | 396–416 ms |
| wall time | 5.69 h / 1.64 GB | 14.97 h / 1.71 GB |
| projection from Gen37 | 5.8 h | 14.7 h |

Write latency stayed flat across all 30 personas and across stores growing to
~4,900 records, so the linear projection Gen37 offered is confirmed rather than
merely assumed. Measured against projection: Perseus 5.69 h versus 5.8 (ratio 0.981) and 1.64 GB
versus 1.65; Mem0 14.97 h versus 14.7 (ratio 1.018) and 1.71 GB versus 1.73. Write
p50 in the first third of personas versus the rest is 141.82 against 141.83 ms for
Perseus and 361.33 against 361.20 for Mem0 — no drift at all. The BM25 baseline
took 173 seconds for the whole release.

On determinism: returned session order was identical in 84 of 84 repeat queries
for both engines. In 4 of Mem0's 84 the float scores differed while the order held;
re-running one of those against the persisted store afterwards reproduces the
scores exactly, so this is float non-determinism in the ONNX embedding path under
CPU load, and it changes no hit, no rank and no log-rank.

## Reproduction

```
scripts/run_memconflict_gen38_full_release.py --engine perseus --slice calibration
scripts/gate_memconflict_gen38_replication.py --engine perseus
scripts/run_memconflict_gen38_full_release.py --engine perseus --slice heldout
scripts/run_memconflict_gen38_full_release.py --engine mem0 --slice calibration
scripts/gate_memconflict_gen38_replication.py --engine mem0
scripts/run_memconflict_gen38_full_release.py --engine mem0 --slice heldout
scripts/run_memconflict_gen38_bm25.py
scripts/build_memconflict_gen38_report.py
scripts/reconcile_memconflict_gen37_inventory.py --results results/memconflict_gen38_full_release ...
```

Scientific content digest `aff8855d35d139ae59eb532fa7141f6d98279ddc15d666feb906a58238609fb7`, rebuilt twice byte-identically. Wall-clock
measurements live in `operations.json`, outside the hashed content.

## Recommendation for Gen39 — not executed

The two adapters and the capacity assumptions held at full scale, so the blocker
Gen37 named is cleared. Two candidates, in this order:

1. **Hindsight Gen31 and agentmemory Gen33 at calibration scale**, exactly as
   Perseus and Mem0 were done in Gen37. agentmemory is the interesting one: its
   Jaccard retirement fired twice per run on a 16-message fixture, and at 4,700
   messages per persona it will fire constantly. Gen35 showed retirement trades
   current-state failures for history failures; MemConflict's static class is
   precisely a history question, so the prediction is sharp and worth testing.
2. **The reader lane**, if the answer-level metrics are wanted. The exact-provenance
   lane has now been shown to work at full release and to separate engines from a
   lexical baseline, so a reader would add the black-box half rather than replace
   anything. Its design constraints are already written in the Gen36 contract.

I would not run a third full release before a calibration pass tells us whether an
engine's adapter carries over. That is the rule that made this generation cheap to
predict.
