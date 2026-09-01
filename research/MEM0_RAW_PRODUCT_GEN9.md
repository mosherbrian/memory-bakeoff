# Mem0 raw-product integration and sentinel

Generation 9 prepared the first faithful Mem0 raw-product configuration.  It
does not publish a core or stress score, and it leaves the historical
shared-LSA `controlled_core` result unchanged.

## Verified upstream and local stack

- Upstream checkout: `mem0ai/mem0`
  `19cb89aff472325c707f64b2f34ae6afdbf7faf7`; its package metadata identifies
  this checkout as `mem0ai` 2.0.19.  The adapter refuses the vendored
  controlled-core copy and records the loaded upstream source path.
- Raw ingestion: upstream `Memory.add(..., infer=False)`, which stores one raw
  benchmark record at a time without LLM extraction, consolidation, or update
  policy.  Mem0 constructs an OpenAI client at `Memory` initialization, so the
  adapter supplies a non-secret placeholder; no LLM call occurs in raw mode.
- Dense embedder: Mem0's supported FastEmbed provider with its source default
  `thenlper/gte-large`, which FastEmbed 0.8.0 resolves to
  `qdrant/gte-large-onnx` snapshot
  `770e825c74a004f165b78793f7c8fc4a95280878`, 1024 dimensions, ONNX Runtime
  1.29.0, CPU.  FastEmbed emitted its current warning that this model now uses
  mean pooling rather than its historical CLS pooling; that is documented
  runtime behavior, not a harness change.
- Vector/lexical store: real embedded persistent Qdrant client 1.19.0 with a
  fresh per-run on-disk collection, dense cosine vectors, and the named `bm25`
  sparse-vector slot.  FastEmbed's `Qdrant/bm25` snapshot was
  `22b8d2af71a76161e18dd432d2cee0eefa66e412`.  The BM25 lane executed in both
  insertion and search.
- Entity lane: inactive in this environment because `spacy` is not installed;
  Mem0 logged the missing lemma/full model and generated no entity boosts.

The initial direct smoke exposed a genuine explicit-config requirement: Qdrant
would otherwise create its generic 1536-D collection while FastEmbed's normal
model produces 1024-D vectors.  The raw-product adapter now configures matching
1024-D dimensions explicitly.  This is a configuration correction, not a
Mem0 retrieval-semantic patch.

## Sentinel and provenance

A six-record, non-scored sentinel included the M011/M012 correction pair and
near-neighbor records M026, M033, and M035.  It completed raw insertions and a
search through upstream Mem0, FastEmbed, and Qdrant.  Returned Mem0 search rows
carried their native Mem0 UUID plus stored `metadata.record_id`; the adapter
maps only that native metadata to a canonical benchmark ID.  The retrieved
items had native provenance (no marker, fuzzy, or subtext reconciliation).

After closing the embedded client, reopening the same Qdrant path/collection
returned five rows with native IDs and an active BM25 score.  This verifies
clean persistence/reopen behavior.  The temporary stores and model caches are
outside the repository and untracked.

## Actual search semantics for the prepared configuration

Pinned `Memory._search_vector_store` does the following:

1. scopes Qdrant by `filters={"user_id": "memory-bakeoff"}`;
2. embeds the query with the FastEmbed dense model;
3. fetches `max(4 * top_k, 60)` dense candidates;
4. performs Qdrant sparse BM25 search over the same scope;
5. applies Mem0's query-length-dependent sigmoid normalization to BM25;
6. applies entity boosts only if entity extraction is available;
7. rejects dense candidates below the explicit semantic threshold (0.1 by
   default) *before* hybrid scoring; and
8. ranks by the additive score divided by active signal weight (2.0 with dense
   plus BM25; 2.5 if entity boosts are also active).

This confirms that the earlier controlled arm's 0.1 refusal/abstention behavior
is present in the real product path.  The next requested score run should keep
this exact configuration—same source checkout, FastEmbed/Qdrant snapshots,
threshold, scope, and no-LLM raw insertion—and execute three fresh core plus
three fresh stress repetitions only after explicit instruction.
