# Letta LoCoMo harness — commit-pinned reproduction receipt (Alice, 2026-09-13)

Repo: `letta-ai/letta-leaderboard` (archived) · **commit** `802a794263279839f9384bfd518ca9da3d059d37` (main head, 2025-10-16T22:53:15Z, "Update README.md")

Fetched from `https://raw.githubusercontent.com/letta-ai/letta-leaderboard/802a7942…/<path>`.

| file | bytes | sha256 |
|---|---|---|
| `locomo_benchmark.py` | 34265 | `0a2f9751a72c7729c7de812f35a4d1cbf15594bc0b2435f676a0eda938ce606b` |
| `locomo_agent.txt` | 1742 | `b1861386f6af41eb39fc5b48e1dbf7e2c9093155f6d5b0a363667adb70b920a0` |
| `benchmark.py` | 2996 | `e1a743aac228b777535e1020d4f584ae2af51b757a88c99ccacee45ecf871ee6` |
| `utils.py` | 20863 | `bf00acc00d2b970ee2b04774ff0f6355d6fa875f5a9e15ed1a5fcfdb03c8212b` |
| `evaluate.py` | 12053 | `4eb4345ee410d997ff6dd07ceb2df71af3359df17ee3903d19b7174df1579ab6` |
| `locomo10.json` | 2805274 | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` |

## Stability check

`locomo_benchmark.py` at commit `802a7942…` hashes to `0a2f9751…` — **identical** to the earlier `main`-tip fetch (Assay's independent re-fetch also got `0a2f9751…`), so the mutable-tip caveat is closed for this file.

## Dataset (was an open caveat)

`locomo10.json` **is committed** (2,805,274 B, sha `79fa87e9…`). Parsed: **10 samples, 1986 QA**, category counts **{1:282, 2:321, 3:96, 4:841, 5:446}** — exactly the authoritative map counts the team derived earlier from `snap-research/locomo` (2nd independent source for those counts).

## Entrypoint (from the repo README)

```
python -m leaderboard.evaluate --benchmark=letta_bench --dataset_size=100 --timeout=100 --repeat=3 --benchmark_variable=core_memory_read_benchmark --model=openai-gpt-4.1-mini
```

The LoCoMo arm constructs `LoCoMoQAFileBenchmark(chunking_strategy="session")` (`locomo_benchmark.py` bottom); needs a Letta server, `OPENAI_API_KEY` (reader + LLM judge), and `text-embedding-3-large`@1536.
