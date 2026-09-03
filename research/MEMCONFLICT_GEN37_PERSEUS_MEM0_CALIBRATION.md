# Gen37 — Perseus and Mem0 on MemConflict, calibration scale

**Evidence class: `external_benchmark_calibration_raw_product`.** This is a
development-exposed calibration pilot on three personas, not an official
MemConflict score, not a full-release result, and not a blind evaluation. The
scored lane is the benchmark-owned `memconflict-exact-whitebox-v1` diagnostic.
`upstream_llm_judge` remains `requires_reader_authorization`: no reader, no LLM,
no external API and no GPU were used.

## What was held fixed

Frozen before either product saw a calibration question, and hashed:

| | |
|---|---|
| benchmark contract | `memconflict-benchmark-v1`, `0521210818e448c8…` |
| dataset | `Step4_4.jsonl`, `8ef9ec8589eccb86…`, upstream `ec51d5d` |
| calibration personas | the three frozen Gen36 ids, unchanged |
| Perseus adapter | `perseus-memconflict-adapter-v1`, `627f812d5296130c…` |
| Mem0 adapter | `mem0-memconflict-adapter-v1`, `920f496be7470fca…` |

Perseus runs its Gen29 identity: official v2.23.2 (`9c82920`), ordinary operator
CLI write, native hybrid recall, limit 5, fresh encrypted vault per persona,
queries served from a byte-for-byte snapshot so a read can never bias a later
one. Mem0 runs its Gen32 identity: package 2.0.19 from the pinned checkout,
`Memory.add(infer=False)`, embedded on-disk Qdrant, FastEmbed dense + BM25
sparse, native search at threshold 0.1 and limit 5, fresh store per persona.

One released dialogue message is one product write. Indexed text is the message
content and nothing else: no persona, session, turn or message identifier, no
role, no date, no label. Provenance lives in a harness ledger keyed by the
product's own write receipt, so a returned item is credited by released session
identity or not at all.

## Preflight

29 checks on unrelated synthetic content, all passing, before any exposure:
pinned identities, one message → one write, persona isolation, reads leaving the
store digest unchanged, native order preserved, every hit mapping through the
ledger, no identifiers in indexed text, no metadata written by Mem0, and
recursive rejection of every scorer-only field and of any future session.

## Contract integrity during the run

| | Perseus | Mem0 |
|---|---|---|
| unmapped provenance items | 0 | 0 |
| future-session leakage | 0 | 0 |
| empty returns | 0 | 0 |
| reads left state unchanged | yes | yes |
| label-blind repeat questions stable | 8/8 | 8/8 |

## Exact-provenance results (development-exposed)

Perseus, 380 measured questions and 19 unmeasured:

| conflict type | measured | hit@2 | hit@3 | hit@5 | log-rank@3 |
|---|---|---|---|---|---|
| dynamic | 315 | 116 | 133 | 165 | 0.351 |
| static | 36 | 4 | 6 | 13 | 0.129 |
| conditional | 29 | 27 | 29 | 29 | 0.953 |
| **overall** | **380** | **147** | **168 (44.2%)** | **207** | **0.376** |

First-support-rank distribution: rank 1 in 107 cases, rank 2 in 40, rank 3 in 21,
rank 4 in 18, rank 5 in 21, no hit in 173.

Mem0, the same 380 measured questions and the same 19 unmeasured:

| conflict type | measured | hit@2 | hit@3 | hit@5 | log-rank@3 |
|---|---|---|---|---|---|
| dynamic | 315 | 111 | 141 | 185 | 0.358 |
| static | 36 | 10 | 10 | 18 | 0.206 |
| conditional | 29 | 29 | 29 | 29 | 1.000 |
| **overall** | **380** | **150** | **180 (47.4%)** | **232** | **0.392** |

First-support-rank distribution: rank 1 in 107 cases, rank 2 in 43, rank 3 in 30,
rank 4 in 31, rank 5 in 21, no hit in 148.

The 19 unmeasured questions are conditional questions in multi-rule sessions,
exactly the set Gen36 marked unaddressable. They are excluded from every
denominator rather than scored zero.

Gen36's frozen BM25 baseline reached hit@3 110/380 on the same questions. That is
context, not a ranking: three development-exposed personas cannot support a
winner claim, and no product setting was tuned from these outcomes.

## What the shape says

Three things hold across both engines, which is what makes them worth reporting
from three personas rather than treated as noise.

