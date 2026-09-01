# Hindsight generation-5 external-PostgreSQL diagnosis

These `raw_product` Hindsight 0.9.2 runs use raw/no-LLM ingestion, pinned ONNX multilingual-e5-small, and an explicitly distinct backend: Homebrew PostgreSQL 17.11 plus pgvector 0.8.6. They do not rehabilitate invalid generation-4 pg0 results.

Three fresh 500-memory RRF runs yielded Hit@5 0.167, 0.208, and 0.250 (mean 0.208); MRR 0.094, 0.111, 0.123; prohibited@5 0.025 each. Native trace showed all 29 relevant targets in retrieval arms, RRF fusion, and final ranking, but only 3/24 positive queries in final top five: the collapse is final ranking, not candidate absence.

The normal local CPU `cross-encoder/ms-marco-MiniLM-L-6-v2` reranker produced three identical fresh stress runs: Hit@5 0.833, MRR 0.812, all-relevant@5 0.708, prohibited@5 0.083, useful-before-harmful 0.917, context 534.462 chars. It stably promotes relevant candidates while increasing prohibited presence. Native strategy-isolation arms were not run because this answers the primary Gen5 diagnostic question.
