# agentmemory intended local-stack smoke: generation 12

Generation 12 ran a non-scored, LLM-free **raw_product** diagnostic against
the pinned upstream agentmemory service.  It does not replace the historical
shared-LSA `controlled_core` results and it publishes no core or stress score.

## Evaluated system

- Independent upstream checkout: `rohitg00/agentmemory`
  `e04ba88819c365c9acf9d6661ea802143e728bd6`, package 0.9.29.
- macOS Darwin 25.5.0 arm64; Node 26.8.1; npm 11.19.0; `iii-sdk` and the
  automatically installed, pinned `iii-engine` 0.11.2.
- Local, documented opt-in embedding configuration:
  `EMBEDDING_PROVIDER=local`, `Xenova/all-MiniLM-L6-v2`, 384 dimensions,
  mean pooling, normalized vectors, and q8 model loading.  The installed
  `@huggingface/transformers` is 4.2.0.  Its direct-download cache contains
  a 23 MB model; the q8 ONNX file SHA-256 is
  `afdb6f1a0e45b715d0bb9b11772f032c399babd23bfc31fed1c170afc848bdb1`.
  This loader does not retain an upstream revision identifier, so the content
  hash—not an invented snapshot revision—is the recorded identity.
- LLM provider: `noop`.  `CONSOLIDATION_ENABLED=false`,
  `GRAPH_EXTRACTION_ENABLED=false`, and `AGENTMEMORY_AUTO_COMPRESS=false`,
  all consistent with the pin's LLM-free raw operation.  No API key, paid
  model, or synthetic/fake embedding was used.
- BM25 plus in-memory cosine vector index, weighted RRF with `k=60`, BM25
  weight 0.4, vector weight 0.6, 5% stream-agreement bonus, candidate depth
  `2 * limit`, then session diversification (maximum three per session).
  Structural graph retrieval is registered but had no LLM-produced graph
  records.  The learned reranker is controlled by `RERANK_ENABLED === "true"`
  and was not enabled (its source default); no reranker model was loaded.
- Native state is held by the pinned iii runtime in an isolated temporary
  SQLite-backed data directory with persisted BM25/vector index support.  The
  service reported 139,182,080 bytes RSS after local-model use.  This is a
  process footprint, not a model-only measurement.

Source references: local embedder
`external/agentmemory/src/providers/embedding/local.ts:8-46`; provider
selection and default weights `src/config.ts:254-281` and
`src/providers/embedding/index.ts:30-50`; hybrid retrieval
`src/state/hybrid-search.ts:20-258`; optional reranker
`src/state/reranker.ts:1-73`; index/runtime wiring `src/index.ts:372-459`.

## Native provenance and scope result

The earlier adapter assumed an arbitrary `type` marker survived `/remember`.
That is false at this pin: unsupported types are normalized to `fact`
(`external/agentmemory/src/functions/remember.ts:50-60`).  The supported
`sourceObservationIds` field does survive storage and `/remember` returns a
native `mem_*` ID; `/smart-search` returns the corresponding native `obsId`.
The adapter now records this returned native-ID-to-canonical-ID mapping and
never performs fuzzy/subtext reconciliation.

Within one isolated project, all eight lifecycle writes had exact native
lineage.  However, that alone is insufficient for a benchmark run.  The
service accepts `project` on `/remember`, but this pin does **not** apply it as
a retrieval filter:

- `/agentmemory/memories?project=...` lists every memory and implements only
  `agentId` filtering (`src/triggers/api.ts:1921-2003`).
- `/agentmemory/smart-search` calls the hybrid searcher without passing
  `project`; the supplied project is used only by the separate lesson lookup
  (`src/functions/smart-search.ts:189-210`).

A separate five-record native-provenance retrieval smoke consequently returned
three records from its own ingest trace and two native IDs from a different
sentinel project.  The updated adapter raises immediately on such an unknown
native ID.  This is correct fail-closed behavior, but it means a scoped
multi-project raw-product score is currently **blocked by product retrieval
contamination**, not by missing provenance transport.

## Lifecycle sentinel

The authoritative non-scored trace is
`results/agentmemory_raw_product_gen12_lifecycle_smoke_clean/trace.json`.
It contains every POST response and a complete native state snapshot after
every operation.  The snapshot helper preserves the server's unfiltered list
response and derives its operation-local count from stored native `project`
metadata, rather than trusting the ignored query filter.

The eight chronological writes used six canonical IDs: old/current build
coordinator (`M011`, `M012`), exact duplicate and paraphrase of `M012`, two
distinct Redis near-neighbors (`M035`, `M036`), and failed/successful generated
Go procedures (`M024`, `M023`).

| Check | Native outcome | Lifecycle classification |
|---|---|---|
| Explicit correction `M011 → M012` | Both remained live; no parent/supersedes relation | Failed stale-value consolidation. Source Jaccard was 0.273, below the strict `> 0.7` rule. |
| Exact duplicate of `M012` | New native ID superseded the earlier `M012`; one retired and two live after the write | Legitimate duplicate supersession. |
| Paraphrase of `M012` | Added as another live `M012`-sourced memory | Duplicate retention; Jaccard 0.308, so the raw rule is lexical-overlap rather than semantic deduplication. |
| `M035` preview vs `M036` development Redis facts | Both survived live | No false collision in this small pair; Jaccard 0.444. This does not overturn the historical 450-distractor controlled finding. |
| `M024` failed vs `M023` successful generated-code procedure | Both survived live | No destructive merge; Jaccard 0.069. Failed procedure remained searchable. |

Final state: eight writes, eight total native rows, seven live rows, one retired
exact duplicate.  Thus the small-sentinel false-supersession rate is 0/5
distinct incoming writes (0%), live survival for distinct facts is 5/5, and
the old correction fact `M011` remains live.  These narrow figures do not
contradict the earlier 418/450 controlled stress failure; they show that this
small canonical subset sits below the same fixed lexical threshold.

The current-build-coordinator query ranked stale `M011` first, followed by the
two current `M012` variants.  The successful generated-code procedure ranked
first for its query, but the failed procedure remained rank two.  Therefore
the pin neither makes an explicit correction win automatically nor suppresses
a prior failed procedure through its write-time lifecycle rule.

`results/agentmemory_raw_product_gen12_lifecycle_smoke/` is retained with
`INVALID.md`: it was an earlier trace whose snapshot counts included a prior
project because the endpoint did not filter it.  No score was computed from
either directory.

## Exact supersession mechanics

`/remember` retrieves up to 50 BM25 candidates (or full-scans only before the
memory index is ready), skips cross-project candidates during *write-time*
comparison, and supersedes the first latest candidate whose normalized token
Jaccard is strictly greater than 0.7.  It marks that predecessor `isLatest`
false and removes it from both indexes; the historical row remains in KV.
The new row gets a fresh ID, `parentId`, and `supersedes` list
(`src/functions/remember.ts:71-241`; tokenization and score
`src/state/schema.ts:95-153`).  Embeddings and reranking do not choose this
supersession candidate set.

## Result and next gate

The intended local stack is provisioned and its native ingestion, local model,
BM25/vector retrieval, exact lineage, and lifecycle state were exercised.  No
authoritative score is publishable yet because project scope is not enforced by
the product search surface.  The future adapter is prepared to fail closed;
do not work around the issue by filtering results in the harness or by fuzzy
mapping foreign records.  A later run needs either a documented upstream
retrieval scope that actually isolates the benchmark bank (for example a
verified isolated `agentId` deployment) or an upstream fix/pin change, both
tested before any core/stress repetitions.
