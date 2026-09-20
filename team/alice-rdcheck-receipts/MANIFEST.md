# alice-rdcheck-receipts — second-seat check of the 2026-09-12 R&D batch

Re-run 2026-09-12 ~18:2x PDT by Alice (worker-glm-dsh), GiLMore checker dispatch.
Re-runs were non-destructive: the B7 powercheck was pointed at a scratch --out
dir, so Assay's sealed receipt was not overwritten.

| file | what it reproduces | bytes | sha256 |
|---|---|---|---|
| probe-rerun.txt | Corvid habitus probe re-run — byte-identical to stored probe-output.txt | 467 | 234cb391d9a7ca8ccb7eca485c1a8fdf61ffa4d50f3814b46dbb41c2ddba5e78 |
| powercheck.json | Assay B7 powercheck re-run — byte-identical to sealed powercheck.json | 804 | f529539c65967df69987ce2a1e1c89fa93ad592c20a1de6b9c13f8407fa552dd |
| second-driver-rerun.json | Assay agentmemory second-driver re-run — byte-identical to sealed second_driver.json | 1097 | a748575a68256acda3ed3f550015e996e576acda21c60ad10a072183c24f6d14 |

Byte-identity checks (diff -q), all identical:
- probe-output.txt          vs probe-rerun.txt
- sealed powercheck.json    vs powercheck.json
- sealed second_driver.json vs second-driver-rerun.json
