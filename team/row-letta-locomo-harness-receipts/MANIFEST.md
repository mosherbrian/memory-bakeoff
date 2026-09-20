# receipts — Letta LoCoMo harness located (Alice, 2026-09-13)

| file | bytes | sha256 | source |
|---|---|---|---|
| `locomo_benchmark.py` | 34265 | `0a2f9751a72c7729c7de812f35a4d1cbf15594bc0b2435f676a0eda938ce606b` | https://raw.githubusercontent.com/letta-ai/letta-leaderboard/main/leaderboard/locomo/locomo_benchmark.py (fetched 2026-09-13) |

## Discovery path

The URL is linked from the pinned Letta blog itself (`team/row-pin-receipts/letta-wayback-20250813233542.html`, sha `82e12dc9…`):

```
https://github.com/letta-ai/letta-leaderboard/blob/main/leaderboard/locomo/locomo_benchmark.py
```

## What the file is

Defines `LoCoMoQAFileBenchmark(Benchmark)` — the file-based LoCoMo QA arm the blog's 74.0% describes: session/secom/turn/time_window chunking, `text-embedding-3-large`@1536, tools `search_files`+`answer_question`, LLM-judge `grade_sample`, gpt-4o-mini for segmentation/summaries.
