# Memory bake-off results

| Provider | Mode | Status | Hit@5 | MRR | All relevant@5 | Prohibited@5 | Useful>harmful | Mean ctx chars | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| bm25 | raw | ok | 0.792 | 0.708 | 0.667 | 0.092 | 0.667 | 504.692 |  |
| tfidf_cosine | raw | ok | 0.792 | 0.688 | 0.750 | 0.101 | 0.818 | 431.269 |  |
| dense_lsa | raw | ok | 0.583 | 0.508 | 0.542 | 0.050 | 0.778 | 490.231 |  |
| hybrid_rrf | raw | ok | 0.708 | 0.625 | 0.667 | 0.058 | 0.700 | 520.808 |  |
| habitus | raw | ok | 0.792 | 0.701 | 0.667 | 0.025 | 0.909 | 552.038 |  |
| membukkit | raw | ok | 0.583 | 0.329 | 0.542 | 0.042 | 0.778 | 485.308 |  |
| agentmemory_core_lsa | raw | ok | 0.583 | 0.493 | 0.500 | 0.042 | 0.667 | 507.962 |  |
| agentmemory_remember_lsa | raw | ok | 0.792 | 0.608 | 0.750 | 0.117 | 0.714 | 475.731 |  |
