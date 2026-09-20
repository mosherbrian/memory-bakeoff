# rd-threads-fetches — pinned primary sources for the R&D thread continuation

Fetched 2026-09-12 ~17:3x PDT by Corvid (worker-glm-dsh3) with `curl -sSL`
(raw bytes, no decoder) for the three open R&D threads. All URLs are
`raw.githubusercontent.com` blobs at exact commits, so they are commit-frozen
by construction. SHA-256 is over the exact bytes.

| file | source URL | pin | bytes | sha256 |
|---|---|---|---|---|
| agentmemory-README.md | https://raw.githubusercontent.com/rohitg00/agentmemory/e04ba88819c365c9acf9d6661ea802143e728bd6/README.md | commit `e04ba888` | 99808 | `49b467eb8da8f74115ac5ed0ea8cc6371c32d1c806b8a09f857319c28204147d` |
| agentmemory-COMPARISON.md | https://raw.githubusercontent.com/rohitg00/agentmemory/e04ba88819c365c9acf9d6661ea802143e728bd6/benchmark/COMPARISON.md | commit `e04ba888` | 10687 | `d74a5290746b19f732d77668769231ae0259c31b6a7e2fe85e2e22bb78f611d4` |
| agentmemory-LONGMEMEVAL.md | https://raw.githubusercontent.com/rohitg00/agentmemory/e04ba88819c365c9acf9d6661ea802143e728bd6/benchmark/LONGMEMEVAL.md | commit `e04ba888` | 3628 | `72a5f411a969691bb893d6cc3613ae4737fa27d1e9e0de64c5e209322244c267` |
| membukkit-README.md | https://raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/README.md | commit `f28a2e58` | 14923 | `a462d9cc3ad652b017ffbb9e2679fc02fda609cf51c8751784d7175706d4eef3` |
| membukkit-benchmarks-guide.md | https://raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/docs/guide/benchmarks.md | commit `f28a2e58` | 11656 | `11c34675e7cca39c0c05bf8483da8961f9e308f8b1e78efee554af24fa5040da` |
| hindsight-README.md | https://raw.githubusercontent.com/vectorize-io/hindsight/ebad478240d3171bb88201ececda5e8d9883d22d/README.md | commit `ebad4782` | 24831 | `7a992a271c1f5480b408412e2165cd93d56cb6426415a9bb5531b129a43c8224` |

## Pins used

- agentmemory `e04ba88819c365c9acf9d6661ea802143e728bd6` (0.9.29) — same pin
  as the row-11 survey and the P1 license receipt.
- membukkit `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807` (0.1.0) — same pin as
  the row-11 survey and the P1 license receipt.
- hindsight `ebad478240d3171bb88201ececda5e8d9883d22d` (v0.9.2) — same pin as
  the row-11 survey and the P1 license receipt.

## Reproduction

```bash
BASE=https://raw.githubusercontent.com
curl -sSL $BASE/rohitg00/agentmemory/e04ba88819c365c9acf9d6661ea802143e728bd6/README.md | sha256sum
curl -sSL $BASE/rohitg00/agentmemory/e04ba88819c365c9acf9d6661ea802143e728bd6/benchmark/COMPARISON.md | sha256sum
curl -sSL $BASE/rohitg00/agentmemory/e04ba88819c365c9acf9d6661ea802143e728bd6/benchmark/LONGMEMEVAL.md | sha256sum
curl -sSL $BASE/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/README.md | sha256sum
curl -sSL $BASE/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/docs/guide/benchmarks.md | sha256sum
curl -sSL $BASE/vectorize-io/hindsight/ebad478240d3171bb88201ececda5e8d9883d22d/README.md | sha256sum
```

## Scope

These are **attribution receipts**: they establish what each vendor's pinned
page says. They do not make any vendor number `verified-by-us` — no engine was
installed or run, and no vendor benchmark was reproduced.

## Addendum — Habitus DEVELOPMENT.md (2026-09-12, R&D pulse)

Fetched to check the survey's `README.md:134-139` / `Hit@5 0.955` pointer,
which is false.

| file | source URL | pin | bytes | sha256 |
|---|---|---|---|---|
| habitus-DEVELOPMENT.md | https://raw.githubusercontent.com/munch2u-a11y/Habitus-AI/f93b770e4b3c1875151dc13eb90421598c3efa5f/DEVELOPMENT.md | commit `f93b770e` | 12567 | `5a86a199477108204d730ec5a4e387433a7b24326cdb05332fbdc76798847d9c` |

Finding: `0.955`/`Hit@5` appears in neither the pinned `README.md`
(sha `8449b7e7…`) nor this `DEVELOPMENT.md`; the latter reports only LLM-free
diagnostic trials (100% pattern reconstruction, <0.8 ms/turn, 100% LOOK/DO
routing). `RESEARCH-4-ENGINES-SURVEY.md:53` is corrected in place.
