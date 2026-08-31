# Reader-impact findings

This is the first **real LLM reader** trial in the bake-off. GPT-5.6 Sol in the current ChatGPT conversation read only each provider's retrieved context. The benchmark harness, not the model, graded every answer deterministically.

## Result

| Provider | Cases | Answer pass | Required coverage | Prohibited-answer rate |
|---|---:|---:|---:|---:|
| bm25 | 14 | 0.857 | 0.857 | 0.000 |
| tfidf_cosine | 14 | 0.857 | 0.857 | 0.071 |
| dense_lsa | 14 | 1.000 | 1.000 | 0.000 |
| hybrid_rrf | 14 | 1.000 | 1.000 | 0.000 |

## Interpretation

- Dense LSA and hybrid RRF supplied enough evidence for the reader to answer all 14 deterministic cases correctly.
- BM25 passed 12/14; both misses were retrieval omissions, and the reader correctly returned `INSUFFICIENT_MEMORY` rather than guessing.
- TF-IDF also passed 12/14, but its failure shape differed: Q008 surfaced only the obsolete deploy command, so the grounded reader emitted a prohibited stale answer; Q016 was an evidence omission and produced `INSUFFICIENT_MEMORY`.
- Q012 exposed multi-hop completeness: BM25 missed part of the credential chain, while TF-IDF/dense/hybrid supplied the secret → Terraform module → workflow chain.
- Q016 exposed procedural retrieval: BM25 and TF-IDF omitted the verified-success NDJSON diagnostic memory; the reader abstained.

## Failed cases

| Provider | Case | Reader answer | Retrieved IDs |
|---|---|---|---|
| bm25 | Q012 | INSUFFICIENT_MEMORY | `['M017', 'M040', 'M039', 'M045', 'M050']` |
| bm25 | Q016 | INSUFFICIENT_MEMORY | `['M028', 'M009', 'M039', 'M050', 'M022']` |
| tfidf_cosine | Q008 | deployctl push --region west | `['M032', 'M031', 'M022', 'M013', 'M045']` |
| tfidf_cosine | Q016 | INSUFFICIENT_MEMORY | `['M009', 'M028', 'M010', 'M046', 'M044']` |

The archived 56-request sidecar trace under `results/sidecar_reader_trace/` contains the exact OpenAI-shaped requests and responses used for this result.
