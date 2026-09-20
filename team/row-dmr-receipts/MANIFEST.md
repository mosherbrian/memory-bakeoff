# row-dmr-receipts — MemGPT DMR attribution check

Fetched 2026-09-12 ~18:3x PDT by Alice (worker-glm-dsh), RD pulse.
Question: does the MemGPT paper report the 93.4% DMR number Zep attributes to it?

| file | source | bytes | sha256 |
|---|---|---|---|
| memgpt-2310.08560v2.html | https://arxiv.org/html/2310.08560v2 (Table 2) | 134657 | 030ddb6f967d94b17b8fbce6ab2ad1c0ba619a326bc7af636a3798e04e266522 |
| memgpt-2310.08560-ar5iv.html | https://ar5iv.labs.arxiv.org/html/2310.08560 (independent render) | 114504 | 0b4467a4a9f54544fe26e4d212ef23d5fa26a9405e3d76423c17032012a4b9cc |

Table 2 (v2) verbatim rows: GPT-4 Turbo / MemGPT 93.4% (ROUGE-L 0.827);
GPT-4 / MemGPT 92.5%; GPT-3.5 Turbo / MemGPT 66.9%; fixed-context baselines
GPT-3.5 38.7%, GPT-4 32.1%, **GPT-4 Turbo 35.3%**.
