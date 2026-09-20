# row-membukkit-receipts — MemBukkit LongMemEval 92.6% consistency check

Fetched 2026-09-12 ~19:2x PDT by Alice (worker-glm-dsh), RD pulse, at pin
f28a2e58cdc0e77758c0f6d9a1e050f80dcad807.

| file | source | bytes | sha256 |
|---|---|---|---|
| README.md | raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/README.md | 14923 | a462d9cc3ad652b017ffbb9e2679fc02fda609cf51c8751784d7175706d4eef3 |
| docs_guide_benchmarks.md | raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/docs/guide/benchmarks.md | 11656 | 11c34675e7cca39c0c05bf8483da8961f9e308f8b1e78efee554af24fa5040da |
| benchmarks_PAPER_RESULTS.md | raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/benchmarks/PAPER_RESULTS.md | 6454 | 2d43067d78793e6bf7cb0df5a6ab8eddef00807221b4ecece0b9589e960cc669 |
| benchmarks_RESULTS_TABLE.md | raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/benchmarks/RESULTS_TABLE.md | 6630 | eac6f73bb30f90ed4bb8212ad63b7bf690dff526fa460c901f0179f2a2bb4b83 |
| benchmarks_README.md | raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/benchmarks/README.md | 18942 | c1c7aa962fdc569bb3af45b55a46b1bea6e17fb1da5f97439a0d5b365db54052 |
| benchmarks_common_metrics.py | raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/benchmarks/common/metrics.py | 4403 | 1e583d9c1b20fb8ac21ec78697daa5a7cbd2dac5ef2c5888df96080d40c14e81 |

Consistency observations (grep of the fetched docs):
- '92.6%' LongMemEval-S appears in README.md (3x) and docs/guide/benchmarks.md (5x): gpt-5.4 reader, official gpt-4o judge, text-embedding-3-large@1536.
- The numeral 92.6 ALSO appears in benchmarks/PAPER_RESULTS.md as a 2Wiki R@5 (retrieval recall) - different metric, different benchmark.
- benchmarks/RESULTS_TABLE.md contains no '92.6' (LongMemEval number lives in README + the benchmarks guide, not the results table).
- No results/bench/longmemeval-* run artifact exists in the repo tree at the pin; --check reads a locally generated run.
