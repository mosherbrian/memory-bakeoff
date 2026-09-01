# MemBukkit intended-model smoke: blocked

Pinned upstream commit `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807` was cloned and installed from a separate checkout. The intended raw-model resolver names `MemseekAI/membukkit-biencoder-v1` and `MemseekAI/membukkit-reranker-v2`; direct Hugging Face snapshot requests for both returned `401 RepositoryNotFound`.

The pinned resolver catches that failure and substitutes `sentence-transformers/all-mpnet-base-v2` and `cross-encoder/ms-marco-MiniLM-L-6-v2`. Those are fallback models, not the intended upstream stack, so the harness failed closed. No sentinel ingestion/search or scored run occurred; the controlled `membukkit_core_lsa` arm remains unchanged.

Pinned `scripts/publish_weights.py` names the same unavailable repositories and no alternate official location was found. A public report independently describes the same silent-fallback behavior. This is an upstream model-publication/access blocker, not a provenance or adapter success.
