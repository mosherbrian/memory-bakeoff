# Letta LoCoMo — commit-pinned reproduction recipe (closes Assay's two caveats)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 11:27 UTC · **Cost:** $0 model spend, public fetches only, one turn.
**Trigger:** follow-up to `ALICE-LETTA-LOCOMO-HARNESS-AND-PIN-STATUS.md` and
Assay's second-driver (`ASSAY-SECOND-DRIVER-LETTA-LOCOMO-HARNESS.md`), which left
two caveats: the harness was pinned only at the mutable `main` tip, and the
in-repo dataset was "not fetch[ed] or check[ed]". Both are now closed.

**Receipts:** `team/row-letta-locomo-harness-receipts/pinned-802a7942/MANIFEST.md`.

## Verdict

The L-S12-02 reproduction path is now **fully specified and commit-pinned**:
harness code, agent system prompt, judge/driver, **and the dataset** are all
committed at one commit and hashed. The 74.0% score itself is still **not run by
us** — class stays `vendor-only` — but nothing about the recipe is now unknown.

## Commit pin

`letta-ai/letta-leaderboard` (archived) · **commit
`802a794263279839f9384bfd518ca9da3d059d37`** (main head, 2025-10-16T22:53:15Z).

| file at the pin | bytes | sha256 |
|---|---:|---|
| `leaderboard/locomo/locomo_benchmark.py` | 34265 | `0a2f9751…` (== `main` tip == Assay's re-fetch) |
| `leaderboard/locomo/locomo_agent.txt` | 1742 | `b1861386…` |
| `leaderboard/benchmark.py` | 2996 | `e1a743aa…` |
| `leaderboard/utils.py` | 20863 | `bf00acc0…` |
| `leaderboard/evaluate.py` | 12053 | `4eb4345e…` |
| `leaderboard/locomo/locomo10.json` | 2805274 | `79fa87e9…` |

The harness file is **byte-stable across three independent fetches** (my
`main` tip, my commit pin, Assay's re-fetch), so the mutable-tip caveat is
closed for it.

## Dataset — was Assay's open caveat, now checked

`locomo10.json` **is committed in the repo** (2,805,274 B, sha `79fa87e9…`).
Parsed locally: **10 samples, 1986 QA**, category counts
**{1: 282, 2: 321, 3: 96, 4: 841, 5: 446}** — exactly the authoritative counts
the team derived earlier from `snap-research/locomo`
(`ALICE-LOCOMO-CATEGORY-MAP.md`). That is a second, independent source for the
counts, and it means the harness does not need an external dataset download.

## Recipe, as pinned

- **Prompt:** `locomo_agent.txt` (`b1861386…`) — "conversation history … provided
  as a series of files … use search_files … final answer_question … convert
  relative time references … prioritize the most recent memory".
- **Arm:** `locomo_benchmark.py` bottom constructs
  `LoCoMoQAFileBenchmark(chunking_strategy="session")` (also `secom`), embedding
  `text-embedding-3-large`@1536, tools `search_files` + `answer_question`,
  judge `grade_sample`; `gpt-4o-mini` for segmentation/summaries.
- **Entrypoint:** `python -m leaderboard.evaluate … --model=openai-gpt-4o-mini`
  (repo README), with a Letta server and `OPENAI_API_KEY` for reader + judge.
- **Dataset:** in-repo at the pin.

## What is still not claimed

- The **74.0 run is not reproduced**; it needs a Letta server and OpenAI keys,
  and the repo is archived/superseded by `letta-ai/letta-evals`.
- I did not pin the *blog's* run configuration beyond the default `session`
  strategy; the blog does not state the chunking strategy explicitly, so the
  default is an inference from the code, not a vendor statement.
- No cost/latency numbers were checked here.

## Ledger

Pointer added to the PROVENANCE `L-S12-02` correction (my section): the located
harness now cites this commit-pinned recipe.
