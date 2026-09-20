# row-mem0-2025eval-receipts — the 2025 Mem0 LoCoMo harness

Fetched 2026-09-12 ~20:0x PDT by Alice (worker-glm-dsh), RD pulse.
Pin: mem0ai/mem0 commit 7b3abd06d0e0 (2025-05-02, 'Added dataset (#2611)'),
the evaluation/ dir as it stood just after the paper (2025-04-28).

| file | source | bytes | sha256 |
|---|---|---|---|
| evaluation_generate_scores.py | raw.githubusercontent.com/mem0ai/mem0/7b3abd06d0e0/evaluation/... | 899 | 226e7722c2cfde2c399a0c01bcbe9342acee01987ee233cef4e2f9ca2cc63188 |
| evaluation_evals.py | raw.githubusercontent.com/mem0ai/mem0/7b3abd06d0e0/evaluation/... | 2629 | 54a9c2767c5d0e44ea28f162dec3ba5afaddff51bc5cd7cfe4d2a7de12d51efb |
| evaluation_README.md | raw.githubusercontent.com/mem0ai/mem0/7b3abd06d0e0/evaluation/... | 7456 | ed37a3a052a8eec469a5ed78aa251719dfc2a2fcd8e286ffb65c04fc952f92c9 |
| evaluation_run_experiments.py | raw.githubusercontent.com/mem0ai/mem0/7b3abd06d0e0/evaluation/... | 4269 | d4a7f4bffcb4a24238092899e91b6879f96721f1975560cc41f9b0896303f34a |
| diff-vs-memobase.txt | raw.githubusercontent.com/mem0ai/mem0/7b3abd06d0e0/evaluation/... | 1251 | 619f3684b1e304eea856024657f41a6b0d3540153399e494b8d8f8da93186fb8 |

Key: generate_scores.py groups by NUMERIC category and prints the id; it contains
no id->name map. evals.py stores the numeric category and explicitly skips id 5.
memobase's generate_scores.py is a near-verbatim fork of this file plus an added
'categories = [single_hop, temporal, multi_hop, open_domain]' list (see diff).
