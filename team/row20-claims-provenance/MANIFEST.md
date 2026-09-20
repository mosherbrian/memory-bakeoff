# row20 provenance fetch receipts

Fetched 2026-09-12 ~17:0x PDT by Alice (worker-glm-dsh), QUEUE row 20.
Raw curl bodies; sha256 over exact bytes. GitHub API JSONs are commit-history
responses used for the first-appearance scans (the .txt files).

| file | source | pin / as-of | role | bytes | sha256 |
|---|---|---|---|---|---|
| mem0-paper-v1.html | https://arxiv.org/html/2504.19413v1 | arXiv v1 2025-04-28 | origin of LangMem 58.10, Zep 65.99, OpenAI 52.90, Mem0 66.88/68.44 | 244706 | 999aea13b219b6fc761cbb517df11dda2c8d9ae0ebf7cdd9b7c0482777005436 |
| zep-paper-v1.html | https://arxiv.org/html/2501.13956v1 | arXiv v1 2025-01-20 | origin of DMR 94.8/93.4, +18.5%, -90% | 137854 | 8a16259db129b4109331df4aa17c404115eceb1d7f2df40d06bc34def7c27049 |
| zep-blog.html | https://blog.getzep.com/zep-a-temporal-knowledge-graph-architecture-for-agent-memory/ | published 2025-01-22 (mutable) | copy of the same DMR text, 2 days after paper v1 | 42009 | 8baa4dd10c5ef329442a1dd45b95456ce4521b0fcf956524cd1ba3cac5e0d232 |
| a_mem-abs-v1.html | https://arxiv.org/abs/2502.12110v1 | arXiv v1 2025-02-17 | first appearance of the six-models/SOTA sentence | 44250 | e4059bc6f5c5dc1fdfe812e29223cd57bd6a8488862cfa62f8cfeb6a90a92013 |
| memos-abs-v1.html | https://arxiv.org/abs/2507.03724v1 | arXiv v1 2025-07-04 | first appearance of memory-OS/MemCube wording | 49394 | 3be958568963f4db1873848d899d1461e7cb55d5bb5f00f57107a024e3d5c67f |
| memgpt-abs-v1.html | https://arxiv.org/abs/2310.08560v1 | arXiv v1 2023-10-12 | first appearance of virtual-context/memory-tiers | 42390 | f53e987e6effdf69589f0fce65c2c90a7159104c0ea3df9e85ff6ae84e0cfa57 |
| memos-paper-v1.html | https://arxiv.org/html/2507.03724v1 | arXiv v1 | grep: 88.83=0, OmniMemEval=0 (numbers NOT in paper) | 471494 | 9debb47805d1389a7a3b23b1be33b5d50f4b5d6bf9aa745c9419e57cc9daee71 |
| memos-paper-v4.html | https://arxiv.org/html/2507.03724v4 | arXiv v4 | grep: 88.83=0, OmniMemEval=0 | 491503 | 331230d1ce8315624f332531a587c18b83e05a8409b319f2ed5825d1f2cb4224 |
| memos-40f8e832.md | https://raw.githubusercontent.com/MemTensor/MemOS/40f8e832/README.md | commit 40f8e832 2026-07-09 | first README appearance of 88.83 etc.; prose says 92.34/93.40 (conflict) | 15422 | 4c1fa8492b5d1e1a1b65701b687bbef82699e5549b51b9148cee491b85bbf80b |
| memobase-locomo-commits.json | https://api.github.com/repos/memodb-io/memobase/commits?path=docs/experiments/locomo-benchmark/README.md | as-of 2026-09-12 | path history (6 commits) | 26607 | 7019af5d7081d5918baa193715517691e426f5afd6b1d39c7efef8836a82bb75 |
| memobase-locomo-scan.txt | derived | 2025-05-05..2025-07-12 | 75.78 first present at 56b63369 2025-07-12 | 353 | 75f714e8a010db3753dfc5670c252b656d071add790d15ce26bd0eba9cc35c7b |
| memobase-readme-commits.json | https://api.github.com/repos/memodb-io/memobase/commits?path=readme.md | as-of 2026-09-12 | path history (53 commits) | 194265 | dbdb429dbffe6ed6c050e4be79472a552c0040987b198bf92ab1aff4dbda44d5 |
| memobase-readme-scan.txt | derived | 2024-10-04..2025-11-23 | under100ms/40-50% first 578e172ca0 2025-08-11; 500~1000ms first 3a8f6fcb50 2025-07-16 | 4285 | 98533a198f7a612de5e6353be01887163b63884b9560fd22308b9e468f36c446 |
| memos-readme-commits.json | https://api.github.com/repos/MemTensor/MemOS/commits?path=README.md | as-of 2026-09-12 | path history (65 commits) | 330990 | 598994992ed3ef0c506132bcc27d9bf5f603a3c021249f97c0d3d26842054905 |
| memos-readme-scan.txt | derived | 2025-07-06..2026-08-25 | 88.83 first present at 40f8e832 2026-07-09 | 3892 | 0f26a6f76527d45bf5040042cb98ae975dd1a16d716987576ab764558da912a3 |
