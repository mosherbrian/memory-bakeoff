# MemBukkit intended models on the MemConflict calibration slice

**Evidence class:** `external_benchmark_calibration_raw_product_exact_provenance`, lane `memconflict-exact-whitebox-v1`.
**Development-exposed calibration on three personas. Not an official MemConflict score, not a
full release, no reader, no upstream judge.** `upstream_llm_judge` remains
`requires_reader_authorization`.

The question was not who wins. It was whether a third, architecturally different product shows
the same static-versus-conditional asymmetry the first two showed, and whether MemBukkit's
routing trace reveals a different cause. Both halves have an answer, and the second one is the
reason this generation was worth running.

## What ran

MemBukkit source `f28a2e58cdc0` — the Gen7/Gen8/Gen40/Gen41 pin. Intended
MemseekAI models at the Gen40 revisions, every file reconciled to its committed manifest before
exposure and offline thereafter. Gen41 raw-product retrieval, `union_lanes=("atomic",)`. Both
models proven on `mps:0`, the frozen product-default identity. No distiller, no LLM, no reader,
no external API; the network was blocked at the socket layer before the first write.

The frozen Gen37 procedure ran unchanged — this generation registers an engine into it rather
than reimplementing it — and the frozen Gen37 scorer and Gen38 static-mechanism diagnostic
produced the numbers below, so they are comparable with the committed calibration results by
construction.

Totals: 14,304 writes of
14,304 attempted, 3 malformed
messages excluded and counted, 14,304 distinct native ids,
0 write failures, 399 questions.

## Adapter, frozen before exposure

`membukkit-memconflict-adapter-v1`. Indexed text is the released message content alone. The write
receipt is an opaque ordinal assigned in write order — never a persona, session, turn or question
identifier — and is never indexed. The query is the released question text alone. Nothing from
the scorer side is written, queried or stored.

One product property forced a decision worth stating plainly. MemBukkit selects by relevance and
then **re-presents the selected hits in date order**, so the order of the public
`MemorySearchResult.hits` is a presentation property, not a ranking. Taking rank off that surface
would have scored a date sort. This adapter reads rank from the relevance order the product
returns internally, and requires per query that it holds exactly the same records the public
surface returned. The equivalence is proven on every one of the
399 questions, not assumed once.

Preflight, on invented content only: bad payloads rejected, six of six synthetic writes mapped,
two messages with identical text kept as two rows under distinct receipts, store isolation
between universes, reads leaving the state digest unchanged, the LLM path refusing rather than
merely unused, and the frozen chronology function raising on a future-session unit.

## Result

Measured 380, unmeasured 19
— the same measured denominator as the committed Perseus and Mem0 calibration, so the columns
below line up question for question.

| metric | MemBukkit | Perseus | Mem0 | BM25 pilot |
| --- | --- | --- | --- | --- |
| Hit@3 | **0.3237** | 0.4421 | 0.4737 | 0.2895 |
| Hit@2 | 0.2684 | — | — | — |
| Hit@5 | 0.4079 | — | — | — |
| log-rank@3 | 0.2621 | 0.3756 | 0.3924 | — |

By conflict class, Hit@3:

| class | measured | hits | MemBukkit | Perseus | Mem0 |
| --- | --- | --- | --- | --- | --- |
| dynamic conflict | 315 | 100 | 0.3175 | 0.4222 | 0.4476 |
| static conflict | 36 | 5 | 0.1389 | 0.1667 | 0.2778 |
| conditional conflict | 29 | 18 | 0.6207 | 1.0000 | 1.0000 |

First-support rank distribution: 1: 67 | 2: 35 | 3: 21 | 4: 15 | 5: 17 | no_hit: 225.

Per persona:

| persona | measured | unmeasured | Hit@3 | rate |
| --- | --- | --- | --- | --- |
| 40a79d0c | 121 | 7 | 38 | 0.3140 |
| 737e8d59 | 129 | 4 | 45 | 0.3488 |
| e02dd733 | 130 | 8 | 40 | 0.3077 |

Contract integrity: 0 unmapped provenance
items, 0 empty returns,
0 returns under five,
0 future-session leaks,
0 write failures, 0
native id replacements. Inventory reconciles exactly on all three personas.

## The finding: static failure is a ranking failure, and now that is measured, not inferred

Gen38 concluded from an admission diagnostic that static failure in Perseus and Mem0 is a ranking
problem rather than an availability problem. MemBukkit allows a sharper test, because its router
opens only part of the bank before the cross-encoder ever sees a candidate. If static failure
were unreachability, the gold record would sit outside the opened region.

It never does.

| static questions | count |
| --- | --- |
| gold support present in the write ledger | 36 |
| hit at 5 | 6 |
| miss, gold **entered** the opened region and lost before the top five | 30 |
| miss, gold never entered the opened region | 0 |

Every static miss — 30 of
30 — had its gold support inside the
candidate region the router opened. Routing exclusion accounts for
0% of static misses and rank loss for
100%. The router opened a median
32.0% of the bank, and the right record was in it every time.

So a third engine, with a different architecture — topic routing, a fine-tuned cross-encoder, and
rank fusion rather than a vector store with a scoring head — fails the same class in the same
place. The record is stored, searchable, and inside the candidate set the reranker scores. It
still does not reach the top five.

The static mechanism split says the same thing from the scorer side. At K3, of
36 static questions,
25 return neither the truth session nor
the contradicting one, 6 return the
contradiction without the truth, 4 return
the truth alone and 1 return both.
"Retrieval prefers the newer contradiction" describes a minority here too.

## Where MemBukkit differs from the other two

Conditional questions. Perseus and Mem0 both sit at 1.0000 on this slice; MemBukkit is at
0.6207. That is the one class
where this product behaves qualitatively differently rather than by a few points, and it is the
main reason its overall Hit@3 lands below both — above the lexical baseline, below the two vector
products. On 29 measured conditional questions across three development-exposed personas, that
gap is worth naming and not worth ranking.

## Determinism

8 label-blind repeat probes against the same unchanged state:
returned order identical 8/8,
selected set identical 8/8,
numeric scores identical 8/8. Reported as
three quantities, not one boolean. Read-side-effect audits found no state change from querying.

## Operations, secondary

Write p50 about 22 ms and query p50 about 1.7 to 1.9 seconds per persona; roughly six minutes per
persona end to end. The query cost is the cross-encoder scoring the opened region on every
question. Scan fraction: p50 0.3205, p90
0.3422, max 0.3617 over
399 queries, derived from the native trace. Capacity is not quality and
timing sits outside the scientific digest.

## Reading rules

Three development-exposed personas. No global winner claim is available from this slice and none
is made. The direct raw path is append and dedupe with no product supersession, verified rather
than assumed: 0 native id replacements and no superseded
rows. Product-default MPS is part of this evaluated-system identity; nothing here claims a forced
CPU run would score the same, and Gen41 measured that it would not be identical.

Scientific digest `7f133d612cfa2e3d0c441546561d421f998688975c072e3c1cf8917f191468f2`, rebuilt with wall-clock and per-item latency
excluded. Adapter `67b80e22625d2e8c84259d600d9f783a04012d3bdd43037f7fde56018231140b`, engine module `a009dedcc0de5c5e1214ac355558f470a84c353f0d3835767dafac10e152670d`.
