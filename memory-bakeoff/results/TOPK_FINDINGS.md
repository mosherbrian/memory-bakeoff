# Top-k and context-budget sensitivity

A fixed `top_k` is not a fixed prompt budget. This sweep records exact returned text size so later systems cannot improve simply by injecting much more context.

| Provider | k | Hit@k | MRR | All relevant@k | Prohibited@k ↓ | Harmful present | Mean harmful count | Mean context chars |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bm25 | 1 | 0.792 | 0.792 | 0.667 | 0.125 | 0.125 | 0.125 | 87.1 |
| bm25 | 3 | 0.875 | 0.833 | 0.750 | 0.153 | 0.417 | 0.458 | 262.9 |
| bm25 | 5 | 0.917 | 0.844 | 0.792 | 0.125 | 0.583 | 0.625 | 410.5 |
| bm25 | 8 | 0.917 | 0.844 | 0.833 | 0.079 | 0.583 | 0.625 | 631.8 |
| bm25 | 10 | 0.958 | 0.848 | 0.875 | 0.068 | 0.583 | 0.625 | 744.8 |
| dense_lsa | 1 | 0.750 | 0.750 | 0.625 | 0.083 | 0.083 | 0.083 | 84.1 |
| dense_lsa | 3 | 0.917 | 0.826 | 0.875 | 0.153 | 0.417 | 0.458 | 250.2 |
| dense_lsa | 5 | 0.958 | 0.837 | 0.958 | 0.125 | 0.583 | 0.625 | 420.6 |
| dense_lsa | 8 | 0.958 | 0.837 | 0.958 | 0.083 | 0.583 | 0.667 | 672.1 |
| dense_lsa | 10 | 0.958 | 0.837 | 0.958 | 0.067 | 0.583 | 0.667 | 862.2 |
| hybrid_rrf | 1 | 0.792 | 0.792 | 0.667 | 0.083 | 0.083 | 0.083 | 85.6 |
| hybrid_rrf | 3 | 0.917 | 0.847 | 0.792 | 0.181 | 0.500 | 0.542 | 263.7 |
| hybrid_rrf | 5 | 0.958 | 0.856 | 0.917 | 0.125 | 0.583 | 0.625 | 442.9 |
| hybrid_rrf | 8 | 0.958 | 0.856 | 0.917 | 0.078 | 0.583 | 0.625 | 711.4 |
| hybrid_rrf | 10 | 0.958 | 0.856 | 0.917 | 0.067 | 0.583 | 0.667 | 880.0 |
| tfidf_cosine | 1 | 0.667 | 0.667 | 0.542 | 0.125 | 0.125 | 0.125 | 80.0 |
| tfidf_cosine | 3 | 0.875 | 0.771 | 0.750 | 0.160 | 0.458 | 0.458 | 207.5 |
| tfidf_cosine | 5 | 0.875 | 0.771 | 0.833 | 0.153 | 0.583 | 0.625 | 297.7 |
| tfidf_cosine | 8 | 0.958 | 0.785 | 0.917 | 0.132 | 0.583 | 0.625 | 375.7 |
| tfidf_cosine | 10 | 0.958 | 0.785 | 0.917 | 0.130 | 0.583 | 0.625 | 390.7 |

## Readout

- Dense LSA reaches 0.958 Hit@5 and 0.958 all-relevant@5 at about 421 mean characters of retrieved context.
- TF-IDF reaches 0.958 Hit@8 at only about 376 mean characters, but its MRR remains much lower (0.785), all-relevant completeness is 0.917, and its prohibited fraction is higher; merely appearing somewhere in the window is not enough.
- BM25 reaches the same 0.958 hit rate only at k=10, at about 745 mean characters, and still trails dense on all-relevant completeness (0.875 vs 0.958).
- Increasing k can reduce the *fraction* of prohibited items simply because the denominator grows. The harness therefore also reports harmful-presence rate and mean harmful-item count, which do not get this cosmetic improvement.
- The benchmark will report context size with every external-engine score and should eventually add a fixed-character/token-budget retrieval condition for publication-quality comparisons.
