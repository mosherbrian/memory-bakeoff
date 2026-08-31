# Mem0 controlled-core findings

Pinned upstream: `mem0ai/mem0` commit `19cb89aff472325c707f64b2f34ae6afdbf7faf7`.

The sandbox cannot install Mem0's default Qdrant stack, so this is a controlled
search-policy arm, not a product run. `vendor/mem0/mem0/utils/scoring.py` matches
upstream Git blob `e85a9cb8e8b263dbab898faa07578044c0a07386` byte-for-byte.

Current Mem0 raw ingestion with `infer=False` stores each message directly after
embedding. Current search over-fetches `max(4*k, 60)` semantic candidates and then
uses `score_and_rank`. Default Qdrant only supplies the BM25 lane when optional
`fastembed` is installed; that dependency is absent here, so this arm deliberately
keeps BM25 and entity boosts inactive and uses the same shared 32-D LSA representation
as the dense control.

At k=5:

- core Hit@5 / all-relevant@5: **0.958 / 0.958**
- 500-record stress Hit@5 / all-relevant@5: **0.583 / 0.542**
- stress prohibited@5: **0.050**
- negative-empty-rate: **0.50**

The stress recall is essentially the dense-LSA control, as expected. The interesting
policy difference is Mem0's semantic threshold (`0.1`): it abstains on half of the
negative cases instead of always filling k with guesses. Product-mode Mem0 remains a
separate future test with its intended embedder, Qdrant/fastembed BM25, entity store,
and optional reranker.
