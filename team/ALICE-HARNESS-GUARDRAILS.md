# Harness guardrails — what our own measurement must do, learned from ten vendor defects

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated capstone: the day's vendor
re-derivations each exposed a defect; these are the requirements for *our* P2/P3
harness so our numbers do not inherit them · **Cost:** $0 (synthesis of
already-hashed receipts), one turn.

**Scope.** This is not `RESEARCH-VENDOR-CLAIM-CHECKLIST.md` (how to judge someone
else's number) — it is what the portfolio must **build in** so its own numbers
are auditable. Each requirement cites the defect that motivated it.

| # | Requirement | Defect it prevents | Receipt |
|---|---|---|---|
| 1 | **Pin the judge *prompt*, not just the judge model.** Store it, hash it, version it. | MemOS scored **89.20** (OmniMemEval) and **77.8** (SmartSearch) under the *same* `gpt-4.1-mini`/`gpt-4o-mini` pair — the prompt moved it 11.4 pts. | `ALICE-LONGMEMEVAL-PROTOCOL-CARD.md` |
| 2 | **The system under test must not supply the judge prompt.** If a provider can override it, the run is self-graded. | `supermemoryai/memorybench` lets providers override `answerPrompt` **and** `judgePrompt` (`ProviderPrompts`; Zep example). | `ALICE-SUPERMEMORY-CLAIM-CHECK.md` |
| 3 | **Pin the dataset category id→name map in code, and assert it.** | Memobase's `generate_scores.py` permutes ids 1/3/4, so its published category names are wrong; the paper's prose order is *not* the JSON id order. | `ALICE-LOCOMO-CATEGORY-MAP.md` |
| 4 | **Ship per-question raw results with the full top-k used.** Never truncate the ranked list below the reported metric. | agentmemory's `retrieved_session_ids` is capped at 10, so its R@20 and MRR are **self-attested**, not re-derivable. | `ALICE-REDERIVE-AGENTMEMORY-LONGMEMEVAL.md` |
| 5 | **Run the full-context null under the same harness** and report it beside every score. | The LongMemEval full-context baseline swings **77.1% → 91.2% across frameworks with no retrieval change** — so a score without its null is uninterpretable. | `ALICE-SMARTSEARCH-CLUSTER.md` |
| 6 | **Every number carries answerer + judge + split + context budget + top-k.** | Hindsight 94.6 is Gemini/Gemini; MemBukkit 92.6 is gpt-5.4 reader + official gpt-4o judge; agentmemory 95.2 is judge-free recall — none comparable. | `ALICE-VENDOR-DATA-TRANSPARENCY.md` |
| 7 | **Distinguish *attributed* from *measured*.** An outside party citing the vendor's number is not an independent measurement. | The Chronos paper cites Hindsight's 91.4/judge config without measuring it → `third-party-attributed`, not `third-party`. | `ALICE-VENDOR-DATA-TRANSPARENCY.md` §6 |
| 8 | **Label and preserve failed/invalid runs; never let a config label stand in for a measurement.** | `product_ingest=True` let a raw run carry a product label (Habitus); OmniMemEval's generic "generous" judge differs from the official rubric. | `ALICE-HABITUS-CLASSFIX-CHECK.md`, `ALICE-OMNIMEMEVAL-JUDGE-CHECK.md` |
| 9 | **Re-derive before citing: recompute the aggregate from the raw rows and diff.** | Memobase reproduced exactly (good); Mem0's docs headline 92.5 did **not** reconcile with its own shipped 91.56 run. | `ALICE-REDERIVE-MEMOBASE-7578.md`, `ALICE-REDERIVE-MEM0-LOCOMO.md` |
| 10 | **Keep the artifact small enough to ship.** Hash + size if too large, with a re-fetch recipe. | Hindsight's dashboard strips per-question detail; the full data is ephemeral CI. | `ALICE-HINDSIGHT-CLAIM-CHECK.md` |

## The three that matter most

1. **Prompt > model.** Requirements 1–2 exist because a matched model pair still
   varied 11.4 points and one harness lets the subject rewrite the rubric. A
   pinned, hash-recorded judge prompt is the single highest-leverage control.
2. **Raw rows or it didn't happen.** Requirements 4, 9, 10 are the difference
   between a number and a receipt. A truncated or stripped artifact converts a
   measurement into an assertion.
3. **The null travels with the score.** Requirement 5 is the portfolio's E-1
   control; the 14 pp framework swing shows the null is not a constant.

## How to use it

- At P2 harness freeze: assert requirements 1–7 in the pre-registration; store
  the judge prompt hash, the category map, and the top-k.
- At P3 report time: for each headline, run requirement 9 (recompute from raw)
  and attach the null (5) and the full protocol line (6).
- At P4 close: requirement 7 governs how outside numbers are labeled.

## Method and limits

- Synthesis only; every item cites an artifact produced and hashed today under
  `team/row-*-receipts/`. No new fetch, benchmark, or LLM.
- These are guardrails for **our** harness, derived from vendor defects; they do
  not replace the charter's pre-registration or Verity's criteria review.
