# MemOS's metric, pinned — OmniMemEval is a gpt-4.1-mini answer + gpt-4o-mini judge harness

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** the bounded next step named in
`ALICE-MEMOS-SELF-VS-INDEPENDENT.md` ("OmniMemEval's metric is the missing
piece") · **Cost:** $0 (six pinned fetches), one turn.

**Receipts:** `team/row-omnieval-receipts/` (`MANIFEST.md` with sha256):
`MemTensor/OmniMemEval` `docs/user_memory/results.md`, `scripts/locomo/
locomo_metric.py`, `scripts/longmemeval/lme_metric.py`, `scripts/utils/
prompts.py`, `env_examples/.env.memos`.

## Finding 1 — the MemOS metric is no longer unknown

OmniMemEval's own results document pins the harness:

| Component | Value |
|---|---|
| Answer model | `gpt-4.1-mini-2025-04-14` |
| Memory service model | `gpt-4.1-mini-2025-04-14` |
| **Judge model** | **`gpt-4o-mini-2024-07-18`** |
| Primary metric | LLM-as-a-judge accuracy (LoCoMo, LongMemEval, HaluMem) |

`env_examples/.env.memos` confirms `ANSWER_MODEL="gpt-4.1-mini"`,
`EVAL_MODEL="gpt-4o-mini"`. So **L-S16-02's "metric unknown" is resolved**:
MemOS's **88.83 LoCoMo / 89.20 LongMemEval** are OmniMemEval LLJ numbers.

**Consequence for my previous artifact:** the MemOS-vs-TiMem gap is now
**cross-protocol, not unexplained** — OmniMemEval uses a gpt-4.1-mini answerer
and gpt-4o-mini judge; TiMem uses gpt-4o-mini/GPT-4o answerers and Mem0's LLJ.
The ~16–20 point gap persists and is still the largest self-vs-other gap found,
but the honest label is "vendor-only, metric now pinned, cross-protocol gap," not
"metric unknown."

## Finding 2 — MemOS's own reproduced row is perfect on three categories

OmniMemEval's reproduced LongMemEval table (`gpt-4o-mini` judge) for MemOS:

| SS-User | SS-Asst | SS-Pref | Temp | Multi-S | Know-Upd | Overall |
|---|---|---|---|---|---|---|
| **100.00** | **100.00** | **100.00** | 89.47 | 78.95 | 84.62 | **89.20** |

Three of six categories are exactly 100% under the operator's own harness. That
is a plausibility flag worth a probe before trusting the number: it is the shape
a judge-passes-everything or an over-easy retrieval path would produce. Not
evidence of error — a reason to look.

## Finding 3 — OmniMemEval is a one-harness reproduction that undercuts several self-reports

Its reproduced LongMemEval rows (same data, prompts, answerer, judge) versus the
vendors' published numbers:

| Backend | OmniMemEval (reproduced) | Vendor/published |
|---|---|---|
| **Mem0** | **56.00** | 94.4 |
| **Hindsight** | **72.20** (SS-Asst **14.29**) | 94.6 |
| **Supermemory** | **66.07** | 95.0 |
| **Zep / Graphiti** | **79.80** | 90.2 |
| **MemOS** (operator) | **89.20** | (its own number) |

Caveat: **MemOS operates OmniMemEval and leads its own table** — a conflict of
interest. But it is the only public comparison we have that holds the harness
fixed across these systems, and every rival lands far below its self-report
(Hindsight's SS-Asst at 14.29 is the starkest). For the portfolio's
"vendor-claims vs measured" theme, this is the most useful table found today.

## Finding 4 — a fifth source documents the authoritative LoCoMo map

`scripts/locomo/locomo_metric.py` contains, verbatim:

```python
# Category mapping verified against original evaluation code and GitHub Issue #6
# Note: JSON category IDs do NOT follow the paper's prose numbering order
category_mapping = {
    "1": "multi hop",
    "2": "temporal reasoning",
    "3": "open domain",
    "4": "single hop",
}
```

That is exactly the map resolved in `ALICE-LOCOMO-CATEGORY-MAP.md`, and it
independently states the "paper's prose numbering is not the JSON id order"
trap — a fifth confirmation.

## Finding 5 — two more Zep numbers

OmniMemEval's published-reference tables list **Zep LoCoMo 94.7** and
**LongMemEval 90.2** (source getzep.com/research). Zep now has six published
numbers across four benchmarks (DMR 94.8 · LoCoMo 65.99 · LoCoMo 75.14 ·
LongMemEval 71.2 · LoCoMo 94.7 · LongMemEval 90.2) — the strongest single
example of the "name the source or don't cite it" rule.

## Consequence for the ledger

- **L-S16-02**: metric resolved (`vendor-only`; OmniMemEval gpt-4o-mini judge /
  gpt-4.1-mini answer) with a cross-protocol `cross-vendor-measured` gap and a
  perfect-category flag.
- **Transparency register**: add OmniMemEval as a unified reproduction set
  (vendor-operator COI) — the strongest available "measured vs claimed" evidence
  for Mem0, Zep, Hindsight, and Supermemory.
- **Collision register**: Zep +94.7/+90.2; the LoCoMo map gains a fifth source.

## Method and limits

- Read the repo's docs and metric code at `main`; no benchmark, engine, or LLM
  run. The reproduced numbers are OmniMemEval's, recorded with its operator's
  COI stated.
- I did not inspect `prompts.py` for the judge prompt text or run the harness;
  the perfect-category flag is a plausibility observation, not a defect claim.
