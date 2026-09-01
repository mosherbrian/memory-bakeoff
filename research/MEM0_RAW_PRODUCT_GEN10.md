# Mem0 raw-product benchmark: generation 10

This is the first scored Mem0 **raw_product** retrieval result.  It evaluates
the frozen Generation 9 configuration, not the historical shared-LSA
`controlled_core` arm and not Mem0's normal LLM-backed extraction/update
product mode.

## Evaluated system

- Upstream `mem0ai/mem0` commit
  `19cb89aff472325c707f64b2f34ae6afdbf7faf7`, package 2.0.19, loaded from an
  independent checkout (the adapter rejects the vendored controlled source).
- Upstream `Memory.add(..., infer=False)`: one canonical fact per raw memory;
  no LLM extraction, update, or supersession.  Mem0 constructs but never calls
  its LLM client in this mode.
- FastEmbed 0.8.0 dense `thenlper/gte-large`, resolved by FastEmbed to
  `qdrant/gte-large-onnx` snapshot
  `770e825c74a004f165b78793f7c8fc4a95280878`, 1024-D, ONNX Runtime 1.29.0 on
  CPU.
- Fresh on-disk embedded Qdrant client 1.19.0 per repetition, dense cosine and
  sparse FastEmbed `Qdrant/bm25` snapshot
  `22b8d2af71a76161e18dd432d2cee0eefa66e412`.
- Scope `user_id=memory-bakeoff`; threshold 0.1; vector candidate depth
  `max(4*k, 60)`; Mem0's additive dense + normalized-BM25 fusion.  Entity boosts
  are inactive because spaCy is absent.

Every returned item in each authoritative run had native Mem0 UUIDs and the
stored native `metadata.record_id`; all 130 returned items per run mapped
directly to canonical IDs.  The adapter fails closed rather than using fuzzy or
subtext reconciliation.

## Results, k=5

Each condition used three independent fresh Qdrant collections.  Relevance and
context metrics were identical across repetitions; the ranges below therefore
show only latency variation.

| Condition | Hit@5 | Recall@5 | Precision@5 | MRR | All relevant@5 | Prohibited@5 | Harmful presence | Mean prohibited count | Useful before harmful | Empty negatives | Context chars | Context words | Retrieval latency ms (mean; range) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Core, 50 records | 1.000 | 0.979 | 0.233 | 0.889 | 0.958 | 0.142 | 0.667 | 0.708 | 0.688 | 0.000 | 434.9 | 64.8 | 791.5; 311.8–1683.6 |
| Stress, 500 records | 0.958 | 0.938 | 0.225 | 0.896 | 0.917 | 0.100 | 0.500 | 0.500 | 0.800 | 0.000 | 519.0 | 75.2 | 537.6; 522.5–562.2 |

Authoritative directories are `results/mem0_raw_product_gen10_core-r{1,2,3}`
and `results/mem0_raw_product_gen10_stress-clean-r{1,2,3}`.

## Negative-query behavior

The earlier shared-LSA controlled policy arm had negative-empty-rate 0.50.  In
this real FastEmbed + Qdrant + BM25 configuration, Q025 and Q026 each returned
five memories in every core and stress repetition.  Consequently,
negative-empty-rate was 0.0 in both conditions.  The threshold was frozen at
0.1; it was not adjusted after observing this difference.

## Comparison boundary

The older `mem0_core_lsa` arm held representation constant and reported core
Hit/all-relevant 0.958/0.958 and stress 0.583/0.542, with stress prohibited@5
0.050 and negative-empty-rate 0.50.  The new raw-product row uses a real
pretrained embedder, real Qdrant, and active BM25, so its stronger stress result
is a result for this complete raw retrieval stack—not evidence that the
controlled policy arm was a product score or that either row measures LLM-backed
Mem0 lifecycle behavior.

One duplicate-process stress artifact is preserved in
`results/mem0_raw_product_gen10_stress-r1` with `INVALID.md`; it is excluded
from every number above.
