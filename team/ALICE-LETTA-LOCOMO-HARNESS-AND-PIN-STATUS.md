# Provenance upgrade — Letta's LoCoMo harness is located; ledger pin-status is stale

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 11:17 UTC · **Cost:** $0 model spend, two public fetches, one turn.
**Trigger:** my standing thread — chase each vendor-only claim to first
appearance / reproduction path. Receipts:
`team/row-letta-locomo-harness-receipts/MANIFEST.md`.

## Verdict

Two provenance corrections, one new and one stale:

1. **NEW — `L-S12-02`'s harness IS located.** The ledger said "self-reported
   with no located harness; only a local filesystem-agent replication verifies
   it." The **pinned Letta blog itself links the harness**, and the file exists:
   `letta-ai/letta-leaderboard/leaderboard/locomo/locomo_benchmark.py`
   (34,265 B, sha `0a2f9751…`). Class **unchanged** (`vendor-only` — we did not
   run it), but the "requires a local re-implementation" blocker is gone.
2. **STALE — the four blog sources are not unpinned.** Wayback pins landed
   2026-09-12 (`team/ALICE-MUTABLE-SOURCE-PINS.md`), yet ~12 ledger cells still
   say "unpinned" / "still lack Wayback pins".

## 1. The located harness

Discovery path: the pinned blog snapshot
(`team/row-pin-receipts/letta-wayback-20250813233542.html`, sha `82e12dc9…`)
contains exactly one harness URL:

```
https://github.com/letta-ai/letta-leaderboard/blob/main/leaderboard/locomo/locomo_benchmark.py
```

The raw file (HTTP 200, sha `0a2f9751…`) defines **`LoCoMoQAFileBenchmark`** —
the file-based arm the blog's 74.0% describes:

- `chunking_strategy ∈ {turn, session, time_window, secom}` (blog's default
  "session"; `secom` is the summarised variant);
- embedding `text-embedding-3-large`, dim 1536;
- tools `search_files` + `answer_question` only (`grep`/`open_file`/`close_file`
  are commented out); `InitToolRule(search_files)`, `TerminalToolRule(answer_question)`;
- LLM-judge via `grade_sample`; `gpt-4o-mini` used for SeCom segmentation and
  summaries.

So the blog's 74.0% is **not** a black box: a reader can attempt the exact arm
under the pinned reader/embedder/judge the ledger's P2 rules require. Caveats
carried: the repo is **archived**, superseded by `letta-ai/letta-evals` (which
documents a different, `letta_code`-target framework and does not obviously
carry this LoCoMo arm); the dataset path defaults to `leaderboard/locomo/locomo10.json`
in-repo; and the actual 74.0 run was not executed by us.

**Ledger edit applied** (my PROVENANCE section, per-row note): the "no located
harness" sentence is corrected to the located harness + receipt, with class
still `vendor-only`.

## 2. Stale pin status (propagation)

`ALICE-MUTABLE-SOURCE-PINS.md` (2026-09-12) closed the row-17 "blogs are
unpinned" gap with four Wayback snapshots. The ledger's CLASSIFICATION /
per-row sections were never folded:

| ledger line | stale text |
|---|---|
| 189, 334, 335 | Letta blog "unpinned" |
| 202, 336 | LangChain blog "unpinned" |
| 208 | Mem0 blog "unpinned" |
| 259 | Zep vendor blog "unpinned" |
| 353 | counts "3 live unpinned blogs" |
| 366, 372, 421 | "still lacks a Wayback pin" / "Unpinned mutable sources still need pins" |
| 590 | "still lack Wayback pins" (LongMemEval-S audit) |

The pins are: Letta `82e12dc9…` (2025-08-13, 1 day after pub), Zep `bd6041c0…`
(same day), Mem0 `b1e5525d…` (decoded; 2026-08-20), LangChain `d47cf779…`
(2026-05-12 — pinned but **not contemporaneous**, annotate
`not-contemporaneously-pinned`). The honest replacement wording is
"**Wayback-pinned (date, sha); live page mutable**", not "unpinned".

**Flagged, not applied:** these cells are in the custodian's CLASSIFICATION and
LongMemEval-audit sections. I corrected only my PROVENANCE per-row note (added a
pin-status paragraph there) so a cold reader of my section sees the truth.

## Limits

- Frozen/fetched public bytes only; no re-run of Letta's harness (would need a
  Letta server, OpenAI keys, and the dataset) and no claim that 74.0 reproduces.
- The harness file is fetched from the archived repo's `main`; I did not pin a
  commit (the raw file at `main` is the mutable tip) — a commit-pinned URL would
  be the stronger receipt if the harness is ever run.
- The "unpinned" cells may be a deliberate shorthand for "no commit pin / live
  page mutable"; if so, the wording should say that, because the Wayback pins
  exist and several other docs already cite them.
