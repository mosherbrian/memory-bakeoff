# Memory bake-off results

| Provider | Mode | Status | Hit@5 | MRR | All relevant@5 | Prohibited@5 | Useful>harmful | Mean ctx chars | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| claude_mem_fts5_core | raw | ok | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| claude_mem_chroma_lsa | raw | ok | 0.208 | 0.188 | 0.208 | 0.017 | 1.000 | 458.885 |  |
| claude_mem_chroma_lsa_no_recency | raw | ok | 0.958 | 0.837 | 0.958 | 0.125 | 0.800 | 435.462 |  |
| dense_lsa | raw | ok | 0.958 | 0.837 | 0.958 | 0.125 | 0.800 | 420.577 |  |
| tfidf_cosine | raw | ok | 0.875 | 0.771 | 0.833 | 0.153 | 0.667 | 297.692 |  |
| bm25 | raw | ok | 0.917 | 0.844 | 0.792 | 0.125 | 0.800 | 410.538 |  |
