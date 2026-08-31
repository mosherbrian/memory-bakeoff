# Memory bake-off results

| Provider | Mode | Status | Hit@5 | MRR | All relevant@5 | Prohibited@5 | Useful>harmful | Mean ctx chars | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| claude_mem_fts5_core | raw | ok | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| claude_mem_chroma_lsa | raw | ok | 0.208 | 0.167 | 0.208 | 0.017 | 1.000 | 339.923 |  |
| claude_mem_chroma_lsa_no_recency | raw | ok | 0.583 | 0.508 | 0.542 | 0.050 | 0.778 | 513.885 |  |
| dense_lsa | raw | ok | 0.583 | 0.508 | 0.542 | 0.050 | 0.778 | 490.231 |  |
| tfidf_cosine | raw | ok | 0.792 | 0.688 | 0.750 | 0.101 | 0.818 | 431.269 |  |
| bm25 | raw | ok | 0.792 | 0.708 | 0.667 | 0.092 | 0.667 | 504.692 |  |
