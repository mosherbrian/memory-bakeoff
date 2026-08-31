# Memory bake-off results

| Provider | Mode | Status | Hit@5 | MRR | All relevant@5 | Prohibited@5 | Useful>harmful | Mean ctx chars | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| bm25 | raw | ok | 0.917 | 0.844 | 0.792 | 0.125 | 0.800 | 410.538 |  |
| dense_lsa | raw | ok | 0.958 | 0.837 | 0.958 | 0.125 | 0.800 | 420.577 |  |
| hybrid_rrf | raw | ok | 0.958 | 0.856 | 0.917 | 0.125 | 0.733 | 442.885 |  |
| mem0 | raw | unavailable | — | — | — | — | — | — | mem0 Python package not installed |
| agentmemory | raw | unavailable | — | — | — | — | — | — | service unavailable at http://127.0.0.1:3111: ConnectionError |
| membukkit | raw | unavailable | — | — | — | — | — | — | membukkit package not installed |
| habitus | raw | unavailable | — | — | — | — | — | — | habitus-ai package not installed |
| claude_mem | raw | ineligible | — | — | — | — | — | — | provider does not expose a supported raw/no-LLM ingestion path |
| hindsight | raw | unavailable | — | — | — | — | — | — | service unavailable at http://127.0.0.1:8888: ConnectionError |
