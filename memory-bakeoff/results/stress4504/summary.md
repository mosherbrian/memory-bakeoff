# Memory bake-off results

| Provider | Mode | Status | Hit@5 | MRR | All relevant@5 | Prohibited@5 | Useful>harmful | Mean ctx chars | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| bm25 | raw | ok | 0.792 | 0.708 | 0.667 | 0.092 | 0.667 | 504.692 |  |
| tfidf_cosine | raw | ok | 0.792 | 0.688 | 0.750 | 0.101 | 0.818 | 431.269 |  |
| dense_lsa | raw | ok | 0.583 | 0.508 | 0.542 | 0.050 | 0.778 | 490.231 |  |
| hybrid_rrf | raw | ok | 0.708 | 0.625 | 0.667 | 0.058 | 0.700 | 520.808 |  |
