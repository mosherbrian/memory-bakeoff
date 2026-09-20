# Assay second-driver — Letta LoCoMo harness located (independent re-fetch)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0 model spend, one public re-fetch
**Thread:** second-driver re-derivations (portfolio provenance)
**Target:** `team/ALICE-LETTA-LOCOMO-HARNESS-AND-PIN-STATUS.md` (Alice) and the
ledger row L-S12-02 provenance correction.
**Verdict: AGREE** on the located-harness claim — independently re-fetched,
byte-identical, and every structural claim checked against the file. The
**74.0% score itself remains `vendor-only`** (not run), and I say so below.

## What was re-derived

| Claim | Independent result |
|---|---|
| harness URL is linked from the pinned Letta blog | **confirmed** — exactly **1** occurrence in the WayBack HTML, `…/locomo_benchmark.py#L784` |
| WayBack blog snapshot sha | `82e12dc9929415…` — matches Alice's pin and the local receipt |
| blog states 74.0% | **confirmed** — "Filesystem … scores **74.0%** of the LoCoMo benchmark" |
| raw harness bytes | **re-fetched 2026-09-13**: 34,265 B, sha256 `0a2f9751a72c7729c7de812f35a4d1cbf15594bc0b2435f676a0eda938ce606b` |
| equals Alice's receipt | `cmp` on the re-fetch vs `team/row-letta-locomo-harness-receipts/locomo_benchmark.py` → **byte-identical** |

`git`-style identity: a fresh `curl` of
`raw.githubusercontent.com/letta-ai/letta-leaderboard/main/leaderboard/locomo/locomo_benchmark.py`
produced the same size and sha as the stored receipt, so the pinned artifact is
re-fetchable, not a one-off local file.

## Content claims checked against the fetched file

| Alice's characterization | grep evidence |
|---|---|
| defines `LoCoMoQAFileBenchmark` | `line 48: class LoCoMoQAFileBenchmark(Benchmark)` |
| chunking `turn / session / time_window / secom` | `690–695` dispatch + `699` `_chunk_by_turn_…` |
| embedding `text-embedding-3-large` @1536 | `800: embedding_model="text-embedding-3-large"`, `803: embedding_dim=1536` |
| tools `search_files` + `answer_question` | `859: tools=["search_files", "answer_question"]` |
| `grep`/`open_file`/`close_file` commented out | `860: # "grep", "open_file", "close_file",` |
| `InitToolRule(search_files)`, `TerminalToolRule(answer_question)` | `867` / `864` |
| LLM judge `grade_sample` | `30` import, `93: grade_sample(...)` |
| `gpt-4o-mini` for segmentation/summaries | `436`, `661: model="gpt-4o-mini"` |

So the blog's 74.0% is tied to a concrete, readable arm under the pinned
reader/embedder/judge — the "requires a local re-implementation" blocker is
genuinely gone.

## What this does **not** verify (class stays `vendor-only`)

- The **74.0 run was not executed** by us; no dataset run, no reader/judge
  re-run. Locating a harness is a provenance upgrade, not a reproduced score,
  and must not be cited as one.
- The dataset defaults to an in-repo `leaderboard/locomo/locomo10.json` path we
  did not fetch or check.
- The repo is archived / superseded by `letta-ai/letta-evals` (Alice's caveat,
  not re-checked here).
- This second-driver covers the **located-harness** claim; Alice's second,
  separate finding (stale "unpinned" ledger cells for four already-pinned blogs)
  is a docs-hygiene propagation item, out of scope for this re-derivation.

## Receipts

- Independent re-fetch: `/tmp/assay-locomo.py` (ephemeral) — 34,265 B, sha256
  `0a2f9751a72c7729c7de812f35a4d1cbf15594bc0b2435f676a0eda938ce606b`
- Stored receipt it matched: `team/row-letta-locomo-harness-receipts/locomo_benchmark.py`
- Pinned blog: `team/row-pin-receipts/letta-wayback-20250813233542.html`
  sha256 `82e12dc992941523c774bfa31b20058c5f84a92f8c0493939653a2ce65ccc713`
- Re-fetch command: `curl -sS -L https://raw.githubusercontent.com/letta-ai/letta-leaderboard/main/leaderboard/locomo/locomo_benchmark.py`

— **Assay** (`worker-glm-dsh2`). No tree modified; public fetch only.
