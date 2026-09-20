# Vendor claim transparency register — what we can re-derive, and what we can only take on faith

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated from RD-THREADS §Alice
thread 2, consolidating the day's re-derivations before P2 tables cite a
vendor number · **Cost:** $0 (synthesis of already-hashed receipts; no new
fetch), one turn.

**How to use it.** Before a P2 table cites a vendor headline, find the row.
"Re-derivable" means we recomputed the number offline from the vendor's shipped
data. "Self-attested" means the vendor documents a recipe but ships no raw run.
"One-origin" means the number exists in exactly one artifact. Nothing here says
a number is false; it says what our evidence can carry.

## Register

| System (rows) | Headline | Shipped raw data? | Durable artifact? | Our verdict | Receipt |
|---|---|---|---|---|---|
| **Memobase** (L-S15-01/02) | LoCoMo 75.78 / 70.91; per-category | **Yes** — raw per-question judge fixtures + scoring script | repo pin `358c16bb` | **Re-derivable, exact** (≥4 dp; both versions) | `ALICE-REDERIVE-MEMOBASE-7578.md` |
| **agentmemory** (L-LME-01) | LongMemEval-S R@5 95.2 · R@10 98.6 · R@20 99.4 · MRR 88.2 | **Yes** — per-question ranked lists | repo pin `e04ba888` | **Partial** — R@5/R@10/NDCG exact; **R@20/MRR self-attested** (lists truncated at 10) | `ALICE-REDERIVE-AGENTMEMORY-LONGMEMEVAL.md` |
| **Mem0 current** (L-S15-01 Pasted "Mem0 66.88") | LoCoMo 92.5 (docs/blog) | **Yes** — harness + per-question results (submodule) | repo (`memory-benchmarks@4b61c5d3`) | **Shipped run re-derivable (91.56); headline 92.5 NOT** — docs rows weigh to 90.23 | `ALICE-REDERIVE-MEM0-LOCOMO.md` |
| **Mem0 2025 paper** (L-S13-02, L-S15-01 rival block, supernode) | LangMem 58.10 · Zep 65.99 · OpenAI 52.90 · Mem0 66.88/68.44 | **No** — eval code is numeric-only; no raw shipped | paper only | **Arithmetic-consistent; measurement not shipped.** Rival block = one origin | row 20; `ALICE-MEM0-2025-EVAL-CHECK.md` |
| **MemBukkit** (L-LME-02) | LongMemEval-S 92.6 (official gpt-4o judge) | **No** — summary + repro recipe; run not shipped | repo docs (run lives in CI) | **Self-attested** (recipe unusually complete) | `ALICE-MEMBUKKIT-926-CHECK.md` |
| **Hindsight** (L-HS-02a/02b/03) | LongMemEval **94.6** (AMB, Gemini answer+judge) · **91.4** (OSS-120B judge) · "highest score of any memory system" | Harness yes; **AMB ships raw per-question rows**; the continuous dashboard strips detail and has no LongMemEval | AMB repo raw outputs; Chronos paper Table 2 | **94.6 = `vendor-only`, recomputed exact (473/500) from AMB raw rows** · **91.4 = `vendor-only` + `third-party-attributed`** (the Chronos paper cites Hindsight's number/judge config; it does not measure Hindsight — Corvid's class refinement) · **"highest" = `not established`** (Chronos High 0.956 is Claude Opus 4.6; GPT-4o-matched Chronos 92.60 < 94.6) | `ALICE-HINDSIGHT-AMB-REDERIVE.md`, `ALICE-CHRONOS-956-CHECK.md`, `ALICE-HINDSIGHT-THIRD-PARTY.md` |
| **MemOS** (L-S16-01/02a/02b) | LoCoMo 88.83 · LongMemEval **89.20** self; **73.07/68.68** (TiMem) · **77.8** (SmartSearch) | **No** — README only; not in paper v1–v4 | README commit `40f8e832`; OmniMemEval results doc | **Self-attested + `third-party-measured` gap (L-S16-02b)**: TiMem measured it (LoCoMo 69.24, LongMemEval 73.07/68.68); three independent values cluster 69–78 vs 89.20 self; metric pinned (OmniMemEval `gpt-4o-mini` judge / `gpt-4.1-mini` answer); 3/6 categories exactly 100 under its own harness | `ALICE-MEMOS-SELF-VS-INDEPENDENT.md`, `ALICE-OMNIMEMEVAL-METRIC.md`, `ALICE-SMARTSEARCH-CLUSTER.md` |
| **Zep** (L-S17-01/02) | DMR 94.8 · LoCoMo 65.99 · LoCoMo 75.14 · LongMemEval 71.2 | **No** — papers/tables only | Zep paper + memobase table | **Arithmetic-consistent; four numbers, none comparable** | `ALICE-REDERIVE-ZEP-HEADLINE.md`; `ALICE-DMR-ATTRIBUTION-CHECK.md` |
| **LangMem** (L-S13-01/02) | 58.10 (via Mem0's run) | **No** | Mem0 paper | **One-origin** (Mem0 measured a rival) | row 20 |
| **Letta** (L-S12-02/03) | 74.0% files-only LoCoMo | **No** | blog, Wayback-pinned | **Self-reported** | `ALICE-MUTABLE-SOURCE-PINS.md` |
| **a_mem** (L-S14-01/02) | six-fold multi-hop; 85–93% tokens | paper body v1 | paper | **Partial** — "six-fold" sourced but narrower (1 model/1 category/ROUGE-L); "85–93%" aggregator-derived | `2502.12110v1` body, sha `5d94b7aa…`; `ALICE-LEDGER-UNSOURCED-ROWS-AUDIT.md` |

## What this establishes for P2

1. **Exactly one vendor headline is fully re-derivable offline from raw rows:
   Memobase** (75.78/70.91 and per-category). **agentmemory** is second
   (R@5/R@10/NDCG). Everything else is self-attested, arithmetic-checked only,
   or one-origin.
2. **"They publish a recipe" ≠ "we can check the number."** MemBukkit and
   Hindsight document full recipes; neither ships the run that produced the
   headline. Mem0 ships a run that disagrees with its own headline.
3. **The Mem0 2025 paper is a single point of failure** for four rival numbers
   (LangMem, Zep, OpenAI, Mem0's own older scores). One measurement; no raw.
4. **Two cross-cutting rules before any per-category table ships:**
   - pin **metric + judge + reader + split + top-k** (Corvid's adopted checklist);
   - pin the **category id→name map** — the authoritative LoCoMo map is
     1=multi-hop, 2=temporal, 3=open-domain, 4=single-hop, 5=adversarial, and
     Memobase's published labels are permuted (`ALICE-LOCOMO-CATEGORY-MAP.md`).
5. **"LongMemEval" is not one number.** At least eight graded referents are in
   play (agentmemory 95.2 recall · MemBukkit 92.6 official · MemOS 89.20 unknown
   · Hindsight 94.6 self / 91.4 judge-swapped · Zep 71.2 / +18.5% · Mem0 94.4 /
   91.0 self-graded · OMEGA 95.4 self-graded · full-context 60.2). Name the
   grader or don't cite it.
6. **Class refinement (Corvid, 23:1x): `third-party` = an external party *measured
   the system itself*; `third-party-attributed` = an external party *cites the
   vendor's number/config* (stays `vendor-only`).** Under that split:
   - **`third-party-measured` = MemOS L-S16-02b** — TiMem (`arXiv:2601.02845`)
     ran the system: LoCoMo 69.24 and LongMemEval 73.07/68.68 vs self 88.83/89.20.
   - **`vendor-only` + `third-party-attributed` = Hindsight 91.4** — the Chronos
     paper (`arXiv:2603.16862` Table 2) cites Hindsight's number and OSS-120B
     judge config; it does **not** measure Hindsight.
   Hindsight's **94.6** stays `vendor-only` (our exact recompute from AMB raw
   rows), and its **"highest score"** superlative is `not established` (Chronos
   High 0.956 is a different, stronger answerer model; AMB itself says the rows
   are "not directly comparable").

## Method and limits

- Pure synthesis of receipts produced and hashed today (each row names its
  artifact + pin). No new network fetch, no benchmark, no LLM.
- "Re-derivable" is bounded by what the vendor shipped; a vendor could hold data
  privately. "Self-attested" is not an accusation — it is the evidence class we
  can carry, and the row's ledger class is unchanged.
- Rows still `unsourced` (**L-S16-03 only**) are not repeated here. L-S14-02
  moved out on 2026-09-13 (`unsourced` → `vendor-only (narrowed)`; see
  `ALICE-LEDGER-UNSOURCED-ROWS-AUDIT.md`).
