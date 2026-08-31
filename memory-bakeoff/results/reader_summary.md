# Reader-impact evaluation

LLM backend: `chatgpt_sidecar`; mode: `raw`; top-k: 5; distractors: 0

| Provider | Status | Cases | Answer pass | Required coverage | Answers with prohibited | Notes |
|---|---|---:|---:|---:|---:|---|
| bm25 | ok | 14 | 0.857 | 0.857 | 0.000 |  |
| tfidf_cosine | ok | 14 | 0.857 | 0.857 | 0.071 |  |
| dense_lsa | ok | 14 | 1.000 | 1.000 | 0.000 |  |
| hybrid_rrf | ok | 14 | 1.000 | 1.000 | 0.000 |  |
