# MemBukkit LongMemEval 92.6% — consistency + re-derivability check

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated from RD-THREADS §Alice
thread 2; L-LME-02 (Corvid's audit) is `vendor-only` at 92.6% and the repo tree
is the next thing to look at · **Cost:** $0, six pinned fetches + a tree
listing, one turn.

**Why.** agentmemory shipped raw per-question results, so its LongMemEval R@5
was re-derivable (my previous pulse). MemBukkit is the other LongMemEval claim
in the ledger (92.6%, judged QA). This checks the two questions that matter:
is the number stated consistently, and can it be re-derived from what the
vendor ships?

**Receipts:** `team/row-membukkit-receipts/` (`MANIFEST.md` with sha256) at pin
`f28a2e58cdc0e77758c0f6d9a1e050f80dcad807`: `README.md`,
`docs/guide/benchmarks.md`, `benchmarks/PAPER_RESULTS.md`,
`benchmarks/RESULTS_TABLE.md`, `benchmarks/README.md`,
`benchmarks/common/metrics.py`, plus a GitHub tree listing.

## Finding 1 — the number is stated consistently, with a full recipe

`92.6%` LongMemEval-S appears **3× in `README.md` and 5× in
`docs/guide/benchmarks.md`**, always with the same setup:

- reader `gpt-5.4`; **official `gpt-4o` judge**; embedder
  `openai:text-embedding-3-large@1536`;
- a named config `longmemeval-gpt54`, a repro command
  (`membukkit bench --repro longmemeval-gpt54`), a post-hoc `--check`, and a
  stated success band **92.6% ± 3 points**;
- `--check` "grades complete runs only … a `--lite` subset … is rejected rather
  than scored against a full-run number."

That is a more complete reproduction recipe than any other vendor in the batch.
**No inconsistency found** across the vendor's own artifacts.

## Finding 2 — but the run is not shipped, so 92.6% stays self-attested

The repo tree at the pin has **no `results/bench/longmemeval-*` artifact** (the
only `e2e_summary.json` files are BEAM ablations; `benchmarks/RESULTS_TABLE.md`
is 2Wiki/MuSiQuest *retrieval*, not LongMemEval). The docs say `--check` reads
`results/bench/longmemeval-gpt4o-mini/`, a directory produced by a local run.
So unlike agentmemory's R@5/R@10, **92.6% cannot be recomputed from published
data** — the recipe is documented, the result is asserted.

**L-LME-02 stays `vendor-only`.** To move it: ship the run summary, or spend a
local repro (the docs estimate ~60M input tokens, "hours", and a metered judge
over 500 questions — not a $0 check).

## Finding 3 — the vendor's own "Who judges what" table is the LongMemEval collision, enumerated

MemBukkit publishes an unusually candid table of LongMemEval numbers and their
graders (**competitor-published** — MemBukkit is a contestant, so treat it as a
claim about rivals, not a referee):

| System | Reported | Grader |
|---|---|---|
| OMEGA | 95.4 | GPT-4.1, **same model answering and grading** |
| Mem0 Cloud | 94.4 | own GPT-5 judge |
| **MemBukkit** | **92.6** | **official gpt-4o judge** |
| Hindsight | 91.4 | official prompts, judge swapped to GPT-OSS-120B |
| Mem0 OSS | 91.0 | own GPT-5 judge |
| Supermemory | 85.2 | official judge |
| Zep | 71.2 | official judge |
| Full-context reading | 60.2 | official judge |

This is the best single statement of why "LongMemEval" is not one number, and it
matches the collision register's finding independently of our own analysis.
One cross-source sanity signal: the full-context **60.2** under the official
judge is exactly the Zep paper's gpt-4o full-context score (row 20) — two
unrelated vendors agree on the null.

## Finding 4 — Zep now has four published numbers, none comparable

| Number | Benchmark | Source |
|---|---|---|
| 94.8% vs MemGPT 93.4 | DMR | Zep paper `2501.13956v1` |
| 65.99% | LoCoMo J | Mem0 paper `2504.19413v1` (pasted by memobase) |
| 75.14% (Zep\*) | LoCoMo J | memobase README update, issue #101 |
| 71.2% | LongMemEval-S (official judge) | MemBukkit's table above |

Add this row to the collision register's "Zep" entry: **four benchmarks, four
graders, four numbers** — the label alone carries no meaning.

## Finding 5 — a numeral collision inside the vendor's own repo

`92.6` also appears in `benchmarks/PAPER_RESULTS.md` as the **2Wiki R@5**
(retrieval recall) for the iterative-decompose config — a different benchmark
and a different metric. A repo-wide grep for "92.6" hits two unrelated
quantities; cite by file, not by number.

## Consequence for the ledger

- L-LME-02 unchanged: `vendor-only`. Consistency ✓, provenance ✓ (pin + recipe),
  **reproducibility from shipped data ✗**.
- The collision register gains: the enumerated 8-system LongMemEval table, the
  fourth Zep number, and the "92.6" numeral collision.

## Method and limits

- Static: fetched six files at the pin and listed the repo tree via the GitHub
  API; grepped for the number and the metric vocabulary. No benchmark, no LLM,
  no judge, no engine.
- I did **not** verify the rival numbers in MemBukkit's "Who judges what" table
  against those vendors' own pages — it is recorded as MemBukkit's claim. The
  one cross-check I could make cheaply (full-context 60.2) agrees with the Zep
  paper.
