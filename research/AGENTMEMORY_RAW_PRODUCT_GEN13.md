# agentmemory raw-product benchmark: generation 13

Generation 13 is the first authoritative retrieval benchmark for the pinned
agentmemory product's documented LLM-free local-embedding path.  It is a
**raw_product** result, not a complete `product` evaluation: no LLM
extraction, consolidation, graph extraction, automatic compression, or learned
reranking was enabled.

## Scope and isolation gate

The pin accepts a `project` field at write time but does not use it to isolate
`/agentmemory/smart-search`.  This run therefore did not depend on `project`
as a harness filter.  Each repetition used a fresh iii data directory and a
distinct native `agentId`; the adapter sends that ID to both supported product
endpoints and does not remove or rerank returned rows.

The successful preflight is preserved at
`results/agentmemory_raw_product_gen13_isolation_preflight-r2/preflight.json`:

- In fresh state A, two records written with different `project` labels but the
  same native agent were both returned by native smart search.
- In fresh state B with a different native agent and independent database,
  neither state-A native ID was returned and the native `/memories` list had
  `total: 0`.

The unsuffixed preflight directory is retained as a failed launcher attempt.
It has no score: the original synchronous CLI invocation waited for the
foreground service command to exit before health probing.  The reusable runner
now launches that documented local CLI asynchronously, waits on `/health`, and
records the clean retry separately rather than replacing the failed artifact.

## Evaluated system

- Upstream: `rohitg00/agentmemory` commit
  `e04ba88819c365c9acf9d6661ea802143e728bd6`, package 0.9.29.
- Host: macOS 26.5.1 arm64 (Darwin 25.5.0), CPython 3.13.15; Node 26.8.1;
  iii-engine 0.11.2.
- Ingestion/retrieval: native `/agentmemory/remember` and
  `/agentmemory/smart-search`, with exact `sourceObservationIds -> mem_* ->
  obsId` lineage.  Every scored row had verified native provenance.
- Embeddings: `EMBEDDING_PROVIDER=local`, q8
  `Xenova/all-MiniLM-L6-v2`, 384 dimensions, `@huggingface/transformers`
  4.2.0.  The downloaded ONNX hash is
  `afdb6f1a0e45b715d0bb9b11772f032c399babd23bfc31fed1c170afc848bdb1`.
- Retrieval: product in-memory cosine plus BM25 RRF (`k=60`, vector 0.6,
  BM25 0.4), 5% stream-agreement bonus, candidate depth `2 * limit`, and at
  most three results per session.  `top_k=5`.
- Disabled, intentionally and explicitly: LLM provider/extractor,
  `CONSOLIDATION_ENABLED`, `GRAPH_EXTRACTION_ENABLED`,
  `AGENTMEMORY_AUTO_COMPRESS`, and learned reranking.

The exact per-run environment, native ingest traces, returned IDs, context
sizes, lifecycle state, and service start/stop records are in the six result
directories named `agentmemory_raw_product_gen13_{core,stress}-r{1,2,3}`.

## Authoritative repeated results

All repetitions were deterministic under the frozen local configuration.

| Condition | Repetitions | Hit@5 | MRR | All-relevant@5 | Prohibited@5 | Harmful presence | Useful before harmful | Mean returned chars |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Core, 50 records | 3 | 1.000 | 0.889 | 1.000 | 0.142 | 0.667 | 0.688 | 428.5 |
| Stress, 500 records | 3 | 1.000 | 0.847 | 0.958 | 0.133 | 0.625 | 0.688 | 495.7 |

The scores are publishable as `raw_product` retrieval results because every
returned native ID mapped exactly to a canonical benchmark record.  They must
not be promoted to complete product scores or compared as if lifecycle loss
were a retrieval improvement.

## Safety and lifecycle finding

Core retained all 50 native memories.  In every stress repetition, the product
retained 82 live memories and retired 418.  All 418 retired records were
stress distractors, and all 418 successor relationships were false against the
harness's explicit `supersedes_id` truth: **418/450 distinct stress
distractors, 92.9%, were falsely superseded**.  There were zero legitimate
benchmark correction supersessions.

Consequently, the raw retrieval score above must be read beside the lifecycle
result, not as credit for making the stress bank easier by deleting valid
near-neighbor records.  Each `lifecycle.json` lists every retired native ID,
its incoming successor, its canonical IDs, and the classification.

## Retrieval behavior worth retaining

- Corrections were retrieved but stale versions were also present: Q007 put
  stale M011 before current M012; Q008/Q009 returned current and prohibited
  historical values together; Q022 put stale M041 before M042.
- All five success/failure procedure pairs (Q014–Q018) retained and commonly
  returned the prohibited failure alongside the relevant successful workflow.
- Scope collisions were not cleanly filtered by benchmark scope.  For example,
  core Q019 returned Atlas M029 plus Beacon M030; stress Q020/Q021 returned
  the prohibited cross-repository owner/version.  This is expected from the
  product retrieval surface evaluated here: native `agentId` isolates the
  deployment, not each record's `project` or benchmark scope.

No reader evaluation was run in this generation.  The next publication should
feed these already-validated retrieval traces into the existing deterministic
reader separately; it must not rerun or overwrite this engine evidence.
