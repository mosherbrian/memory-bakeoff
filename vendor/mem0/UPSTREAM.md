# Mem0 vendored search policy

Pinned upstream: `mem0ai/mem0` commit `19cb89aff472325c707f64b2f34ae6afdbf7faf7`.

Exact Git-blob match:
- `mem0/utils/scoring.py` — `e85a9cb8e8b263dbab898faa07578044c0a07386`

The raw/core arm reproduces current `Memory._search_vector_store` policy with shared
LSA semantic vectors: over-fetch `max(4 * k, 60)`, semantic threshold 0.1, then the
vendored `score_and_rank`. BM25 and entity signals are explicitly inactive because
current default Qdrant only exposes BM25 when optional `fastembed` is installed, and
that dependency is not available in this sandbox. This is a controlled semantic-only
Mem0 policy arm, not a full product run.
