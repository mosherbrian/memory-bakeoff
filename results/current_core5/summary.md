# Memory bake-off results

| Provider | Mode | Status | Hit@5 | MRR | All relevant@5 | Prohibited@5 | Useful>harmful | Mean ctx chars | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| bm25 | raw | ok | 0.917 | 0.844 | 0.792 | 0.125 | 0.800 | 410.538 |  |
| tfidf_cosine | raw | ok | 0.875 | 0.771 | 0.833 | 0.153 | 0.667 | 297.692 |  |
| dense_lsa | raw | ok | 0.958 | 0.837 | 0.958 | 0.125 | 0.800 | 420.577 |  |
| hybrid_rrf | raw | ok | 0.958 | 0.856 | 0.917 | 0.125 | 0.733 | 442.885 |  |
| habitus | raw | ok | 0.875 | 0.785 | 0.750 | 0.097 | 0.923 | 264.577 |  |
| membukkit | raw | ok | 0.958 | 0.525 | 0.958 | 0.125 | 0.667 | 410.500 |  |
| agentmemory_core_lsa | raw | ok | 0.958 | 0.868 | 0.958 | 0.125 | 0.933 | 444.769 |  |