**Conditional questions are nearly free.** 29/29 for both engines, and Mem0
answers every one at rank 1. The gold support session for these is the one that
established the preference rule, and the question names the item, so any
competent retriever lands on it.

**Static conflict is where both engines fail.** Perseus 6/36, Mem0 10/36. The
question asks which of two contradictory statements is true, the truth was stated
long ago, and the contradiction is recent. Retrieval by similarity has no reason
to prefer the older statement, so it mostly does not surface it. This is the
MemConflict analogue of Round 2's `false_persistence`, and it reproduces on an
external corpus built by other people.

**Both engines land on rank 1 exactly 107 times.** Identical, from completely
different retrieval stacks — Perseus's FTS5+dense RRF and Mem0's FastEmbed+BM25.
They then diverge in the tail: Mem0 recovers more support at ranks 3-5 (232
hit@5 against 207) and has 148 misses against Perseus's 173. Neither difference
is a claim about product quality on three development-exposed personas.

## Operational measurements

Gen36 estimated 0.3–1.0 seconds per write and 12–40 hours per engine for the full
release. Measured:

| | Perseus | Mem0 |
|---|---|---|
| writes | 14,304 | 14,304 |
| write latency p50 | 143 ms | 348–359 ms |
| query latency p50 | 22 ms | 394–402 ms |
| calibration wall time | 0.58 h | 1.47 h |
| store per persona | ~55 MB | ~58 MB |
| projected full release | 5.8 h, 1.65 GB | 14.7 h, 1.73 GB |

Write latency was flat across personas and across a store growing to ~4,800
records, so there is no nonlinear slowdown to report at this scale.

## A product behaviour visible only at scale

Perseus accepted 14,304 writes and ended with fewer active entities than writes.
The product said why, in its own receipts: five writes in the first persona
returned `action: "quarantined (interference score 0.909 > bound 0.900)"`, and
the same admission bound fired in the other personas. This is a native admission
decision, not loss and not a harness error, and it is invisible at Round 2's
sixteen writes. The harness records the receipt verbatim; it does not infer a
cause.

Mem0's inventory needed a correction of my own making. The count captured during
the run came from `get_all()`, whose `top_k` argument defaults to **20** and which
ignores a `limit` kwarg, so the leaf recorded 20 points against 4,762 writes — a
page size wearing the costume of a store count. Counted properly afterwards, with
`client.count(exact=True)` against each persisted collection, Mem0 holds exactly
what was written: 4,762, 4,844 and 4,698, difference zero. The reconciliation is
published in `inventory-reconciliation.json`, and the leaf's misleading number is
left in place with the explanation rather than quietly rewritten.

Perseus, counted the same way, quarantined **25 of 14,304** writes (0.17%) across
the three personas: 5, 11 and 9, every one carrying a native reason string with
its interference score.

## Gen38 recommendation — not executed

Both engines are stable, so feasibility does not force the order and accuracy must
not choose it.

**Recommendation: one full-release pass for Perseus first, then Mem0, serially.**
Perseus is projected at 5.8 hours and Mem0 at 14.7 hours, and the two projections
agree with each other to within 2% — the linear 10x estimate and the rate-based
estimate land on the same number for both engines, because per-persona stores are
isolated and write latency is flat. Total is about 20.5 hours of wall time and
3.4 GB of local storage, which is an overnight-plus-a-day job rather than the
2-7 days Gen36 feared.

Two operational notes for whoever schedules it. Mem0's query latency is 394-402 ms
against Perseus's 22-26 ms, so its 3,750 queries cost about 25 minutes against
Perseus's 90 seconds; that gap is in the projection already. And embedded Qdrant
permits one client per storage folder per process, so Mem0 personas must be opened
strictly in sequence — a parallel-persona design would need separate processes.

Hindsight and agentmemory should not advance until this pass lands, exactly as
Gen36 recommended. One retrieval pass per engine remains the right call: every
label-blind repeat was byte-identical in returned session order and score, in both
engines, so mechanically tripling 3,750 queries would buy nothing.

## Reproduction

```
scripts/preflight_memconflict_gen37_products.py
scripts/run_memconflict_gen37_calibration.py --engine perseus
scripts/run_memconflict_gen37_calibration.py --engine mem0
scripts/build_memconflict_gen37_report.py
```

Scientific content digest `63dafdf6bbc51dce3bc6f5b6dd47e912b7ab28f3d30a113acdf6d7cb80778f12`, reproduced byte for byte. Wall-clock
measurements live in `operations.json` and are deliberately outside the hashed
content.
